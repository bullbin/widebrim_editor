from .script import ScriptPlayer
from .const import PATH_SCRIPT_LOGO
from ...madhatter.hat_io.asset_script import GdScript
from ...engine.file import FileInterface
from ...engine.state.enum_mode import GAMEMODES

from widebrim.madhatter.hat_io.asset_sav import Layton2SaveSlot

class ResetHelper(ScriptPlayer):
    def __init__(self, laytonState, screenController):

        # HACK - This fixes a bug where title reset spawns incorrectly
        laytonState.saveSlot = Layton2SaveSlot()
        laytonState.resetState()

        ScriptPlayer.__init__(self, laytonState, screenController, GdScript())
        self._script.load(FileInterface.getData(PATH_SCRIPT_LOGO))
        self._isActive = False
        self.screenController.fadeOut(callback=self._makeActive)

    def doOnKill(self):
        self.laytonState.setGameMode(GAMEMODES.Title)
        return super().doOnKill()