from __future__ import annotations
from typing import Dict, Optional
from editor.d_operandMultichoice import DialogMultipleChoice
from editor.e_room.modifiers import modifyBoundary, modifyEventSelection, modifySpritePath
from editor.e_room.utils import getShortenedString
from widebrim.engine.const import PATH_EXT_EVENT
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.gamemodes.room.const import PATH_ANIM_BGANI, PATH_FILE_HINTCOIN, PATH_FILE_TOBJ, PATH_PACK_TOBJ
from widebrim.madhatter.hat_io.asset_dat.place import BgAni, EventEntry, Exit, TObjEntry, HintCoin
from wx import TreeCtrl, TreeItemId, ID_OK
from pygame import Surface, Rect
from pygame.draw import rect as drawRectangle
from pygame.draw import circle as drawCircle

class RefreshInformation():
    def __init__(self, fullTreeRefresh = False, backgroundRefresh = False):
        self.fullTreeRefresh = fullTreeRefresh
        self.backgroundRefresh = backgroundRefresh

class TreeObjectPlaceData():

    def __init__(self):
        self._treeRoot : Optional[TreeItemId] = None
        self.__isModified = False
    
    def _createRootItem(self, treeCtrl : TreeCtrl, branchRoot : TreeItemId, name : str, index : Optional[int] = None):
        if index == None:
            self._treeRoot = treeCtrl.AppendItem(branchRoot, "New " + name)
        else:
            self._treeRoot = treeCtrl.AppendItem(branchRoot, "%s %i" % (name, (index + 1)))

    def isValid(self) -> bool:
        return False

    def renderSelectionLine(self, surface : Surface):
        """Render this group as a selection boundary on a surface.

        Args:
            surface (Surface): pygame Surface for rendering.
        """
        pass
    
    def renderSelectionAlphaFill(self, surface : Surface):
        """Render this group as a selection plane on a surface.

        Args:
            surface (Surface): pygame Surface for rendering.
        """
        pass
    
    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):
        """Create representation of this group onto a tree.

        Args:
            state (Layton2GameState): Game state container for file access.
            treeCtrl (TreeCtrl): Tree object to modify.
            branchRoot (TreeItemId): Tree item to append items into.
            index (Optional[int], optional): New item index for convenient naming. Defaults to None.
        """
        pass

    def deleteTreeItems(self, treeCtrl : TreeCtrl):
        """Deletes representation of group from tree.

        Args:
            treeCtrl (TreeCtrl): Tree object to modify.
        """
        if self._treeRoot != None:
            treeCtrl.DeleteChildren(self._treeRoot)
            treeCtrl.Delete(self._treeRoot)
    
    def isItemSelected(self, selectedId : TreeItemId) -> bool:
        """Returns true if any item within the group is selected.

        Args:
            selectedId (TreeItemId): Tree item to check.

        Returns:
            bool: True if any item within the group is selected.
        """
        return False
    
    def modifyItem(self, state : Layton2GameState, treeCtrl : TreeCtrl, selectedId : TreeItemId, parent, previewImage : Surface) -> RefreshInformation:
        return RefreshInformation()
    
    @staticmethod
    def fromPlaceData(data) -> TreeObjectPlaceData:
        return TreeObjectPlaceData()

