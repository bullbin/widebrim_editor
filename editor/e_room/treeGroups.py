from __future__ import annotations
from typing import Optional
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.gamemodes.room.const import PATH_FILE_HINTCOIN, PATH_FILE_TOBJ, PATH_PACK_TOBJ
from widebrim.madhatter.hat_io.asset_dat.place import TObjEntry
from wx import TreeCtrl, TreeItemId
from pygame import Surface

class TreeObjectPlaceData():
    def __init__(self):
        self._treeRoot : Optional[TreeItemId] = None
    
    def isValid(self) -> bool:
        return False
    
    def renderSelectionLine(self, surface : Surface):
        pass
    
    def renderSelectionAlphaFill(self, surface : Surface):
        pass
    
    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):
        pass

    def deleteTreeItems(self, treeCtrl : TreeCtrl):
        if self._treeRoot != None:
            treeCtrl.DeleteChildren(self._treeRoot)
            treeCtrl.Delete(self._treeRoot)
    
    def isItemSelected(self, selectedId : TreeItemId) -> bool:
        return False
    
    @staticmethod
    def fromPlaceData(data) -> TreeObjectPlaceData:
        return TreeObjectPlaceData()

class TreeGroupTObj(TreeObjectPlaceData):
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

    def __getTObjText(self, state : Layton2GameState):
        if self.__tObj.idTObj != -1:
            return state.getFileAccessor().getPackedString(PATH_PACK_TOBJ % state.language.value, PATH_FILE_TOBJ % self.__tObj.idTObj)
        return state.getFileAccessor().getPackedString(PATH_PACK_TOBJ % state.language.value, PATH_FILE_HINTCOIN)

    def createTreeItems(self, state : Layton2GameState, treeCtrl : TreeCtrl, branchRoot : TreeItemId, index : Optional[int] = None):

        def getMinSmallest(text : str, minChars=48, extra="(...)", addSpace=True):
            text = " ".join(text.split("\n"))
            if len(text) <= minChars:
                return text
            else:
                if addSpace:
                    extra = " " + extra

                text = text[:minChars - len(extra)]

                # Rewind to space before last cutoff word
                while len(text) > 0 and text[-1] != " ":
                    text = text[:-1]

                # Rewind to word before spaces
                while len(text) > 0 and text[-1] == " ":
                    text = text[:-1]

                text = text + extra
                if addSpace:
                    checkLen = len(extra) + 1
                    if len(text) >= checkLen:
                        if text[-checkLen] == " ":
                            return text[:-checkLen] + extra[1:]

                return text

        if index == None:
            self._treeRoot = treeCtrl.AppendItem(branchRoot, "New Comment")
        else:
            self._treeRoot = treeCtrl.AppendItem(branchRoot, "Comment %i" % (index + 1))
        
        self.itemComment = treeCtrl.AppendItem(self._treeRoot, '"%s"' % getMinSmallest(self.__getTObjText(state)), data=self.__tObj.idTObj)

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

class TreeGroupBgAni(TreeObjectPlaceData):
    pass