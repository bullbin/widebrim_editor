from pygame import Surface
from editor.nopush_editor import editorDrawInput

import wx
from wx import Bitmap
from pygame.image import tostring
from widebrim.engine.const import RESOLUTION_NINTENDO_DS
from widebrim.engine.state.manager import Layton2GameState
from widebrim.engine_ext.utils import getImageFromPath
from widebrim.gamemodes.nazo_popup.mode.const import PATH_BG_DRAWINPUT
from widebrim.madhatter.hat_io.asset_dat.nazo import NazoData

from widebrim.madhatter.hat_io.asset_script import GdScript
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2

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

# TODO - Are any puzzles subtype 0 or 1? Names in ROM don't have translations for handler 20 or 21 (but then again, they don't have one for 35...)
# TODO - Migrate ratios between 1:1 to 2:2 correctly...

class DrawInputEditor(editorDrawInput):
    def __init__(self, parent, state : Layton2GameState, nazoData : NazoData, puzzleScript : GdScript):
        super().__init__(parent)

        self.__nazoData = nazoData
        self.__script = puzzleScript
        self.__state = state

        if nazoData.idHandler in HANDLER_TO_INDEX:
            self.drawInputPickType.SetSelection(HANDLER_TO_INDEX[nazoData.idHandler])
        else:
            self.drawInputPickType.SetSelection(1)
        
        self.drawInputSetAnswer.Bind(wx.EVT_CHAR, self.__filterKeypresses)

        self.bgInput.SetBitmap(Bitmap.FromBuffer(RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1],
                                                 tostring(Surface(RESOLUTION_NINTENDO_DS), "RGB")))

        if self.__nazoData.idHandler in [20,21,22]:
            self.drawInputPickDebug.SetSelection(self.__nazoData.idHandler - 20)

        self.__disableUnavailableOptions()
        self.__processScriptFile()

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
                self.drawInputSetLength.SetSelection(HANDLER_TO_LENGTH[self.__nazoData.idHandler] - 1)
            self.drawInputSetLength.Disable()
        else:
            self.drawInputSetLength.Enable()
        
        if len(self.drawInputSetAnswer.GetValue()) > self.drawInputSetLength.GetSelection() + 1:
            value = self.drawInputSetAnswer.GetValue()[:self.drawInputSetLength.GetSelection() + 1]
            self.drawInputSetAnswer.SetValue(value)
        self.drawInputSetAnswer.SetMaxLength(self.drawInputSetLength.GetSelection() + 1)

        output = ""
        for char in self.drawInputSetAnswer.GetValue():
            if (selection == 0 and not char.isdigit()) or (selection != 0 and char.isdigit()):
                output = output + char

        if len(output) == 0:
            if selection == 0:
                output = "a"
            else:
                output = "0"
        self.drawInputSetAnswer.SetValue(output)

    def __processScriptFile(self):
        for indexCommand in range(self.__script.getInstructionCount()):
            command = self.__script.getInstruction(indexCommand)
            opcode = int.from_bytes(command.opcode, byteorder='little')
            if opcode == OPCODES_LT2.SetAnswer.value and len(command.operands) >= 2:
                self.drawInputSetAnswer.SetValue(command.operands[1].value)
            elif opcode == OPCODES_LT2.SetAnswerBox.value and len(command.operands) >= 4:
                length = command.operands[3].value
                selectedLength = self.drawInputSetLength.GetSelection() + 1
                if self.drawInputPickType.GetSelection() < 2:
                    if length > 0 and length < 5:
                        self.drawInputSetLength.SetSelection(length - 1)
                else:
                    if length != selectedLength:
                        print("Warning: Length mismatch!", length, selectedLength)
            elif opcode == OPCODES_LT2.SetDrawInputBG.value and len(command.operands) >= 1:
                background = getImageFromPath(self.__state, PATH_BG_DRAWINPUT % command.operands[0].value)
                if background != None:
                    self.bgInput.SetBitmap(Bitmap.FromBuffer(RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1],
                                                            tostring(background, "RGB")))
        # Unneeded but who cares
        self.__disableUnavailableOptions()

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
    
    def drawInputSetLengthOnChoice(self, event):
        self.__disableUnavailableOptions()
        return super().drawInputSetLengthOnChoice(event)
    
    def __filterKeypresses(self, event):
        selection = self.drawInputPickType.GetSelection()
        char = event.GetUnicodeKey()
        if char == wx.WXK_NONE or char == wx.WXK_BACK:
            event.Skip()
        else:
            char = chr(char)
            if selection == 0:
                if char.isascii():
                    event.Skip()
            else:
                if char.isdigit():
                    event.Skip()

    def drawInputSetAnswerOnText(self, event):
        return super().drawInputSetAnswerOnText(event)