from typing import Dict, List, Optional
from editor.asset_management.character import CharacterEntry, computeCharacterNames
from editor.asset_management.puzzle import PuzzleEntry, getPuzzles
from editor.branch_management import EventBranchManager
from editor.branch_management.branch_chapter.branch_chapter import ChapterBranchManager
from editor.branch_management.branch_event.branch_event import EventBranchIcons
from editor.e_puzzle import FramePuzzleEditor
from editor.e_room import FramePlaceConditionalEditor
from editor.e_script.e_script_event import FrameEventEditor
from editor.e_script.e_script_generic_unpacked import FrameScriptEditorUnpackedEvent
from editor.gui.command_annotator.bank import ScriptVerificationBank
from editor.asset_management.room import PlaceGroup, getPlaceGroups
from editor.treeUtils import isItemOnPathToItem
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.common import logSevere
from ..nopush_editor import pageOverview
from widebrim.engine.state.manager import Layton2GameState
from editor.asset_management import getCharacters, getEvents
from wx import ImageList, TreeItemId

from widebrim.engine.const import PATH_DB_RC_ROOT
from widebrim.engine_ext.utils import substituteLanguageString
from widebrim.madhatter.hat_io.asset_dlz.ev_lch import EventDescriptorBankNds

from editor.icons.getIconFromRom import getImageAndSetVariable

# TODO - Check if pages already open
# TODO - Chapter progression needs to be reloaded after event changes

