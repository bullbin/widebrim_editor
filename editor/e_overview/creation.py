from typing import Dict, List
from editor.asset_management.event import EventConditionAwaitingViewedExecutionGroup, EventConditionPuzzleExecutionGroup, PuzzleExecutionGroup, TeaExecutionGroup
from editor.asset_management.puzzle import PuzzleEntry, getPuzzles
from editor.e_script import FrameScriptEditor
from editor.e_puzzle import FramePuzzleEditor
from editor.e_room import FramePlaceEditor
from editor.gui.command_annotator.bank import ScriptVerificationBank
from editor.asset_management.room import PlaceGroup, getPlaceGroups
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.hat_io.asset_dlz.ev_inf2 import EventInfoList
from widebrim.madhatter.hat_io.asset_storyflag import StoryFlag
from ..nopush_editor import pageOverview
from widebrim.engine.state.manager import Layton2GameState
from editor.asset_management import getCharacters, getEvents
import wx

from widebrim.engine.const import PATH_DB_EV_INF2, PATH_DB_RC_ROOT, PATH_DB_STORYFLAG, PATH_PROGRESSION_DB
from widebrim.engine_ext.utils import substituteLanguageString
from widebrim.madhatter.hat_io.asset_dlz.ev_lch import EventDescriptorBankNds

from editor.icons.getIconFromRom import getImageAndSetVariable

# TODO - Check if pages already open

