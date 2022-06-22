from typing import Any, Callable, Dict, List, Optional, Tuple
from editor.d_operandMultichoice import DialogMultipleChoice
from editor.d_pickerBgx import DialogPickerBgx
from editor.gui.command_annotator.bank import OperandCompatibility, OperandType
from wx import TextEntryDialog, ID_OK, MessageDialog, ICON_WARNING, OK, CENTER

def strCheckFunction() -> Callable[[str], Tuple[bool, Any]]:
    def output(x : str) -> bool:
        return (True, x)
    return output

def numCheckFunction() -> Callable[[str], Tuple[bool, Any]]:
    def output(x : str) -> bool:
        try:
            x = int(x)
            return (True, x)
        except:
            return (False, 0)
    return output

def floatCheckFunction() -> Callable[[str], Tuple[bool, Any]]:
    def output(x : str) -> bool:
        try:
            x = float(x)
        except:
            return (False, 0)
        return (True, x)
    return output

def rangeIntCheckFunction(minimum : int, maximum : int) -> Callable[[str], Tuple[bool, Any]]:
    def output(x : str) -> bool:
        try:
            x = int(x)
            return (minimum <= x <= maximum, x)
        except:
            return (False, 0)
    return output

def rangeFloatCheckFunction(minimum : float, maximum : float) -> Callable[[str], Tuple[bool, Any]]:
    def output(x : str) -> bool:
        try:
            x = float(x)
        except:
            return (False, 0)
        return (minimum <= x <= maximum, x)
    return output

def multipleChoiceFunction(choices : List[str]) -> Callable[[str], Tuple[bool, Any]]:
    def output(x : str) -> bool:
        if len(choices) > 0:
            return (x in choices, choices[0])
        return (x in choices, "")
    return output

class VerifiedDialog():
    def __init__(self, dialog : TextEntryDialog, funcCheckInput : Callable[[Any], bool], errorOnBadInputMessage : str = "Bad text entry!"):
        self._dialog = dialog
        self._funcCheckInput = funcCheckInput
        self._msgBadEntry = errorOnBadInputMessage
    
    def do(self, defaultValue : str) -> Optional[Any]:
        previousValue = defaultValue
        while True:
            self._dialog.SetValue(previousValue)
            val = self._dialog.ShowModal()
            if val == ID_OK:
                wasAccepted, outputVal = self._funcCheckInput(self._dialog.GetValue())
                if wasAccepted:
                    return outputVal
                else:
                    MessageDialog(self._dialog.GetParent(), self._msgBadEntry, "Value not Accepted", style=ICON_WARNING|OK|CENTER).ShowModal()
            else:
                return None

class BackgroundDialog():
    def __init__(self, parent, state, filesystem):
        self._root = "/data_lt2/bg"
        self._dialog = DialogPickerBgx(parent, state, filesystem, self._root)
    
    def do(self, defaultValue : str) -> Optional[str]:
        self._dialog.setDefaultRelativePath(defaultValue)
        value = self._dialog.ShowModal()
        if value == ID_OK:
            return (self._dialog.GetPath()[len(self._root) + 1:][:-4]) + ".bgx"
        return None

class MultipleChoiceDialog():
    def __init__(self, parent, state, filesystem, choices : Dict[str, str], title = None):
        self._dialog = DialogMultipleChoice(parent, choices, title)
    
    def do(self, defaultValue : str) -> Optional[str]:
        self._dialog.SetSelection(defaultValue)
        value = self._dialog.ShowModal()
        if value == ID_OK:
            return self._dialog.GetSelection()
        return None

