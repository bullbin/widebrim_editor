from ..engine.state.layer import ScreenCollection
from ..engine.state.enum_mode import GAMEMODES
from ..gamemodes import EventPlayer, RoomPlayer, NarrationPlayer
from pygame.event import post, Event
from pygame import QUIT

class ScreenCollectionGameModeSpawner(ScreenCollection):
    def __init__(self, laytonState):
        ScreenCollection.__init__(self)

        self.laytonState = laytonState
        self._currentActiveGameMode = 0
        self._currentActiveGameModeObject = None

    def _loadGameMode(self, indexGameMode):

        if indexGameMode == GAMEMODES.DramaEvent.value:
            self.addToCollection(EventPlayer(self.laytonState))
        elif indexGameMode == GAMEMODES.Room.value:
            self.addToCollection(RoomPlayer(self.laytonState))
        elif indexGameMode == GAMEMODES.Narration.value:
            self.addToCollection(NarrationPlayer(self.laytonState))
            
        else:
            if indexGameMode == GAMEMODES.INVALID.value:
                self._voidGameMode()
            else:
                print("Missing connection for type", indexGameMode)
                self._currentActiveGameMode = indexGameMode
                self._currentActiveGameModeObject = None
            return False
        
        self._currentActiveGameMode = indexGameMode
        self._currentActiveGameModeObject = self._layers[-1]
        return True
    
    def _voidGameMode(self):
        self._currentActiveGameMode = 0
        self._currentActiveGameModeObject = None

    def _triggerQuit(self):
        print("Ending execution...")
        post(Event(QUIT))
    
    def _switchToNextGameMode(self):
        print("Switching to next gamemode...", self.laytonState.getGameModeNext().name)
        self.laytonState.setGameMode(self.laytonState.getGameModeNext())
        self.laytonState.setGameModeNext(GAMEMODES.INVALID)

    def update(self, gameClockDelta):

        if self._currentActiveGameMode != self.laytonState.getGameMode().value or self.laytonState.gameModeRestartRequired:
            # Destroy current gamemode instance and set to new one
            # TODO - Only allow spawning when fader has faded all the way out
            if self._currentActiveGameModeObject != None:
                self.removeFromCollection(self._layers.index(self._currentActiveGameModeObject))
                print("Killed active gamemode!")
            
            self._loadGameMode(self.laytonState.getGameMode().value)
            self.laytonState.gameModeRestartRequired = False

        elif self._currentActiveGameMode == GAMEMODES.INVALID.value:
            # Nothing running in current mode, so execution can finish
            self._triggerQuit()

        elif self._currentActiveGameModeObject == None or self._currentActiveGameModeObject.getContextState():
            # Kill this layer
            # TODO - Force fade out on kill before next spawn
            if self._currentActiveGameModeObject != None:
                self.removeFromCollection(self._layers.index(self._currentActiveGameModeObject))

            # Void current instance
            self._voidGameMode()

            # Load next game mode for for next update to grab
            self._switchToNextGameMode()

        # Override original update to ensure game mode object cannot be deleted, as logic above does that properly
        for indexLayer in range(len(self._layers) - 1, -1, -1):
            layer = self._layers[indexLayer]
            layer.update(gameClockDelta)
            if layer.getContextState() and layer != self._currentActiveGameModeObject:
                self.removeFromCollection(indexLayer)