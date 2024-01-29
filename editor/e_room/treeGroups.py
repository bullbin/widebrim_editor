from __future__ import annotations
from typing import Dict, List, Optional

from editor.d_operandMultichoice import DialogMultipleChoice
from ..d_pickerEvent import DialogEvent
from editor.d_pickerRoom import DialogSelectRoom
from editor.e_room.modifiers import modifyBoundary, modifyEventSelection, modifySpriteBoundary, modifySpritePath, modifySpritePosition
from editor.e_room.utils import blitBoundingAlphaFill, blitBoundingLine, getShortenedString
from widebrim.engine.const import PATH_EXT_EVENT, PATH_EXT_EXIT
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.gamemodes.room.const import PATH_ANIM_BGANI, PATH_FILE_HINTCOIN, PATH_FILE_TOBJ, PATH_PACK_TOBJ
from widebrim.madhatter.common import logSevere
from widebrim.madhatter.hat_io.asset_dat.place import BgAni, EventEntry, Exit, PlaceData, TObjEntry, HintCoin
from wx import TreeCtrl, TreeItemId, ID_OK
from pygame import Surface
from pygame.draw import circle as drawCircle

# TODO - Linting and docstrings

def _getMapString(bank : Dict[int, str], id : int) -> str:
    if id in bank:
        return bank[id]
    return "Undefined (%i)" % id

class RefreshInformation():
    def __init__(self, fullTreeRefresh = False, backgroundRefresh = False):
        self.fullTreeRefresh = fullTreeRefresh
        self.backgroundRefresh = backgroundRefresh

