from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES

class PuzzlePlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)
        laytonState.setGameModeNext(GAMEMODES.Room)

        baseEventId = laytonState.entryEvInfo
        if baseEventId != None:
            # TODO - Has to be converted to external index, then subtracted 1.

            if laytonState.entryNzList != None:
                laytonState.saveSlot.puzzleData.getPuzzleData(laytonState.entryNzList.idExternal - 1).wasSolved = True
                laytonState.saveSlot.puzzleData.getPuzzleData(laytonState.entryNzList.idExternal - 1).wasEncountered = True

            baseEventId = baseEventId.idEvent + 3
            laytonState.setEventId(baseEventId)
            laytonState.setGameModeNext(GAMEMODES.DramaEvent)

        self._canBeKilled = True