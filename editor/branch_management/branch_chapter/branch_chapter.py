from typing import Dict, Optional
from editor.branch_management.branch_event.utils import getNameForEvent
from editor.branch_management.branch_master import BranchManager
from widebrim.engine.const import PATH_DB_EV_INF2, PATH_DB_STORYFLAG, PATH_PROGRESSION_DB
from widebrim.engine.state.manager.state import Layton2GameState
from wx import TreeCtrl, TreeItemId
from widebrim.engine_ext.utils import substituteLanguageString
from widebrim.madhatter.common import logSevere

from widebrim.madhatter.hat_io.asset_dlz.ev_inf2 import EventInfoList
from widebrim.madhatter.hat_io.asset_storyflag import StoryFlag

class ChapterBranchManager(BranchManager):
    def __init__(self, state: Layton2GameState, treeCtrl: TreeCtrl, hideEditControls=False):
        super().__init__(state, treeCtrl, hideEditControls)
    
    def canItemHaveMoreConditions(self, item : TreeItemId) -> bool:
        if self._branchRoot == None or not(item.IsOk()):
            return False

        if self._isItemWithinPathToItem(item, self._branchRoot):
            while (parent := self._treeCtrl.GetItemParent(item)) != self._branchRoot:
                item = parent
        else:
            return False
        
        if self._treeCtrl.GetChildrenCount(item, False) < 8:
            return True
        return False

    def getCorrespondingItem(self, identifier: int) -> Optional[TreeItemId]:
        child, _cookie = self._treeCtrl.GetFirstChild(self._branchRoot)
        while child.IsOk():
            if self._getComparativeItemData(child) == identifier:
                return child
            child = self._treeCtrl.GetNextSibling(child)
        return None
    
    def getCorrespondingChapter(self, item : TreeItemId) -> Optional[int]:
        if self._isItemWithinPathToItem(item, self._branchRoot):
            while (parent := self._treeCtrl.GetItemParent(item)) != self._branchRoot:
                item = parent
        else:
            return None
        return self._getComparativeItemData(item)

    def getCorrespondingActivatedItem(self, item : TreeItemId):
        return None

    def createTreeBranches(self, branchParent: TreeItemId):

        def getStoryflagToEventMap() -> Dict[int, int]:
            # TODO - Would love to not load from filesystem - maybe pass EventManager information in so we don't reparse
            # TODO - Have to figure out a decent system for not making permanent changes to ROM
            evInf = EventInfoList()
            if (data := self._state.getFileAccessor().getData(substituteLanguageString(self._state, PATH_DB_EV_INF2))) != None:
                evInf.load(data)
            
            output = {}

            for indexEvInf in range(evInf.getCountEntries()):
                entry = evInf.getEntry(indexEvInf)
                if entry.indexStoryFlag != None:
                    if entry.indexStoryFlag not in output:
                        output[entry.indexStoryFlag] = [entry.idEvent]
                    else:
                        output[entry.indexStoryFlag].append(entry.idEvent)
            
            return output

        if self._branchRoot != None:
            self.remove()

        mapStoryflagToEvent = getStoryflagToEventMap()
        storyFlag = StoryFlag()
        if (data := self._state.getFileAccessor().getPackedData(PATH_PROGRESSION_DB, PATH_DB_STORYFLAG)):
            storyFlag.load(data)

        self._branchRoot = branchParent

        for group in storyFlag.flagGroups:

            if group.getChapter() == 0:
                if group.isEmpty():
                    continue

            flagRoot = self._addIntoTreeAtCorrectId(group.getChapter(), "Chapter " + str(group.getChapter()), self._branchRoot)
            for indexFlag in range(8):
                flag = group.getFlag(indexFlag)
                if flag != None:
                    # TODO - There are intentional false cases, e.g. chapter 760 which refers to an impossible puzzle
                    #        This stops the game from accidentally rolling over to chapter 0

                    # Check puzzle completion
                    if flag.type == 2:
                        nzLstEntry = self._state.getNazoListEntry(flag.param)
                        if nzLstEntry != None:
                            self._treeCtrl.AppendItem(flagRoot, 'Solve "%03i - %s"' % (nzLstEntry.idExternal, nzLstEntry.name))
                        else:
                            self._treeCtrl.AppendItem(flagRoot, "Progression blocker - illegal puzzle")
                    
                    # Check storyflag set
                    # TODO - Method to generate event friendly names, make it possible to update
                    elif flag.type == 1:
                        if flag.param in mapStoryflagToEvent:
                            if len(mapStoryflagToEvent[flag.param]) == 1:
                                self._treeCtrl.AppendItem(flagRoot, "Play event " + getNameForEvent(self._state, mapStoryflagToEvent[flag.param][0]))
                            else:
                                desc = ""
                                for indexEventId, eventId in enumerate(mapStoryflagToEvent[flag.param]):
                                    if indexEventId == 0:
                                        desc = str(eventId)
                                    elif indexEventId != len(mapStoryflagToEvent[flag.param]) - 1:
                                        desc = desc + ", " + str(eventId)
                                    else:
                                        desc = " or " + str(eventId)
                                self._treeCtrl.AppendItem(flagRoot, "Play events " + desc)
                        else:
                            self._treeCtrl.AppendItem(flagRoot, "Story flag " + str(flag.param) + " set")
    
    def addTrackedChapter(self, chapter : int):
        flagRoot = self._addIntoTreeAtCorrectId(chapter, "Chapter " + str(chapter), self._branchRoot)
    
    # TODO - Internalize these to make adding faster
    def addTrackedConditionalEvent(self, chapter : int, eventId : int):
        flagRoot = self.getCorrespondingItem(chapter)
        if flagRoot == None:
            logSevere("ManagerChapter: Failed to find chapter for conditional event!")
            return

        if self.canItemHaveMoreConditions(flagRoot):
            self._treeCtrl.AppendItem(flagRoot, "Play event " + getNameForEvent(self._state, eventId))
        else:
            logSevere("ManagerChapter: Desynchronized from StoryFlags! Failed to add conditional event.")
    
    def addTrackedConditionalPuzzle(self, chapter : int, internalPuzzleId : int):
        flagRoot = self.getCorrespondingItem(chapter)
        if flagRoot == None:
            logSevere("ManagerChapter: Failed to find chapter for conditional event!")
            return

        if self.canItemHaveMoreConditions(flagRoot):
            nzLstEntry = self._state.getNazoListEntry(internalPuzzleId)
            if nzLstEntry != None:
                self._treeCtrl.AppendItem(flagRoot, 'Solve "%03i - %s"' % (nzLstEntry.idExternal, nzLstEntry.name))
            else:
                self._treeCtrl.AppendItem(flagRoot, "Progression blocker - illegal puzzle")
        else:
            logSevere("ManagerChapter: Desynchronized from StoryFlags! Failed to add conditional puzzle.")

    def deleteTrackedChapter(self, chapter : int) -> bool:
        # NOTE - This doesn't match deletion behaviour on zero for original, be careful!
        item = self.getCorrespondingItem(chapter)
        if item == None:
            return False
        self._treeCtrl.DeleteChildren(item)
        self._treeCtrl.Delete(item)
        return True