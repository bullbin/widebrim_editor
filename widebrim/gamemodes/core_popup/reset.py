from .script import ScriptPlayer
from .const import PATH_SCRIPT_LOGO
from ...madhatter.hat_io.asset_script import GdScript
from ...engine.file import FileInterface
from ...engine.state.enum_mode import GAMEMODES

class ResetHelper(ScriptPlayer):
    def __init__(self, laytonState, screenController):
        ScriptPlayer.__init__(self, laytonState, screenController, GdScript())
        self._script.load(FileInterface.getData(PATH_SCRIPT_LOGO))
        self._isActive = False
        self.screenController.fadeOut(callback=self._makeActive)

    def doOnKill(self):
        self.laytonState.setGameMode(GAMEMODES.Title)
        return super().doOnKill()