from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES

class NamePlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)
        
        if laytonState.getGameMode() == GAMEMODES.Name:
            # Player is entering the name on their save file!
            laytonState.setGameMode(GAMEMODES.Room)
        else:
            # Player is entering the hamster name
            # TODO - Set hamster BG
            laytonState.setGameMode(GAMEMODES.DramaEvent)
            laytonState.setEventId(11101)

        self._canBeKilled = True