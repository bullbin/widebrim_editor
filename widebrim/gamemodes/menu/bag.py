from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from widebrim.engine.state.state import Layton2GameState
    from widebrim.engine_ext.state_game import ScreenController

from widebrim.engine.state.layer import ScreenLayerNonBlocking
from widebrim.engine.state.enum_mode import GAMEMODES

class BagPlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState : Layton2GameState, screenController : ScreenController):
        ScreenLayerNonBlocking.__init__(self)
        laytonState.setGameMode(GAMEMODES.Room)
        self._canBeKilled = True