class TreeGroupTObj(TreeObjectPlaceData):

    COLOR_LINE = (255,0,0)

    def __init__(self):
        super().__init__()
        self.__tObj         : TObjEntry = TObjEntry()
        self.itemComment    : Optional[TreeItemId] = None
        self.itemChar       : Optional[TreeItemId] = None
        self.itemBounding   : Optional[TreeItemId] = None

    def isValid(self) -> bool:
        if self._treeRoot != None:
            return self._treeRoot.IsOk()
        return False

    def renderSelectionLine(self, surface: Surface):
        drawRectangle(surface, TreeGroupTObj.COLOR_LINE, Rect(self.__tObj.bounding.x, self.__tObj.bounding.y, self.__tObj.bounding.width, self.__tObj.bounding.height), width=3)

    def __getTObjText(self, state : Layton2GameState):
        if self.__tObj.idTObj != -1:
            return state.getFileAccessor().getPackedString(PATH_PACK_TOBJ % state.language.value, PATH_FILE_TOBJ % self.__tObj.idTObj)
        return state.getFileAccessor().getPackedString(PATH_PACK_TOBJ % state.language.value, PATH_FILE_HINTCOIN)

    def modifyItem(self, state: Layton2GameState, treeCtrl : TreeCtrl, selectedId: TreeItemId, parent, previewImage: Surface) -> RefreshInformation:
        if self._treeRoot != None:
            if selectedId == self.itemChar:
                choices = {"Layton":"Layton will appear in the text window for this comment.", "Luke":"Luke will appear in the text window for this comment."}
                dlg = DialogMultipleChoice(parent, choices, "Change Comment Character")
                try:
                    dlg.SetSelection({0:"Layton", 1:"Luke"}[self.__tObj.idChar])
                except KeyError:
                    pass
                mode = dlg.ShowModal()
                if mode == ID_OK:
                    if dlg.GetSelection() == "Layton":
                        self.__tObj.idChar = 0
                    else:
                        self.__tObj.idChar = 1
                    treeCtrl.SetItemText(selectedId, "Speaker: %s" % dlg.GetSelection())
                    treeCtrl.SetItemData(selectedId, self.__tObj.idChar)
                return RefreshInformation()
            elif selectedId == self.itemComment:
                # TODO
                return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)
            else:
                boundaryX = self.__tObj.bounding.x
                boundaryY = self.__tObj.bounding.y
                width = self.__tObj.bounding.width
                height = self.__tObj.bounding.height

                modifyBoundary(parent, state, previewImage, self.__tObj.bounding, color=TreeGroupTObj.COLOR_LINE)
                changed = boundaryX != self.__tObj.bounding.x or boundaryY != self.__tObj.bounding.y or width != self.__tObj.bounding.width or height != self.__tObj.bounding.height
                return RefreshInformation(backgroundRefresh=changed)

        return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)

    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):
        self._createRootItem(treeCtrl, branchRoot, "Comment", index)
        self.itemComment = treeCtrl.AppendItem(self._treeRoot, '"%s"' % getShortenedString(self.__getTObjText(state)), data=self.__tObj.idTObj)

        if self.__tObj.idChar == 0:
            self.itemChar = treeCtrl.AppendItem(self._treeRoot, "Speaker: Layton", data=self.__tObj.idChar)
        elif self.__tObj.idChar == 1:
            self.itemChar = treeCtrl.AppendItem(self._treeRoot, "Speaker: Luke", data=self.__tObj.idChar)
        else:
            # TODO - Can hint coin image be pulled? What happens with invalid image?
            self.itemChar = treeCtrl.AppendItem(self._treeRoot, "Speaker: Undefined", data=self.__tObj.idChar)
        
        self.itemBounding = treeCtrl.AppendItem(self._treeRoot, "Edit interaction area...", data=self.__tObj.bounding)

    def deleteTreeItems(self, treeCtrl : TreeCtrl):
        super().deleteTreeItems(treeCtrl)
        self.itemComment = None
        self.itemChar = None
        self.itemBounding = None

    def isItemSelected(self, selectedId : TreeItemId) -> bool:
        if self._treeRoot != None:
            return selectedId == self.itemBounding or selectedId == self.itemChar or selectedId == self.itemComment
        return False

    @staticmethod
    def fromPlaceData(data : TObjEntry) -> TreeGroupTObj:
        output = TreeGroupTObj()
        output.__tObj = data
        return output

