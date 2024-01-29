from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from editor.asset_management.plz_txt.jiten import createNextNewRoomTitleId, getFreeRoomJitenNameTagId, getUsedRoomNameTags
from editor.asset_management.room import PlaceGroup, getPackPathForPlaceIndex
from editor.d_operandMultichoice import DialogMultipleChoice
from editor.d_pickerBgx import DialogPickerBgx
from editor.e_room.modifiers import modifySpritePosition
from editor.e_room.utils import blitBoundingAlphaFill, blitBoundingLine, getBoundingFromSurface
from editor.e_script.get_input_popup import VerifiedDialog
from editor.treeUtils import isItemOnPathToItem
from widebrim.engine.anim.font.static import generateImageFromString
from widebrim.madhatter.common import log, logSevere
from widebrim.madhatter.hat_io.asset import File
from .treeGroups import TreeGroupBackgroundAnimation, TreeGroupEventSpawner, TreeGroupExit, TreeGroupHintCoin, TreeGroupTObj, TreeObjectPlaceData
from editor.nopush_editor import editorRoom
from widebrim.engine.const import PATH_ANI, PATH_EXT_EVENT, PATH_EXT_EXIT, PATH_PACK_PLACE_NAME, PATH_PLACE_BG, PATH_PLACE_MAP, PATH_TEXT_PLACE_NAME, RESOLUTION_NINTENDO_DS
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.engine_ext.utils import getBottomScreenAnimFromPath, getImageFromPath, getTopScreenAnimFromPath, getTxt2String, substituteLanguageString
from filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from wx import TreeItemId, Bitmap, ID_OK, TextEntryDialog
from widebrim.gamemodes.room.const import PATH_ANIM_BGANI, PATH_ANIM_MAPICON, PATH_PACK_PLACE
from pygame import Surface, BLEND_RGB_SUB
from pygame.image import tostring
from widebrim.madhatter.hat_io.asset_dat.place import BgAni, EventEntry, Exit, HintCoin, PlaceData, PlaceDataNds, TObjEntry

from re import search, match

# TODO - Fix need to double click
# TODO - Cache anims and bg (slowdown blitting)
# TODO - AutoEvent
# TODO - Verify functionality to check that all hitboxes can be reached (e.g., hint coins)
# TODO - Rewrite draw code to support multi-selection (select all in group) without horrible overdraw
# TODO - Set up background redraw requests on per-screen basis (speedup)
# TODO - Enable change all for properties too

