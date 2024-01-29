from typing import Dict, Optional
from .gen_editor import PickerMultipleChoice
from wx import ID_CANCEL, ID_OK

class DialogMultipleChoice(PickerMultipleChoice):
    def __init__(self, parent, choicesDict : Dict[str, str], newTitle : Optional[str] = None):
        super().__init__(parent)
        if newTitle != None:
            self.SetTitle(newTitle)

        self.textOperandDescription.Clear()   
        self._choices = choicesDict
        self._choicesKeys = list(choicesDict.keys())
        self.choiceOperand.Set(self._choicesKeys)
        
        if len(self._choicesKeys) > 0:
            self.SetSelection(self._choicesKeys[0])
        else:
            self.btnAgree.Disable()
    
    def GetSelection(self) -> Optional[str]:
        if len(self._choicesKeys) > 0:
            return self._choicesKeys[self.choiceOperand.GetSelection()]
        return None
    
    def SetSelection(self, string):
        try:
            indexValue = self._choicesKeys.index(string)
        except ValueError:
            indexValue = 0
        
        if len(self._choicesKeys) > 0:
            self.textOperandDescription.SetValue(self._choices[self._choicesKeys[indexValue]])
            self.choiceOperand.SetSelection(indexValue)

    def choiceOperandOnChoice(self, event):
        selection = self.choiceOperand.GetSelection()
        description = self._choices[self._choicesKeys[selection]]
        self.textOperandDescription.SetValue(description)
        return super().choiceOperandOnChoice(event)
    
    def btnCancelOnButtonClick(self, event):
        self.EndModal(ID_CANCEL)
        return super().btnCancelOnButtonClick(event)
    
    def btnAgreeOnButtonClick(self, event):
        self.EndModal(ID_OK)
        return super().btnAgreeOnButtonClick(event)