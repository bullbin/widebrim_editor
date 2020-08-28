from . import EventPlayer
from ..engine.state.enum_mode import GAMEMODES

# Hack mixes Puzzle and EndPuzzle to skip gamemode correctly

class PuzzlePlayer(EventPlayer):
    def __init__(self, laytonState, screenController):

        laytonState.setGameModeNext(GAMEMODES.Room)

        baseEventId = laytonState.entryEvInfo
        if baseEventId != None:

            if laytonState.entryNzList != None:
                laytonState.saveSlot.puzzleData.getPuzzleData(laytonState.entryNzList.idExternal - 1).wasSolved = True
                laytonState.saveSlot.puzzleData.getPuzzleData(laytonState.entryNzList.idExternal - 1).wasEncountered = True

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