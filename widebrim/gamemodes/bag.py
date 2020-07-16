from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES

class BagPlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)
        laytonState.setGameModeNext(GAMEMODES.Room)
        self._canBeKilled = True