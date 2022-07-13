from typing import Any, Callable, Dict, List, Optional, Tuple
from editor.asset_management.plz_txt.jiten import createNextNewRoomTitleId, getFreeRoomJitenNameTagId, getUsedRoomNameTags
from editor.asset_management.room import PlaceGroup, getPackPathForPlaceIndex
from editor.d_operandMultichoice import DialogMultipleChoice
from editor.e_script.get_input_popup import VerifiedDialog
from widebrim.madhatter.hat_io.asset import File
from .treeGroups import TreeGroupBackgroundAnimation, TreeGroupEventSpawner, TreeGroupExit, TreeGroupHintCoin, TreeGroupTObj, TreeObjectPlaceData
from editor.nopush_editor import editorRoom
from widebrim.engine.const import PATH_DB_PLACEFLAG, PATH_EXT_EVENT, PATH_PACK_PLACE_NAME, PATH_PLACE_BG, PATH_PLACE_MAP, PATH_PROGRESSION_DB, PATH_TEXT_PLACE_NAME, RESOLUTION_NINTENDO_DS
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.engine_ext.utils import getBottomScreenAnimFromPath, getImageFromPath, substituteLanguageString
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from wx import TreeItemId, Bitmap, ID_OK, TextEntryDialog
from widebrim.gamemodes.room.const import PATH_ANIM_BGANI, PATH_PACK_PLACE
from pygame import Surface
from pygame.image import tostring

from widebrim.madhatter.hat_io.asset_dat.place import PlaceData, PlaceDataNds
from widebrim.madhatter.hat_io.asset_placeflag import PlaceFlag

from re import search

# TODO - AutoEvent