class FramePlaceEditor(editorRoom):

    INVALID_FRAME_COLOR = (255,0,0)

    ALPHA_FILL_DESELECTED = 48
    ALPHA_FILL_SELECTED = 127

    THICKNESS_DESELECTED = 1
    THICKNESS_SELECTED = 2

    def __init__(self, parent, filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, groupPlace : PlaceGroup):
        super().__init__(parent)
        self._filesystem = filesystem
        self._state = state
        self._groupPlace = groupPlace

        self.__treeRoot                     : Optional[TreeItemId] = None

        self.__treeRootProperties           : Optional[TreeItemId] = None
        self.__treeRootHintCoin             : Optional[TreeItemId] = None
        self.__treeRootBackgroundAnim       : Optional[TreeItemId] = None
        self.__treeRootEventSpawner         : Optional[TreeItemId] = None
        self.__treeRootTextObjectSpawner    : Optional[TreeItemId] = None
        self.__treeRootExit                 : Optional[TreeItemId] = None

        self.__treeItemName                 : Optional[TreeItemId] = None
        self.__treeItemMapPos               : Optional[TreeItemId] = None
        self.__treeItemSound                : Optional[TreeItemId] = None

        self.__treeItemsTObj                : List[TreeGroupTObj]                   = []
        self.__treeItemsEventSpawner        : List[TreeGroupEventSpawner]           = []
        self.__treeItemsHintCoin            : List[TreeGroupHintCoin]               = []
        self.__treeItemsBgAni               : List[TreeGroupBackgroundAnimation]    = []
        self.__treeItemsExits               : List[TreeGroupExit]                   = []

        self.__invalidSurface = Surface(RESOLUTION_NINTENDO_DS)
        self.__invalidSurface.fill(FramePlaceEditor.INVALID_FRAME_COLOR)
        self.__imagesExit           : Dict[int, Surface]  = {}

        self._lastValidSuggestion   : Optional[PlaceData] = None
        self._lastSelectedGroup     : Optional[Type[TreeObjectPlaceData]] = None
        self._loaded                : bool = False

    def _getListPlaceData(self) -> Tuple[List[TreeItemId], List[PlaceData]]:
        return ([], [])

    def _getActiveState(self) -> Optional[PlaceDataNds]:
        return self._lastValidSuggestion

    def treeParamOnTreeSelChanged(self, event):
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if not(self.treeParam):
            return super().treeParamOnTreeSelChanged(event)
        
        item = self.treeParam.GetFocusedItem()

        self.btnRoomCreateNew.Disable()
        self.btnRoomDelete.Disable()
        self.checkRoomApplyToAll.Disable()
        for itemDestination in [self.__treeRootHintCoin, self.__treeRootBackgroundAnim, self.__treeRootEventSpawner,
                                self.__treeRootTextObjectSpawner, self.__treeRootExit]:
            if isItemOnPathToItem(self.treeParam, item, itemDestination):
                # TODO - Can just reverse (don't allow nodes on branch to properties)
                self.btnRoomCreateNew.Enable()
                self.btnRoomDelete.Enable()

                if itemDestination != self.__treeRootHintCoin:
                    self.checkRoomApplyToAll.Enable()
                break
        
        noItemSelected = True
        for itemDestination in self.__treeItemsHintCoin + self.__treeItemsBgAni + self.__treeItemsEventSpawner + self.__treeItemsTObj + self.__treeItemsExits:
            itemDestination : TreeObjectPlaceData
            if itemDestination.isItemSelected(item):
                noItemSelected = False
                if self._lastSelectedGroup != itemDestination:
                    self._lastSelectedGroup = itemDestination
                    self.__generateBackgrounds()
                break
        
        if noItemSelected and self._lastSelectedGroup != None:
            self._lastSelectedGroup = None
            self.__generateBackgrounds()

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
                bg0, bg1 = self.__getBackgroundBottomScreenLayers(treeGroup, hideSelected=True, topmostSelected=False, showHitbox=True, simulateMoveMode=True)
            else:
                bg0, bg1 = self.__getBackgroundBottomScreenLayers(treeGroup, hideSelected=True, topmostSelected=False, showHitbox=True, simulateMoveMode=False)
            
            # TODO - Layer backgrounds!
            return (bg0, bg1)

        item = self.treeParam.GetSelection()
        if item == self.__treeItemName:
            # TODO - Select name
            newId = modifyName()
            if newId != None:
                if self.checkRoomApplyToAll.IsChecked():
                    for placeData in self._getListPlaceData()[1]:
                        if placeData != self._getActiveState():
                            placeData.idNamePlace = newId

                self.treeParam.SetItemData(item, newId)
                self.treeParam.SetItemText(item, "Name: %s" % self._filesystem.getPackedString(substituteLanguageString(self._state, PATH_PACK_PLACE_NAME), PATH_TEXT_PLACE_NAME % newId))
                if self._getActiveState().idNamePlace != newId:
                    self._getActiveState().idNamePlace = newId
                    self.__generateBackgrounds()
            return super().treeParamOnTreeItemActivated(event)
        elif item == self.__treeItemMapPos:
            oldPos = self._getActiveState().posMap
            self._getActiveState().posMap = modifySpritePosition(self, self._state, self.__getBackgroundTopScreen(False), PATH_ANIM_MAPICON, self._getActiveState().posMap, color=(255,255,255))
            self.treeParam.SetItemData(item, self._getActiveState().posMap)
            if oldPos != self._getActiveState().posMap:
                self.__generateBackgrounds()
            return super().treeParamOnTreeItemActivated(event)

        for obj in self.__treeItemsTObj + self.__treeItemsEventSpawner + self.__treeItemsHintCoin + self.__treeItemsBgAni + self.__treeItemsExits:
            obj : TreeObjectPlaceData
            if obj.isItemSelected(item) and obj.isModifiable(item):
                if not(self.checkRoomApplyToAll.IsEnabled()) or (self.checkRoomApplyToAll.IsEnabled() and self.checkRoomApplyToAll.IsChecked()):
                    otherPlaceData = [self._getActiveState()]
                    for placeData in self._getListPlaceData()[1]:
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
                    self.__generateBackgrounds()
                return super().treeParamOnTreeItemActivated(event)
        
        print("Cannot edit!")
        return super().treeParamOnTreeItemActivated(event)

    def __generateTree(self):

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

        self.__treeItemsTObj = []
        self.__treeItemsEventSpawner = []
        self.__treeItemsHintCoin = []
        self.__treeItemsBgAni = []
        self.__treeItemsExits = []

        if self.__treeRoot != None:
            treeRootPropertiesExpanded = self.treeParam.IsExpanded(self.__treeRootProperties)
            treeRootTObjExpanded = self.treeParam.IsExpanded(self.__treeRootTextObjectSpawner)
            treeRootEventSpawnerExpanded = self.treeParam.IsExpanded(self.__treeRootEventSpawner)
            treeRootHintCoinExpanded = self.treeParam.IsExpanded(self.__treeRootHintCoin)
            treeRootBgAniExpanded = self.treeParam.IsExpanded(self.__treeRootBackgroundAnim)
            treeRootExitExpanded = self.treeParam.IsExpanded(self.__treeRootExit)

        self.treeParam.DeleteAllItems()
        dataPlace = self._getActiveState()
        if dataPlace == None:
            self.Thaw()
            return

        def generateDetailBranch():
            self.__treeRootProperties = self.treeParam.AppendItem(self.__treeRoot, "Properties")
            self.__treeItemName = self.treeParam.AppendItem(self.__treeRootProperties, "Name: %s" % self._filesystem.getPackedString(substituteLanguageString(self._state, PATH_PACK_PLACE_NAME), PATH_TEXT_PLACE_NAME % dataPlace.idNamePlace), data=dataPlace.idNamePlace)
            self.__treeItemMapPos = self.treeParam.AppendItem(self.__treeRootProperties, "Edit map pinpoint position...", data=dataPlace.posMap)
            self.__treeItemSound = self.treeParam.AppendItem(self.__treeRootProperties, "Change background music (ID %i)..." % dataPlace.idSound, data=dataPlace.idSound)
            expandIfEnabled(self.__treeRootProperties, treeRootPropertiesExpanded)

        def generateTextBranch():
            self.__treeRootTextObjectSpawner = self.treeParam.AppendItem(self.__treeRoot, "Text Popups")
            for idTObj in range(dataPlace.getCountObjText()):
                newTObj = TreeGroupTObj.fromPlaceData(dataPlace.getObjText(idTObj))
                newTObj.createTreeItems(self._state, self.treeParam, self.__treeRootTextObjectSpawner, idTObj)
                self.__treeItemsTObj.append(newTObj)
            expandIfEnabled(self.__treeRootTextObjectSpawner, treeRootTObjExpanded)
        
        def generateEventBranch():
            self.__treeRootEventSpawner = self.treeParam.AppendItem(self.__treeRoot, "Event Spawners")
            for idEventSpawner in range(dataPlace.getCountObjEvents()):
                newEventSpawner = TreeGroupEventSpawner.fromPlaceData(dataPlace.getObjEvent(idEventSpawner))
                newEventSpawner.createTreeItems(self._state, self.treeParam, self.__treeRootEventSpawner, idEventSpawner)
                self.__treeItemsEventSpawner.append(newEventSpawner)
            expandIfEnabled(self.__treeRootEventSpawner, treeRootEventSpawnerExpanded)

        def generateHintBranch():
            self.__treeRootHintCoin = self.treeParam.AppendItem(self.__treeRoot, "Hint Coins")
            for idHintCoin in range(dataPlace.getCountHintCoin()):
                newHintCoin = TreeGroupHintCoin.fromPlaceData(dataPlace.getObjHintCoin(idHintCoin))
                newHintCoin.createTreeItems(self._state, self.treeParam, self.__treeRootHintCoin, idHintCoin)
                self.__treeItemsHintCoin.append(newHintCoin)
            expandIfEnabled(self.__treeRootHintCoin, treeRootHintCoinExpanded)
        
        def generateBgAniBranch():
            self.__treeRootBackgroundAnim = self.treeParam.AppendItem(self.__treeRoot, "Background Animations")
            for idBgAni in range(dataPlace.getCountObjBgEvent()):
                newBgAni = TreeGroupBackgroundAnimation.fromPlaceData(dataPlace.getObjBgEvent(idBgAni))
                newBgAni.createTreeItems(self._state, self.treeParam, self.__treeRootBackgroundAnim, idBgAni)
                self.__treeItemsBgAni.append(newBgAni)
            expandIfEnabled(self.__treeRootBackgroundAnim, treeRootBgAniExpanded)

        def generateExitBranch():
            self.__treeRootExit = self.treeParam.AppendItem(self.__treeRoot, "Exits")
            for idExit in range(dataPlace.getCountExits()):
                newExit = TreeGroupExit.fromPlaceData(dataPlace.getExit(idExit))
                newExit.createTreeItems(self._state, self.treeParam, self.__treeRootExit, idExit)
                self.__treeItemsExits.append(newExit)
            expandIfEnabled(self.__treeRootExit, treeRootExitExpanded)

        self.__treeRoot = self.treeParam.AddRoot("Root")
        generateDetailBranch()
        generateEventBranch()
        generateTextBranch()
        generateHintBranch()
        generateBgAniBranch()
        generateExitBranch()

        self.Thaw()
    
    def reloadActivePlaceData(self):
        self.__generateTree()
        self.__generateBackgrounds()

    def refreshExitImages(self):
        # TODO - Not great but should ideally only be called once. No limit on exit images other than byte
        for indexImage in range(256):
            pathExit = PATH_EXT_EXIT % indexImage
            if self._filesystem.doesFileExist(PATH_ANI % pathExit):
                activeAnim = getBottomScreenAnimFromPath(self._state, PATH_EXT_EXIT % indexImage)
                if activeAnim.getActiveFrame() != None:
                    self.__imagesExit[indexImage] = activeAnim.getActiveFrame()
                elif indexImage in self.__imagesExit:
                    del self.__imagesExit[indexImage]

    def __getBackgroundBottomScreenLayers(self, selectedElement : Optional[Type[TreeObjectPlaceData]] = None, hideSelected : bool = False, topmostSelected : bool = False, showHitbox : bool = True, simulateMoveMode : bool = False) -> Tuple[Surface, Surface]:
        # TODO - Should we still show selected elements that are hidden from movemode? Currently we do...
        # TODO - How can we make movemode clearer on selected elements?

        # Topmost stores selection, does not need fancy filtering...
        surfTopmost = Surface(RESOLUTION_NINTENDO_DS).convert_alpha()
        surfTopmost.fill((255,255,255,0))

        # Alpha stores transparent boxes above everything
        surfAlpha = Surface(RESOLUTION_NINTENDO_DS).convert_alpha()
        surfAlpha.fill((255,255,255,0))

        surfColorForeground = Surface(RESOLUTION_NINTENDO_DS).convert_alpha()
        surfColorBackground = Surface(RESOLUTION_NINTENDO_DS)
        surfAlphaForeground = Surface(RESOLUTION_NINTENDO_DS).convert_alpha()
        surfAlphaBackground = Surface(RESOLUTION_NINTENDO_DS).convert_alpha()

        for surf in [surfColorForeground, surfAlphaBackground, surfAlphaForeground]:
            surf.fill((255,255,255,0))

        dataPlace = self._getActiveState()
        if dataPlace == None:
            return (surfColorBackground, surfAlphaForeground)
        
        baseBg = getImageFromPath(self._state, PATH_PLACE_BG % dataPlace.bgMainId)
        if (baseBg == None):
            baseBg = self.__invalidSurface.copy()

        surfColorBackground.blit(baseBg, (0,0))
        
        layerColor = surfColorBackground
        layerAlpha = surfAlphaBackground

        for item, indexBgAni in zip(reversed(self.__treeItemsBgAni), range(dataPlace.getCountObjBgEvent() -1, -1, -1)):
            bgAni = dataPlace.getObjBgEvent(indexBgAni)
            anim = getBottomScreenAnimFromPath(self._state, PATH_ANIM_BGANI % bgAni.name)
            anim.setPos(bgAni.pos)

            if item != selectedElement:
                anim.draw(layerColor)
                if showHitbox and not(simulateMoveMode):
                    if self.checkAlphaFillHitbox.IsChecked():
                        blitBoundingAlphaFill(layerAlpha, getBoundingFromSurface(anim.getActiveFrame(), bgAni.pos), TreeGroupBackgroundAnimation.COLOR_LINE, alpha=FramePlaceEditor.ALPHA_FILL_DESELECTED)
                    else:
                        blitBoundingAlphaFill(layerAlpha, getBoundingFromSurface(anim.getActiveFrame(), bgAni.pos), TreeGroupBackgroundAnimation.COLOR_LINE, alpha=0)
                    blitBoundingLine(layerAlpha, getBoundingFromSurface(anim.getActiveFrame(), bgAni.pos), TreeGroupBackgroundAnimation.COLOR_LINE, width=FramePlaceEditor.THICKNESS_DESELECTED)
            else:
                if not(hideSelected):
                    if topmostSelected:
                        targetColor = surfTopmost
                        targetAlpha = surfTopmost
                    else:
                        targetColor = layerColor
                        targetAlpha = layerAlpha

                    blitBoundingAlphaFill(targetAlpha, getBoundingFromSurface(anim.getActiveFrame(), bgAni.pos), TreeGroupBackgroundAnimation.COLOR_LINE, alpha=FramePlaceEditor.ALPHA_FILL_SELECTED)
                    anim.draw(targetColor)
                    blitBoundingLine(targetAlpha, getBoundingFromSurface(anim.getActiveFrame(), bgAni.pos), TreeGroupBackgroundAnimation.COLOR_LINE, width=FramePlaceEditor.THICKNESS_SELECTED)
                
                layerColor = surfColorForeground
                layerAlpha = surfAlphaForeground
        
        # TODO - Draw interface...

        for item, indexExit in zip(reversed(self.__treeItemsExits), range(dataPlace.getCountExits() - 1, -1, -1)):
            placeExit = dataPlace.getExit(indexExit)
            if item != selectedElement:
                if showHitbox and ((not(simulateMoveMode) and placeExit.canBePressedImmediately()) or simulateMoveMode):
                    if simulateMoveMode and placeExit.idImage in self.__imagesExit:
                        layerColor.blit(self.__imagesExit[placeExit.idImage], (placeExit.bounding.x, placeExit.bounding.y))
                    if self.checkAlphaFillHitbox.IsChecked():
                        item.renderSelectionAlphaFill(layerAlpha, alpha=FramePlaceEditor.ALPHA_FILL_DESELECTED)
                    else:
                        item.renderSelectionAlphaFill(layerAlpha, alpha=0)
                    item.renderSelectionLine(layerAlpha, overrideWidth=FramePlaceEditor.THICKNESS_DESELECTED)
            else:
                if not(hideSelected):
                    if topmostSelected:
                        targetColor = surfTopmost
                        targetAlpha = surfTopmost
                    else:
                        targetColor = layerColor
                        targetAlpha = layerAlpha

                    item.renderSelectionAlphaFill(targetAlpha, alpha=FramePlaceEditor.ALPHA_FILL_SELECTED)
                    if placeExit.idImage in self.__imagesExit:
                        targetColor.blit(self.__imagesExit[placeExit.idImage], (placeExit.bounding.x, placeExit.bounding.y))
                    item.renderSelectionLine(targetAlpha, overrideWidth=FramePlaceEditor.THICKNESS_SELECTED)
                
                layerColor = surfColorForeground
                layerAlpha = surfAlphaForeground
        
        for item in reversed(self.__treeItemsTObj + self.__treeItemsHintCoin):
            item : TreeObjectPlaceData
            if item != selectedElement:
                if (showHitbox and not(simulateMoveMode)):
                    if self.checkAlphaFillHitbox.IsChecked():
                        item.renderSelectionAlphaFill(layerAlpha, alpha=FramePlaceEditor.ALPHA_FILL_DESELECTED)
                    else:
                        item.renderSelectionAlphaFill(layerAlpha, alpha=0)
                    item.renderSelectionLine(layerAlpha, overrideWidth=FramePlaceEditor.THICKNESS_DESELECTED)
            else:
                if not(hideSelected):
                    if topmostSelected:
                        target = surfTopmost
                    else:
                        target = layerAlpha
                    item.renderSelectionAlphaFill(target, alpha=FramePlaceEditor.ALPHA_FILL_SELECTED)
                    item.renderSelectionLine(target, overrideWidth=FramePlaceEditor.THICKNESS_SELECTED)
                
                layerColor = surfColorForeground
                layerAlpha = surfAlphaForeground
        
        for item, indexObjEvent in zip(reversed(self.__treeItemsEventSpawner), range(dataPlace.getCountObjEvents() - 1, -1, -1)):
            # TODO - Handle masking gracefully (ID 0) (plus bg ani)
            objEvent = dataPlace.getObjEvent(indexObjEvent)
            anim = getBottomScreenAnimFromPath(self._state, PATH_EXT_EVENT % (objEvent.idImage & 0xff))
            anim.setPos((objEvent.bounding.x, objEvent.bounding.y))

            if item != selectedElement:
                anim.draw(layerColor)
                if showHitbox and not(simulateMoveMode):
                    if self.checkAlphaFillHitbox.IsChecked():
                        item.renderSelectionAlphaFill(layerAlpha, alpha=FramePlaceEditor.ALPHA_FILL_DESELECTED)
                    else:
                        item.renderSelectionAlphaFill(layerAlpha, alpha=0)
                    item.renderSelectionLine(layerAlpha, overrideWidth=FramePlaceEditor.THICKNESS_DESELECTED)
            else:
                if not(hideSelected):
                    if topmostSelected:
                        targetColor = surfTopmost
                        targetAlpha = surfTopmost
                    else:
                        targetColor = layerColor
                        targetAlpha = layerAlpha
                        
                    item.renderSelectionAlphaFill(targetAlpha, alpha=FramePlaceEditor.ALPHA_FILL_SELECTED)
                    anim.draw(targetColor)
                    item.renderSelectionLine(targetAlpha, overrideWidth=FramePlaceEditor.THICKNESS_SELECTED)
                
                layerColor = surfColorForeground
                layerAlpha = surfAlphaForeground
        
        surfColorBackground.blit(surfAlphaBackground, (0,0))
        surfColorForeground.blit(surfAlphaForeground, (0,0))
        surfColorForeground.blit(surfTopmost, (0,0))
        return (surfColorBackground, surfColorForeground)

    def __getBackgroundTopScreen(self, includeMoveAnim : bool = True) -> Surface:
        if self._getActiveState() == None:
            return self.__invalidSurface
        
        pathBgSub = PATH_PLACE_MAP % self._getActiveState().bgMapId
        bgBase = getImageFromPath(self._state, pathBgSub)
        if bgBase == None:
            bgBase = self.__invalidSurface.copy()
        
        POS_CENTER_TEXT_ROOM_TITLE  = (170,7)
        POS_CENTER_TEXT_OBJECTIVE   = (128,172)

        # TODO - Copied from old widebrim! Use text renderer, research into what method game uses to render here (what's permitted? newlines?)
        surfObjective = generateImageFromString(self._state.fontEvent, "Preview Objective")
        posObjective = (POS_CENTER_TEXT_OBJECTIVE[0] - surfObjective.get_width() // 2, POS_CENTER_TEXT_OBJECTIVE[1])
        bgBase.blit(surfObjective, posObjective, special_flags=BLEND_RGB_SUB)

        if (titleText := self._state.getFileAccessor().getPackedString(PATH_PACK_PLACE_NAME % self._state.language.value, PATH_TEXT_PLACE_NAME % self._getActiveState().idNamePlace)) != "":
            surfRoomTitle = generateImageFromString(self._state.fontEvent, titleText)
            posRoomTitle = (POS_CENTER_TEXT_ROOM_TITLE[0] - surfRoomTitle.get_width() // 2, POS_CENTER_TEXT_ROOM_TITLE[1])
            bgBase.blit(surfRoomTitle, posRoomTitle, special_flags=BLEND_RGB_SUB)
        
        if includeMoveAnim:
            anim = getTopScreenAnimFromPath(self._state, PATH_ANIM_MAPICON, pos=self._getActiveState().posMap)
            if anim != None:
                anim.draw(bgBase)
        
        return bgBase

    def checkboxShowHitboxOnCheckBox(self, event):
        self.__generateBackgrounds()
        return super().checkboxShowHitboxOnCheckBox(event)
    
    def checkboxShowInterfaceOnCheckBox(self, event):
        self.__generateBackgrounds()
        return super().checkboxShowInterfaceOnCheckBox(event)

    def checkAlphaFillHitboxOnCheckBox(self, event):
        self.__generateBackgrounds()
        return super().checkAlphaFillHitboxOnCheckBox(event)

    def __generateBackgrounds(self):
        self.Freeze()

        bg0, bg1 = self.__getBackgroundBottomScreenLayers(self._lastSelectedGroup, hideSelected=False, topmostSelected=True, showHitbox = self.checkboxShowHitbox.IsChecked(),
                                                         simulateMoveMode = self.checkboxShowInterface.IsChecked())
        bg0.blit(bg1, (0,0))
        background = bg0
        self.bitmapRoomBottom.SetBitmap(Bitmap.FromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

        background = self.__getBackgroundTopScreen()
        self.bitmapRoomTop.SetBitmap(Bitmap.FromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

        self.Thaw()
    
    def bitmapRoomBottomOnLeftDClick(self, event):
        # TODO - Regex matching with range limits, special class for this entry mode
        # TODO - Can error if out of range because this is not checked!
        # TODO - Offer functionality to generate template
        # TODO - Apply to all functionality
        if self._getActiveState() != None:
            reMatchString = "/data_lt2/bg/map/main([0-9]+).arc"
            dlg = DialogPickerBgx(self, self._state, self._state.getFileAccessor(), "/data_lt2/bg/map", reMatchString, "main%i.arc" % self._getActiveState().bgMainId)
            if dlg.ShowModal() == ID_OK:
                groupingMatch = int(match(reMatchString, dlg.GetPath()).group(1))
                if groupingMatch != self._getActiveState().bgMainId:
                    self._getActiveState().bgMainId = groupingMatch
                    self.__generateBackgrounds()
        return super().bitmapRoomBottomOnLeftDClick(event)
    
    def bitmapRoomTopOnLeftDClick(self, event):
        # TODO - Same as bottom bg TODOs
        if self._getActiveState() != None:
            reMatchString = "/data_lt2/bg/map/map([0-9]+).arc"
            dlg = DialogPickerBgx(self, self._state, self._state.getFileAccessor(), "/data_lt2/bg/map", reMatchString, "map%i.arc" % self._getActiveState().bgMapId)
            if dlg.ShowModal() == ID_OK:
                groupingMatch = int(match(reMatchString, dlg.GetPath()).group(1))
                if groupingMatch != self._getActiveState().bgMapId:
                    self._getActiveState().bgMapId = groupingMatch
                    self.__generateBackgrounds()
        return super().bitmapRoomTopOnLeftDClick(event)

    def btnRoomCreateNewOnButtonClick(self, event):
        # TODO - Disable button if too many
        item = self.treeParam.GetSelection()
        if isItemOnPathToItem(self.treeParam, item, self.__treeRootEventSpawner):
            if self.checkRoomApplyToAll.IsChecked():
                maxEventCount = 0
                for placeData in self._getListPlaceData()[1]:
                    maxEventCount = max(placeData.getCountObjEvents(), maxEventCount)

                # TODO - Make constant in madhatter
                if maxEventCount >= 16:
                    # TODO - Warning message
                    event.Skip()
                    return
                
                for placeData in self._getListPlaceData()[1]:
                    placeData.addObjEvent(EventEntry())
            else:
                if self._getActiveState().getCountObjEvents() < 16:
                    self._getActiveState().addObjEvent(EventEntry())
                else:
                    # TODO - Warning message
                    event.Skip()
                    return

            currentData = self._getActiveState()
            newEntry = currentData.getObjEvent(currentData.getCountObjEvents() - 1)
            self.__treeItemsEventSpawner.append(TreeGroupEventSpawner.fromPlaceData(newEntry))
            self.__treeItemsEventSpawner[-1].createTreeItems(self._state, self.treeParam, self.__treeRootEventSpawner, index=(currentData.getCountObjEvents() - 1))
            self.__generateBackgrounds()

        elif isItemOnPathToItem(self.treeParam, item, self.__treeRootTextObjectSpawner):
            if self.checkRoomApplyToAll.IsChecked():
                maxTObj = 0
                for placeData in self._getListPlaceData()[1]:
                    maxTObj = max(maxTObj, placeData.getCountObjText())
                if maxTObj >= 16:
                    # TODO - Warning message
                    event.Skip()
                    return
                
                for placeData in self._getListPlaceData()[1]:
                    placeData.addObjText(TObjEntry())
            else:
                if self._getActiveState().getCountObjText() < 16:
                    self._getActiveState().addObjText(TObjEntry())
                else:
                    # TODO - Warning message
                    event.Skip()
                    return
            currentData = self._getActiveState()
            newEntry = currentData.getObjText(currentData.getCountObjText() - 1)
            self.__treeItemsTObj.append(TreeGroupTObj.fromPlaceData(newEntry))
            self.__treeItemsTObj[-1].createTreeItems(self._state, self.treeParam, self.__treeRootTextObjectSpawner, index=(currentData.getCountObjText() - 1))
            self.__generateBackgrounds()

        elif isItemOnPathToItem(self.treeParam, item, self.__treeRootHintCoin):
            # Hints are different - because the game stores hints by their index across all room data, we cannot allow events to have different hint counts
            # Although it is possible to remove the topmost hints without breaking things, in reality there's no real reason to do this...
            maxHintCount = 0
            for placeData in self._getListPlaceData()[1]:
                maxHintCount = max(placeData.getCountHintCoin(), maxHintCount)

            # TODO - Make constant in madhatter
            # If there are 4 hints already at any point in the placedata, we cannot allow any more to be created
            if maxHintCount >= 4:
                # TODO - Warning message
                event.Skip()
                return
            
            for placeData in self._getListPlaceData()[1]:
                placeData.addObjHintCoin(HintCoin())
            
            currentData = self._getActiveState()
            newEntry = currentData.getObjHintCoin(currentData.getCountHintCoin() - 1)
            self.__treeItemsHintCoin.append(TreeGroupHintCoin.fromPlaceData(newEntry))
            self.__treeItemsHintCoin[-1].createTreeItems(self._state, self.treeParam, self.__treeRootHintCoin, index=(currentData.getCountHintCoin() - 1))
            self.__generateBackgrounds()

        elif isItemOnPathToItem(self.treeParam, item, self.__treeRootBackgroundAnim):
            if self.checkRoomApplyToAll.IsChecked():
                maxBgAni = 0
                for placeData in self._getListPlaceData()[1]:
                    maxBgAni = max(maxBgAni, placeData.getCountObjBgEvent())
                if maxBgAni >= 12:
                    # TODO - Warning message
                    event.Skip()
                    return
                
                for placeData in self._getListPlaceData()[1]:
                    placeData.addObjBgEvent(BgAni())
            else:
                if self._getActiveState().getCountObjBgEvent() < 12:
                    self._getActiveState().addObjBgEvent(BgAni())
                else:
                    # TODO - Warning message
                    event.Skip()
                    return

            currentData = self._getActiveState()
            newEntry = currentData.getObjBgEvent(currentData.getCountObjBgEvent() - 1)
            self.__treeItemsBgAni.append(TreeGroupBackgroundAnimation.fromPlaceData(newEntry))
            self.__treeItemsBgAni[-1].createTreeItems(self._state, self.treeParam, self.__treeRootBackgroundAnim, index=(currentData.getCountObjBgEvent() - 1))
            self.__generateBackgrounds()

        elif isItemOnPathToItem(self.treeParam, item, self.__treeRootExit):
            if self.checkRoomApplyToAll.IsChecked():
                maxExit = 0
                for placeData in self._getListPlaceData()[1]:
                    maxExit = max(maxExit, placeData.getCountExits())
                if maxExit >= 12:
                    # TODO - Warning message
                    event.Skip()
                    return
                
                for placeData in self._getListPlaceData()[1]:
                    placeData.addExit(Exit())
            else:
                if self._getActiveState().getCountExits() < 12:
                    self._getActiveState().addExit(Exit())
                else:
                    # TODO - Warning message
                    event.Skip()
                    return

            currentData = self._getActiveState()
            newEntry = currentData.getExit(currentData.getCountExits() - 1)
            self.__treeItemsExits.append(TreeGroupExit.fromPlaceData(newEntry))
            self.__treeItemsExits[-1].createTreeItems(self._state, self.treeParam, self.__treeRootExit, index=(currentData.getCountExits() - 1))
            self.__generateBackgrounds()

        return super().btnRoomCreateNewOnButtonClick(event)
    
    def btnRoomDeleteOnButtonClick(self, event):
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if not(self.treeParam):
            return super().btnRoomDeleteOnButtonClick(event)
        
        item = self.treeParam.GetFocusedItem()

        placeData = self._getActiveState()
        if placeData == None:
            return super().btnRoomDeleteOnButtonClick(event)
        
        def findTreeItem(group : List[TreeObjectPlaceData], methodGetItemAtIndex : Callable[[int],Optional[Union[HintCoin, Exit, TObjEntry, BgAni, EventEntry]]], count : int) -> Optional[int]:
            if len(group) != count:
                logSevere("Duplicate length mismatch!")
            for treeGroup, indexGroup in zip(group, range(count)):
                if treeGroup.isItemSelected(item):
                    return indexGroup
            return None

        def purgeDuplicate(group : List[TreeObjectPlaceData], methodGetItem : Callable[[int], Union[HintCoin, Exit, TObjEntry, BgAni, EventEntry]],
                           methodRemoveItem : Callable[[int], bool], methodGetCountItem : Callable[[], int]) -> bool:
            
            def removeDuplicate(reference : Union[HintCoin, Exit, TObjEntry, BgAni, EventEntry], dataPlace : PlaceData) -> Optional[int]:
                if type(reference) == HintCoin:
                    for index in range(dataPlace.getCountHintCoin() - 1, -1, -1):
                        if dataPlace.getObjHintCoin(index) == reference:
                            dataPlace.removeObjHintCoin(index)
                            return index
                elif type(reference) == Exit:
                    for index in range(dataPlace.getCountExits() - 1, -1, -1):
                        if dataPlace.getExit(index) == reference:
                            dataPlace.removeExit(index)
                            return index
                elif type(reference) == TObjEntry:
                    for index in range(dataPlace.getCountObjText() - 1, -1, -1):
                        if dataPlace.getObjText(index) == reference:
                            dataPlace.removeObjText(index)
                            return index
                elif type(reference) == BgAni:
                    for index in range(dataPlace.getCountObjBgEvent() - 1, -1, -1):
                        if dataPlace.getObjBgEvent(index) == reference:
                            dataPlace.removeObjBgEvent(index)
                            return index
                else:
                    for index in range(dataPlace.getCountObjEvents() - 1, -1, -1):
                        if dataPlace.getObjEvent(index) == reference:
                            dataPlace.removeObjEvent(index)
                            return index
                return None

            reference = findTreeItem(group, methodGetItem, methodGetCountItem())
            if reference != None:
                if not(self.checkRoomApplyToAll.IsEnabled()) or (self.checkRoomApplyToAll.IsEnabled() and self.checkRoomApplyToAll.IsChecked()):
                    for placeData in self._getListPlaceData()[1]:
                        if placeData != self._getActiveState():
                            removeDuplicate(methodGetItem(reference), placeData)
                
                group[reference].deleteTreeItems(self.treeParam)
                group.pop(reference)
                removeDuplicate(methodGetItem(reference), self._getActiveState())
                for indexGroup, treeGroup in enumerate(group):
                    treeGroup.setNameIndex(self.treeParam, indexGroup)
                return True
            return False

        # TODO - rewrite this, this is genuinely terrible
        nothingHappened = True

        if nothingHappened and purgeDuplicate(self.__treeItemsBgAni, placeData.getObjBgEvent, placeData.removeObjBgEvent, placeData.getCountObjBgEvent):
            nothingHappened = False
        if nothingHappened and purgeDuplicate(self.__treeItemsHintCoin, placeData.getObjHintCoin, placeData.removeObjHintCoin, placeData.getCountHintCoin):
            nothingHappened = False
        if nothingHappened and purgeDuplicate(self.__treeItemsEventSpawner, placeData.getObjEvent, placeData.removeObjEvent, placeData.getCountObjEvents):
            nothingHappened = False
        if nothingHappened and purgeDuplicate(self.__treeItemsTObj, placeData.getObjText, placeData.removeObjText, placeData.getCountObjText):
            nothingHappened = False
        if nothingHappened and purgeDuplicate(self.__treeItemsExits, placeData.getExit, placeData.removeExit, placeData.getCountExits):
            nothingHappened = False
        
        if not(nothingHappened):
            self.__generateBackgrounds()
        return super().btnRoomDeleteOnButtonClick(event)