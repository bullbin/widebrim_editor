from typing import Any, Dict, Optional
from editor.gui.command_annotator.bank import OperandCompatibility, OperandType

_DEFAULT_VALUES : Dict[OperandType, Any] = {OperandType.StandardS32         : 0,
                                            OperandType.StandardString      : "",
                                            OperandType.StandardF32         : 1.0,
                                            OperandType.StandardU16         : 0,

                                            OperandType.StringGamemode      : "drama event",
                                            OperandType.ModeBackground      : 3,
                                            OperandType.IndexVoiceId        : -1,
                                            
                                            OperandType.Pitch               : 1,
                                            
                                            OperandType.StringCharAnim      : "NONE"}

def getDefaultValue(opType : OperandType) -> Optional[Any]:
    if opType in _DEFAULT_VALUES:
        return _DEFAULT_VALUES[opType]
    
    try:
        opType = OperandCompatibility[opType.name]
    except ValueError:
        return None
    if opType in _DEFAULT_VALUES:
        return _DEFAULT_VALUES[opType]
    return None