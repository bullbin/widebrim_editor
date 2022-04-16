from typing import List
from widebrim.madhatter.hat_io.asset_script import Operand

class InstructionValidator():
    def __init__(self):
        pass

    @staticmethod
    def isValid(operands : List[Operand]) -> bool:
        return False

class OperandValidator():
    def __init__(self):
        pass

    @staticmethod
    def isValid(data) -> bool:
        return False

class ValidatorSigned32(OperandValidator):
    @staticmethod
    def isValid(data) -> bool:
        if type(data) == int:
            return True
        return False

class ValidatorFloat32(OperandValidator):
    @staticmethod
    def isValid(data) -> bool:
        if type(data) == float:
            return True
        return False

class ValidatorString(OperandValidator):
    @staticmethod
    def isValid(data) -> bool:
        if type(data) == str:
            return True
        return False