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
from .const import PATH_BG_DRAWINPUT
from ....madhatter.typewriter.stringsLt2 import OPCODES_LT2

class HandlerDrawInput(BaseQuestionObject):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, callbackOnTerminate)
        self._pathBg = None
        self._answers = [None,None,None,None]
    
    def _doUnpackedCommand(self, opcode, operands):
        if opcode == OPCODES_LT2.SetAnswerBox.value:
            return False
        elif opcode == OPCODES_LT2.SetAnswer.value:
            if 0 <= operands[0].value < len(self._answers):
                self._answers[operands[0].value] = operands[1].value
            else:
                return False
        elif opcode == OPCODES_LT2.SetDrawInputBG.value and len(operands) == 1:
            self._pathBg = PATH_BG_DRAWINPUT % operands[0].value
        else:
            return super()._doUnpackedCommand(opcode, operands)
        return True
    
    def _doOnJudgementPress(self):
        # TODO - Disable touch when faders active
        self.screenController.setBgMain(self._pathBg)