class TreeGroupEventSpawner(TreeObjectPlaceData):

    COLOR_LINE = (0,255,0)

    def __init__(self):
        super().__init__()
        self.__eventEntry   : EventEntry = EventEntry()
        self.itemBounding   : Optional[TreeItemId] = None
        self.itemImage      : Optional[TreeItemId] = None
        self.itemIdEvent    : Optional[TreeItemId] = None

    def isItemSelected(self, selectedId : TreeItemId) -> bool:
        if self._treeRoot != None:
            return selectedId == self.itemBounding or selectedId == self.itemImage or selectedId == self.itemIdEvent
        return False

    def modifyItem(self, state: Layton2GameState, treeCtrl : TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface) -> RefreshInformation:
        if not(self.isItemSelected(selectedId)):
            return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)
        
        if selectedId == self.itemBounding:
            # TODO - Offer way to infer from sprite boundary, either move sprite position or change boundary (should merge at some point with sprite in preview)
            boundaryX = self.__eventEntry.bounding.x
            boundaryY = self.__eventEntry.bounding.y
            width = self.__eventEntry.bounding.width
            height = self.__eventEntry.bounding.height

            modifyBoundary(parent, state, previewImage, self.__eventEntry.bounding, color=TreeGroupEventSpawner.COLOR_LINE)
            changed = boundaryX != self.__eventEntry.bounding.x or boundaryY != self.__eventEntry.bounding.y or width != self.__eventEntry.bounding.width or height != self.__eventEntry.bounding.height
            return RefreshInformation(backgroundRefresh=changed)

        elif selectedId == self.itemImage:
            # TODO - Handle hidden trigger gracefully
            # TODO - Prevent user entering hidden trigger image! Might be broken here, untested
            idImage = self.__eventEntry.idImage
            outPath = modifySpritePath(parent, state, (PATH_EXT_EVENT % (self.__eventEntry.idImage & 0xff)).split("/")[1],
                                       pathRoot = "/data_lt2/ani/eventobj", reMatchString="/data_lt2/ani/eventobj/obj_([0-9]+).arc", allowEmptyImage=True)
            if outPath == "":
                # Hidden trigger
                newId = 0
            else:
                newId = int(outPath)

            self.__eventEntry.idImage = newId
            treeCtrl.SetItemData(self.itemImage, newId)
            if newId == 0:
                treeCtrl.SetItemText(self.itemImage, "Image: None, hidden trigger")
            else:
                treeCtrl.SetItemText(self.itemImage, "Image: %s" % (PATH_EXT_EVENT % idImage))

            if newId != idImage:
                return RefreshInformation(backgroundRefresh=True)
            else:
                return RefreshInformation(backgroundRefresh=False)
        else:
            idEvent = self.__eventEntry.idEvent
            self.__eventEntry.idEvent = modifyEventSelection(parent, state, self.__eventEntry.idEvent)
            treeCtrl.SetItemText(self.itemIdEvent, "Event: %i" % self.__eventEntry.idEvent)
            treeCtrl.SetItemData(self.itemIdEvent, self.__eventEntry.idEvent)
            return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)

    def renderSelectionLine(self, surface: Surface):
        drawRectangle(surface, TreeGroupEventSpawner.COLOR_LINE, Rect(self.__eventEntry.bounding.x, self.__eventEntry.bounding.y, self.__eventEntry.bounding.width, self.__eventEntry.bounding.height), width=3)

    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):
        self._createRootItem(treeCtrl, branchRoot, "Event Spawner", index)

        idImage = self.__eventEntry.idImage & 0xff
        if idImage == 0:
            self.itemImage = treeCtrl.AppendItem(self._treeRoot, "Image: None, hidden trigger", data=self.__eventEntry.idImage)
        else:
            self.itemImage = treeCtrl.AppendItem(self._treeRoot, "Image: %s" % (PATH_EXT_EVENT % idImage), data=self.__eventEntry.idImage)

        # TODO - Get event name method...
        self.itemIdEvent = treeCtrl.AppendItem(self._treeRoot, "Event: %i" % self.__eventEntry.idEvent, data=self.__eventEntry.idEvent)

        self.itemBounding = treeCtrl.AppendItem(self._treeRoot, "Edit interaction area...", data=self.__eventEntry.bounding)

    @staticmethod
    def fromPlaceData(data : EventEntry) -> TreeGroupEventSpawner:
        output = TreeGroupEventSpawner()
        output.__eventEntry = data
        return output

