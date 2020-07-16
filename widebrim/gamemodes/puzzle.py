from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES

class PuzzlePlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)
        laytonState.setGameModeNext(GAMEMODES.Room)
        
        screenController.modifyPaletteMain(0)
        screenController.modifyPaletteSub(0)

        baseEventId = laytonState.entryEvInfo
        if baseEventId != None:
            # TODO - Has to be converted to external index, then subtracted 1.
            laytonState.saveSlot.puzzleData.getPuzzleData(baseEventId.dataPuzzle).wasSolved = True
            laytonState.saveSlot.puzzleData.getPuzzleData(baseEventId.dataPuzzle).wasEncountered = True
            baseEventId = baseEventId.idEvent + 3
            laytonState.setEventId(baseEventId)
            laytonState.setGameModeNext(GAMEMODES.DramaEvent)

        self._canBeKilled = True