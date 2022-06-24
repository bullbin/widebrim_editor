from typing import Dict, List, Optional, Tuple
from editor.asset_management.event import EventConditionAwaitingViewedExecutionGroup, EventConditionPuzzleExecutionGroup, PuzzleExecutionGroup, TeaExecutionGroup, createBlankEvent, createBlankPuzzleEventChain, createConditionalRevisit, createConditionalRevisitAndPuzzleLimit, getFreeEventViewedFlags
from editor.asset_management.puzzle import PuzzleEntry, getPuzzles
from editor.d_operandMultichoice import DialogMultipleChoice
from editor.e_script import FrameScriptEditor
from editor.e_puzzle import FramePuzzleEditor
from editor.e_script.get_input_popup import VerifiedDialog, rangeIntCheckFunction
from editor.gui.command_annotator.bank import ScriptVerificationBank
from editor.asset_management.room import getPlaceGroups
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.common import logSevere
from .nopush_editor import pageOverview
from widebrim.engine.state.manager import Layton2GameState
from editor.asset_management import getCharacters, getEvents
import wx

from widebrim.engine.const import PATH_ANI, PATH_DB_RC_ROOT
from widebrim.engine_ext.utils import substituteLanguageString
from widebrim.madhatter.hat_io.asset_image import AnimatedImage, getTransparentLaytonPaletted
from widebrim.madhatter.hat_io.asset_dlz.ev_lch import EventDescriptorBankNds
from PIL.Image import Image as ImageType
from PIL import Image

# TODO - Check if pages already open