class TreeGroupHintCoin(TreeObjectPlaceData):
    
    COLOR_LINE = (255,255,0)
    
    def __init__(self):
        super().__init__()
        self.__hintEntry    : HintCoin = HintCoin()
        self.itemBounding : Optional[TreeItemId] = None

    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):
        self._createRootItem(treeCtrl, branchRoot, "Hint Coin", index)
        self.itemBounding = treeCtrl.AppendItem(self._treeRoot, "Edit interaction area...", data=self.__hintEntry.bounding)
    
    def renderSelectionLine(self, surface: Surface):
        drawRectangle(surface, TreeGroupHintCoin.COLOR_LINE, Rect(self.__hintEntry.bounding.x, self.__hintEntry.bounding.y, self.__hintEntry.bounding.width, self.__hintEntry.bounding.height), width=3)

    def isItemSelected(self, selectedId: TreeItemId) -> bool:
        if self._treeRoot != None:
            return selectedId == self.itemBounding
        return False

    def modifyItem(self, state: Layton2GameState, treeCtrl : TreeCtrl, selectedId: TreeItemId, parent, previewImage: Surface) -> RefreshInformation:
        boundaryX = self.__hintEntry.bounding.x
        boundaryY = self.__hintEntry.bounding.y
        width = self.__hintEntry.bounding.width
        height = self.__hintEntry.bounding.height

        modifyBoundary(parent, state, previewImage, self.__hintEntry.bounding, color=TreeGroupHintCoin.COLOR_LINE)
        changed = boundaryX != self.__hintEntry.bounding.x or boundaryY != self.__hintEntry.bounding.y or width != self.__hintEntry.bounding.width or height != self.__hintEntry.bounding.height
        return RefreshInformation(backgroundRefresh=changed)

    @staticmethod
    def fromPlaceData(data : HintCoin) -> TreeGroupHintCoin:
        output = TreeGroupHintCoin()
        output.__hintEntry = data
        return output

class TreeGroupBackgroundAnimation(TreeObjectPlaceData):

    COLOR_LINE = (255,0,255)

    def __init__(self):
        super().__init__()
        self.__bgAniEntry   : BgAni = BgAni()
        self.itemPos        : Optional[TreeItemId] = None
        self.itemBgPath     : Optional[TreeItemId] = None

    def isItemSelected(self, selectedId: TreeItemId) -> bool:
        if self._treeRoot != None:
            return selectedId == self.itemPos or selectedId == self.itemBgPath
        return False

    def modifyItem(self, state: Layton2GameState, treeCtrl: TreeCtrl, selectedId: TreeItemId, parent, previewImage: Surface) -> RefreshInformation:
        if selectedId == self.itemPos:
            pass
        elif selectedId == self.itemBgPath:
            oldPath = self.__bgAniEntry.name
            outPath = modifySpritePath(parent, state, oldPath,
                                       pathRoot = "/data_lt2/ani/bgani", reMatchString="/data_lt2/ani/bgani/(.+).arc")
            newPath = outPath + ".spr"
            self.__bgAniEntry.name = newPath
            treeCtrl.SetItemData(self.itemBgPath, newPath)
            if newPath != oldPath:
                return RefreshInformation(backgroundRefresh=True)
            else:
                return RefreshInformation(backgroundRefresh=False)
        return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)

    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):
        self._createRootItem(treeCtrl, branchRoot, "Background Animation", index)
        self.itemBgPath = treeCtrl.AppendItem(self._treeRoot, "Image: %s" % (PATH_ANIM_BGANI % self.__bgAniEntry.name), data=self.__bgAniEntry.name)
        self.itemPos = treeCtrl.AppendItem(self._treeRoot, "Edit animation position...", data=self.__bgAniEntry.pos)
    
    def renderSelectionLine(self, surface: Surface):
        # TODO - Get BG anim dimensions
        drawCircle(surface, TreeGroupBackgroundAnimation.COLOR_LINE, self.__bgAniEntry.pos, radius=3, width=3)
    
    @staticmethod
    def fromPlaceData(data : BgAni) -> TreeGroupBackgroundAnimation:
        output = TreeGroupBackgroundAnimation()
        output.__bgAniEntry = data
        return output

