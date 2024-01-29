from typing import Optional
from editor.branch_management.branch_chapter.branch_chapter import ChapterBranchManager
from widebrim.engine.state.manager.state import Layton2GameState
from .gen_editor import PickerNode
from wx import Window, ID_OK, ID_CANCEL

class DialogSelectChapter(PickerNode):
    def __init__(self, parent : Window, state : Layton2GameState, defaultChapter : Optional[int] = None, title : Optional[str] = None):
        super().__init__(parent)
        self._managerChapter = ChapterBranchManager(state, self.treeData, True)
        rootItem = self.treeData.AddRoot("You shouldn't see this!")
        self._managerChapter.createTreeBranches(rootItem)
        self.btnConfirmSelected.Disable()

        self._lastSelected : Optional[int] = None

        if title != None:
            self.SetTitle(title)
        if defaultChapter != None:
            self.setChapterSelection(defaultChapter)
            if self._lastSelected != None:
                self.treeData.SelectItem(self._managerChapter.getCorrespondingItem(self._lastSelected))
        
    def setChapterSelection(self, chapter : int):
        selection = self._managerChapter.getCorrespondingItem(chapter)
        if selection != None:
            if chapter != self._lastSelected:
                self._lastSelected = chapter

                if not(self.btnConfirmSelected.IsEnabled()):
                    self.textActiveSelection.Enable()
                    self.btnConfirmSelected.Enable()

                self.textActiveSelection.SetLabelText("Chapter %i" % chapter)

    def treeDataOnTreeSelChanged(self, event):
        if self.treeData:
            chapter = self._managerChapter.getCorrespondingChapter(self.treeData.GetSelection())
            if chapter != None:
                self.setChapterSelection(chapter)
        return super().treeDataOnTreeSelChanged(event)

    def GetSelection(self) -> Optional[int]:
        return self._lastSelected
    
    def btnConfirmSelectedOnButtonClick(self, event):
        self.EndModal(ID_OK)
        return super().btnConfirmSelectedOnButtonClick(event)
    
    def btnCancelOnButtonClick(self, event):
        self.EndModal(ID_CANCEL)
        return super().btnCancelOnButtonClick(event)
