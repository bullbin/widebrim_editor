# SetDrawInputBG
# BG name

# SetAnswerBox 4
# Unk
# Unk
# Unk
# Length

# SetAnswer
# SomeIndexAnswer
# Text

from widebrim.engine.const import RESOLUTION_NINTENDO_DS
from .base import BaseQuestionObject
from ....madhatter.typewriter.stringsLt2 import OPCODES_LT2

class HandlerDrawInput(BaseQuestionObject):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, callbackOnTerminate)
    
    def _doUnpackedCommand(self, opcode, operands):
        return super()._doUnpackedCommand(opcode, operands)
    
    def _doOnJudgementPress(self):
        pass