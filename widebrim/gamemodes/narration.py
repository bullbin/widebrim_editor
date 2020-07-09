from ..engine.state.layer import ScreenLayerNonBlocking

class NarrationPlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState):
        ScreenLayerNonBlocking.__init__(self)
        self._canBeKilled = True