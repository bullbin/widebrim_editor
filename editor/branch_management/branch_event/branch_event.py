from math import inf
from wx import TreeCtrl, TreeItemId
from typing import Any, Dict, Optional, Tuple, List, Type
from widebrim.engine.const import PATH_DB_EV_INF2, PATH_DB_RC_ROOT
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.engine_ext.utils import substituteLanguageString
from widebrim.madhatter.common import logSevere
from widebrim.madhatter.hat_io.asset_dlz.ev_inf2 import EventInfoList

from widebrim.madhatter.hat_io.asset_dlz.ev_lch import EventDescriptorBank, EventDescriptorBankNds
from editor.asset_management.event import EventConditionAwaitingViewedExecutionGroup, EventConditionPuzzleExecutionGroup, EventExecutionGroup, PuzzleExecutionGroup, TeaExecutionGroup
from .utils import getNameForEvent
from editor.branch_management.branch_master import BranchManager
# TODO - Improve removable support
# TODO - Improve comment renaming (can take same approach as tabs...)
# TODO - Multiple puzzle launcher entries should have same launcher (same behaviour as old implementation)

def _getCommentForEvent(eventId : int, eventDescriptor : Type[EventDescriptorBank]) -> str:
    if (entry := eventDescriptor.searchForEntry(eventId)) != None:
        return entry.description
    return ""

def _getCommentWithJoiner(originalName : str, eventId : int, eventDescriptor : Type[EventDescriptorBank]) -> str:
    comment = _getCommentForEvent(eventId, eventDescriptor)
    if comment == "":
        return originalName
    return originalName + " - " + comment

def _loadEventDescriptorBank(state : Layton2GameState) -> Type[EventDescriptorBank]:
    evLch = EventDescriptorBankNds()
    if (data := state.getFileAccessor().getData(substituteLanguageString(state, PATH_DB_RC_ROOT % ("%s/ev_lch.dlz")))) != None:
        evLch.load(data)
    return evLch

def _loadEventInformationBank(state : Layton2GameState) -> EventInfoList:
    evInf = EventInfoList()
    if (data := state.getFileAccessor().getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)
    return evInf

class EventBranchIcons():
    def __init__(self, idImagePuzzle = -1, idImageEvent = -1, idImageConditional = -1, idImageBad = -1, idImageRemovable = -1, idImageTea = -1):
        self.idImagePuzzle      = idImagePuzzle
        self.idImageEvent       = idImageEvent
        self.idImageConditional = idImageConditional
        self.idImageBad         = idImageBad
        self.idRemovable        = idImageRemovable
        self.idTea              = idImageTea

class EventActivatedItem():
    def __init__(self, state : Layton2GameState, data : int, isEvent : bool = False, isPuzzle : bool = False):
        # TODO - Return group for changing conditionals!
        self.__state = state
        self.__data : int = data
        self.isEvent : bool = isEvent
        self.isPuzzle : bool = isPuzzle
        self.isNothing : bool = not(self.isEvent or self.isPuzzle)
    
    def getTabName(self):
        if self.isNothing:
            return "BAD TAB"
        elif self.isPuzzle:
            if self.__data > 256:
                return "Puzzle i%03d" % (self.__data - 256)
            else:
                entry = self.__state.getNazoListEntry(self.__data)
                return entry.name
        else:
            return getNameForEvent(self.__state, self.__data)

    def getInternalPuzzleId(self) -> Optional[int]:
        if self.isPuzzle:
            if self.__data > 256:
                return self.__data - 256
            return self.__data
        return None
    
    def getEventId(self) -> Optional[int]:
        if self.isEvent:
            return self.__data
        return

    def isPuzzleInternalOnly(self):
        if self.isPuzzle:
            return self.__data < 256
        return False