class TreeObjectPlaceData():

    def __init__(self):
        self._treeRoot : Optional[TreeItemId] = None
        self.__isModified = False
        self.__nameStr = ""
    
    def isModifiable(self, selectedId):
        if self._treeRoot != None:
            return selectedId != self._treeRoot
        return False

    def _createRootItem(self, treeCtrl : TreeCtrl, branchRoot : TreeItemId, name : str, index : Optional[int] = None):
        self.__nameStr = name
        if index == None:
            self._treeRoot = treeCtrl.AppendItem(branchRoot, "New " + name)
        else:
            self._treeRoot = treeCtrl.AppendItem(branchRoot, "%s %i" % (name, (index + 1)))

    def setNameIndex(self, treeCtrl : TreeCtrl, index : int):
        if self.isValid():
            treeCtrl.SetItemText(self._treeRoot, "%s %i" % (self.__nameStr, (index + 1)))

    def isValid(self) -> bool:
        if self._treeRoot != None:
            return self._treeRoot.IsOk()
        return False

    def renderSelectionLine(self, surface : Surface, overrideWidth : Optional[int] = None):
        """Render this group as a selection boundary on a surface.

        Args:
            surface (Surface): pygame Surface for rendering.
        """
        pass
    
    def renderSelectionAlphaFill(self, surface : Surface, alpha : int = 120):
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
    
    def modifyItem(self, state : Layton2GameState, treeCtrl : TreeCtrl, selectedId : TreeItemId, parent, previewImage : Surface, foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        return RefreshInformation()
    
    def modifyAllItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, selectedId : TreeItemId, parent, previewImage : Surface, otherPlaceData : List[PlaceData], foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        """Modify all place data items sharing an equivalent entry to that of which this object is controlling. Note that this modifies data and may break references.

        Args:
            state (Layton2GameState): _description_
            treeCtrl (TreeCtrl): _description_
            selectedId (TreeItemId): _description_
            parent (_type_): _description_
            previewImage (Surface): _description_
            otherPlaceData (List[PlaceData]): List of all place datas for this control to affect. The place data relevant to the current control should be at index 0.

        Returns:
            RefreshInformation: _description_
        """
        return self.modifyItem(state, treeCtrl, selectedId, parent, previewImage, foregroundImage=foregroundImage)
    
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

    def renderSelectionLine(self, surface: Surface, overrideWidth : Optional[int] = None):
        if overrideWidth != None:
            blitBoundingLine(surface, self.__tObj.bounding, TreeGroupTObj.COLOR_LINE, width=overrideWidth)
        else:
            blitBoundingLine(surface, self.__tObj.bounding, TreeGroupTObj.COLOR_LINE)

    def renderSelectionAlphaFill(self, surface: Surface, alpha : int = 120):
        blitBoundingAlphaFill(surface, self.__tObj.bounding, TreeGroupTObj.COLOR_LINE, alpha=alpha)

    def __getTObjText(self, state : Layton2GameState):
        if self.__tObj.idTObj != -1:
            return state.getFileAccessor().getPackedString(PATH_PACK_TOBJ % state.language.value, PATH_FILE_TOBJ % self.__tObj.idTObj)
        return state.getFileAccessor().getPackedString(PATH_PACK_TOBJ % state.language.value, PATH_FILE_HINTCOIN)

    def modifyItem(self, state: Layton2GameState, treeCtrl : TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, foregroundImage : Optional[Surface] = None) -> RefreshInformation:
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
            elif selectedId == self.itemBounding:
                changed = modifyBoundary(parent, state, previewImage, self.__tObj.bounding, color=TreeGroupTObj.COLOR_LINE, foreground=foregroundImage)
                return RefreshInformation(backgroundRefresh=changed)

        return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)

    def modifyAllItems(self, state: Layton2GameState, treeCtrl: TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, otherPlaceData: List[PlaceData], foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        mismatchFound = False
        similarEntries : List[TObjEntry] = []
        for placeData in otherPlaceData[1:]:
            foundForData = False
            for indexTObj in range(placeData.getCountObjText()):
                tObjEntry = placeData.getObjText(indexTObj)
                if tObjEntry == self.__tObj:
                    similarEntries.append(tObjEntry)
                    foundForData = True
                    break
            
            if not(foundForData):
                mismatchFound = True
            
        # TODO - Error on mismatch
        if mismatchFound:
            logSevere("Mismatch trying to solve for identical TObj!")
        
        output = self.modifyItem(state, treeCtrl, selectedId, parent, previewImage, foregroundImage=foregroundImage)
        for entry in similarEntries:
            entry.idChar = self.__tObj.idChar
            entry.idTObj = self.__tObj.idTObj
            entry.bounding.cloneInto(self.__tObj.bounding)
        return output

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
            return selectedId == self._treeRoot or selectedId == self.itemBounding or selectedId == self.itemChar or selectedId == self.itemComment
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
            return selectedId == self._treeRoot or selectedId == self.itemBounding or selectedId == self.itemImage or selectedId == self.itemIdEvent
        return False

    def modifyItem(self, state: Layton2GameState, treeCtrl : TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        if selectedId == self.itemBounding:
            changed = modifySpriteBoundary(parent, state, previewImage, self.__eventEntry.bounding, TreeGroupEventSpawner.COLOR_LINE,
                                           (PATH_EXT_EVENT % (self.__eventEntry.idImage & 0xff)), foreground=foregroundImage)
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
        elif selectedId == self.itemIdEvent:
            self.__eventEntry.idEvent = modifyEventSelection(parent, state, self.__eventEntry.idEvent)
            treeCtrl.SetItemText(self.itemIdEvent, "Event: %i" % self.__eventEntry.idEvent)
            treeCtrl.SetItemData(self.itemIdEvent, self.__eventEntry.idEvent)
            return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)
        else:
            return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)

    def modifyAllItems(self, state: Layton2GameState, treeCtrl: TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, otherPlaceData: List[PlaceData], foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        mismatchFound = False
        similarEntries : List[EventEntry] = []
        for placeData in otherPlaceData[1:]:
            foundForData = False
            for indexEvent in range(placeData.getCountObjEvents()):
                eventEntry = placeData.getObjEvent(indexEvent)
                if eventEntry == self.__eventEntry:
                    similarEntries.append(eventEntry)
                    foundForData = True
                    break
            
            if not(foundForData):
                mismatchFound = True
            
        # TODO - Error on mismatch
        if mismatchFound:
            logSevere("Mismatch trying to solve for identical event spawners!")

        output = self.modifyItem(state, treeCtrl, selectedId, parent, previewImage, foregroundImage=foregroundImage)
        for entry in similarEntries:
            entry.bounding.cloneInto(self.__eventEntry.bounding)
            entry.idEvent = self.__eventEntry.idEvent
            entry.idImage = self.__eventEntry.idImage
        return output

    def renderSelectionLine(self, surface: Surface, overrideWidth : Optional[int] = None):
        if overrideWidth == None:
            blitBoundingLine(surface, self.__eventEntry.bounding, TreeGroupEventSpawner.COLOR_LINE)
        else:
            blitBoundingLine(surface, self.__eventEntry.bounding, TreeGroupEventSpawner.COLOR_LINE, width=overrideWidth)

    def renderSelectionAlphaFill(self, surface: Surface, alpha : int = 120):
        blitBoundingAlphaFill(surface, self.__eventEntry.bounding, TreeGroupEventSpawner.COLOR_LINE, alpha=alpha)

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
    
    def renderSelectionLine(self, surface: Surface, overrideWidth : Optional[int] = None):
        if overrideWidth == None:
            blitBoundingLine(surface, self.__hintEntry.bounding, TreeGroupHintCoin.COLOR_LINE)
        else:
            blitBoundingLine(surface, self.__hintEntry.bounding, TreeGroupHintCoin.COLOR_LINE, width=overrideWidth)

    def renderSelectionAlphaFill(self, surface: Surface, alpha : int = 120):
        blitBoundingAlphaFill(surface, self.__hintEntry.bounding, TreeGroupHintCoin.COLOR_LINE, alpha=alpha)

    def isItemSelected(self, selectedId: TreeItemId) -> bool:
        if self._treeRoot != None:
            return selectedId == self._treeRoot or selectedId == self.itemBounding
        return False

    def modifyItem(self, state: Layton2GameState, treeCtrl : TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        if self._treeRoot != None:
            if selectedId == self.itemBounding:
                changed = modifyBoundary(parent, state, previewImage, self.__hintEntry.bounding, color=TreeGroupHintCoin.COLOR_LINE, foreground=foregroundImage)
                return RefreshInformation(backgroundRefresh=changed)
        return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)
    
    def modifyAllItems(self, state: Layton2GameState, treeCtrl: TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, otherPlaceData: List[PlaceData], foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        # Get original hint index
        indexHintData = 0
        for indexHint in range(otherPlaceData[0].getCountHintCoin()):
            hint = otherPlaceData[0].getObjHintCoin(indexHint)
            if hint == self.__hintEntry:
                indexHintData = indexHint
                break
        
        mismatchHintCount = False
        modifyEntries : List[HintCoin] = []
        for placeData in otherPlaceData[1:]:
            if placeData.getCountHintCoin() > indexHintData:
                modifyEntries.append(placeData.getObjHintCoin(indexHintData))
            else:
                mismatchHintCount = True

        # TODO - Warn on mismatch count
        if mismatchHintCount:
            logSevere("Mismatch trying to solve for identical hint coins!")

        output = self.modifyItem(state, treeCtrl, selectedId, parent, previewImage, foregroundImage=foregroundImage)
        for entry in modifyEntries:
            entry.bounding.cloneInto(self.__hintEntry.bounding)

        return output

    @staticmethod
    def fromPlaceData(data : HintCoin) -> TreeGroupHintCoin:
        output = TreeGroupHintCoin()
        output.__hintEntry = data
        return output

class TreeGroupBackgroundAnimation(TreeObjectPlaceData):

    COLOR_LINE = (127,63,127)

    def __init__(self):
        super().__init__()
        self.__bgAniEntry   : BgAni = BgAni()
        self.itemPos        : Optional[TreeItemId] = None
        self.itemBgPath     : Optional[TreeItemId] = None

    def isItemSelected(self, selectedId: TreeItemId) -> bool:
        if self._treeRoot != None:
            return selectedId == self._treeRoot or selectedId == self.itemPos or selectedId == self.itemBgPath
        return False

    def modifyItem(self, state: Layton2GameState, treeCtrl: TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        if selectedId == self.itemPos:
            oldPos = self.__bgAniEntry.pos
            newPos = modifySpritePosition(parent, state, previewImage, PATH_ANIM_BGANI % self.__bgAniEntry.name, oldPos, foreground=foregroundImage, color=TreeGroupBackgroundAnimation.COLOR_LINE)
            treeCtrl.SetItemData(selectedId, newPos)
            if newPos != oldPos:
                self.__bgAniEntry.pos = newPos
                return RefreshInformation(backgroundRefresh=True)
            return RefreshInformation(backgroundRefresh=False)
        elif selectedId == self.itemBgPath:
            oldPath = self.__bgAniEntry.name
            outPath = modifySpritePath(parent, state, oldPath,
                                       pathRoot = "/data_lt2/ani/bgani", reMatchString="/data_lt2/ani/bgani/(.+).arc")
            newPath = outPath + ".spr"
            self.__bgAniEntry.name = newPath
            treeCtrl.SetItemData(self.itemBgPath, newPath)
            treeCtrl.SetItemText(self.itemBgPath, "Image: %s" % (PATH_ANIM_BGANI % newPath))
            if newPath != oldPath:
                return RefreshInformation(backgroundRefresh=True)
            else:
                return RefreshInformation(backgroundRefresh=False)
        return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)

    def modifyAllItems(self, state: Layton2GameState, treeCtrl: TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, otherPlaceData: List[PlaceData], foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        mismatchFound = False
        similarEntries : List[BgAni] = []
        for placeData in otherPlaceData[1:]:
            foundForEntry = False
            for indexBgAni in range(placeData.getCountObjBgEvent()):
                bgAni = placeData.getObjBgEvent(indexBgAni)
                if bgAni == self.__bgAniEntry:
                    foundForEntry = True
                    similarEntries.append(bgAni)
                    break
            if not(foundForEntry):
                mismatchFound = True

        # TODO - Warning on mismatch
        if mismatchFound:
            logSevere("Mismatch trying to solve for identical BG Ani entries!")

        output = self.modifyItem(state, treeCtrl, selectedId, parent, previewImage, foregroundImage=foregroundImage)
        for entry in similarEntries:
            entry.name = self.__bgAniEntry.name
            entry.pos = self.__bgAniEntry.pos
        return output

    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):
        self._createRootItem(treeCtrl, branchRoot, "Background Animation", index)
        self.itemBgPath = treeCtrl.AppendItem(self._treeRoot, "Image: %s" % (PATH_ANIM_BGANI % self.__bgAniEntry.name), data=self.__bgAniEntry.name)
        self.itemPos = treeCtrl.AppendItem(self._treeRoot, "Edit animation position...", data=self.__bgAniEntry.pos)
    
    def renderSelectionLine(self, surface: Surface, overrideWidth : Optional[int] = None):
        # TODO - Get BG anim dimensions
        drawCircle(surface, TreeGroupBackgroundAnimation.COLOR_LINE, self.__bgAniEntry.pos, radius=3, width=2)
    
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
            return selectedId in [self._treeRoot, self.itemBounding, self.itemSound, self.itemPosTransition, self.itemArrowImage, self.itemExitType, self.itemExitTermination]
        return super().isItemSelected(selectedId)

    def modifyItem(self, state: Layton2GameState, treeCtrl: TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, foregroundImage : Optional[Surface] = None) -> RefreshInformation:

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
                changed = modifySpriteBoundary(parent, state, previewImage, self.__placeExit.bounding, TreeGroupExit.COLOR_LINE,
                                               PATH_EXT_EXIT % self.__placeExit.idImage, foreground=foregroundImage)
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
                self.__placeExit.idImage = treeCtrl.GetItemData(self.itemArrowImage)
                return RefreshInformation(backgroundRefresh=True)
            
            elif selectedId == self.itemSound:
                mapNoiseToComments : Dict[int, str] = {2:"No noise will be made. This is ignored if using this exit spawns an event.",
                                                       0:"Default footsteps walking sound. This is ignored if using this exit spawns an event.",
                                                       1:"Wooden door creaking noise. This is ignored if using this exit spawns an event.",
                                                       3:"Wooden door creaking noise (duplicate). This is ignored if using this exit spawns an event.",
                                                       4:"Loud metallic sliding door noise. This is ignored if using this exit spawns an event."}
                changed = doMultipleChoiceDialogFromKeyBank(mapNoiseToComments, TreeGroupExit.MAP_NOISE_DESCRIPTION, "Change Sound",
                                                            self.__placeExit.idSound, "Sound: %s")
                self.__placeExit.idSound = treeCtrl.GetItemData(self.itemSound)
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
                        if dlg.GetSelection() == "Room":
                            extraDatDlg = DialogSelectRoom(parent, state, self.__placeExit.spawnData)
                            if extraDatDlg.ShowModal() == ID_OK:
                                self.__placeExit.spawnData = extraDatDlg.GetSelection()
                                treeCtrl.SetItemText(self.itemExitTermination, "Destination: Room %i" % self.__placeExit.spawnData)
                            else:
                                return RefreshInformation()

                        elif dlg.GetSelection() == "Event":
                            extraDatDlg = DialogEvent(parent, state, self.__placeExit.spawnData)
                            if extraDatDlg.ShowModal() == ID_OK:
                                self.__placeExit.spawnData = extraDatDlg.GetSelection()
                                treeCtrl.SetItemText(self.itemExitTermination, "Destination: Event %i" % self.__placeExit.spawnData)
                            else:
                                return RefreshInformation()

                        if self.__placeExit.canSpawnEvent():
                            if not(dlg.GetSelection() == "Event"):
                                # Need to update, since we're still setup for spawning events
                                self.__placeExit.modeDecoding = 0
                                treeCtrl.SetItemText(self.itemExitType, "Exit Type: %s" % _getMapString(TreeGroupExit.MAP_TYPE_TO_OPTIONS, self.__placeExit.modeDecoding))
                                
                        else:
                            if not(dlg.GetSelection() == "Room"):
                                # Need to update, since we're still setup for spawning rooms
                                self.__placeExit.modeDecoding = 2
                                treeCtrl.SetItemText(self.itemExitType, "Exit Type: %s" % _getMapString(TreeGroupExit.MAP_TYPE_TO_OPTIONS, self.__placeExit.modeDecoding))
                                # TODO - Update sound to silent

                        treeCtrl.SetItemData(self.itemExitType, self.__placeExit.modeDecoding)
                        treeCtrl.SetItemData(self.itemExitTermination, self.__placeExit.spawnData)
                        return RefreshInformation(backgroundRefresh=True)
                    return RefreshInformation()
            
            elif selectedId == self.itemExitType:
                if self.__placeExit.canSpawnEvent():
                    pass
                pass

            elif selectedId == self.itemPosTransition:
                pass
                        
        return super().modifyItem(state, treeCtrl, selectedId, parent, previewImage)

    def modifyAllItems(self, state: Layton2GameState, treeCtrl: TreeCtrl, selectedId: TreeItemId, parent, previewImage : Surface, otherPlaceData: List[PlaceData], foregroundImage : Optional[Surface] = None) -> RefreshInformation:
        
        mismatchFound = False
        similarEntries : List[Exit] = []
        for placeData in otherPlaceData[1:]:
            foundForData = False
            for indexExit in range(placeData.getCountExits()):
                exitEntry = placeData.getExit(indexExit)
                if exitEntry == self.__placeExit:
                    similarEntries.append(exitEntry)
                    foundForData = True
                    break
            
            if not(foundForData):
                mismatchFound = True
            
        # TODO - Error on mismatch
        if mismatchFound:
            logSevere("Mismatch trying to solve for identical exits!")

        output = self.modifyItem(state, treeCtrl, selectedId, parent, previewImage, foregroundImage=foregroundImage)
        for entry in similarEntries:
            entry.bounding.cloneInto(self.__placeExit.bounding)
            entry.idImage = self.__placeExit.idImage
            entry.idSound = self.__placeExit.idSound
            entry.posTransition = self.__placeExit.posTransition
            entry.modeDecoding = self.__placeExit.modeDecoding
            entry.spawnData = self.__placeExit.spawnData

        return output

    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):

        self._createRootItem(treeCtrl, branchRoot, "Exit", index)
        self.itemBounding = treeCtrl.AppendItem(self._treeRoot, "Edit interaction area...", data=self.__placeExit.bounding)
        self.itemPosTransition = treeCtrl.AppendItem(self._treeRoot, "Edit map pinpoint destination...", data=self.__placeExit.posTransition)
        self.itemArrowImage = treeCtrl.AppendItem(self._treeRoot, "Exit Image: %s" % _getMapString(TreeGroupExit.MAP_ID_TO_IMAGE_DESCRIPTION, self.__placeExit.idImage),
                                                  data=self.__placeExit.idImage)
        self.itemExitType = treeCtrl.AppendItem(self._treeRoot, "Exit Type: %s" % _getMapString(TreeGroupExit.MAP_TYPE_TO_OPTIONS, self.__placeExit.modeDecoding),
                                                  data=self.__placeExit.modeDecoding)
        
        if self.__placeExit.canSpawnEvent():
            self.itemExitTermination = treeCtrl.AppendItem(self._treeRoot, "Destination: Event %i" % self.__placeExit.spawnData,
                                                           data=self.__placeExit.spawnData)
        else:
            self.itemExitTermination = treeCtrl.AppendItem(self._treeRoot, "Destination: Room %i" % self.__placeExit.spawnData,
                                                           data=self.__placeExit.spawnData)

        self.itemSound = treeCtrl.AppendItem(self._treeRoot, "Sound: %s" % _getMapString(TreeGroupExit.MAP_NOISE_DESCRIPTION, self.__placeExit.idSound),
                                             data=self.__placeExit.idSound)

    def renderSelectionLine(self, surface: Surface, overrideWidth : Optional[int] = None):
        if overrideWidth == None:
            blitBoundingLine(surface, self.__placeExit.bounding, TreeGroupExit.COLOR_LINE)
        else:
            blitBoundingLine(surface, self.__placeExit.bounding, TreeGroupExit.COLOR_LINE, width=overrideWidth)

    def renderSelectionAlphaFill(self, surface: Surface, alpha : int = 120):
        blitBoundingAlphaFill(surface, self.__placeExit.bounding, TreeGroupExit.COLOR_LINE, alpha=alpha)

    @staticmethod
    def fromPlaceData(data : Exit) -> TreeGroupExit:
        output = TreeGroupExit()
        output.__placeExit = data
        return output