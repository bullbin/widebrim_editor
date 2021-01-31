from . import EventPlayer
from ..engine.state.enum_mode import GAMEMODES

# Overlay_EndPuzzle
class EndPuzzlePlayer(EventPlayer):
    def __init__(self, laytonState, screenController):

        self.laytonState = laytonState
        self.laytonState.setGameModeNext(GAMEMODES.Room)

        baseEventId = laytonState.entryEvInfo
        if baseEventId != None:
            wasSkipped = self.laytonState.wasPuzzleSkipped
            if self.laytonState.getCurrentNazoListEntry() != None:
                puzzleState = self.laytonState.saveSlot.puzzleData.getPuzzleData((self.laytonState.getCurrentNazoListEntry().idExternal - 1))
                if not(puzzleState.wasSolved):
                    wasSkipped = True

            # There's special behaviour for puzzle 135 (sword puzzle)
            if baseEventId.dataPuzzle == 0x87:
                if wasSkipped:
                    baseEventId = baseEventId.idEvent + 3
                else:
                    baseEventId = baseEventId.idEvent + 4
            else:
                if wasSkipped:
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