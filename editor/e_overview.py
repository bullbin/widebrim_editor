from typing import Dict, List
from editor.asset_management.event import EventConditionAwaitingViewedExecutionGroup, EventConditionPuzzleExecutionGroup, PuzzleExecutionGroup, TeaExecutionGroup
from editor.asset_management.puzzle import PuzzleEntry, getPuzzles
from editor.e_script import FrameScriptEditor
from editor.e_puzzle import FramePuzzleEditor
from .nopush_editor import pageOverview
from widebrim.engine.state.state import Layton2GameState
from editor.asset_management import getCharacters, getEvents
import wx

# TODO - Check if pages already open

class FrameOverview(pageOverview):

    def __init__(self, parent, state : Layton2GameState, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(640, 640), style=wx.TAB_TRAVERSAL, name=wx.EmptyString):
        super().__init__(parent, id, pos, size, style, name)
        self._characters = getCharacters(state)
        self._eventsLoose, self._eventsGrouped = getEvents(state)
        self._puzzles : List[List[PuzzleEntry]] = [[],[],[]]
        self._idToPuzzleEntry : Dict[int, PuzzleEntry] = {}
        # TODO - Puzzles?

        self._state = state
        self._treeItemEvent = None
        self._treeItemPuzzle = None
        self._loaded = False
    
    def ensureLoaded(self):
        if not(self._loaded):
            self._refresh()
            self._loaded = True
    
    def __loadPuzzleCache(self):
        self._puzzles = getPuzzles(self._state)
        for entry in self._puzzles[0] + self._puzzles[1] + self._puzzles[2]:
            self._idToPuzzleEntry[entry.idInternal] = entry

    def __isItemWithinPathToItem(self, itemSearchEnd, itemSearch) -> bool:
        if itemSearchEnd == itemSearch:
            return True
        treeParent = self.treeOverview.GetItemParent(itemSearchEnd)
        while treeParent != self.treeOverview.GetRootItem():
            if treeParent == itemSearch:
                return True
            treeParent = self.treeOverview.GetItemParent(treeParent)
        return False

    def treeOverviewOnTreeItemActivated(self, event):

        def handleEventItem(item):
            eventId = self.treeOverview.GetItemData(item)

            if type(eventId) != int:
                print("Cannot launch", eventId)
                return

            treeParent = self.treeOverview.GetItemParent(item)

            name = str(eventId)
            if (entry := self.treeOverview.GetItemData(treeParent)) != None:
                print("Branch detected!")
                if type(entry) == EventConditionAwaitingViewedExecutionGroup:
                    dictName = {entry.idBase :  str(entry.idBase) + " (Initial)", entry.idViewed : str(entry.idBase) + " (Viewed)"}
                    name = dictName[eventId]
                elif type(entry) == EventConditionPuzzleExecutionGroup:
                    dictName = {entry.idBase :  str(entry.idBase) + " (Initial)", entry.idViewed : str(entry.idBase) + " (Viewed)", entry.idSuccessful : str(entry.idBase) + " (Met Limit)"}
                    name = dictName[eventId]
                elif type(entry) == PuzzleExecutionGroup:
                    # TODO - Should probably just group this :(
                    if entry.idInternalPuzzle in self._idToPuzzleEntry:
                        puzzleDetails = self._idToPuzzleEntry[entry.idInternalPuzzle]
                        name = "Puzzle " + str(puzzleDetails.idExternal)
                    else:
                        name = "Puzzle i" + str(entry.idInternalPuzzle)
                    dictName = {entry.idBase :  name + " (Initial)", entry.idRetry : name + " (Retry)", entry.idSkip : name + " (Skip)", entry.idSolve : name + " (Solved)", entry.idReturnAfterSolve : name + " (Already Solved)"}
                    name = dictName[eventId]
                else:
                    print("Unrecognised branch type" , str(entry))

            # TODO - Want to click here, but wx seems to have a problem with strange page change events
            #        (this is immediately overridden, plus multiple page changes are being registered...)
            self.GetParent().Freeze()
            self.GetParent().AddPage(FrameScriptEditor(self.GetParent(), eventId, self._state), name)
            self.GetParent().Thaw()

        def handlePuzzleItem(item):
            idInternal = self.treeOverview.GetItemData(item)
            if type(idInternal) != int:
                print("Cannot launch puzzle", idInternal)
                return
            # TODO - See above
            # TODO - Add page method this is stupid
            self.GetParent().Freeze()
            self.GetParent().AddPage(FramePuzzleEditor(self.GetParent(), idInternal, self._state), self.treeOverview.GetItemText(item))
            self.GetParent().Thaw()

        item = event.GetItem()

        if self._treeItemEvent != None and self.__isItemWithinPathToItem(item, self._treeItemEvent):
            handleEventItem(item)
        elif self._treeItemPuzzle != None and self.__isItemWithinPathToItem(item, self._treeItemPuzzle):
            handlePuzzleItem(item)
        else:
            print("Unrecognised!")
            
        return super().treeOverviewOnTreeItemActivated(event)

    def _refresh(self):

        self.treeOverview.DeleteAllItems()
        self.treeOverview.SetIndent(30)
        
        rootItem = self.treeOverview.AddRoot("You shouldn't see this!")

        def addIfDataNotNone(data, root, nameTag, nameTagIfNotPresent = None):
            if data == None:
                if nameTagIfNotPresent != None:
                    self.treeOverview.AppendItem(root, nameTagIfNotPresent, data=data)
            else:
                self.treeOverview.AppendItem(root, nameTag, data=data)

        def generateEventBranch():
            eventItem = self.treeOverview.AppendItem(rootItem, "Events")
            standardItem = self.treeOverview.AppendItem(eventItem, "Standard")
            puzzleItem = self.treeOverview.AppendItem(eventItem, "Puzzles")
            teaItem = self.treeOverview.AppendItem(eventItem, "Tea Minigame")
            badItem = self.treeOverview.AppendItem(eventItem, "Misconfigured")

            self._treeItemEvent = eventItem

            databaseIn, databaseMissing = self._eventsLoose
            
            order = {}
            for idEvent in databaseIn + databaseMissing:
                order[idEvent] = idEvent
            for group in self._eventsGrouped:
                ids = []
                for id in group.group:
                    if id != None:
                        ids.append(id)
                if len(ids) > 0:
                    baseId = min(ids)
                    order[baseId] = group
                else:
                    print("No data for group " + str(group))

            keys = list(order.keys())
            keys.sort()

            condPuzzle = {}

            for key in keys:
                entry = order[key]

                if key not in databaseMissing:
                    info = self._state.getEventInfoEntry(key)
                else:
                    info = None

                if type(entry) == int:
                    # Just add event to list
                    name = str(entry)

                    if entry in databaseIn:
                        if info.typeEvent == 1 or info.typeEvent == 4:
                            name = "Removable " + name
                    # TODO - Remove, just for testing to not clutter space
                    # TODO - constant
                    if entry >= 20000:
                        self.treeOverview.AppendItem(badItem, name, data=entry)
                    else:
                        self.treeOverview.AppendItem(standardItem, name, data=entry)
                else:
                    
                    if type(entry) == EventConditionAwaitingViewedExecutionGroup:
                        branchRoot = self.treeOverview.AppendItem(standardItem, "Conditional on " + str(key), data=entry)
                        self.treeOverview.AppendItem(branchRoot, "On initial execution", data=entry.idBase)
                        self.treeOverview.AppendItem(branchRoot, "On future executions", data=entry.idViewed)

                    elif type(entry) == EventConditionPuzzleExecutionGroup:
                        branchRoot = self.treeOverview.AppendItem(standardItem, "Conditional on " + str(key), data=entry)
                        self.treeOverview.AppendItem(branchRoot, "On initial execution", data=entry.idBase)
                        if entry.idViewed != None:
                            self.treeOverview.AppendItem(branchRoot, "On future executions unless limit met", data=entry.idViewed)
                        else:
                            self.treeOverview.AppendItem(branchRoot, "(untracked)", data=entry.idViewed)

                        if entry.idSuccessful != None:
                            self.treeOverview.AppendItem(branchRoot, "On reaching puzzle requirement", data=entry.idSuccessful)
                        else:
                            self.treeOverview.AppendItem(branchRoot, "(untracked)", data=entry.idSuccessful)

                    elif type(entry) == TeaExecutionGroup:
                        branchRoot = self.treeOverview.AppendItem(teaItem, "Branch on " + str(key), data=entry)
                        for group in entry.group:
                            self.treeOverview.AppendItem(branchRoot, str(group), data=group)
                    
                    elif type(entry) == PuzzleExecutionGroup:
                        condPuzzle[entry.idInternalPuzzle] = entry
                    
                    else:
                        print("Unknown :: " + str(entry))
            
            idPuzzles = list(condPuzzle.keys())
            idPuzzles.sort()

            for key in idPuzzles:
                entry = condPuzzle[key]
                # TODO - Can reuse puzzle data
                if (nzLstEntry := self._state.getNazoListEntry(entry.idInternalPuzzle)) != None:
                    puzzleEntryName = "%03d - %s" % (nzLstEntry.idExternal, nzLstEntry.name)
                else:
                    puzzleEntryName = "i%03d" % entry.idInternalPuzzle

                branchRoot = self.treeOverview.AppendItem(puzzleItem, puzzleEntryName, data=entry)
                self.treeOverview.AppendItem(branchRoot, "On initial execution", data=entry.idBase)
                addIfDataNotNone(entry.idRetry, branchRoot, "On future executions while puzzle is unsolved")
                addIfDataNotNone(entry.idSkip, branchRoot, "On execution if puzzle is skipped")
                addIfDataNotNone(entry.idSolve, branchRoot, "On execution if puzzle is solved")
                addIfDataNotNone(entry.idReturnAfterSolve, branchRoot, "On future executions while puzzle is solved")

        def generatePuzzleBranch():
            puzzleItem = self.treeOverview.AppendItem(rootItem, "Puzzles")
            normalItem = self.treeOverview.AppendItem(puzzleItem, "Standard")
            wifiItem = self.treeOverview.AppendItem(puzzleItem, "WiFi")
            specialItem = self.treeOverview.AppendItem(puzzleItem, "Special")

            self.__loadPuzzleCache()
            self._treeItemPuzzle = puzzleItem

            def fillPuzzleBranch(root, entryList : List[PuzzleEntry]):

                def getKey(entry : PuzzleEntry):
                    return entry.idExternal

                entryList.sort(key=getKey)
                for entry in entryList:
                    name = "%03i - %s" % (entry.idExternal, entry.name)
                    self.treeOverview.AppendItem(root, name, data=entry.idInternal)
            
            fillPuzzleBranch(normalItem, self._puzzles[0])
            fillPuzzleBranch(wifiItem, self._puzzles[1])
            fillPuzzleBranch(specialItem, self._puzzles[2])

        generateEventBranch()
        generatePuzzleBranch()