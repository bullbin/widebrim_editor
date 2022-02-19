from typing import List
from widebrim.gui.custom_valid_func import ValidatorBackgroundPath, ValidatorColorComponent
from widebrim.gui.gdscript_valid_func import InstructionValidator, ValidatorSigned32
from widebrim.madhatter.hat_io.asset_script import Operand

class CommandSetBackgroundValidator(InstructionValidator):
    @staticmethod
    def isValid(operands : List[Operand]) -> bool:
        if len(operands) >= 2:
            if ValidatorBackgroundPath.isValid(operands[0].value):
                if ValidatorSigned32.isValid(operands[1].value):
                    return True
        return False

class CommandRgb888TripletValidator(InstructionValidator):
    @staticmethod
    def isValid(operands : List[Operand]) -> bool:
        if len(operands) >= 3:
            if ValidatorColorComponent.isValid(operands[0].value):
                if ValidatorColorComponent.isValid(operands[1].value):
                    if ValidatorColorComponent.isValid(operands[2].value):
                        return True
        return False