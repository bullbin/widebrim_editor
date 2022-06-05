from typing import Any, Callable, Optional, Tuple
from editor.d_pickerBgx import DialogPickerBgx
from editor.gui.command_annotator.bank import OperandCompatibility, OperandType
from wx import TextEntryDialog, ID_OK

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
                    # TODO - Error
                    pass
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

def getDialogForType(parent, state, filesystem, operandType : OperandType) -> Optional[VerifiedDialog]:
    compatDict = {OperandType.StandardS32           : VerifiedDialog(TextEntryDialog(parent, "Enter a number"), numCheckFunction()),
                  OperandType.StandardString        : VerifiedDialog(TextEntryDialog(parent, "Enter a string"), strCheckFunction()),
                  OperandType.StandardF32           : VerifiedDialog(TextEntryDialog(parent, "Enter a decimal"), floatCheckFunction()),
                  OperandType.StandardU16           : VerifiedDialog(TextEntryDialog(parent, "Enter a short"), numCheckFunction()),
                  
                  OperandType.StringBackground      : BackgroundDialog(parent, state, filesystem),
                  
                  OperandType.ColorComponent8       : VerifiedDialog(TextEntryDialog(parent, "Enter an 8-bit color component"), rangeIntCheckFunction(0,255)),
                  OperandType.ColorComponent8       : VerifiedDialog(TextEntryDialog(parent, "Enter a 5-bit color component"), rangeIntCheckFunction(0,31)),
                  
                  OperandType.IndexCharacterSlot    : VerifiedDialog(TextEntryDialog(parent, "Enter a character position slot ID"), rangeIntCheckFunction(0,7)),
                  OperandType.ModeBackground                : VerifiedDialog(TextEntryDialog(parent, "Enter a NDS BG mode"), rangeIntCheckFunction(0,3)),
                  OperandType.IndexEventDataCharacter       : VerifiedDialog(TextEntryDialog(parent, "Enter a character index"), rangeIntCheckFunction(0,7))}
    
    if operandType in compatDict:
        return compatDict[operandType]
    
    operandType = OperandCompatibility[operandType.name]
    if operandType in compatDict:
        return compatDict[operandType]
    
    return None