from editor.asset_management.event import EventConditionAwaitingViewedExecutionGroup, EventConditionPuzzleExecutionGroup, PuzzleExecutionGroup, TeaExecutionGroup
from editor.e_script import FrameScriptEditor
from .nopush_editor import pageOverview
from widebrim.engine.state.state import Layton2GameState
from editor.asset_management import getCharacters, getEvents
import wx

class FrameOverview(pageOverview):

    def __init__(self, parent, state : Layton2GameState, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(640, 640), style=wx.TAB_TRAVERSAL, name=wx.EmptyString):
        super().__init__(parent, id, pos, size, style, name)
        self._characters = getCharacters(state)
        self._eventsLoose, self._eventsGrouped = getEvents(state)

        self._state = state
        self._treeItemEvent = None
        self._refresh()
    
    def treeOverviewOnTreeItemActivated(self, event):
        item = event.GetItem()

        isEvent = False
        isPuzzle = False

        treeParent = self.treeOverview.GetItemParent(item)
        while treeParent != self.treeOverview.GetRootItem():
            if treeParent == self._treeItemEvent:
                isEvent = True
                break
            treeParent = self.treeOverview.GetItemParent(treeParent)

        if isEvent:
            
            eventId = self.treeOverview.GetItemData(item)

            if type(eventId) != int:
                print("Cannot launch", eventId)
                return super().treeOverviewOnTreeItemActivated(event)

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
                    name = "Puzzle " + str(entry.idInternalPuzzle)
                    dictName = {entry.idBase :  name + " (Initial)", entry.idRetry : name + " (Retry)", entry.idSkip : name + " (Skip)", entry.idSolve : name + " (Solved)", entry.idReturnAfterSolve : name + " (Already Solved)"}
                    name = dictName[eventId]
                else:
                    print("Unrecognised branch type" , str(entry))

            # TODO - Want to click here, but wx seems to have a problem with strange page change events
            #        (this is immediately overridden, plus multiple page changes are being registered...)
            self.GetParent().AddPage(FrameScriptEditor(self.GetParent(), eventId, self._state), name)
        return super().treeOverviewOnTreeItemActivated(event)

    def _refresh(self):
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

        self.treeOverview.DeleteAllItems()
        self.treeOverview.SetIndent(30)
        rootItem = self.treeOverview.AddRoot("You shouldn't see this!")
        eventItem = self.treeOverview.AppendItem(rootItem, "Events")
        standardItem = self.treeOverview.AppendItem(eventItem, "Standard")
        puzzleItem = self.treeOverview.AppendItem(eventItem, "Puzzles")
        teaItem = self.treeOverview.AppendItem(eventItem, "Tea Minigame")
        badItem = self.treeOverview.AppendItem(eventItem, "Misconfigured")

        self._treeItemEvent = eventItem

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

        def addIfDataNotNone(data, root, nameTag, nameTagIfNotPresent = None):
            if data == None:
                if nameTagIfNotPresent != None:
                    self.treeOverview.AppendItem(root, nameTagIfNotPresent, data=data)
            else:
                self.treeOverview.AppendItem(root, nameTag, data=data)

        for key in idPuzzles:
            entry = condPuzzle[key]
            # branchRoot = self.treeOverview.AppendItem(puzzleItem, "Puzzle " + str(entry.idInternalPuzzle) + " with branch root at " + str(entry.idBase), data=entry)
            # TODO - External ID? Names? nz_lst.dlz provides it
            branchRoot = self.treeOverview.AppendItem(puzzleItem, str(entry.idInternalPuzzle), data=entry)
            self.treeOverview.AppendItem(branchRoot, "On initial execution", data=entry.idBase)
            addIfDataNotNone(entry.idRetry, branchRoot, "On future executions while puzzle is unsolved")
            addIfDataNotNone(entry.idSkip, branchRoot, "On execution if puzzle is skipped")
            addIfDataNotNone(entry.idSolve, branchRoot, "On execution if puzzle is solved")
            addIfDataNotNone(entry.idReturnAfterSolve, branchRoot, "On future executions while puzzle is solved")