class GameModeDialog(MultipleChoiceDialog):
    def __init__(self, parent, state, filesystem):
        choices  = {"drama event"   :"""Gamemode to play another event.
                                        \nWhen this gamemode is started, the game will switch to the event corresponding to the stored event index.
                                        \nTo switch events, you must use the 'Set next event ID' command to change the stored ID, otherwise the engine will loop the running event. """,
                    "room"          :"""Gamemode that handles room exploration.
                                        \nNote that the room handler is allowed to switch to the drama event gamemode in certain circumstances, so this gamemode is not guaranteed.
                                        \nTo switch rooms, you must use the 'Set next launched room' command. If you want to continue in the current room state, this is not needed.""",
                    "puzzle"        :"""""",
                    "movie"         :"""Gamemode that performs movie playback.
                                        \nTo use this gamemode, you must use the 'Set next played movie ID' to tell the game which movie to play.
                                        \nThis mode requires that the gamemode submode be set to tell the game how to continue after playback has ended. This should be 'drama event', as all other modes will loop.""",
                    "narration"     :"""Gamemode that performs the letter reading sequences.
                                        \nNote that this gamemode uses the next event ID to decide which sequence to play. Therefore, it requires that it be called with events 10010, 10030, 13190 or 17190. Only 4 sequences are supported.
                                        \nThis mode requires that the gamemode submode be set to tell the game how to continue after the narration sequence has ended. Since it uses the next event ID, the next gamemode submode should be 'drama event'.""",
                    "menu"          :"""""",
                    "staff"         :"""""",
                    "name"          :"""""",
                    "challenge"     :"""""",
                    "sub herb"      :"""""",
                    "sub camera"    :"""""",
                    "sub ham"       :"""""",
                    "passcode"      :"""""",
                    "diary"         :"""""",
                    "nazoba"        :""""""}
        super().__init__(parent, state, filesystem, choices, "Change Selected Gamemode")
    
    def do(self, defaultValue: str) -> Optional[str]:
        return super().do(defaultValue.lower())

class ScreenModeDialog(MultipleChoiceDialog):
    def __init__(self, parent, state, filesystem):
        choices  = {"0" :"""Map to BG0. Refer to GBAtek for more information about this mode.""",
                    "1" :"""Map to BG1. Refer to GBAtek for more information about this mode.""",
                    "2" :"""Map to BG2. Refer to GBAtek for more information about this mode.""",
                    "3" :"""Recommended. Map to BG3, which supports extended colors needed for normal image display."""}
        super().__init__(parent, state, filesystem, choices, "Change Image Mapping")
    
    def do(self, defaultValue: str) -> Optional[int]:
        value = super().do(defaultValue)
        if value != None and value.isdigit():
            return int(value)
        return None

def getDialogForType(parent, state, filesystem, operandType : OperandType) -> Optional[VerifiedDialog]:
    compatDict = {OperandType.StandardS32               : VerifiedDialog(TextEntryDialog(parent, "Enter a number"), rangeIntCheckFunction(-(2 ** 31), (2 ** 31) - 1)),
                  OperandType.StandardString            : VerifiedDialog(TextEntryDialog(parent, "Enter a string"), strCheckFunction()),
                  OperandType.StandardF32               : VerifiedDialog(TextEntryDialog(parent, "Enter a decimal"), floatCheckFunction()),
                  OperandType.StandardU16               : VerifiedDialog(TextEntryDialog(parent, "Enter a short"), rangeIntCheckFunction(0, (2 ** 16) - 1)),
                  
                  OperandType.StringGamemode            : GameModeDialog(parent, state, filesystem),
                  OperandType.StringBackground          : BackgroundDialog(parent, state, filesystem),
                  
                  OperandType.ColorComponent8           : VerifiedDialog(TextEntryDialog(parent, "Enter an 8-bit color component"), rangeIntCheckFunction(0,255)),
                  OperandType.ColorComponent5           : VerifiedDialog(TextEntryDialog(parent, "Enter a 5-bit color component"), rangeIntCheckFunction(0,31)),
                  
                  OperandType.Volume                    : VerifiedDialog(TextEntryDialog(parent, "Enter a new value for volume"), rangeFloatCheckFunction(0, 1)),

                  OperandType.IndexCharacterSlot        : VerifiedDialog(TextEntryDialog(parent, "Enter a character position slot ID"), rangeIntCheckFunction(0,7)),
                  OperandType.ModeBackground            : ScreenModeDialog(parent, state, filesystem),
                  OperandType.IndexEventDataCharacter   : VerifiedDialog(TextEntryDialog(parent, "Enter a character index"), rangeIntCheckFunction(0,7))}
    
    if operandType in compatDict:
        return compatDict[operandType]
    
    operandType = OperandCompatibility[operandType.name]
    if operandType in compatDict:
        return compatDict[operandType]
    
    return None