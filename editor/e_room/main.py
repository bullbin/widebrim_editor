from tkinter import N
from typing import List, Optional
from editor.asset_management.room import PlaceGroup, getPackPathForPlaceIndex
from editor.e_room.treeGroups import TreeGroupTObj
from editor.nopush_editor import editorRoom
from widebrim.engine.const import PATH_EXT_EVENT, PATH_PACK_PLACE_NAME, PATH_PLACE_BG, PATH_PLACE_MAP, PATH_TEXT_PLACE_NAME, RESOLUTION_NINTENDO_DS
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.engine_ext.utils import getBottomScreenAnimFromPath, getImageFromPath, substituteLanguageString
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from wx import TreeItemId, Bitmap
from widebrim.gamemodes.room.const import PATH_ANIM_BGANI, PATH_PACK_PLACE
from pygame import Surface
from pygame.image import tostring

from widebrim.madhatter.hat_io.asset_dat.place import PlaceData, PlaceDataNds

class FramePlaceEditor(editorRoom):

    INVALID_FRAME_COLOR = (255,0,0)

    def __init__(self, parent, filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, groupPlace : PlaceGroup):
        super().__init__(parent)
        self._filesystem = filesystem
        self._state = state
        self._groupPlace = groupPlace
        self._dataPlace = []

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

        self._loaded = False
        self.__invalidSurface = Surface(RESOLUTION_NINTENDO_DS)
        self.__invalidSurface.fill(FramePlaceEditor.INVALID_FRAME_COLOR)
    
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

    def listStateOnListBox(self, event):
        self._generateTree()
        self._generateBackgrounds()
        return super().listStateOnListBox(event)

    def treeParamOnTreeSelChanged(self, event):
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

    def _getActiveState(self) -> Optional[PlaceDataNds]:
        selection = self.listState.GetSelection()
        if selection == 0 or len(self._dataPlace) == 0:
            return None
        else:
            return self._dataPlace[selection - 1]

    def _generateList(self):
        self.listState.Clear()
        self.listState.Append("(Common State)")
        
        for index in self._groupPlace.indicesStates:
            if index == 0:
                self.listState.Append("Default State")
            else:
                self.listState.Append("State " + str(index))
        
        self.listState.SetSelection(1)

    def _generateTree(self):

        self.Freeze()

        def expandIfEnabled(item : TreeItemId, expanded : bool):
            if expanded:
                self.treeParam.Expand(item)
            else:
                self.treeParam.Collapse(item)

        treeRootPropertiesExpanded = False
        treeRootTObjExpanded = False

        self._treeItemsTObj = []

        if self._treeRoot != None:
            treeRootPropertiesExpanded = self.treeParam.IsExpanded(self._treeRootProperties)
            treeRootTObjExpanded = self.treeParam.IsExpanded(self._treeRootTextObjectSpawner)

        self.treeParam.DeleteAllItems()
        dataPlace = self._getActiveState()
        if dataPlace == None:
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

        self._treeRoot = self.treeParam.AddRoot("Root")
        generateDetailBranch()
        generateTextBranch()

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

        self.Freeze()

        dataPlace = self._getActiveState()
        if dataPlace == None:
            return
        
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