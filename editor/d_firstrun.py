from .nopush_editor import FirstRunWarning
from wx import ID_OK, ID_ABORT

# TODO - Only allow input once fully scrolled

class DialogFirstRunWarning(FirstRunWarning):
    def __init__(self, parent):
        super().__init__(parent)
    
    def buttonAgreeOnButtonClick(self, event):
        if self.IsModal():
            self.EndModal(ID_OK)
        else:
            self.Close()
        return super().buttonAgreeOnButtonClick(event)
    
    def buttonDisagreeOnButtonClick(self, event):
        if self.IsModal():
            self.EndModal(ID_ABORT)
        else:
            self.Close()
        return super().buttonDisagreeOnButtonClick(event)