from typing import Optional
from editor.asset_management.event import getEvents
from editor.branch_management import EventBranchManager
from widebrim.engine.state.manager.state import Layton2GameState
from .nopush_editor import PickerEvent
from wx import MessageDialog, YES_NO, ID_YES, ID_OK, ID_CANCEL, TreeItemId

# TODO - Improve warnings. Behaviour is known for all event types, enforce it

class DialogEvent(PickerEvent):
    def __init__(self, parent, state : Layton2GameState, lastSelected : Optional[int] = None):
        super().__init__(parent)
        self._eventManager = EventBranchManager(state, self.treeEvent, hideEditControls=True)
        root = self.treeEvent.AddRoot("You shouldn't see this!")
        self._eventManager.createTreeBranches(root, getEvents(state.getFileAccessor(), state))
        
        # TODO - Default selection (requires event manager changes)
        self.btnConfirmSelected.Disable()
        self._idSelected : Optional[int] = lastSelected
        self._lastGoodItem : Optional[TreeItemId] = None
    
    def GetSelection(self) -> int:
        return self._idSelected

    def _switchPreview(self, idEvent : int):
        self._idSelected = idEvent
        self._lastGoodItem = self.treeEvent.GetSelection()
        self.btnConfirmSelected.Enable()

    def _isEventSafe(self, idEvent : int):
        if idEvent in self._eventManager.getTrackedEvents():
            return True
        if idEvent in self._eventManager.getUntrackedEvents():
            return True
        
        for group in self._eventManager.getBranchedEventGroups():
            if idEvent == group.group[0]:
                return True
        return False

    def treeEventOnTreeSelChanged(self, event):
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if not(self.treeEvent):
            return super().treeEventOnTreeSelChanged(event)

        item = event.GetItem()
        if item == self._lastGoodItem:
            return super().treeEventOnTreeSelChanged(event)

        response = self._eventManager.getCorrespondingActivatedItem(item)
        if response.isNothing:
            return super().treeEventOnTreeSelChanged(event)
        elif response.isEvent:
            
            if self.checkConditionalWarning.IsChecked():
                if self._isEventSafe(response.getEventId()):
                    self._switchPreview(response.getEventId())
                else:
                    dlg = MessageDialog(self, """Jumping to this event may cause unintended playback problems. Are you sure you want to select this event?\n\nBecause this event relies on conditional behaviour, playing back this event may cause unintended problems. It is recommended to choose the topmost event for a conditional branch instead.""",
                    caption="Event not Recommended", style=YES_NO).ShowModal()
                    if dlg == ID_YES:
                        self._switchPreview(response.getEventId())
                    else:
                        if self._lastGoodItem != None:
                            self.treeEvent.SelectItem(self._lastGoodItem)
            else:
                self._switchPreview(response.getEventId())
        return super().treeEventOnTreeSelChanged(event)
    
    def btnConfirmSelectedOnButtonClick(self, event):
        self.EndModal(ID_OK)
        return super().btnConfirmSelectedOnButtonClick(event)
    
    def btnCancelOnButtonClick(self, event):
        self.EndModal(ID_CANCEL)
        return super().btnCancelOnButtonClick(event)