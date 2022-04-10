from editor.nopush_editor import editorDrawInput

import wx
from widebrim.madhatter.hat_io.asset_dat.nazo import NazoData

from widebrim.madhatter.hat_io.asset_script import GdScript

HANDLER_TO_INDEX = {35:4,
                    32:3,
                    28:2,
                    16:0}
INDEX_TO_HANDLER = {4:35,
                    3:32,
                    2:28,
                    0:16}
HANDLER_TO_LENGTH = {35:4,
                     32:3,
                     28:2}

class DrawInputEditor(editorDrawInput):
    def __init__(self, parent, nazoData : NazoData, puzzleScript : GdScript, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 600,268 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        super().__init__(parent, id, pos, size, style, name)

        self.__nazoData = nazoData
        self.__script = puzzleScript

        if nazoData.idHandler in HANDLER_TO_INDEX:
            self.drawInputPickType.SetSelection(HANDLER_TO_INDEX[nazoData.idHandler])
        else:
            self.drawInputPickType.SetSelection(1)
        self.__disableUnavailableOptions()
    
    def __disableUnavailableOptions(self):
        selection = self.drawInputPickType.GetSelection()

        # Only show debug on handlers with multiple variants
        if selection == 1:
            self.drawInputPickDebug.Enable()
        else:
            self.drawInputPickDebug.Disable()
            self.drawInputPickDebug.SetSelection(0)
        
        # Hide length on if length is predetermined
        if selection > 1:
            if self.__nazoData.idHandler in HANDLER_TO_LENGTH:
                self.drawInputSetLength.Set
                self.drawInputSetLength.SetSelection(HANDLER_TO_LENGTH[self.__nazoData.idHandler] - 1)
            self.drawInputSetLength.Disable()
        else:
            self.drawInputSetLength.Enable()
        
    
    def __updateNazoData(self):
        selection = self.drawInputPickType.GetSelection()
        if selection in INDEX_TO_HANDLER:
            self.__nazoData.idHandler = INDEX_TO_HANDLER[selection]
        else:
            self.__nazoData.idHandler = 20 + self.drawInputPickDebug.GetSelection()
    
    def drawInputPickTypeOnChoice(self, event):
        self.__updateNazoData()
        self.__disableUnavailableOptions()
        return super().drawInputPickTypeOnChoice(event)
    
    def drawInputPickDebugOnChoice(self, event):
        self.__updateNazoData()
        return super().drawInputPickDebugOnChoice(event)