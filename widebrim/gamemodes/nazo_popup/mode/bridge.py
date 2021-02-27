from .onOff import HandlerOnOff
from ....engine.const import RESOLUTION_NINTENDO_DS

# TODO - Research required. Seems to not care about script?

class HandlerBridge(HandlerOnOff):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, callbackOnTerminate)
        self._setPuzzleTouchBounds(RESOLUTION_NINTENDO_DS[0])
    
    def hasRestartButton(self):
        return True
    
    def hasSubmitButton(self):
        return False