from .base import BaseQuestionObject
from ....engine.const import RESOLUTION_NINTENDO_DS
from .const import PATH_ANI_FREEBUTTON
from ....engine.anim.button import AnimatedButton
from ....engine_ext.utils import getAnimFromPath
from ....madhatter.typewriter.stringsLt2 import OPCODES_LT2

class  HandlerFreeButton(BaseQuestionObject):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, callbackOnTerminate)
        self.buttons = []
    
    def _doUnpackedCommand(self, opcode, operands):
        if opcode == OPCODES_LT2.AddOnOffButton.value and len(operands) == 5:
            buttonAnim = getAnimFromPath(PATH_ANI_FREEBUTTON % operands[2].value)
            if buttonAnim != None:
                buttonAnim.setPos((operands[0].value, operands[1].value + RESOLUTION_NINTENDO_DS[1]))
                self.buttons.append(AnimatedButton(buttonAnim, "on", "off"))
                return True
        
        return super()._doUnpackedCommand(opcode, operands)
    
    def drawPuzzleElements(self, gameDisplay):
        for button in self.buttons:
            button.draw(gameDisplay)
        return super().drawPuzzleElements(gameDisplay)
    
    def updatePuzzleElements(self, gameClockDelta):
        for button in self.buttons:
            button.update(gameClockDelta)
        return super().updatePuzzleElements(gameClockDelta)
    
    def handleTouchEventPuzzleElements(self, event):
        for button in self.buttons:
            if button.handleTouchEvent(event):
                return True
        return super().handleTouchEventPuzzleElements(event)