from typing import List, Optional
from editor.asset_management.puzzle import PuzzleEntry, getPuzzles
from editor.gen_editor import PickerEvent
from wx import Window, ID_OK, ID_CANCEL, TreeItemId
from widebrim.engine.state.manager.state import Layton2GameState

class DialogSelectPuzzle(PickerEvent):
    def __init__(self, parent : Window, state : Layton2GameState, defaultPuzzleIndex : Optional[int] = None):
        super().__init__(parent)
        self.btnConfirmSelected.SetLabel("Use selected room")
        self._state = state
        self.btnConfirmSelected.Disable()

        rootItem = self.treeEvent.AddRoot("You shouldn't see this!")

        puzzleItem = self.treeEvent.AppendItem(rootItem, "Puzzles")
        normalItem = self.treeEvent.AppendItem(puzzleItem, "Standard")
        wifiItem = self.treeEvent.AppendItem(puzzleItem, "WiFi")
        specialItem = self.treeEvent.AppendItem(puzzleItem, "Special")

        self._puzzles = getPuzzles(self._state)
            
        def fillPuzzleBranch(root, entryList : List[PuzzleEntry]):

            def getKey(entry : PuzzleEntry):
                return entry.idExternal

            entryList.sort(key=getKey)
            for entry in entryList:
                name = "%03i - %s" % (entry.idExternal, entry.name)
                self.treeEvent.AppendItem(root, name, data=entry.idInternal)
        
        fillPuzzleBranch(normalItem, self._puzzles[0])
        fillPuzzleBranch(wifiItem, self._puzzles[1])
        fillPuzzleBranch(specialItem, self._puzzles[2])
        
        self._idSelected : Optional[int] = None
        self._lastGoodItem : Optional[TreeItemId] = None

        if defaultPuzzleIndex != None:
            self._switchPreview(defaultPuzzleIndex)
    
    def GetSelection(self) -> Optional[int]:
        return self._idSelected
    
    def _switchPreviewByPuzzleItem(self, item : TreeItemId):
        if self.treeEvent.GetItemData(item) != None:
            self._idSelected = self.treeEvent.GetItemData(item)
            self._lastGoodItem = item
            self.btnConfirmSelected.SetLabel("Use " + self.treeEvent.GetItemText(item))
            self.btnConfirmSelected.Enable()

    def _switchPreview(self, idPuzzle : int):

        def exploreBranch(branchRoot : TreeItemId):
            if self.treeEvent.GetItemData(branchRoot) == idPuzzle:
                return branchRoot
            else:
                child, _cookie = self.treeEvent.GetFirstChild(branchRoot)
                while child.IsOk():
                    if self.treeEvent.GetChildrenCount(child, False) > 0:
                        if (output := exploreBranch(child)) != None:
                            return output
                    if self.treeEvent.GetItemData(child) == idPuzzle:
                        return child
                    child = self.treeEvent.GetNextSibling(child)
                return None

        item = exploreBranch(self.treeEvent.GetRootItem())
        if item != None:
            self._switchPreviewByPuzzleItem(item)
    
    def treeEventOnTreeSelChanged(self, event):
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if not(self.treeEvent):
            return super().treeEventOnTreeSelChanged(event)

        item = event.GetItem()
        if item == self._lastGoodItem:
            return super().treeEventOnTreeSelChanged(event)
        else:
            self._switchPreviewByPuzzleItem(item)
        return super().treeEventOnTreeSelChanged(event)

    def btnConfirmSelectedOnButtonClick(self, event):
        self.EndModal(ID_OK)
        return super().btnConfirmSelectedOnButtonClick(event)
    
    def btnCancelOnButtonClick(self, event):
        self.EndModal(ID_CANCEL)
        return super().btnCancelOnButtonClick(event)
