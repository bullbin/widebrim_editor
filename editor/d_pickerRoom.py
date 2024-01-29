from typing import Optional
from editor.asset_management.room import PlaceGroup, getPlaceGroups
from editor.gen_editor import PickerEvent
from wx import Window, ID_OK, ID_CANCEL, TreeItemId
from widebrim.engine.state.manager.state import Layton2GameState

class DialogSelectRoom(PickerEvent):
    def __init__(self, parent : Window, state : Layton2GameState, defaultRoomIndex : Optional[int] = None):
        super().__init__(parent)
        self.btnConfirmSelected.SetLabel("Use selected room")
        self._state = state
        self.btnConfirmSelected.Disable()

        placeGroups = getPlaceGroups(state.getFileAccessor())
        self._treeItemPlace = self.treeEvent.AddRoot("Rooms")
        for group in placeGroups:
            self.treeEvent.AppendItem(self._treeItemPlace, "Room " + str(group.indexPlace), data=group)
        
        self._idSelected : Optional[PlaceGroup] = None
        self._lastGoodItem : Optional[TreeItemId] = None

        if defaultRoomIndex != None:
            self._switchPreview(defaultRoomIndex)
    
    def GetSelection(self) -> Optional[int]:
        if self._idSelected != None:
            return self._idSelected.indexPlace
        return self._idSelected
    
    def _switchPreviewByRoomItem(self, item : TreeItemId):
        self._idSelected = self.treeEvent.GetItemData(item)
        self._lastGoodItem = item
        self.btnConfirmSelected.SetLabel("Use Room %i" % self._idSelected.indexPlace)
        self.btnConfirmSelected.Enable()

    def _switchPreview(self, idRoom : int):
        child, _cookie = self.treeEvent.GetFirstChild(self._treeItemPlace)
        child : TreeItemId
        while child.IsOk():
            if (data := self.treeEvent.GetItemData(child)) != None:
                data : PlaceGroup
                if data.indexPlace == idRoom:
                    self._switchPreviewByRoomItem(child)
                    return
            child = self.treeEvent.GetNextSibling(child)
    
    def treeEventOnTreeSelChanged(self, event):
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if not(self.treeEvent):
            return super().treeEventOnTreeSelChanged(event)

        item = event.GetItem()
        if item == self._lastGoodItem:
            return super().treeEventOnTreeSelChanged(event)
        else:
            self._switchPreviewByRoomItem(item)
        return super().treeEventOnTreeSelChanged(event)

    def btnConfirmSelectedOnButtonClick(self, event):
        self.EndModal(ID_OK)
        return super().btnConfirmSelectedOnButtonClick(event)
    
    def btnCancelOnButtonClick(self, event):
        self.EndModal(ID_CANCEL)
        return super().btnCancelOnButtonClick(event)