class FrameOverviewTreeGen(pageOverview):

    LOG_MODULE_NAME : str = "OverviewGen"

    SIZE_ICONS = (16,16)

    def __init__(self, parent, filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, instructionBank : ScriptVerificationBank):
        super().__init__(parent)
        self._bankInstructions = instructionBank
        self._filesystem = filesystem
        self._state = state

        self._characters : List[CharacterEntry] = []
        self._characterNames : List[str] = []
        self._eventsLoose = ([], [])
        self._eventsGrouped = []

        self._puzzles : List[List[PuzzleEntry]] = [[],[],[]]
        self._idToPuzzleEntry : Dict[int, PuzzleEntry] = {}
        # TODO - Puzzles?

        self.__useIcons = False
        self.__icons = ImageList(FrameOverviewTreeGen.SIZE_ICONS[0], FrameOverviewTreeGen.SIZE_ICONS[1])

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
        
        iconPack = EventBranchIcons(idImagePuzzle = self.__idImagePuzzle, idImageEvent = self.__idImageEvent, idImageConditional = self.__idImageConditional,
                                    idImageBad = self.__idImageBad, idImageRemovable = self.__idRemovable, idImageTea = self.__idTea)
        self._eventManager = EventBranchManager(state, self.treeOverview, iconPack=iconPack)
        self._chapterManager = ChapterBranchManager(state, self.treeOverview)

        self._treeItemEvent     : Optional[TreeItemId] = None
        self._treeItemPuzzle    : Optional[TreeItemId] = None
        self._treeItemCharacter : Optional[TreeItemId] = None
        self._treeItemChapter   : Optional[TreeItemId] = None
        self._treeItemPlace     : Optional[TreeItemId] = None
        
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

    def _isItemWithinPathToItem(self, itemSearchEnd : TreeItemId, itemSearch) -> bool:
        return isItemOnPathToItem(self.treeOverview, itemSearchEnd, itemSearch)

    def treeOverviewOnTreeItemActivated(self, event):
        # TODO - Can probably get bitmap from icons
        self.GetParent().Freeze()

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
            if item != self._treeItemPlace:
                groupPlace : PlaceGroup = self.treeOverview.GetItemData(item)
                self.GetParent().AddPage(FramePlaceConditionalEditor(self.GetParent(), self._filesystem, self._state, groupPlace), self.treeOverview.GetItemText(item))

        def handleEventItem(item):
            response = self._eventManager.getCorrespondingEventActivatedItem(item)
            if not(response.isNothing):
                if response.isEvent:
                    self.GetParent().AddPage(FrameEventEditor(self.GetParent(), self._state, self._bankInstructions, response.getEventId(), self._characters, self._characterNames), response.getTabName(), bitmap=self.__icons.GetBitmap(self.__idImageEvent))
                elif response.isPuzzle:
                    if not(response.isPuzzleInternalOnly()):
                        # TODO - Prevent user from spawning this until they have added a nazo list entry (should actually get nazo data...)
                        logSevere("Crucial puzzle data missing!", name=FrameOverviewTreeGen.LOG_MODULE_NAME)
                    else:
                        self.GetParent().AddPage(FramePuzzleEditor(self.GetParent(), self._filesystem, response.getInternalPuzzleId(), self._state), response.getTabName(), bitmap=self.__icons.GetBitmap(self.__idImagePuzzle))

        def handleChapterItem(item):
            pass

        item = event.GetItem()

        if self._treeItemEvent != None and self._isItemWithinPathToItem(item, self._treeItemEvent):
            handleEventItem(item)
        elif self._treeItemPuzzle != None and self._isItemWithinPathToItem(item, self._treeItemPuzzle):
            handlePuzzleItem(item)
        elif self._treeItemPlace != None and self._isItemWithinPathToItem(item, self._treeItemPlace):
            handlePlaceItem(item)
        else:
            wasHandled = False
            if (data := self.treeOverview.GetItemData(item)) != None:
                if type(data) == str:
                    if len(data) > 4 and data[-4:] == ".gds":
                        self.GetParent().AddPage(FrameScriptEditorUnpackedEvent(self.GetParent(), self._state, self._bankInstructions, data), "Intro Event", bitmap=self.__icons.GetBitmap(self.__idImageEvent))
                        wasHandled = True
            
            if not(wasHandled):
                logSevere("Unrecognised!", name=FrameOverviewTreeGen.LOG_MODULE_NAME)
        
        self.GetParent().Thaw()
            
        return super().treeOverviewOnTreeItemActivated(event)

    def _refresh(self):
        # TODO - Don't want to reload this every time!
        self._characters = getCharacters(self._state)
        self._characterNames = computeCharacterNames(self._state, self._characters)

        # TODO - Compile this database when needed. Ideally should not be loaded here...
        evLch = EventDescriptorBankNds()
        if (data := self._filesystem.getData(substituteLanguageString(self._state, PATH_DB_RC_ROOT % ("%s/ev_lch.dlz")))) != None:
            evLch.load(data)

        self.treeOverview.DeleteAllItems()

        if self.__useIcons:
            self.treeOverview.SetImageList(self.__icons)
        
        rootItem = self.treeOverview.AddRoot("You shouldn't see this!")

        def generateEventBranch():
            self._treeItemEvent = self.treeOverview.AppendItem(rootItem, "Events", image=self.__idImageEvent)
            self._eventManager.createTreeBranches(self._treeItemEvent, getEvents(self._state.getFileAccessor(), self._state))

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
            for indexCharacter, characterName in enumerate(zip(self._characters, self._characterNames)):
                character, name = characterName
                if name == None:
                    name = "Character %i" % character.getIndex()
                self.treeOverview.AppendItem(characterItem, "%i - %s" % (character.getIndex(), name), data=character)

        def generatePlaceBranch():
            placeGroups = getPlaceGroups(self._filesystem)
            self._treeItemPlace = self.treeOverview.AppendItem(rootItem, "Rooms")
            self.treeOverview.AppendItem(self._treeItemPlace, "Bootstrap Room")
            for group in placeGroups:
                self.treeOverview.AppendItem(self._treeItemPlace, "Room " + str(group.indexPlace), data=group)

        def generateStoryflagBranch():
            self._treeItemChapter = self.treeOverview.AppendItem(rootItem, "Chapter Progression")
            self._chapterManager.createTreeBranches(self._treeItemChapter)

        # TODO - Add way to access progression marker for room 0 (empty by default!)
        # TODO - Display progression markers per-room

        generateEventBranch()
        generatePuzzleBranch()
        generateCharacterBranch()
        generatePlaceBranch()
        generateStoryflagBranch()

        self.treeOverview.AppendItem(rootItem, "Introduction Event", data="/data_lt2/script/logo.gds")

        # Generate branch for mysteries, journal, anton's diary