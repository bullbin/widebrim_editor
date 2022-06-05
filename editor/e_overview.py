from typing import Dict, List, Optional, Tuple
from editor.asset_management.event import EventConditionAwaitingViewedExecutionGroup, EventConditionPuzzleExecutionGroup, PuzzleExecutionGroup, TeaExecutionGroup
from editor.asset_management.puzzle import PuzzleEntry, getPuzzles
from editor.e_script import FrameScriptEditor
from editor.e_puzzle import FramePuzzleEditor
from editor.gui.command_annotator.bank import ScriptVerificationBank
from editor.asset_management.room import getPlaceGroups
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
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
        self._characters = getCharacters(state)
        self._eventsLoose, self._eventsGrouped = getEvents(self._filesystem, state)
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
            
            # self.treeOverview.SetItemBold(eventItem, True)

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
                    imageId = self.__idImageEvent

                    if entry in databaseIn:
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

                branchRoot = self.treeOverview.AppendItem(puzzleItem, puzzleEntryName, data=entry, image=self.__idImagePuzzle)

                self.treeOverview.AppendItem(branchRoot, "Edit puzzle data...", data=entry.idInternalPuzzle, image=self.__idImagePuzzle)

                self.treeOverview.AppendItem(branchRoot, "On initial execution" + getEventComment(entry.idBase), data=entry.idBase, image=self.__idImageEvent)
                addIfDataNotNone(entry.idRetry, branchRoot, "On future executions while puzzle is unsolved" + getEventComment(entry.idRetry), image=self.__idImageEvent)
                addIfDataNotNone(entry.idSkip, branchRoot, "On execution if puzzle is skipped" + getEventComment(entry.idSkip), image=self.__idImageEvent)
                addIfDataNotNone(entry.idSolve, branchRoot, "On execution if puzzle is solved" + getEventComment(entry.idSolve), image=self.__idImageEvent)
                addIfDataNotNone(entry.idReturnAfterSolve, branchRoot, "On future executions while puzzle is solved" + getEventComment(entry.idReturnAfterSolve), image=self.__idImageEvent)

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