class FramePlaceEditor(editorRoom):

    INVALID_FRAME_COLOR = (255,0,0)

    def __init__(self, parent, filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, groupPlace : PlaceGroup):
        super().__init__(parent)
        self._filesystem = filesystem
        self._state = state
        self._groupPlace = groupPlace
        
        self._dataPlace         : List[PlaceData]             = []
        self._treeToPlaceData   : Dict[TreeItemId, PlaceData] = {}

        self._treeRoot                  : Optional[TreeItemId] = None

        self._treeItemName              : Optional[TreeItemId] = None
        self._treeItemMapPos            : Optional[TreeItemId] = None
        self._treeItemSound             : Optional[TreeItemId] = None

        self._treeRootProperties        : Optional[TreeItemId] = None
        self._treeRootConditional       : Optional[TreeItemId] = None
        self._treeRootHintCoin          : Optional[TreeItemId] = None
        self._treeRootBackgroundAnim    : Optional[TreeItemId] = None
        self._treeRootEventSpawner      : Optional[TreeItemId] = None
        self._treeRootTextObjectSpawner : Optional[TreeItemId] = None
        self._treeRootExit              : Optional[TreeItemId] = None
        self._treeRootAutoevent         : Optional[TreeItemId] = None

        self._treeItemsTObj             : List[TreeGroupTObj] = []
        self._treeItemsEventSpawner     : List[TreeGroupEventSpawner] = []
        self._treeItemsHintCoin         : List[TreeGroupHintCoin] = []
        self._treeItemsBgAni            : List[TreeGroupBackgroundAnimation] = []
        self._treeItemsExits            : List[TreeGroupExit] = []

        self._loaded = False
        self.__invalidSurface = Surface(RESOLUTION_NINTENDO_DS)
        self.__invalidSurface.fill(FramePlaceEditor.INVALID_FRAME_COLOR)

        self.__lastValidSuggestion = None
    
    def ensureLoaded(self):
        if self._loaded:
            return

        pathPack = getPackPathForPlaceIndex(self._groupPlace.indexPlace)
        pack = self._filesystem.getPack(pathPack)
        for index in self._groupPlace.indicesStates:
            loadedPlace = PlaceDataNds()
            if (data := pack.getFile(PATH_PACK_PLACE % (self._groupPlace.indexPlace, index))) != None:
                loadedPlace.load(data)
            self._dataPlace.append(loadedPlace)

        self._generateList()
        self._generateTree()
        self._generateBackgrounds()
        self._loaded = True

    def treeStateProgressionOnTreeSelChanged(self, event):
        if self.__lastValidSuggestion != self._getActiveState():
            self._generateTree()
            self._generateBackgrounds()
        return super().treeStateProgressionOnTreeSelChanged(event)

    def treeParamOnTreeSelChanged(self, event):
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if not(self.treeParam):
            return super().treeParamOnTreeSelChanged(event)
        
        item = self.treeParam.GetFocusedItem()
        print(self.treeParam.GetItemText(item), "->", self.treeParam.GetItemData(item))

        for tobj in self._treeItemsTObj:
            if tobj.isItemSelected(item):
                print("TObj select, highlight mode")
                if item == tobj.itemBounding:
                    print("\tBound select")
                elif item == tobj.itemChar:
                    print("\tChar select")
                else:
                    print("\tMessage select")
                # TODO - Save changes to TObj on modification
                return super().treeParamOnTreeSelChanged(event)

        return super().treeParamOnTreeSelChanged(event)
    
    def treeParamOnTreeItemActivated(self, event):

        def modifyName() -> Optional[int]:

            def strCheckFunction() -> Callable[[str], Tuple[bool, Any]]:
                def output(x : str) -> bool:
                    if 0 < len(x) <= 32:
                        return (True, x)
                    return (False, "")
                return output

            usedNames = getUsedRoomNameTags(self._state)
            freeIds = getFreeRoomJitenNameTagId(self._state, usedTags=usedNames)
            uniqueNames = {}
            for key in usedNames.keys():
                value = usedNames[key]
                if value in uniqueNames:
                    uniqueNames[value].append(key)
                else:
                    uniqueNames[value] = [key]
            
            names = list(uniqueNames.keys())
            names.sort()
            
            # TODO - Rename room support ("toolbar...?")
            # TODO - Proper room name management (cannot delete names)
            # TODO - Bad if they can select this using a custom room name!
            if len(freeIds) > 0:
                choices = {"Create new room name...":"Creates a new room name.\nTo rename an active room tag, use the toolbar."}
            else:
                choices = {}
            choicesToKeys = {}
            for name in names:
                if len(uniqueNames[name]) == 1:
                    choices[name] = name
                    choicesToKeys[name] = uniqueNames[name][0]
                else:
                    for indexKey, key in enumerate(uniqueNames[name]):
                        newName = "[Copy %i] %s" % (indexKey, name)
                        choices[newName] = name
                        choicesToKeys[newName] = key
            
            while True:
                dlg = DialogMultipleChoice(self, choices, "Change Room Name...")
                value = dlg.ShowModal()
                if value != ID_OK:
                    return None
                value = dlg.GetSelection()
                if value in choicesToKeys:
                    return choicesToKeys[value]

                # Only reason for it not being there is that they have chosen to create a new value
                dlg = VerifiedDialog(TextEntryDialog(self, "Enter a string"), strCheckFunction())
                newName = dlg.do("New Room Title")
                if newName != None:
                    return createNextNewRoomTitleId(self._state, newName)

        def getBackgroundDevoidOfControl(treeGroup) -> Surface:
            pathBgMain = PATH_PLACE_BG % self._getActiveState().bgMainId
            background = getImageFromPath(self._state, pathBgMain)
            if background == None:
                background = self.__invalidSurface

            for spawner in self._treeItemsBgAni + self._treeItemsEventSpawner + self._treeItemsExits + self._treeItemsTObj + self._treeItemsHintCoin:
                if spawner != treeGroup:
                    spawner.renderSelectionLine(background)
            return background

        item = self.treeParam.GetSelection()
        if item == self._treeItemName:
            # TODO - Select name
            newId = modifyName()
            # TODO - Change all
            self.treeParam.SetItemData(item, newId)
            self.treeParam.SetItemText(item, "Name: %s" % self._filesystem.getPackedString(substituteLanguageString(self._state, PATH_PACK_PLACE_NAME), PATH_TEXT_PLACE_NAME % newId))
            self._getActiveState().idNamePlace = newId
            return super().treeParamOnTreeItemActivated(event)

        for obj in self._treeItemsTObj + self._treeItemsEventSpawner + self._treeItemsHintCoin + self._treeItemsBgAni + self._treeItemsExits:
            obj : TreeObjectPlaceData
            if obj.isItemSelected(item):
                result = obj.modifyItem(self._state, self.treeParam, item, self, getBackgroundDevoidOfControl(obj))
                print("Modified: %s" % self.treeParam.GetItemText(item))
                if result.backgroundRefresh:
                    self._generateBackgrounds()

                return super().treeParamOnTreeItemActivated(event)
        print("Cannot edit!")
        return super().treeParamOnTreeItemActivated(event)

    def syncChanges(self):
        pathPack = getPackPathForPlaceIndex(self._groupPlace.indexPlace)
        pack = self._filesystem.getPack(pathPack)

        datPlace = PATH_PACK_PLACE.replace("%i", "([0-9]*)")

        contents : Dict[int, Dict[int, File]] = {}
        for file in pack.files:
            
            if (result := search(datPlace, file.name)) != None:
                indexPlace = int(result.group(1))
                indexSubPlace = int(result.group(2))
                
                if indexPlace != self._groupPlace.indexPlace:
                    if indexPlace not in contents:
                        contents[indexPlace] = {}
                    
                    contents[indexPlace][indexSubPlace] = file

        contents[self._groupPlace.indexPlace] = {}
        for indexSubPlace, fileData in enumerate(self._dataPlace):
            fileData.save()
            contents[self._groupPlace.indexPlace][indexSubPlace] = File(name=PATH_PACK_PLACE % (self._groupPlace.indexPlace, indexSubPlace), data=fileData.data)

        pack.files = []
        indicesPlaces = list(contents.keys())
        indicesPlaces.sort()
        for indexPlace in indicesPlaces:
            indicesSubPlaces = list(contents[indexPlace].keys())
            indicesSubPlaces.sort()
            for indexSubPlace in indicesSubPlaces:
                pack.files.append(contents[indexPlace][indexSubPlace])

        pack.save()
        pack.compress()
        self._filesystem.writeableFs.replaceFile(pathPack, pack.data)
        print("Synced and sorted room pack!")

    def _getActiveState(self) -> Optional[PlaceDataNds]:
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if not(self.treeStateProgression):
            return self.__lastValidSuggestion

        selection = self.treeStateProgression.GetSelection()
        if selection in self._treeToPlaceData:
            self.__lastValidSuggestion = selection
            return self._treeToPlaceData[selection]
        return self.__lastValidSuggestion

    def _generateList(self):
        self.Freeze()

        placeFlag = PlaceFlag()
        if (data := self._filesystem.getPackedData(PATH_PROGRESSION_DB, PATH_DB_PLACEFLAG)):
            placeFlag.load(data)

        self.treeStateProgression.DeleteAllItems()
        rootTreeProgression = self.treeStateProgression.AddRoot("You shouldn't be able to see this!")
        
        selection = None
        for trueIndex, index in enumerate(self._groupPlace.indicesStates):
            if index == 0:
                selection = self.treeStateProgression.AppendItem(rootTreeProgression, "Default State", data=self._dataPlace[trueIndex])
                self._treeToPlaceData[selection] = self._dataPlace[trueIndex]
            else:
                
                entry = placeFlag.entries[self._groupPlace.indexPlace]
                chapterEntry = entry.getEntry(index)
                chapterMin = chapterEntry.chapterStart
                chapterMax = chapterEntry.chapterEnd

                subroomRoot = self.treeStateProgression.AppendItem(rootTreeProgression, "State " + str(index) + (": Chapter %i to %i" % (chapterMin, chapterMax)),
                                                                   data=self._dataPlace[trueIndex])
                self._treeToPlaceData[subroomRoot] = self._dataPlace[trueIndex]

                if chapterMin == 0 or chapterMax == 0:
                    self.treeStateProgression.AppendItem(subroomRoot, "Terminate subroom discovery on encounter")
                    continue
                
                counterEntry = entry.getCounterEntry(index)
                if counterEntry.indexEventCounter != 0:
                    if counterEntry.decodeMode == 0:
                        # Value same as val at index
                        self.treeStateProgression.AppendItem(subroomRoot, "Variable " + str(counterEntry.indexEventCounter) + " equals " + str(counterEntry.unk1))
                    elif counterEntry.decodeMode == 1:
                        # Value different than val at index
                        self.treeStateProgression.AppendItem(subroomRoot, "Variable " + str(counterEntry.indexEventCounter) + " doesn't equal " + str(counterEntry.unk1))
                    elif counterEntry.decodeMode == 2:
                        # Value less than val at index
                        self.treeStateProgression.AppendItem(subroomRoot, "Variable " + str(counterEntry.indexEventCounter) + " greater than or equal to " + str(counterEntry.unk1))
                    else:
                        self.treeStateProgression.AppendItem(subroomRoot, "Misconfigured counter condition")

        if selection != None:
            self.treeStateProgression.SelectItem(selection)
        self.Thaw()

    def _generateTree(self):

        self.Freeze()

        def expandIfEnabled(item : TreeItemId, expanded : bool):
            if expanded:
                self.treeParam.Expand(item)
            else:
                self.treeParam.Collapse(item)

        treeRootPropertiesExpanded      = False
        treeRootTObjExpanded            = False
        treeRootEventSpawnerExpanded    = False
        treeRootHintCoinExpanded        = False
        treeRootBgAniExpanded           = False
        treeRootExitExpanded            = False

        self._treeItemsTObj = []
        self._treeItemsEventSpawner = []
        self._treeItemsHintCoin = []
        self._treeItemsBgAni = []
        self._treeItemsExits = []

        if self._treeRoot != None:
            treeRootPropertiesExpanded = self.treeParam.IsExpanded(self._treeRootProperties)
            treeRootTObjExpanded = self.treeParam.IsExpanded(self._treeRootTextObjectSpawner)
            treeRootEventSpawnerExpanded = self.treeParam.IsExpanded(self._treeRootEventSpawner)
            treeRootHintCoinExpanded = self.treeParam.IsExpanded(self._treeRootHintCoin)
            treeRootBgAniExpanded = self.treeParam.IsExpanded(self._treeRootBackgroundAnim)
            treeRootExitExpanded = self.treeParam.IsExpanded(self._treeRootExit)

        self.treeParam.DeleteAllItems()
        dataPlace = self._getActiveState()
        if dataPlace == None:
            self.Thaw()
            return

        def generateDetailBranch():
            self._treeRootProperties = self.treeParam.AppendItem(self._treeRoot, "Properties")
            self._treeItemName = self.treeParam.AppendItem(self._treeRootProperties, "Name: %s" % self._filesystem.getPackedString(substituteLanguageString(self._state, PATH_PACK_PLACE_NAME), PATH_TEXT_PLACE_NAME % dataPlace.idNamePlace), data=dataPlace.idNamePlace)
            self._treeItemMapPos = self.treeParam.AppendItem(self._treeRootProperties, "Edit map pinpoint position...", data=dataPlace.posMap)
            self._treeItemSound = self.treeParam.AppendItem(self._treeRootProperties, "Change background music (ID %i)..." % dataPlace.idSound, data=dataPlace.idSound)
            expandIfEnabled(self._treeRootProperties, treeRootPropertiesExpanded)

        def generateTextBranch():
            self._treeRootTextObjectSpawner = self.treeParam.AppendItem(self._treeRoot, "Text Popups")
            for idTObj in range(dataPlace.getCountObjText()):
                newTObj = TreeGroupTObj.fromPlaceData(dataPlace.getObjText(idTObj))
                newTObj.createTreeItems(self._state, self.treeParam, self._treeRootTextObjectSpawner, idTObj)
                self._treeItemsTObj.append(newTObj)
            expandIfEnabled(self._treeRootTextObjectSpawner, treeRootTObjExpanded)
        
        def generateEventBranch():
            self._treeRootEventSpawner = self.treeParam.AppendItem(self._treeRoot, "Event Spawners")
            for idEventSpawner in range(dataPlace.getCountObjEvents()):
                newEventSpawner = TreeGroupEventSpawner.fromPlaceData(dataPlace.getObjEvent(idEventSpawner))
                newEventSpawner.createTreeItems(self._state, self.treeParam, self._treeRootEventSpawner, idEventSpawner)
                self._treeItemsEventSpawner.append(newEventSpawner)
            expandIfEnabled(self._treeRootEventSpawner, treeRootEventSpawnerExpanded)

        def generateHintBranch():
            self._treeRootHintCoin = self.treeParam.AppendItem(self._treeRoot, "Hint Coins")
            for idHintCoin in range(dataPlace.getCountHintCoin()):
                newHintCoin = TreeGroupHintCoin.fromPlaceData(dataPlace.getObjHintCoin(idHintCoin))
                newHintCoin.createTreeItems(self._state, self.treeParam, self._treeRootHintCoin, idHintCoin)
                self._treeItemsHintCoin.append(newHintCoin)
            expandIfEnabled(self._treeRootHintCoin, treeRootHintCoinExpanded)
        
        def generateBgAniBranch():
            self._treeRootBackgroundAnim = self.treeParam.AppendItem(self._treeRoot, "Background Animations")
            for idBgAni in range(dataPlace.getCountObjBgEvent()):
                newBgAni = TreeGroupBackgroundAnimation.fromPlaceData(dataPlace.getObjBgEvent(idBgAni))
                newBgAni.createTreeItems(self._state, self.treeParam, self._treeRootBackgroundAnim, idBgAni)
                self._treeItemsBgAni.append(newBgAni)
            expandIfEnabled(self._treeRootBackgroundAnim, treeRootBgAniExpanded)

        def generateExitBranch():
            self._treeRootExit = self.treeParam.AppendItem(self._treeRoot, "Exits")
            for idExit in range(dataPlace.getCountExits()):
                newExit = TreeGroupExit.fromPlaceData(dataPlace.getExit(idExit))
                newExit.createTreeItems(self._state, self.treeParam, self._treeRootExit, idExit)
                self._treeItemsExits.append(newExit)
            expandIfEnabled(self._treeRootExit, treeRootExitExpanded)

        self._treeRoot = self.treeParam.AddRoot("Root")
        generateDetailBranch()
        generateEventBranch()
        generateTextBranch()
        generateHintBranch()
        generateBgAniBranch()
        generateExitBranch()

        self.Thaw()
    
    def _generateBackgrounds(self):

        def blitAnimsToBackground(placeData : PlaceData, backgroundSurf : Surface):
            for indexBgAni in range(placeData.getCountObjBgEvent()):
                bgAni = placeData.getObjBgEvent(indexBgAni)
                if (anim := getBottomScreenAnimFromPath(self._state, PATH_ANIM_BGANI % bgAni.name)) != None:
                    anim.setPos(bgAni.pos)
                    anim.draw(backgroundSurf)
            
            for indexObjEvent in range(placeData.getCountObjEvents()):
                objEvent = placeData.getObjEvent(indexObjEvent)
                if objEvent.idImage & 0xff != 0:
                    if (eventAsset := getBottomScreenAnimFromPath(self._state, PATH_EXT_EVENT % (objEvent.idImage & 0xff))) != None:
                        eventAsset.setPos((objEvent.bounding.x, objEvent.bounding.y))
                        eventAsset.draw(backgroundSurf)
                
            # TODO - Sort by draw and collision order (TObj and Hint on top?)
            for spawner in self._treeItemsBgAni + self._treeItemsEventSpawner + self._treeItemsExits + self._treeItemsTObj + self._treeItemsHintCoin:
                spawner.renderSelectionLine(backgroundSurf)
        
        def blitTopInterfaceToBackground(placeData : PlaceData, backgroundSurf : Surface):
            pass

        dataPlace = self._getActiveState()
        if dataPlace == None:
            return

        self.Freeze()
        
        pathBgMain = PATH_PLACE_BG % dataPlace.bgMainId
        pathBgSub = PATH_PLACE_MAP % dataPlace.bgMapId

        background = getImageFromPath(self._state, pathBgMain)
        if background == None:
            background = self.__invalidSurface

        # TODO - Cache result, this is slow
        blitAnimsToBackground(dataPlace, background)
        
        if self.checkboxShowHitbox.IsChecked():
            pass
        if self.checkboxShowInterface.IsChecked():
            pass

        self.bitmapRoomBottom.SetBitmap(Bitmap.FromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))
        
        background = getImageFromPath(self._state, pathBgSub)
        if background == None:
            background = self.__invalidSurface
        
        self.bitmapRoomTop.SetBitmap(Bitmap.FromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

        self.Thaw()