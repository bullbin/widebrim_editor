from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from editor.asset_management.plz_txt.jiten import createNextNewRoomTitleId, getFreeRoomJitenNameTagId, getUsedRoomNameTags
from editor.asset_management.room import PlaceGroup, getPackPathForPlaceIndex
from editor.d_operandMultichoice import DialogMultipleChoice
from editor.e_room.modifiers import modifySpritePosition
from editor.e_room.utils import blitBoundingAlphaFill, blitBoundingLine, getBoundingFromSurface
from editor.e_script.get_input_popup import VerifiedDialog
from editor.treeUtils import isItemOnPathToItem
from widebrim.madhatter.hat_io.asset import File
from .treeGroups import TreeGroupBackgroundAnimation, TreeGroupEventSpawner, TreeGroupExit, TreeGroupHintCoin, TreeGroupTObj, TreeObjectPlaceData
from editor.nopush_editor import editorRoom
from widebrim.engine.const import PATH_DB_PLACEFLAG, PATH_EXT_EVENT, PATH_PACK_PLACE_NAME, PATH_PLACE_BG, PATH_PLACE_MAP, PATH_PROGRESSION_DB, PATH_TEXT_PLACE_NAME, RESOLUTION_NINTENDO_DS
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.engine_ext.utils import getBottomScreenAnimFromPath, getImageFromPath, substituteLanguageString
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from wx import TreeItemId, Bitmap, ID_OK, TextEntryDialog
from widebrim.gamemodes.room.const import PATH_ANIM_BGANI, PATH_ANIM_MAPICON, PATH_PACK_PLACE
from pygame import Surface
from pygame.image import tostring

from widebrim.madhatter.hat_io.asset_dat.place import EventEntry, HintCoin, PlaceData, PlaceDataNds
from widebrim.madhatter.hat_io.asset_placeflag import PlaceFlag

from re import search

# TODO - Fix need to double click
# TODO - Cache anims and bg (slowdown blitting)
# TODO - AutoEvent