class FrameOverviewTreeGen (pageOverview):

    SIZE_ICONS = (16,16)

    def __init__(self, parent, filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, instructionBank : ScriptVerificationBank):
        super().__init__(parent)
        self._bankInstructions = instructionBank
        self._filesystem = filesystem
        self._state = state

        self._characters = []
        self._eventsLoose = ([], [])
        self._eventsGrouped = []
        self._puzzles : List[List[PuzzleEntry]] = [[],[],[]]
        self._idToPuzzleEntry : Dict[int, PuzzleEntry] = {}
        # TODO - Puzzles?

        self.__useIcons = False
        self.__icons = wx.ImageList(FrameOverviewTreeGen.SIZE_ICONS[0], FrameOverviewTreeGen.SIZE_ICONS[1])

        def useIconsIfFound(pathImage : str, forceImageIndex : int = 0):
            output = getImageAndSetVariable(self._filesystem, pathImage, self.__icons, forceImageIndex=forceImageIndex, resize=FrameOverviewTreeGen.SIZE_ICONS)
            if output != -1:
                self.__useIcons = True
            return output
        
        self.__idImagePuzzle        = useIconsIfFound("event/nazo_icon.arc")
        self.__idImageEvent         = useIconsIfFound("subgame/photo/check_icon.arc")
        self.__idImageConditional   = useIconsIfFound("event/diary_icon.arc")
        self.__idImageBad           = useIconsIfFound("map/icon_buttons.arc")
        self.__idImageWifi          = useIconsIfFound("menu/wifi/wifi_ant.arj", forceImageIndex=3)
        self.__idRemovable          = useIconsIfFound("nazo/onoff/q49_x.arc")
        self.__idSpecial            = useIconsIfFound("tobj/icon.arc", forceImageIndex=2)
        self.__idTea                = useIconsIfFound("subgame/tea/tea_icon.arc", forceImageIndex=2)
        
        self._treeItemEvent = None
        self._treeItemPuzzle = None
        self._treeItemCharacter = None
        self._treeItemPlace = None
        
        self._loaded = False
        self.GetParent().SetDoubleBuffered(True)
    
    def ensureLoaded(self):
        if not(self._loaded):
            self._refresh()
            self._loaded = True
    
    def _loadPuzzleCache(self):
        self._puzzles = getPuzzles(self._state)
        for entry in self._puzzles[0] + self._puzzles[1] + self._puzzles[2]:
            self._idToPuzzleEntry[entry.idInternal] = entry

    def _isItemWithinPathToItem(self, itemSearchEnd : wx.TreeItemId, itemSearch) -> bool:
        if itemSearchEnd == itemSearch:
            return True
        elif itemSearchEnd == self.treeOverview.GetRootItem():
            return False
        elif not(itemSearchEnd.IsOk()):
            return False
        treeParent = self.treeOverview.GetItemParent(itemSearchEnd)
        while treeParent != self.treeOverview.GetRootItem():
            if treeParent == itemSearch:
                return True
            treeParent = self.treeOverview.GetItemParent(treeParent)
        return False

    def treeOverviewOnTreeItemActivated(self, event):
        # TODO - Can probably get bitmap from icons
        self.GetParent().Freeze()

        def handleEventItem(item):
            eventId = self.treeOverview.GetItemData(item)

            if type(eventId) != int:
                print("Cannot launch", eventId)
                return
            
            treeParent = self.treeOverview.GetItemParent(item)

            if eventId < 10000:
                # HACK - This is a puzzle instead!
                if self.__useIcons:
                    self.GetParent().AddPage(FramePuzzleEditor(self.GetParent(), self._filesystem, eventId, self._state), self.treeOverview.GetItemText(treeParent), bitmap=self.__icons.GetBitmap(self.__idImagePuzzle))
                else:
                    self.GetParent().AddPage(FramePuzzleEditor(self.GetParent(), self._filesystem, eventId, self._state), self.treeOverview.GetItemText(treeParent))
                return

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
            # TODO - GetItemText...?
            if self.__useIcons:
                self.GetParent().AddPage(FrameScriptEditor(self.GetParent(), self._filesystem, self._bankInstructions, eventId, self._state), name, bitmap=self.__icons.GetBitmap(self.__idImageEvent))
            else:
                self.GetParent().AddPage(FrameScriptEditor(self.GetParent(), self._filesystem, self._bankInstructions, eventId, self._state), name)

        def handlePuzzleItem(item):
            idInternal = self.treeOverview.GetItemData(item)
            if type(idInternal) != int:
                print("Cannot launch puzzle", idInternal)
                return
            # TODO - See above
            # TODO - Add page method this is stupid
            if self.__useIcons:
                self.GetParent().AddPage(FramePuzzleEditor(self.GetParent(), self._filesystem, idInternal, self._state), self.treeOverview.GetItemText(item), bitmap=self.__icons.GetBitmap(self.__idImagePuzzle))
            else:
                self.GetParent().AddPage(FramePuzzleEditor(self.GetParent(), self._filesystem, idInternal, self._state), self.treeOverview.GetItemText(item))

        def handlePlaceItem(item):
            groupPlace : PlaceGroup = self.treeOverview.GetItemData(item)
            self.GetParent().AddPage(FramePlaceEditor(self.GetParent(), self._filesystem, self._state, groupPlace), self.treeOverview.GetItemText(item))

        item = event.GetItem()

        if self._treeItemEvent != None and self._isItemWithinPathToItem(item, self._treeItemEvent):
            handleEventItem(item)
        elif self._treeItemPuzzle != None and self._isItemWithinPathToItem(item, self._treeItemPuzzle):
            handlePuzzleItem(item)
        elif self._treeItemPlace != None and self._isItemWithinPathToItem(item, self._treeItemPlace):
            handlePlaceItem(item)
        else:
            print("Unrecognised!")
        
        self.GetParent().Thaw()
            
        return super().treeOverviewOnTreeItemActivated(event)

    def _refresh(self):
        # TODO - Don't want to reload this every time!
        self._characters = getCharacters(self._state)
        self._eventsLoose, self._eventsGrouped = getEvents(self._filesystem, self._state)

        # TODO - Compile this database when needed. Ideally should not be loaded here...
        evLch = EventDescriptorBankNds()
        if (data := self._filesystem.getData(substituteLanguageString(self._state, PATH_DB_RC_ROOT % ("%s/ev_lch.dlz")))) != None:
            evLch.load(data)

        self.treeOverview.DeleteAllItems()

        if self.__useIcons:
            self.treeOverview.SetImageList(self.__icons)
        
        rootItem = self.treeOverview.AddRoot("You shouldn't see this!")

        def getEventComment(eventId, prefix = " - "):
            if (commentEntry := evLch.searchForEntry(eventId)) != None:
                return prefix + commentEntry.description
            return ""

        def addIfDataNotNone(data, root, nameTag, nameTagIfNotPresent = None, image=-1):
            if data == None:
                if nameTagIfNotPresent != None:
                    self.treeOverview.AppendItem(root, nameTagIfNotPresent, data=data, image=image)
            else:
                self.treeOverview.AppendItem(root, nameTag, data=data, image=image)

        def generateEventBranch():
            eventItem = self.treeOverview.AppendItem(rootItem, "Events", image=self.__idImageEvent)
            standardItem = self.treeOverview.AppendItem(eventItem, "Standard", image=self.__idImageEvent)
            puzzleItem = self.treeOverview.AppendItem(eventItem, "Puzzles", image=self.__idImagePuzzle)
            teaItem = self.treeOverview.AppendItem(eventItem, "Tea Minigame", image=self.__idTea)
            badItem = self.treeOverview.AppendItem(eventItem, "Misconfigured", image=self.__idImageBad)

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
                    if info == None:
                        print("Fail", key)
                else:
                    info = None

                if type(entry) == int:
                    # Just add event to list
                    name = str(entry)
                    imageId = self.__idImageEvent

                    if entry in databaseIn:
                        # TODO - 4 shouldn't be possible here...
                        if info.typeEvent == 1 or info.typeEvent == 4:
                            name = "Removable " + name
                            imageId = self.__idRemovable

                    # TODO - Remove, just for testing to not clutter space
                    # TODO - constant
                    if entry >= 20000:
                        self.treeOverview.AppendItem(badItem, name + getEventComment(entry), data=entry, image=imageId)
                    else:
                        self.treeOverview.AppendItem(standardItem, name + getEventComment(entry), data=entry, image=imageId)
                else:
                    if type(entry) == EventConditionAwaitingViewedExecutionGroup:
                        branchRoot = self.treeOverview.AppendItem(standardItem, "Conditional on " + str(key) + getEventComment(key), data=entry, image=self.__idImageConditional)
                        self.treeOverview.AppendItem(branchRoot, "On initial execution" + getEventComment(entry.idBase), data=entry.idBase, image=self.__idImageEvent)
                        self.treeOverview.AppendItem(branchRoot, "On future executions" + getEventComment(entry.idViewed), data=entry.idViewed, image=self.__idImageEvent)

                    elif type(entry) == EventConditionPuzzleExecutionGroup:
                        branchRoot = self.treeOverview.AppendItem(standardItem, "Conditional on " + str(key) + getEventComment(key), data=entry, image=self.__idImageConditional)
                        self.treeOverview.AppendItem(branchRoot, "On initial execution" + getEventComment(entry.idBase), data=entry.idBase, image=self.__idImageEvent)
                        if entry.idViewed != None:
                            self.treeOverview.AppendItem(branchRoot, "On future executions unless limit met" + getEventComment(entry.idViewed), data=entry.idViewed, image=self.__idImageEvent)
                        else:
                            self.treeOverview.AppendItem(branchRoot, "(untracked)", data=entry.idViewed, image=self.__idImageEvent)

                        if entry.idSuccessful != None:
                            self.treeOverview.AppendItem(branchRoot, "On reaching puzzle requirement" + getEventComment(entry.idSuccessful), data=entry.idSuccessful, image=self.__idImageEvent)
                        else:
                            self.treeOverview.AppendItem(branchRoot, "(untracked)", data=entry.idSuccessful, image=self.__idImageEvent)

                    elif type(entry) == TeaExecutionGroup:
                        branchRoot = self.treeOverview.AppendItem(teaItem, "Branch on " + str(key) + getEventComment(key), data=entry, image=self.__idImageConditional)
                        for group in entry.group:
                            self.treeOverview.AppendItem(branchRoot, str(group) + getEventComment(group), data=group, image=self.__idImageEvent)
                    
                    elif type(entry) == PuzzleExecutionGroup:
                        # There can be duplicate events - see A Work of Art
                        if entry.idInternalPuzzle in condPuzzle:
                            condPuzzle[entry.idInternalPuzzle].append(entry)
                        else:
                            condPuzzle[entry.idInternalPuzzle] = [entry]
                    
                    else:
                        print("Unknown :: " + str(entry))
            
            idPuzzles = list(condPuzzle.keys())
            idPuzzles.sort()

            def addPuzzleEntryToBranch(head, entry):
                self.treeOverview.AppendItem(head, "On initial execution" + getEventComment(entry.idBase), data=entry.idBase, image=self.__idImageEvent)
                addIfDataNotNone(entry.idRetry, head, "On future executions while puzzle is unsolved" + getEventComment(entry.idRetry), image=self.__idImageEvent)
                addIfDataNotNone(entry.idSkip, head, "On execution if puzzle is skipped" + getEventComment(entry.idSkip), image=self.__idImageEvent)
                addIfDataNotNone(entry.idSolve, head, "On execution if puzzle is solved" + getEventComment(entry.idSolve), image=self.__idImageEvent)
                addIfDataNotNone(entry.idReturnAfterSolve, head, "On future executions while puzzle is solved" + getEventComment(entry.idReturnAfterSolve), image=self.__idImageEvent)

            def isPuzzleRemovable(entry):
                info = self._state.getEventInfoEntry(entry.idBase)
                isRemovable = False
                if info != None and info.typeEvent == 4:
                    isRemovable = True
                return isRemovable

            for key in idPuzzles:
                entry = condPuzzle[key][0]

                if (nzLstEntry := self._state.getNazoListEntry(entry.idInternalPuzzle)) != None:
                    puzzleEntryName = "%03d - %s" % (nzLstEntry.idExternal, nzLstEntry.name)
                else:
                    puzzleEntryName = "i%03d" % entry.idInternalPuzzle

                entryGroup = condPuzzle[key]
                if len(entryGroup) == 1:
                    if isPuzzleRemovable(entry):
                        branchRoot = self.treeOverview.AppendItem(puzzleItem, "Removable " + puzzleEntryName, data=entry, image=self.__idRemovable)
                    else:
                        branchRoot = self.treeOverview.AppendItem(puzzleItem, puzzleEntryName, data=entry, image=self.__idImagePuzzle)
                    self.treeOverview.AppendItem(branchRoot, "Edit puzzle data...", data=entry.idInternalPuzzle, image=self.__idImagePuzzle)
                    addPuzzleEntryToBranch(branchRoot, entry)
                else:
                    # TODO - Fix naming, unclear since they're the same under this paradigm
                    puzzleRoot = self.treeOverview.AppendItem(puzzleItem, puzzleEntryName, data=entry, image=self.__idImagePuzzle)
                    self.treeOverview.AppendItem(puzzleRoot, "Edit puzzle data...", data=entry.idInternalPuzzle, image=self.__idImagePuzzle)
                    for entry in entryGroup:
                        if isPuzzleRemovable(entry):
                            branchRoot = self.treeOverview.AppendItem(puzzleRoot, "Removable " + str(entry.idBase), data=entry, image=self.__idImageEvent)
                        else:
                            branchRoot = self.treeOverview.AppendItem(puzzleRoot, str(entry.idBase), data=entry, image=self.__idImageEvent)
                        addPuzzleEntryToBranch(branchRoot, entry)

        def generatePuzzleBranch():
            puzzleItem = self.treeOverview.AppendItem(rootItem, "Puzzles", image=self.__idImagePuzzle)
            normalItem = self.treeOverview.AppendItem(puzzleItem, "Standard", image=self.__idImagePuzzle)
            wifiItem = self.treeOverview.AppendItem(puzzleItem, "WiFi", image=self.__idImageWifi)
            specialItem = self.treeOverview.AppendItem(puzzleItem, "Special", image=self.__idSpecial)

            self._loadPuzzleCache()
            self._treeItemPuzzle = puzzleItem

            def fillPuzzleBranch(root, entryList : List[PuzzleEntry]):

                def getKey(entry : PuzzleEntry):
                    return entry.idExternal

                entryList.sort(key=getKey)
                for entry in entryList:
                    name = "%03i - %s" % (entry.idExternal, entry.name)
                    self.treeOverview.AppendItem(root, name, data=entry.idInternal, image=self.__idImagePuzzle)
            
            fillPuzzleBranch(normalItem, self._puzzles[0])
            fillPuzzleBranch(wifiItem, self._puzzles[1])
            fillPuzzleBranch(specialItem, self._puzzles[2])

        def generateCharacterBranch():
            characterItem = self.treeOverview.AppendItem(rootItem, "Characters")
            self._treeItemCharacter = characterItem
            for indexCharacter, character in enumerate(self._characters):
                self.treeOverview.AppendItem(characterItem, "Character " + str(indexCharacter + 1))

        def generatePlaceBranch():
            placeGroups = getPlaceGroups(self._filesystem)
            self._treeItemPlace = self.treeOverview.AppendItem(rootItem, "Rooms")
            self.treeOverview.AppendItem(self._treeItemPlace, "Bootstrap Room")
            for group in placeGroups:
                self.treeOverview.AppendItem(self._treeItemPlace, "Room " + str(group.indexPlace), data=group)

        def generateStoryflagBranch():
            
            def getStoryflagToEventMap() -> Dict[int, int]:
                evInf = EventInfoList()
                if (data := self._filesystem.getData(substituteLanguageString(self._state, PATH_DB_EV_INF2))) != None:
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

            storyFlag = StoryFlag()

            if (data := self._filesystem.getPackedData(PATH_PROGRESSION_DB, PATH_DB_STORYFLAG)):
                storyFlag.load(data)
            
            branchRoot = self.treeOverview.AppendItem(rootItem, "Chapter Progression")
            flagRoot = self.treeOverview.AppendItem(branchRoot, "Chapter 0 (erroneous)")

            mapStoryflagToEvent = getStoryflagToEventMap()

            for group in storyFlag.flagGroups:

                if group.getChapter() == 0:
                    isEmpty = True
                    for indexFlag in range(8):
                        # TODO - Do we terminate early? Think so but needs checking
                        if group.getFlag(indexFlag).type != 0:
                            isEmpty = False
                    if isEmpty:
                        continue

                flagRoot = self.treeOverview.AppendItem(branchRoot, "Chapter " + str(group.getChapter()))
                for indexFlag in range(8):
                    flag = group.getFlag(indexFlag)
                    if flag != None:

                        # TODO - There are intentional false cases, e.g. chapter 760 which refers to an impossible puzzle
                        #        This stops the game from accidentally rolling over to chapter 0

                        # Check puzzle completion
                        if flag.type == 2:
                            nzLstEntry = self._state.getNazoListEntry(flag.param)
                            if nzLstEntry != None:
                                self.treeOverview.AppendItem(flagRoot, 'Solve "%03i - %s"' % (nzLstEntry.idExternal, nzLstEntry.name))
                            else:
                                self.treeOverview.AppendItem(flagRoot, "Progression blocker - illegal puzzle")
                        
                        # Check storyflag set
                        # TODO - Method to generate event friendly names
                        elif flag.type == 1:
                            if flag.param in mapStoryflagToEvent:
                                if len(mapStoryflagToEvent[flag.param]) == 1:
                                    self.treeOverview.AppendItem(flagRoot, "Play event " + str(mapStoryflagToEvent[flag.param][0]))
                                else:
                                    desc = ""
                                    for indexEventId, eventId in enumerate(mapStoryflagToEvent[flag.param]):
                                        if indexEventId == 0:
                                            desc = str(eventId)
                                        elif indexEventId != len(mapStoryflagToEvent[flag.param]) - 1:
                                            desc = desc + ", " + str(eventId)
                                        else:
                                            desc = " or " + str(eventId)
                                    self.treeOverview.AppendItem(flagRoot, "Play events " + desc)
                            else:
                                self.treeOverview.AppendItem(flagRoot, "Story flag " + str(flag.param) + " set")
        
        # TODO - Add way to access progression marker for room 0 (empty by default!)
        # TODO - Display progression markers per-room

        generateEventBranch()
        generatePuzzleBranch()
        generateCharacterBranch()
        generatePlaceBranch()
        generateStoryflagBranch()

        # Generate branch for mysteries, journal, anton's diary