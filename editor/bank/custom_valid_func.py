from .gdscript_valid_func import OperandValidator

class ValidatorBackgroundPath(OperandValidator):
    # TODO - Check language pathing
    @staticmethod
    def isValid(data) -> bool:
        if type(data) == str:
            return True
        return False

class ValidatorColorComponent(OperandValidator):
    @staticmethod
    def isValid(data) -> bool:
        if type(data) == int and 0 <= data < 256:
            return True
        return False