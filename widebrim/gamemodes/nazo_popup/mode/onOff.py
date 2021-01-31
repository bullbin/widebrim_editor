# 7, 3

from .base import BaseQuestionObject

class HandlerOnOff(BaseQuestionObject):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, callbackOnTerminate)
    
    def hasRestartButton(self):
        return False