class FramePlaceEditor(editorRoom):

    INVALID_FRAME_COLOR = (255,0,0)
    ALPHA_FILL_DESELECTED = 48
    ALPHA_FILL_SELECTED = 127

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
        self._lastSelectedGroup = None
    
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
            self.btnRoomCreateNew.Disable()
            self.btnRoomDelete.Disable()
            self.checkRoomApplyToAll.Disable()
            self._generateTree()
            self._generateBackgrounds()
        return super().treeStateProgressionOnTreeSelChanged(event)

    def treeParamOnTreeSelChanged(self, event):
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if not(self.treeParam):
            return super().treeParamOnTreeSelChanged(event)
        
        item = self.treeParam.GetFocusedItem()
        print(self.treeParam.GetItemText(item), "->", self.treeParam.GetItemData(item))

        self.btnRoomCreateNew.Disable()
        self.btnRoomDelete.Disable()
        self.checkRoomApplyToAll.Disable()
        for itemDestination in [self._treeRootHintCoin, self._treeRootBackgroundAnim, self._treeRootEventSpawner,
                                self._treeRootTextObjectSpawner, self._treeRootExit]:
            if isItemOnPathToItem(self.treeParam, item, itemDestination):
                # TODO - Can just reverse (don't allow nodes on branch to properties)
                self.btnRoomCreateNew.Enable()
                self.btnRoomDelete.Enable()

                if itemDestination != self._treeRootHintCoin:
                    self.checkRoomApplyToAll.Enable()
                break
        
        noItemSelected = True
        for itemDestination in self._treeItemsHintCoin + self._treeItemsBgAni + self._treeItemsEventSpawner + self._treeItemsTObj + self._treeItemsExits:
            itemDestination : TreeObjectPlaceData
            if itemDestination.isItemSelected(item):
                noItemSelected = False
                if self._lastSelectedGroup != itemDestination:
                    self._lastSelectedGroup = itemDestination
                    self._generateBackgrounds()
                break
        
        if noItemSelected and self._lastSelectedGroup != None:
            self._lastSelectedGroup = None
            self._generateBackgrounds()

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
            if type(treeGroup) == TreeGroupExit:
                # TODO - match if the tree group relates to an immediate exit and don't show movemode
                bg0, bg1 = self._getBackgroundBottomScreenLayers(treeGroup, hideSelected=True, topmostSelected=False, showHitbox=True, simulateMoveMode=True)
            else:
                bg0, bg1 = self._getBackgroundBottomScreenLayers(treeGroup, hideSelected=True, topmostSelected=False, showHitbox=True, simulateMoveMode=False)
            
            # TODO - Layer backgrounds!
            return (bg0, bg1)

        item = self.treeParam.GetSelection()
        if item == self._treeItemName:
            # TODO - Select name
            newId = modifyName()
            if newId != None:
                if self.checkRoomApplyToAll.IsChecked():
                    for placeData in self._dataPlace:
                        if placeData != self._getActiveState():
                            placeData.idNamePlace = newId

                self.treeParam.SetItemData(item, newId)
                self.treeParam.SetItemText(item, "Name: %s" % self._filesystem.getPackedString(substituteLanguageString(self._state, PATH_PACK_PLACE_NAME), PATH_TEXT_PLACE_NAME % newId))
                self._getActiveState().idNamePlace = newId
            return super().treeParamOnTreeItemActivated(event)
        elif item == self._treeItemMapPos:
            oldPos = self._getActiveState().posMap
            self._getActiveState().posMap = modifySpritePosition(self, self._state, Surface((256,192)), PATH_ANIM_MAPICON, self._getActiveState().posMap, color=(255,255,255))
            self.treeParam.SetItemData(item, self._getActiveState().posMap)
            if oldPos != self._getActiveState().posMap:
                self._generateBackgrounds()
            return super().treeParamOnTreeItemActivated(event)

        for obj in self._treeItemsTObj + self._treeItemsEventSpawner + self._treeItemsHintCoin + self._treeItemsBgAni + self._treeItemsExits:
            obj : TreeObjectPlaceData
            if obj.isItemSelected(item) and obj.isModifiable(item):
                if not(self.checkRoomApplyToAll.IsEnabled()) or (self.checkRoomApplyToAll.IsEnabled() and self.checkRoomApplyToAll.IsChecked()):
                    otherPlaceData = [self._getActiveState()]
                    for placeData in self._dataPlace:
                        if placeData != self._getActiveState():
                            otherPlaceData.append(placeData)
                    background, foreground = getBackgroundDevoidOfControl(obj)
                    result = obj.modifyAllItems(self._state, self.treeParam, item, self, background, otherPlaceData, foregroundImage=foreground)
                    print("Modified all: %s" % self.treeParam.GetItemText(item))
                else:
                    background, foreground = getBackgroundDevoidOfControl(obj)
                    result = obj.modifyItem(self._state, self.treeParam, item, self, background, foregroundImage=foreground)
                    print("Modified: %s" % self.treeParam.GetItemText(item))

                # TODO - Save changes?
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
    
    def _getBackgroundBottomScreenLayers(self, selectedElement : Optional[Type[TreeObjectPlaceData]] = None, hideSelected : bool = False, topmostSelected : bool = False, showHitbox : bool = True, simulateMoveMode : bool = False) -> Tuple[Surface, Surface]:
        # TODO - Should we still show selected elements that are hidden from movemode? Currently we do...
        # TODO - How can we make movemode clearer on selected elements?
        # TODO - Show exit directions in movemode

        surfAlpha = Surface(RESOLUTION_NINTENDO_DS).convert_alpha()
        surfTopmost = Surface(RESOLUTION_NINTENDO_DS).convert_alpha()
        surfBottom = Surface(RESOLUTION_NINTENDO_DS)
        surfAlpha.fill((255,255,255,0))
        surfTopmost.fill((255,255,255,0))

        dataPlace = self._getActiveState()
        if dataPlace == None:
            return (surfBottom, surfAlpha)
        
        surfBottom.blit(getImageFromPath(self._state, PATH_PLACE_BG % dataPlace.bgMainId), (0,0))
        drawLayer = surfBottom

        for item, indexBgAni in zip(self._treeItemsBgAni, range(dataPlace.getCountObjBgEvent())):
            bgAni = dataPlace.getObjBgEvent(indexBgAni)
            anim = getBottomScreenAnimFromPath(self._state, PATH_ANIM_BGANI % bgAni.name)
            anim.setPos(bgAni.pos)

            if item != selectedElement:
                anim.draw(drawLayer)
                if showHitbox and not(simulateMoveMode):
                    if self.checkAlphaFillHitbox.IsChecked():
                        blitBoundingAlphaFill(drawLayer, getBoundingFromSurface(anim.getActiveFrame(), bgAni.pos), TreeGroupBackgroundAnimation.COLOR_LINE, alpha=FramePlaceEditor.ALPHA_FILL_DESELECTED)
                    blitBoundingLine(drawLayer, getBoundingFromSurface(anim.getActiveFrame(), bgAni.pos), TreeGroupBackgroundAnimation.COLOR_LINE)
            else:
                if not(hideSelected):
                    if topmostSelected:
                        target = surfTopmost
                    else:
                        target = drawLayer
                    blitBoundingAlphaFill(target, getBoundingFromSurface(anim.getActiveFrame(), bgAni.pos), TreeGroupBackgroundAnimation.COLOR_LINE, alpha=FramePlaceEditor.ALPHA_FILL_SELECTED)
                    anim.draw(target)
                    blitBoundingLine(target, getBoundingFromSurface(anim.getActiveFrame(), bgAni.pos), TreeGroupBackgroundAnimation.COLOR_LINE)
                drawLayer = surfAlpha

        for item, indexExit in zip(self._treeItemsExits, range(dataPlace.getCountExits())):
            placeExit = dataPlace.getExit(indexExit)
            if item != selectedElement:
                if showHitbox and ((not(simulateMoveMode) and placeExit.canBePressedImmediately()) or simulateMoveMode):
                    if self.checkAlphaFillHitbox.IsChecked():
                        item.renderSelectionAlphaFill(drawLayer, alpha=FramePlaceEditor.ALPHA_FILL_DESELECTED)
                    item.renderSelectionLine(drawLayer)
            else:
                if not(hideSelected):
                    if topmostSelected:
                        target = surfTopmost
                    else:
                        target = drawLayer

                    item.renderSelectionAlphaFill(target, alpha=FramePlaceEditor.ALPHA_FILL_SELECTED)
                    item.renderSelectionLine(target)
                drawLayer = surfAlpha
        
        for item in self._treeItemsTObj + self._treeItemsHintCoin:
            item : TreeObjectPlaceData
            if item != selectedElement:
                if (showHitbox and not(simulateMoveMode)):
                    if self.checkAlphaFillHitbox.IsChecked():
                        item.renderSelectionAlphaFill(drawLayer, alpha=FramePlaceEditor.ALPHA_FILL_DESELECTED)
                    item.renderSelectionLine(drawLayer)
            else:
                if not(hideSelected):
                    if topmostSelected:
                        target = surfTopmost
                    else:
                        target = drawLayer
                    item.renderSelectionAlphaFill(target, alpha=FramePlaceEditor.ALPHA_FILL_SELECTED)
                    item.renderSelectionLine(target)
                drawLayer = surfAlpha
        
        for item, indexObjEvent in zip(self._treeItemsEventSpawner, range(dataPlace.getCountObjEvents())):
            # TODO - Handle masking gracefully (ID 0) (plus bg ani)
            objEvent = dataPlace.getObjEvent(indexObjEvent)
            anim = getBottomScreenAnimFromPath(self._state, PATH_EXT_EVENT % (objEvent.idImage & 0xff))
            anim.setPos((objEvent.bounding.x, objEvent.bounding.y))

            if item != selectedElement:
                anim.draw(drawLayer)
                if showHitbox and not(simulateMoveMode):
                    if self.checkAlphaFillHitbox.IsChecked():
                        item.renderSelectionAlphaFill(drawLayer, alpha=FramePlaceEditor.ALPHA_FILL_DESELECTED)
                    item.renderSelectionLine(drawLayer)
            else:
                if not(hideSelected):
                    if topmostSelected:
                        target = surfTopmost
                    else:
                        target = drawLayer
                    item.renderSelectionAlphaFill(target, alpha=FramePlaceEditor.ALPHA_FILL_SELECTED)
                    anim.draw(target)
                    item.renderSelectionLine(target)
                drawLayer = surfAlpha
        
        surfAlpha.blit(surfTopmost, (0,0))
        return (surfBottom, surfAlpha)

        # bg ani -> immediate exit -> tobj -> (touch) hints -> events -> exits

    def _getBackgroundTopScreenLayers(self, selectedElement : Optional[Any] = None, hideSelected : bool = False) -> Tuple[Surface, Surface]:
        pass

    def checkboxShowHitboxOnCheckBox(self, event):
        self._generateBackgrounds()
        return super().checkboxShowHitboxOnCheckBox(event)
    
    def checkboxShowInterfaceOnCheckBox(self, event):
        self._generateBackgrounds()
        return super().checkboxShowInterfaceOnCheckBox(event)

    def checkAlphaFillHitboxOnCheckBox(self, event):
        self._generateBackgrounds()
        return super().checkAlphaFillHitboxOnCheckBox(event)

    def _generateBackgrounds(self):
        
        def blitTopInterfaceToBackground(placeData : PlaceData, backgroundSurf : Surface):
            pass

        dataPlace = self._getActiveState()
        if dataPlace == None:
            return

        self.Freeze()
        
        pathBgSub = PATH_PLACE_MAP % dataPlace.bgMapId

        bg0, bg1 = self._getBackgroundBottomScreenLayers(self._lastSelectedGroup, hideSelected=False, topmostSelected=True, showHitbox = self.checkboxShowHitbox.IsChecked(),
                                                         simulateMoveMode = self.checkboxShowInterface.IsChecked())
        bg0.blit(bg1, (0,0))
        background = bg0

        self.bitmapRoomBottom.SetBitmap(Bitmap.FromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))
        
        background = getImageFromPath(self._state, pathBgSub)
        if background == None:
            background = self.__invalidSurface
        
        self.bitmapRoomTop.SetBitmap(Bitmap.FromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

        self.Thaw()
    
    def btnRoomCreateNewOnButtonClick(self, event):
        item = self.treeParam.GetSelection()
        if isItemOnPathToItem(self.treeParam, item, self._treeRootEventSpawner):
            if self.checkRoomApplyToAll.IsChecked():
                maxEventCount = 0
                for placeData in self._dataPlace:
                    maxEventCount = max(placeData.getCountObjEvents(), maxEventCount)

                # TODO - Make constant in madhatter
                if maxEventCount >= 16:
                    # TODO - Warning message
                    event.Skip()
                    return
                
                for placeData in self._dataPlace:
                    placeData.addObjEvent(EventEntry())
            else:
                if self._getActiveState().getCountObjEvents() < 16:
                    self._getActiveState().addObjEvent(EventEntry())
                else:
                    # TODO - Warning message
                    return

            currentData = self._getActiveState()
            newEntry = currentData.getObjEvent(currentData.getCountObjEvents() - 1)
            self._treeItemsEventSpawner.append(TreeGroupEventSpawner.fromPlaceData(newEntry))
            self._treeItemsEventSpawner[-1].createTreeItems(self._state, self.treeParam, self._treeRootEventSpawner, index=(currentData.getCountObjEvents() - 1))
            self._generateBackgrounds()

        elif isItemOnPathToItem(self.treeParam, item, self._treeRootTextObjectSpawner):
            pass
        elif isItemOnPathToItem(self.treeParam, item, self._treeRootHintCoin):
            # Hints are different - because the game stores hints by their index across all room data, we cannot allow events to have different hint counts
            # Although it is possible to remove the topmost hints without breaking things, in reality there's no real reason to do this...
            maxHintCount = 0
            for placeData in self._dataPlace:
                maxHintCount = max(placeData.getCountHintCoin(), maxHintCount)

            # TODO - Make constant in madhatter
            # If there are 4 hints already at any point in the placedata, we cannot allow any more to be created
            if maxHintCount >= 4:
                # TODO - Warning message
                event.Skip()
                return
            
            for placeData in self._dataPlace:
                placeData.addObjHintCoin(HintCoin())
            
            currentData = self._getActiveState()
            newEntry = currentData.getObjHintCoin(currentData.getCountHintCoin() - 1)
            self._treeItemsHintCoin.append(TreeGroupHintCoin.fromPlaceData(newEntry))
            self._treeItemsHintCoin[-1].createTreeItems(self._state, self.treeParam, self._treeRootHintCoin, index=(currentData.getCountHintCoin() - 1))
            self._generateBackgrounds()

        elif isItemOnPathToItem(self.treeParam, item, self._treeRootBackgroundAnim):
            pass
        elif isItemOnPathToItem(self.treeParam, item, self._treeRootExit):
            pass


        return super().btnRoomCreateNewOnButtonClick(event)
    
    def btnRoomDeleteOnButtonClick(self, event):
        return super().btnRoomDeleteOnButtonClick(event)