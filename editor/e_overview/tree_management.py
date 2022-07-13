from typing import Dict, List, Optional
from editor.asset_management.event import PuzzleExecutionGroup, createBlankEvent, createBlankPuzzleEventChain, createConditionalRevisit, createConditionalRevisitAndPuzzleLimit, getFreeEventViewedFlags
from editor.asset_management.puzzle import PuzzleEntry
from editor.d_operandMultichoice import DialogMultipleChoice
from editor.e_script.get_input_popup import VerifiedDialog, rangeIntCheckFunction
from editor.gui.command_annotator.bank import ScriptVerificationBank
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.common import logSevere
from .creation import FrameOverviewTreeGen
import wx

class FrameOverview(FrameOverviewTreeGen):

    def __init__(self, parent, filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, instructionBank : ScriptVerificationBank):
        super().__init__(parent, filesystem, state, instructionBank)
    
    def __isEventIdSafe(self, eventId : int, useGap = True, gap = 5):

        idRange = []

        def addToRange(listId : List[int]):
            for id in listId:
                if id != None:
                    if id not in idRange:
                        idRange.append(id)

        for group in self._eventManager.getBranchedEventGroups():
            idGroup = group.group
            addToRange(idGroup)

        for loose in [self._eventManager.getTrackedEvents(), self._eventManager.getUntrackedEvents()]:
            print("LOOSE EVENT", loose)
            addToRange(loose)
        
        if useGap:
            baseIndex = (eventId // gap) * gap
            for x in range(gap):
                if (baseIndex + x) in idRange:
                    return False
            return True
        else:
            return not(eventId in idRange)

    def __getPuzzleSelection(self, filterUnused=False) -> List[PuzzleEntry]:
        if len(self._puzzles[0]) == 0:
            self._loadPuzzleCache()
        if len(self._puzzles[0]) == 0:
            return []

        # TODO - Not foolproof, since not all puzzles are captured by this technique
        idsUsed : List[int] = []
        for group in self._eventManager.getBranchedEventGroups():
            if type(group) == PuzzleExecutionGroup:
                group : PuzzleExecutionGroup
                if group.idInternalPuzzle in idsUsed:
                    logSevere("Duplicate puzzle mapping to internal ", group.idInternalPuzzle)
                else:
                    idsUsed.append(group.idInternalPuzzle)
        idsUsed.sort()

        # TODO - self._idToPuzzleEntry
        availableEntries = list(self._puzzles[0])

        if filterUnused:
            for id in idsUsed:
                for entry in availableEntries:
                    if entry.idInternal == id:
                        availableEntries.remove(entry)
                        break
        
        return availableEntries

    def __getNextFreeEventId(self, packMin = 10, packMax = 20, gap = 5, estimatePackLimit = True, excludeId = []) -> Optional[int]:
        idRange : Dict[str, List[int]]= {}

        def getNextFreeEvent() -> Optional[int]:
            genKeys = []
            for idxPack in range((packMax - packMin) + 1):
                idxPack = packMin + idxPack
                if idxPack == 24:
                    genKeys.append("24a")
                    genKeys.append("24b")
                    genKeys.append("24c")
                else:
                    genKeys.append(str(idxPack))

            for key in genKeys:
                minBase = 000
                maxBase = 1000

                if not(key[-1].isdigit()):
                    if key[-1] == "a":
                        maxBase = 300
                    elif key[-1] == "b":
                        minBase = 300
                        maxBase = 600
                    else:
                        minBase = 600
                    packKey = int(key[:-1])
                else:
                    packKey = int(key)

                # For 24, override gap to be 10 (convention)
                if packKey == 24:
                    workingGap = max(gap, 10)
                else:
                    workingGap = gap

                if key in idRange:
                    if estimatePackLimit:
                        if len(idRange[key]) < 60:
                            for baseIndex in range(minBase, maxBase, workingGap):
                                newId = (packKey * 1000) + baseIndex
                                if newId not in idRange[key] and newId not in excludeId:
                                    return newId
                        else:
                            continue
                    else:
                        for baseIndex in range(minBase, maxBase, workingGap):
                            newId = (packKey * 1000) + baseIndex
                            if newId not in idRange[key]and newId not in excludeId:
                                return newId
                else:
                    return (packKey * 1000) + minBase
            
            return None

        def getBaseIndex(idEvent : int):
            # Observation: Event chains use maximally 5 events, so the game often separates events by 5.
            # Not guaranteed, but for autodetection purposes it's fine
            return (idEvent // gap) * gap

        def addToRange(listId : List[int]):
            for id in listId:
                if id != None:
                    packId = id // 1000
                    subId = id % 1000
                    
                    packKey = str(packId)

                    if packId == 24:
                        if subId < 300:
                            packKey = "24a"
                        elif subId < 600:
                            packKey = "24b"
                        else:
                            packKey = "24c"

                    if packMin <= packId <= packMax:
                        baseIndex = getBaseIndex(id)

                        if packKey not in idRange:
                            idRange[packKey] = [baseIndex]
                        else:
                            if baseIndex not in idRange[packKey]:
                                idRange[packKey].append(baseIndex)

        for group in self._eventManager.getBranchedEventGroups():
            idGroup = group.group
            addToRange(idGroup)

        for loose in [self._eventManager.getTrackedEvents(), self._eventManager.getUntrackedEvents()]:
            print(loose)
            addToRange(loose)

        return getNextFreeEvent()

    def __doEventIdDialog(self, packMin, packMax) -> Optional[int]:
        choices = {}

        for x in range(packMin, packMax + 1):
            choices["Automatic, Pack " + str(x)] = "Chooses the first available event ID in pack " + str(x) + "."
        choices["Automatic, first available pack"] = "Choices the first available event ID from any pack."
        choices["Manual ID"] = """Any ID that sits within the permitted packs will be allowed. Event IDs are 5-digit numbers, with the first 2 digits being the pack ID and the last 3 being the sub ID.
                                  \nThe pack ID must sit in range """ + str(packMin) + "-" + str(packMax) + ", while the sub ID can be any number.\nTypically, the sub ID should end in 0 or 5."

        choicesKeys = list(choices.keys())
        idOutput = None

        while True:
            dlg = DialogMultipleChoice(self, choices, "Select an Event ID")
            result = dlg.ShowModal()
            if result != wx.ID_OK:
                break
            
            # Automatic from pack
            if choicesKeys.index(dlg.GetSelection()) <= (packMax - packMin):
                packId = packMin + choicesKeys.index(dlg.GetSelection())
                idEvent = self.__getNextFreeEventId(packId, packId)
                if idEvent != None:
                    idOutput = idEvent
                    break
                else:
                    # TODO - Error message from wx
                    pass
                
            # Automatic from any
            elif dlg.GetSelection() == choicesKeys[-2]:
                idEvent = self.__getNextFreeEventId(packMin, packMax)
                if idEvent != None:
                    idOutput = idEvent
                    break
                else:
                    # TODO - Error message from wx
                    pass
            
            # Manual
            else:
                defaultValue = packMin * 1000
                while True:
                    manualDlgId = VerifiedDialog(wx.TextEntryDialog(self, "Enter the Event ID"), rangeIntCheckFunction(packMin * 1000, (packMax * 1000) + 999), "The entered value must sit within the range!")
                    idEvent = manualDlgId.do(str(defaultValue))
                    if idEvent == None:
                        break
                    else:
                        idEvent = int(idEvent)
                        if self.__isEventIdSafe(idEvent):
                            idOutput = idEvent
                            break
                        else:
                            # TODO - Error message from wx
                            pass
                
                if idOutput != None:
                    break
        
        return idOutput

    def btnDeleteOnButtonClick(self, event):
        itemFocused = self.treeOverview.GetFocusedItem()
        print(self.treeOverview.GetItemText(itemFocused))
        return super().btnDeleteOnButtonClick(event)
    
    def btnCreateNewOnButtonClick(self, event):
        if self._isItemWithinPathToItem(self.treeOverview.GetFocusedItem(), self._treeItemEvent):
            # TODO - Find branch (standard branch, puzzle branch, tea branch, etc)
            #        Could skip a popup, maybe...

            # Steps:
            # - If the user just wants to create a standard event (e.g., one ran during interaction, one ran when exploring), ask for an ID
            # - If the user wants to create a puzzle event, ask for the puzzle then generate a branch with first available ID
            # - If the user wants to create a tea event, ask for the tea then generate a branch with first available ID

            choices = {"Standard Sequence":"Creates a new single event sequence. This sequence will never branch and will always play the same way.",
                       "Conditional Sequence":"Creates a new event chain that will use branching to change which sequence is played.",
                       "Puzzle Sequence":"Creates a conditional sequence tied to a puzzle. This sequence will branch depending on whether the attached puzzle was solved or skipped, for example.",
                       "Tea Sequence":"Creates a conditional sequence tied to a tea encounter. This sequence will branch depending on the outcome of the tea minigame."}
            choicesKeys = list(choices.keys())

            dlg = DialogMultipleChoice(self, choices, "Select New Event Type")
            if dlg.ShowModal() == wx.ID_OK:
                idxSelection = choicesKeys.index(dlg.GetSelection())
                if idxSelection == 0:
                    idEvent = self.__doEventIdDialog(10, 19)
                    if idEvent != None:
                        self._eventManager.addLooseEvent(createBlankEvent(self._filesystem, self._state, idEvent))

                elif idxSelection == 1:
                    
                    availableFlagsViewed = getFreeEventViewedFlags(self._filesystem, self._state)
                    if len(availableFlagsViewed) == 0:
                        # TODO - wx error for ran out of flags!
                        return super().btnCreateNewOnButtonClick(event)

                    choices = {"Branch on event being revisited":"""This condition creates two events: an event for first playback and an event for revisited playbacks.
                                                                    \nThis only affects event playback, so it is up to event designers whether they make major changes to the game state in the revisited event. This is (generally) atypical.""",
                               "Branch on meeting puzzle limit":"""This condition creates three events: an event for first playback, an event for revisited playbacks and an event when the amount of required solved puzzles has been met. If the puzzle limit was not met, the game will play back the revisiting event. As such, design the revisiting event with this fact in mind.
                                                                   \nNote that this condition only affects event playback, not how the rooms are presented. All gameplay outside of the event will be unaffected unless modified by the puzzle limit met event.
                                                                   \nThe event played when puzzle limit is met should change the state of the game, such that some milestone is met (and this event cannot be revisited)."""}
                    choicesKeys = list(choices.keys())

                    dlg = DialogMultipleChoice(self, choices, "Select Conditional Type")
                    if dlg.ShowModal() == wx.ID_OK:
                        idEvent = self.__doEventIdDialog(10, 19)
                        if idEvent != None:
                            if choicesKeys.index(dlg.GetSelection()) == 0:
                                self._eventManager.addEventGroup(createConditionalRevisit(self._filesystem, self._state, idEvent, availableFlagsViewed[0]))
                            else:
                                puzzleCountDlg = VerifiedDialog(wx.TextEntryDialog(self, "Set Puzzle Count"), rangeIntCheckFunction(1, 255), "The limit must sit between 1 and 255 puzzles!")
                                status = puzzleCountDlg.do("1")
                                if status == None:
                                    # TODO - go back? this whole method is bad
                                    return super().btnCreateNewOnButtonClick(event)
                                else:
                                    self._eventManager.addEventGroup(createConditionalRevisitAndPuzzleLimit(self._filesystem, self._state, idEvent, availableFlagsViewed[0], int(status)))

                elif idxSelection == 2:
                    idEvent = self.__doEventIdDialog(20, 26)
                    if idEvent == None:
                        return super().btnCreateNewOnButtonClick(event)
                        
                    entries = self.__getPuzzleSelection()

                    choices = {}
                    choicesToEntry : Dict[str, PuzzleEntry] = {}

                    for entry in entries:
                        name = "%03d - %s" % (entry.idExternal, entry.name)
                        choices[name] = "Attach this event to " + entry.name
                        choicesToEntry[name] = entry
                    
                    dlg = DialogMultipleChoice(self, choices, "Select Puzzle for Attachment")
                    if dlg.ShowModal() != wx.ID_OK:
                        return super().btnCreateNewOnButtonClick(event)
                    
                    entry = choicesToEntry[dlg.GetSelection()]
                    self._eventManager.addEventGroup(createBlankPuzzleEventChain(self._filesystem, self._state, idEvent, entry.idInternal, entry.idExternal))
                else:
                    idEvent = self.__doEventIdDialog(30,30)

        return super().btnCreateNewOnButtonClick(event)
    
    def btnDuplicateOnButtonClick(self, event):
        return super().btnDuplicateOnButtonClick(event)
    
    def btnEditConditionOnButtonClick(self, event):
        return super().btnEditConditionOnButtonClick(event)
    
    def btnGetRefOnButtonClick(self, event):
        return super().btnGetRefOnButtonClick(event)