class TreeGroupExit(TreeObjectPlaceData):

    COLOR_LINE = (0,0,255)

    MAP_ID_TO_IMAGE_DESCRIPTION : Dict[int, str] = {0:"Pointing hand",
                                                    5:"Arrow, up",
                                                    2:"Arrow, down",
                                                    1:"Arrow, left",
                                                    3:"Arrow, right",
                                                    4:"Arrow, forwards",
                                                    6:"Arrow, backwards-left",
                                                    7:"Arrow, backwards-right"}

    MAP_TYPE_TO_OPTIONS : Dict[int, str] = {0:"Room, move mode only",
                                            1:"Room, tap anytime",
                                            2:"Event, branching behaviour",
                                            3:"Event, tap anytime"}
    
    MAP_NOISE_DESCRIPTION : Dict[int, str] = {2:"Silent",
                                              0:"Footsteps",
                                              1:"Door creaking",
                                              3:"Door creaking 2",
                                              4:"Train door sliding"}

    def __init__(self):
        super().__init__()
        self.__placeExit            : Exit = Exit()
        self.itemBounding           : Optional[TreeItemId] = None
        self.itemSound              : Optional[TreeItemId] = None
        self.itemPosTransition      : Optional[TreeItemId] = None
        self.itemArrowImage         : Optional[TreeItemId] = None
        self.itemExitType           : Optional[TreeItemId] = None
        self.itemExitTermination    : Optional[TreeItemId] = None

    def isItemSelected(self, selectedId: TreeItemId) -> bool:
        if self._treeRoot != None:
            return selectedId in [self.itemBounding, self.itemSound, self.itemPosTransition, self.itemArrowImage, self.itemExitType, self.itemExitTermination]
        return super().isItemSelected(selectedId)

    def modifyItem(self, state: Layton2GameState, treeCtrl: TreeCtrl, selectedId: TreeItemId, parent, previewImage: Surface) -> RefreshInformation:

        def doMultipleChoiceDialogFromKeyBank(bankComments : Dict[int, str], bankChoices : Dict[int, str], title : str, currentChoice : int, treeStr : str):
            choicesToKey = {}
            choices = {}
            for key in bankComments:
                if key in bankChoices:
                    choices[bankChoices[key]] = bankComments[key]
                    choicesToKey[bankChoices[key]] = key
            
            dlg = DialogMultipleChoice(parent, choices, title)
            try:
                dlg.SetSelection(bankChoices[currentChoice])
            except KeyError:
                pass
            if dlg.ShowModal() == ID_OK:
                newId = choicesToKey[dlg.GetSelection()]
                treeCtrl.SetItemText(selectedId, treeStr % bankChoices[newId])
                treeCtrl.SetItemData(selectedId, newId)
                return True
            return False

        if self.isItemSelected(selectedId):
            if selectedId == self.itemBounding:
                boundaryX = self.__placeExit.bounding.x
                boundaryY = self.__placeExit.bounding.y
                width = self.__placeExit.bounding.width
                height = self.__placeExit.bounding.height

                modifyBoundary(parent, state, previewImage, self.__placeExit.bounding, color=TreeGroupExit.COLOR_LINE)
                changed = boundaryX != self.__placeExit.bounding.x or boundaryY != self.__placeExit.bounding.y or width != self.__placeExit.bounding.width or height != self.__placeExit.bounding.height
                return RefreshInformation(backgroundRefresh=changed)
            
            elif selectedId == self.itemArrowImage:
                mapExitIdToComments = {0:"A hand pointing towards the bottom-left will show when in move mode.",
                                       5:"A yellow ground arrow pointing upwards will show when in move mode.",
                                       2:"A yellow ground arrow pointing downwards will show when in move mode.",
                                       1:"A yellow ground arrow pointing left will show when in move mode.",
                                       3:"A yellow ground arrow pointing right will show when in move mode.",
                                       4:"A yellow ground arrow pointing forwards will show when in move mode.",
                                       6:"A yellow ground arrow pointing backwards-left will show when in move mode.",
                                       7:"A yellow ground arrow pointing backwards-right will show when in move mode."}
                
                changed = doMultipleChoiceDialogFromKeyBank(mapExitIdToComments, TreeGroupExit.MAP_ID_TO_IMAGE_DESCRIPTION, "Change Exit Image",
                                                            self.__placeExit.idImage, "Exit Image: %s")
                return RefreshInformation()
            
            elif selectedId == self.itemSound:
                mapNoiseToComments : Dict[int, str] = {2:"No noise will be made. This is ignored if using this exit spawns an event.",
                                                       0:"Default footsteps walking sound. This is ignored if using this exit spawns an event.",
                                                       1:"Wooden door creaking noise. This is ignored if using this exit spawns an event.",
                                                       3:"Wooden door creaking noise (duplicate). This is ignored if using this exit spawns an event.",
                                                       4:"Loud metallic sliding door noise. This is ignored if using this exit spawns an event."}
                changed = doMultipleChoiceDialogFromKeyBank(mapNoiseToComments, TreeGroupExit.MAP_NOISE_DESCRIPTION, "Change Sound",
                                                            self.__placeExit.idSound, "Sound: %s")
                return RefreshInformation()
            
            elif selectedId == self.itemExitTermination:
                while True:
                    choices = {"Room":"Using this exit will move Layton and Luke into another room.",
                               "Event":"Using this exit will cause an event to playback."}
                    dlg = DialogMultipleChoice(parent, choices, "Change Exit Destination")
                    if self.__placeExit.canSpawnEvent():
                        dlg.SetSelection("Event")
                    else:
                        dlg.SetSelection("Room")
                    
                    if dlg.ShowModal() == ID_OK:
                        # TODO - Event and room trees, also handling wrong type
                        pass
                    return RefreshInformation()
            
            elif selectedId == self.itemExitType:
                pass

            elif selectedId == self.itemPosTransition:
                pass
                        
        return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)

    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):

        def getMapString(bank : Dict[int, str], id : int) -> str:
            if id in bank:
                return bank[id]
            return "Undefined (%i)" % id

        self._createRootItem(treeCtrl, branchRoot, "Exit", index)
        self.itemBounding = treeCtrl.AppendItem(self._treeRoot, "Edit interaction area...", data=self.__placeExit.bounding)
        self.itemPosTransition = treeCtrl.AppendItem(self._treeRoot, "Edit map pinpoint destination...", data=self.__placeExit.posTransition)
        self.itemArrowImage = treeCtrl.AppendItem(self._treeRoot, "Exit Image: %s" % getMapString(TreeGroupExit.MAP_ID_TO_IMAGE_DESCRIPTION, self.__placeExit.idImage),
                                                  data=self.__placeExit.idImage)
        self.itemExitType = treeCtrl.AppendItem(self._treeRoot, "Exit Type: %s" % getMapString(TreeGroupExit.MAP_TYPE_TO_OPTIONS, self.__placeExit.modeDecoding),
                                                  data=self.__placeExit.modeDecoding)
        
        if self.__placeExit.canSpawnEvent():
            self.itemExitTermination = treeCtrl.AppendItem(self._treeRoot, "Destination: Event %i" % self.__placeExit.spawnData,
                                                           data=self.__placeExit.spawnData)
        else:
            self.itemExitTermination = treeCtrl.AppendItem(self._treeRoot, "Destination: Room %i" % self.__placeExit.spawnData,
                                                           data=self.__placeExit.spawnData)

        self.itemSound = treeCtrl.AppendItem(self._treeRoot, "Sound: %s" % getMapString(TreeGroupExit.MAP_NOISE_DESCRIPTION, self.__placeExit.idSound),
                                             data=self.__placeExit.idSound)

    def renderSelectionLine(self, surface: Surface):
        drawRectangle(surface, TreeGroupExit.COLOR_LINE, Rect(self.__placeExit.bounding.x, self.__placeExit.bounding.y, self.__placeExit.bounding.width, self.__placeExit.bounding.height), width=3)

    @staticmethod
    def fromPlaceData(data : Exit) -> TreeGroupExit:
        output = TreeGroupExit()
        output.__placeExit = data
        return output