class FrameOverview(pageOverview):

    SIZE_ICONS = (16,16)

    def __init__(self, parent, filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, instructionBank : ScriptVerificationBank, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(640, 640), style=wx.TAB_TRAVERSAL, name=wx.EmptyString):

        self._bankInstructions = instructionBank
        self._filesystem = filesystem

        # TODO - Maybe make class variable. Should only load once though
        def prepareIcons(size : Tuple[int,int]):

            def getFrameOfImage(aniPath : str, frameIndex=0) -> Optional[ImageType]:
                if (data := self._filesystem.getData(PATH_ANI % aniPath)) != None:
                    if len(aniPath) > 3:
                        if aniPath[-3:] == "arc":
                            image = AnimatedImage.fromBytesArc(data)
                        else:
                            image = AnimatedImage.fromBytesArj(data)

                        if image != None and len(image.frames) > frameIndex and frameIndex >= 0:
                            image = image.frames[frameIndex].getComposedFrame()
                            if image.mode != "RGBA":
                                image = getTransparentLaytonPaletted(image)
                                if image.width != image.height:
                                    dim = max(image.width, image.height)
                                    output = Image.new("RGBA", (dim,dim))
                                    marginLeft = (dim - image.width) // 2
                                    marginUp = (dim - image.height) // 2
                                    output.paste(image, (marginLeft, marginUp))
                                    image = output
                            return image
                return None
            
            def pillowToWx(image : ImageType, resize : Optional[Tuple[int,int]] = None) -> wx.Bitmap:
                if resize != None:
                    image = image.resize(size)
                
                output = wx.Bitmap.FromBufferRGBA(image.width, image.height, image.tobytes())
                return output
            
            def getThumbnailImage(aniPath : str, resize=(16,16), forceImageIndex=0) -> Optional[wx.Bitmap]:
                image = getFrameOfImage(aniPath, frameIndex=forceImageIndex)
                if image != None:
                    image = pillowToWx(image, resize=resize)
                    return image
                return None
            
            def getImageAndSetVariable(aniPath : str, resize=(16,16), forceImageIndex=0) -> int:
                image = getThumbnailImage(aniPath, resize, forceImageIndex)
                if image != None:
                    self.__icons.Add(image)
                    self.__useIcons = True
                    return self.__icons.GetImageCount() - 1
                return -1

            self.__idImagePuzzle = getImageAndSetVariable("event/nazo_icon.arc", size)
            self.__idImageEvent = getImageAndSetVariable("subgame/photo/check_icon.arc", size)
            self.__idImageConditional = getImageAndSetVariable("event/diary_icon.arc", size)
            self.__idImageBad = getImageAndSetVariable("map/icon_buttons.arc", size)
            self.__idImageWifi = getImageAndSetVariable("menu/wifi/wifi_ant.arj", size, forceImageIndex=3)
            self.__idRemovable = getImageAndSetVariable("nazo/onoff/q49_x.arc", size)
            self.__idSpecial = getImageAndSetVariable("tobj/icon.arc", size, forceImageIndex=2)
            self.__idTea = getImageAndSetVariable("subgame/tea/tea_icon.arc", size, forceImageIndex=2)

        super().__init__(parent, id, pos, size, style, name)
        self._characters = []
        self._eventsLoose = ([], [])
        self._eventsGrouped = []
        self._puzzles : List[List[PuzzleEntry]] = [[],[],[]]
        self._idToPuzzleEntry : Dict[int, PuzzleEntry] = {}
        # TODO - Puzzles?

        self.__icons = wx.ImageList(FrameOverview.SIZE_ICONS[0], FrameOverview.SIZE_ICONS[1])
        self.__idImageEvent         = -1
        self.__idImagePuzzle        = -1
        self.__idImageConditional   = -1
        self.__idImageBad           = -1
        self.__idImageWifi          = -1
        self.__idRemovable          = -1
        self.__idSpecial            = -1
        self.__idTea                = -1
        self.__useIcons = False
        prepareIcons(FrameOverview.SIZE_ICONS)
        
        self._state = state
        self._treeItemEvent = None
        self._treeItemPuzzle = None
        self._treeItemCharacter = None
        self._treeItemPlace = None
        self._loaded = False
        self._areCommentsLoaded = False

        self.GetParent().SetDoubleBuffered(True)
    
    def ensureLoaded(self):
        if not(self._loaded):
            self._refresh()
            self._loaded = True
    
    def __loadPuzzleCache(self):
        self._puzzles = getPuzzles(self._state)
        for entry in self._puzzles[0] + self._puzzles[1] + self._puzzles[2]:
            self._idToPuzzleEntry[entry.idInternal] = entry

    def __isItemWithinPathToItem(self, itemSearchEnd : wx.TreeItemId, itemSearch) -> bool:
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

        item = event.GetItem()

        if self._treeItemEvent != None and self.__isItemWithinPathToItem(item, self._treeItemEvent):
            handleEventItem(item)
        elif self._treeItemPuzzle != None and self.__isItemWithinPathToItem(item, self._treeItemPuzzle):
            handlePuzzleItem(item)
        else:
            print("Unrecognised!")
        
        self.GetParent().Thaw()
            
        return super().treeOverviewOnTreeItemActivated(event)

    def setCommentStatus(self, status : bool):
        if status != self._areCommentsLoaded:
            self._areCommentsLoaded = status
            self._refresh()
    
    def triggerReloadEventComment(self, eventId : int):
        # TODO - Filter branch by event, might need map to do this easily
        self._refresh()

    def _refresh(self):
        # TODO - Don't want to reload this every time!
        self._characters = getCharacters(self._state)
        self._eventsLoose, self._eventsGrouped = getEvents(self._filesystem, self._state)

        evLch = EventDescriptorBankNds()
        if self._areCommentsLoaded:
            # TODO - Compile this database when needed. Ideally should not be loaded here...
            evLch = EventDescriptorBankNds()
            if (data := self._filesystem.getData(substituteLanguageString(self._state, PATH_DB_RC_ROOT % ("%s/ev_lch.dlz")))) != None:
                evLch.load(data)

        self.treeOverview.DeleteAllItems()

        if self.__useIcons:
            self.treeOverview.SetImageList(self.__icons)
        
        rootItem = self.treeOverview.AddRoot("You shouldn't see this!")

        def getEventComment(eventId, prefix = " - "):
            if self._areCommentsLoaded:
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

            self.__loadPuzzleCache()
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

        generateEventBranch()
        generatePuzzleBranch()
        generateCharacterBranch()
        generatePlaceBranch()

        # Generate branch for mysteries, journal, anton's diary
    
    def __isEventIdSafe(self, eventId : int, useGap = True, gap = 5):

        idRange = []

        def addToRange(listId : List[int]):
            for id in listId:
                if id != None:
                    if id not in idRange:
                        idRange.append(id)

        for group in self._eventsGrouped:
            idGroup = group.group
            addToRange(idGroup)

        for loose in self._eventsLoose:
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
            self.__loadPuzzleCache()
        if len(self._puzzles[0]) == 0:
            return []

        # TODO - Not foolproof, since not all puzzles are captured by this technique
        idsUsed : List[int] = []
        for group in self._eventsGrouped:
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

        for group in self._eventsGrouped:
            idGroup = group.group
            addToRange(idGroup)

        for loose in self._eventsLoose:
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
        itemFocused = self.treeOverview.GetFocusedItem()
        if self.__isItemWithinPathToItem(self.treeOverview.GetFocusedItem(), self._treeItemEvent):
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
                        # TODO - Use return to reduce recalculation of everything
                        self._eventsLoose[0].append(createBlankEvent(self._filesystem, self._state, idEvent))
                        self._refresh()

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
                                self._eventsGrouped.append(createConditionalRevisit(self._filesystem, self._state, idEvent, availableFlagsViewed[0]))
                            else:
                                puzzleCountDlg = VerifiedDialog(wx.TextEntryDialog(self, "Set Puzzle Count"), rangeIntCheckFunction(1, 255), "The limit must sit between 1 and 255 puzzles!")
                                status = puzzleCountDlg.do("1")
                                if status == None:
                                    # TODO - go back? this whole method is bad
                                    return super().btnCreateNewOnButtonClick(event)
                                else:
                                    self._eventsGrouped.append(createConditionalRevisitAndPuzzleLimit(self._filesystem, self._state, idEvent, availableFlagsViewed[0], int(status)))
                            self._refresh()

                elif idxSelection == 2:
                    idEvent = self.__doEventIdDialog(20, 26)
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
                    self._eventsGrouped.append(createBlankPuzzleEventChain(self._filesystem, self._state, idEvent, entry.idInternal, entry.idExternal))
                    self._refresh()

                else:
                    idEvent = self.__doEventIdDialog(30,30)
        return super().btnCreateNewOnButtonClick(event)
    
    def btnDuplicateOnButtonClick(self, event):
        return super().btnDuplicateOnButtonClick(event)
    
    def btnEditConditionOnButtonClick(self, event):
        return super().btnEditConditionOnButtonClick(event)
    
    def btnGetRefOnButtonClick(self, event):
        return super().btnGetRefOnButtonClick(event)