class EventBranchManager(BranchManager):
    def __init__(self, state : Layton2GameState, treeCtrl : TreeCtrl, hideEditControls=False, iconPack : EventBranchIcons = EventBranchIcons()):
        super().__init__(state, treeCtrl, hideEditControls)
        self.__icons = iconPack

        self.__eventBranches = []
        self.__eventsUntracked = []
        self.__eventsTracked = []
        
        self.__rootStandard : Optional[TreeItemId] = None
        self.__rootPuzzle   : Optional[TreeItemId] = None
        self.__rootTea      : Optional[TreeItemId] = None
        self.__rootBad      : Optional[TreeItemId] = None

        self.__mapEventIdToTreeItem : Dict[int, TreeItemId] = {}
        self.__mapGroupToTreeItem   : Dict[Type[EventExecutionGroup], TreeItemId] = {}
        self.__mapPuzzleIdToGroup : Dict[int, List[PuzzleExecutionGroup]] = {}        

    def getTrackedEvents(self) -> List[int]:
        return self.__eventsTracked
    
    def getUntrackedEvents(self) -> List[int]:
        return self.__eventsUntracked
    
    def getBranchedEventGroups(self) -> List[Type[EventExecutionGroup]]:
        return self.__eventBranches

    def createTreeBranches(self, branchParent : TreeItemId, eventGroups : Tuple[Tuple[List[int], List[int]], List[Type[EventExecutionGroup]]]):
        # TODO - Icon passing through (icon collection object?)
        self._branchRoot = branchParent
        self.__rootStandard = self._treeCtrl.AppendItem(branchParent, "Standard", image=self.__icons.idImageEvent)
        self.__rootPuzzle = self._treeCtrl.AppendItem(branchParent, "Puzzle Launchers", image=self.__icons.idImagePuzzle)
        self.__rootTea = self._treeCtrl.AppendItem(branchParent, "Tea Minigame", image=self.__icons.idTea)
        self.__rootBad = self._treeCtrl.AppendItem(branchParent, "Misconfigured", image=self.__icons.idImageBad)

        ungrouped, eventBranches = eventGroups
        eventsTracked, eventsUntracked = ungrouped

        bankDescriptor = _loadEventDescriptorBank(self._state)
        bankInfo = _loadEventInformationBank(self._state)
        for event in eventsTracked:
            self.__addTrackedEvent(event, bankDescriptor, bankInfo)
        for event in eventsUntracked:
            self.__addUntrackedEvent(event, bankDescriptor)
        
        for group in eventBranches:
            self.addEventGroup(group, eventDescriptor=bankDescriptor, eventInformation=bankInfo)
        
    def getCorrespondingItem(self, eventId : int) -> Optional[TreeItemId]:
        if eventId in self.__mapEventIdToTreeItem:
            return self.__mapEventIdToTreeItem[eventId]
        return None
    
    def getCorrespondingEventActivatedItem(self, treeItem : TreeItemId) -> EventActivatedItem:
        # If the item has no children, its either the tail of a branch or an individual item
        itemParent : TreeItemId = self._treeCtrl.GetItemParent(treeItem)
        if not(itemParent.IsOk()):
            return None

        if self._isItemWithinPathToItem(treeItem, self.__rootStandard):
            # Item can immediately be launched
            # TODO - Event activation groups
            # This is only valid when we're activating leaves, so check there's zero children
            if self._treeCtrl.GetChildrenCount(treeItem, recursively=False) == 0:
                return EventActivatedItem(self._state, self._treeCtrl.GetItemData(treeItem), isEvent=True)
                
        elif self._isItemWithinPathToItem(treeItem, self.__rootPuzzle):
            # Trying to launch puzzle
            # This is only valid when we're activating leaves, so check there's zero children
            if self._treeCtrl.GetChildrenCount(treeItem, recursively=False) == 0:
                data = self._treeCtrl.GetItemData(treeItem)
                if data < 10000:
                    return EventActivatedItem(self._state, data, isPuzzle=True)

                # TODO - Tab name of event
                return EventActivatedItem(self._state, data, isEvent=True)

        return EventActivatedItem(self._state, 0)

    def _getComparativeItemData(self, treeItem : TreeItemId) -> Optional[int]:
        data = self._treeCtrl.GetItemData(treeItem)
        if data == None or type(data) == int:
            return data
        elif issubclass(type(data), EventExecutionGroup):
            data : Type[EventExecutionGroup]
            comparison = [inf]
            for id in data.group:
                if id != None:
                    comparison.append(id)
            return min(comparison)
        else:
            logSevere("No item match found for data", str(data))
            return data

    def __addUntrackedEvent(self, eventId : int, eventDescriptor : Type[EventDescriptorBank]) -> bool:
        if self._branchRoot == None or eventId in self.__mapEventIdToTreeItem:
            return False

        comment = _getCommentForEvent(eventId, eventDescriptor)
        if comment != "":
            name = str(eventId) + " - " + comment
        else:
            name = str(eventId)
        
        if eventId >= 20000:
            self.__mapEventIdToTreeItem[self._addIntoTreeAtCorrectId(eventId, name, self.__rootBad, data=eventId, icon=self.__icons.idImageBad)] = eventId
        else:
            self.__mapEventIdToTreeItem[self._addIntoTreeAtCorrectId(eventId, name, self.__rootStandard, data=eventId, icon=self.__icons.idImageEvent)] = eventId
        self.__eventsUntracked.append(eventId)
        return True

    def __addTrackedEvent(self, eventId : int, eventDescriptor : Type[EventDescriptorBank], eventInformation : EventInfoList) -> bool:
        if self._branchRoot == None or eventId in self.__mapEventIdToTreeItem:
            return False

        comment = _getCommentForEvent(eventId, eventDescriptor)
        if comment != "":
            name = str(eventId) + " - " + comment
        else:
            name = str(eventId)
        
        # Shouldn't be possible to not have an entry (checked by event groupings) but could maybe fallback to untracked to prevent loss?
        entry = eventInformation.searchForEntry(eventId)
        if entry.typeEvent == 1 or entry.typeEvent == 4:
            isRemovable = True
            name = "Removable - " + name
        else:
            isRemovable = False
        
        if eventId >= 20000:
            if isRemovable:
                icon = self.__icons.idRemovable
            else:
                icon = self.__icons.idImageBad
            self.__mapEventIdToTreeItem[self._addIntoTreeAtCorrectId(eventId, name, self.__rootBad, data=eventId, icon=icon)] = eventId
        else:
            if isRemovable:
                icon = self.__icons.idRemovable
            else:
                icon = self.__icons.idImageEvent
            self.__mapEventIdToTreeItem[self._addIntoTreeAtCorrectId(eventId, name, self.__rootStandard, data=eventId, icon=icon)] = eventId
        self.__eventsTracked.append(eventId)
        return True

    def updateGroup(self, eventGroup : Type[EventDescriptorBank]):
        if type(eventGroup) == PuzzleExecutionGroup:
            if eventGroup.idInternalPuzzle in self.__mapPuzzleIdToGroup:
                if len(self.__mapPuzzleIdToGroup[eventGroup.idInternalPuzzle]) > 1:
                    groups = list(self.__mapPuzzleIdToGroup[eventGroup.idInternalPuzzle])
                    for group in groups:
                        self.removeEventGroup(group)
                    for group in groups:
                        self.addEventGroup(group)
        else:
            self.removeEventGroup(eventGroup)
            self.addEventGroup(eventGroup)

    def addLooseEvent(self, eventId : int, eventDescriptor : Optional[Type[EventDescriptorBank]] = None, eventInformation : Optional[EventInfoList] = None) -> bool:
        if eventDescriptor == None:
            eventDescriptor = _loadEventDescriptorBank(self._state)
        if eventInformation == None:
            eventInformation = _loadEventInformationBank(self._state)
        
        if (_entry := eventInformation.searchForEntry(eventId)) == None:
            if self.__addUntrackedEvent(eventId, eventDescriptor):
                return True
        else:
            if self.__addTrackedEvent(eventId, eventDescriptor, eventInformation):
                return True
        return False

    def addEventGroup(self, group : Type[EventExecutionGroup], eventDescriptor : Optional[Type[EventDescriptorBank]] = None, eventInformation : Optional[EventInfoList] = None) -> bool:
        # TODO - How to update the comments??

        if eventDescriptor == None:
            eventDescriptor = _loadEventDescriptorBank(self._state)
        if eventInformation == None:
            eventInformation = _loadEventInformationBank(self._state)

        def addPuzzleGroup(group : PuzzleExecutionGroup) -> TreeItemId:

            def spawnPuzzleItems(rootItem : TreeItemId, group : PuzzleExecutionGroup):
                # HACK - Not great, but puzzle ID is always below event ID...
                if not(self._disableEditControls):
                    self._addIntoTreeAtCorrectId(group.idInternalPuzzle, "Edit puzzle data...", rootItem, data=group.idInternalPuzzle, icon=self.__icons.idImagePuzzle)
                
                self._treeCtrl.AppendItem(rootItem, "On first attempt", data=group.idBase, image=self.__icons.idImageEvent)
                if group.idRetry != None:
                    self._treeCtrl.AppendItem(rootItem, "On next attempts", data=group.idRetry, image=self.__icons.idImageEvent)
                if group.idSkip != None:
                    self._treeCtrl.AppendItem(rootItem, "On skipping puzzle", data=group.idSkip, image=self.__icons.idImageEvent)
                if group.idSolve != None:
                    self._treeCtrl.AppendItem(rootItem, "On first time solving", data=group.idSolve, image=self.__icons.idImageEvent)
                if group.idReturnAfterSolve != None:
                    self._treeCtrl.AppendItem(rootItem, "On next visits after solving", data=group.idReturnAfterSolve, image=self.__icons.idImageEvent)
            
            entryExternal = self._state.getNazoListEntry(group.idInternalPuzzle)
            if entryExternal == None:
                logSevere("Missing external entry for puzzle", group.idInternalPuzzle)
                idExternal = 256 + group.idInternalPuzzle
                name = "UNKNOWN"
            else:
                idExternal = entryExternal.idExternal
                name = entryExternal.name

            entry = eventInformation.searchForEntry(group.idBase)
            isRemovable = entry.typeEvent == 4
            if isRemovable:
                prefixRemovable = "Removable - "
                targetIcon = self.__icons.idRemovable
            else:
                prefixRemovable = ""
                targetIcon = self.__icons.idImagePuzzle

            # Headache - there are puzzles for this already
            if group.idInternalPuzzle in self.__mapPuzzleIdToGroup:
                
                if not(isRemovable):
                    targetIcon = self.__icons.idImageEvent

                # If there is one item in the tree (no branching), we need to convert to branching
                if len(self.__mapPuzzleIdToGroup[group.idInternalPuzzle]) == 1:
                    
                    # Pull out the out group, then delete it from the tree
                    oldGroup = self.__mapPuzzleIdToGroup[group.idInternalPuzzle][0]
                    oldGroupInfoEntry = eventInformation.searchForEntry(oldGroup.idBase)
                    isOldGroupRemovable = oldGroupInfoEntry.typeEvent == 4
                    self.removeEventGroup(oldGroup, eventDescriptor=eventDescriptor, eventInformation=eventInformation)

                    # Add generic puzzle

                    # HACK - Stored external and internal puzzle entries by offsetting unmapped internal IDs. Bad!
                    if isOldGroupRemovable or isRemovable:
                        prefixOldRemovable = "Removable - "
                        targetOldIcon = self.__icons.idRemovable
                    else:
                        prefixOldRemovable = ""
                        targetOldIcon = self.__icons.idImagePuzzle

                    if idExternal < 0:
                        rootParent = self._addIntoTreeAtCorrectId(idExternal, prefixOldRemovable + ("i%03i" % (idExternal - 256)), self.__rootPuzzle, data=idExternal, icon=targetOldIcon)
                    else:
                        rootParent = self._addIntoTreeAtCorrectId(idExternal, prefixOldRemovable + ("%03i - %s" % (idExternal, name)), self.__rootPuzzle, data=idExternal, icon=targetOldIcon)
                    
                    # Recover old group details
                    rootOldGroup = self._addIntoTreeAtCorrectId(oldGroup.idBase, str(oldGroup.idBase), rootParent, data=oldGroup, icon=self.__icons.idImageEvent)
                    spawnPuzzleItems(rootOldGroup, oldGroup)
                    self.__mapPuzzleIdToGroup[group.idInternalPuzzle] = [oldGroup]
                    self.__mapGroupToTreeItem[oldGroup] = rootOldGroup
                    self.__eventBranches.append(oldGroup)

                # If we're already branching, find the parent to add to
                else:
                    # Find puzzle root item
                    rootParent = self._treeCtrl.GetItemParent(self.__mapGroupToTreeItem[self.__mapPuzzleIdToGroup[group.idInternalPuzzle][0]])
                    if isRemovable and prefixRemovable not in self._treeCtrl.GetItemText(rootParent):
                        self._treeCtrl.SetItemText(rootParent, prefixRemovable + self._treeCtrl.GetItemText(rootParent))
                        self._treeCtrl.SetItemImage(rootParent, self.__icons.idRemovable)

                branchRoot = self._addIntoTreeAtCorrectId(group.idBase, prefixRemovable + str(group.idBase), rootParent, data=group, icon=targetIcon)
                self.__mapPuzzleIdToGroup[group.idInternalPuzzle].append(group)
            
            # If there's no puzzles, live laugh love
            # NOTE - On both empty and grouped puzzle events, the data is the internal ID of the puzzle!
            # This can be isolated fairly easily since the root branch will refer to the group with its mapping.
            else:
                self.__mapPuzzleIdToGroup[group.idInternalPuzzle] = [group]
                if idExternal < 0:
                    branchRoot = self._addIntoTreeAtCorrectId(idExternal, prefixRemovable + ("i%03i" % (idExternal - 256)), self.__rootPuzzle, data=idExternal, icon=targetIcon)
                else:
                    branchRoot = self._addIntoTreeAtCorrectId(idExternal, prefixRemovable + ("%03i - %s" % (idExternal, name)), self.__rootPuzzle, data=idExternal, icon=targetIcon)
            
            spawnPuzzleItems(branchRoot, group)
            return branchRoot

        def addEventConditionalGroup(group : EventConditionPuzzleExecutionGroup) -> TreeItemId:
            name = _getCommentWithJoiner(("Conditional on %i story puzzles solved - " % group.limit) + str(group.idBase), group.idBase, eventDescriptor)
            branchRoot = self._addIntoTreeAtCorrectId(group.idBase, name, self.__rootStandard, data=group, icon=self.__icons.idImageConditional)
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("First visit", group.idBase, eventDescriptor), data=group.idBase, image=self.__icons.idImageEvent)
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("Visits when not enough puzzles solved", group.idViewed, eventDescriptor), data=group.idViewed, image=self.__icons.idImageEvent)
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("Visits when enough puzzles solved", group.idSuccessful, eventDescriptor), data=group.idSuccessful, image=self.__icons.idImageEvent)
            return branchRoot
        
        def addEventViewedGroup(group : EventConditionAwaitingViewedExecutionGroup) -> TreeItemId:
            name = _getCommentWithJoiner("Conditional on revisiting - " + str(group.idBase), group.idBase, eventDescriptor)
            branchRoot = self._addIntoTreeAtCorrectId(group.idBase, name, self.__rootStandard, data=group, icon=self.__icons.idImageConditional)
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("First visit", group.idBase, eventDescriptor), data=group.idBase, image=self.__icons.idImageEvent)
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("Next visits", group.idViewed, eventDescriptor), data=group.idViewed, image=self.__icons.idImageEvent)
            return branchRoot

        def addTeaGroup(group : TeaExecutionGroup) -> TreeItemId:
            name = _getCommentWithJoiner(str(group.idBase), group.idBase, eventDescriptor)
            branchRoot = self._addIntoTreeAtCorrectId(group.idBase, name, self.__rootTea, data=group, icon=self.__icons.idTea)
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("First encounter", group.idBase, eventDescriptor), data=group.idBase, image=self.__icons.idImageEvent)
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("First time serving tea successfully", group.idSolve, eventDescriptor), data=group.idSolve, image=self.__icons.idImageEvent)
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("On serving the wrong tea", group.idFail, eventDescriptor), data=group.idFail, image=self.__icons.idImageEvent)
            # TODO - Is this correct? Skip??
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("On skipping the tea minigame", group.idSkip, eventDescriptor), data=group.idSkip, image=self.__icons.idImageEvent)
            self._treeCtrl.AppendItem(branchRoot, _getCommentWithJoiner("On retrying the tea minigame", group.idRetry, eventDescriptor), data=group.idRetry, image=self.__icons.idImageEvent)
            return branchRoot
            
        if group in self.__mapGroupToTreeItem or self._branchRoot == None:
            return False
        
        if group in self.__eventBranches:
            logSevere("Bad: Event Manager has detected multiple copies of the same group!")

        if type(group) == PuzzleExecutionGroup:
            branchRoot = addPuzzleGroup(group)
        elif type(group) == TeaExecutionGroup:
            branchRoot = addTeaGroup(group)
        elif type(group) == EventConditionAwaitingViewedExecutionGroup:
            branchRoot = addEventViewedGroup(group)
        elif type(group) == EventConditionPuzzleExecutionGroup:
            branchRoot = addEventConditionalGroup(group)
        else:
            logSevere("Unknown group:", str(group))
            return False

        self.__mapGroupToTreeItem[group] = branchRoot
        self.__eventBranches.append(group)
        return True

    def removeEvent(self, eventId : int) -> bool:
        if eventId in self.__mapEventIdToTreeItem:
            # Clear from tree
            self._treeCtrl.Delete(self.__mapEventIdToTreeItem[eventId])
            del self.__mapEventIdToTreeItem[eventId]

            # Remove from event groupings (don't reload databases, please...)
            if eventId in self.__eventsTracked:
                self.__eventsTracked.remove(eventId)
            elif eventId in self.__eventsUntracked:
                self.__eventsUntracked.remove(eventId)
        return True

    def removeEventGroup(self, eventGroup : Type[EventDescriptorBank], eventDescriptor : Optional[Type[EventDescriptorBank]] = None, eventInformation : Optional[EventInfoList] = None) -> bool:
        if eventGroup in self.__mapGroupToTreeItem:
            if type(eventGroup) == PuzzleExecutionGroup:
                eventGroup : PuzzleExecutionGroup
                # If there is one in the tree, we don't need to do anything
                if len(self.__mapPuzzleIdToGroup[eventGroup.idInternalPuzzle]) == 1:
                    del self.__mapPuzzleIdToGroup[eventGroup.idInternalPuzzle]
                else:
                    # If there is more than one, we now need to fix it...
                    treeItemEventDecider = self.__mapGroupToTreeItem[eventGroup]
                    treeItemPuzzleParent = self._treeCtrl.GetItemParent(treeItemEventDecider)

                    # Make a copy of the current groups in the tree
                    newGroups = list(self.__mapPuzzleIdToGroup[eventGroup.idInternalPuzzle])
                    
                    # Delete all references to the puzzle group from the tree
                    del self.__mapPuzzleIdToGroup[eventGroup.idInternalPuzzle]

                    # Delete all copies of the groups from the tree
                    for groups in newGroups:
                        del self.__mapGroupToTreeItem[groups]
                        self.__eventBranches.remove(groups)
                    self._treeCtrl.DeleteChildren(treeItemPuzzleParent)
                    self._treeCtrl.Delete(treeItemPuzzleParent)

                    # Remove the deleted group from the tree, then rebuild the tree (HACK)
                    newGroups.remove(eventGroup)
                    for group in newGroups:
                        self.addEventGroup(group, eventDescriptor=eventDescriptor, eventInformation=eventInformation)

                    return True

            parentItem = self.__mapGroupToTreeItem[eventGroup]
            self._treeCtrl.DeleteChildren(parentItem)
            self._treeCtrl.Delete(parentItem)
            del self.__mapGroupToTreeItem[eventGroup]
            self.__eventBranches.remove(eventGroup)

        return True