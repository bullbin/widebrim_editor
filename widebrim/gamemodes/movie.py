from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES

class MoviePlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)
        print("Movie handler called on ID", laytonState.getMovieNum())
        laytonState.setMovieNum(-1)
        laytonState.setGameMode(laytonState.getGameModeNext())
        self.doOnKill()