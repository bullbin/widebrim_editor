# TODO - AutoEvent method
# Probably check autoevent on spawn, then set event ID and next gamemode to event which defaults back to room.

from ..engine.state.layer import ScreenLayerNonBlocking

class RoomPlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState):
        ScreenLayerNonBlocking.__init__(self)
        print("Attempted to load room!")
        self._canBeKilled = True