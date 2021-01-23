from . import EventPlayer
from ..engine.state.enum_mode import GAMEMODES

# Overlay_EndPuzzle
class EndPuzzlePlayer(EventPlayer):
    def __init__(self, laytonState, screenController):

        laytonState.setGameModeNext(GAMEMODES.Room)

        baseEventId = laytonState.entryEvInfo
        if baseEventId != None:
            # TODO - Check if puzzle was actually solved

            # There's special behaviour for puzzle 135 (sword puzzle)
            if baseEventId.dataPuzzle == 0x87:
                baseEventId = baseEventId.idEvent + 4
            else:
                baseEventId = baseEventId.idEvent + 3
                
            laytonState.setEventId(baseEventId)
            EventPlayer.__init__(self, laytonState, screenController)
        else:
            EventPlayer.__init__(self, laytonState, screenController)
            self._makeInactive()
            self.doOnKill()
    
    def doOnKill(self):
        self.laytonState.setGameMode(self.laytonState.getGameModeNext())
        return super().doOnKill()