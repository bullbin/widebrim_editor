from ...engine.state.layer import ScreenLayerNonBlocking
from ...madhatter.hat_io.asset_sav import Layton2SaveFile
from ...engine.anim.fader import Fader
from .const import PATH_BG_TITLE_SUB
from ...engine.config import PATH_SAVE
from .main_title import MenuScreen
from ...gamemodes.core_popup.save import SaveLoadScreenPopup

class TitlePlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)

        saveBytes = None
        saveData = Layton2SaveFile()
        try:
            with open(PATH_SAVE, 'rb') as saveIn:
                saveBytes = saveIn.read()
            if not(saveData.load(saveBytes)):
                saveData = Layton2SaveFile()
        except FileNotFoundError:
            pass

        self.popup = None

        def callbackTerminate():
            self._canBeKilled = True

        def callbackSpawnTitle():
            screenController.fadeOutMain(callback=callbackStartMainScreenAnim)
        
        def callbackSpawnContinue():
            screenController.fadeOutMain(callback=callbackStartContinueScreen)
        
        def callbackSpawnBonus():
            screenController.fadeOutMain(callback=callbackStartBonusScreen)

        def callbackStartMainScreenAnim():
            self.popup = MenuScreen(laytonState, screenController, saveData,
                                    callbackSpawnTitle, callbackSpawnContinue, callbackSpawnBonus, callbackTerminate)
        
        def callbackStartContinueScreen():
            self.popup = SaveLoadScreenPopup(laytonState, screenController, 0, callbackSpawnTitle, callbackSpawnTitle)
        
        def callbackStartBonusScreen():
            self.popup = SaveLoadScreenPopup(laytonState, screenController, 1, callbackSpawnTitle, callbackSpawnTitle)

        self.screenController = screenController
        self.laytonState = laytonState
        self.logoAlphaFader = Fader(1000, initialActiveState=False, callbackOnDone=callbackStartMainScreenAnim)

        def callbackStartLogoAnim():
            self.logoAlphaFader.setActiveState(True)
        
        def callbackStartTitleScreen():
            self.screenController.setBgSub(PATH_BG_TITLE_SUB)
            self.screenController.fadeInSub(duration=3600, callback=callbackStartLogoAnim)
        
        # TODO - Save corrupt screen
        callbackStartTitleScreen()

    def update(self, gameClockDelta):
        self.logoAlphaFader.update(gameClockDelta)
        if self.popup != None:
            self.popup.update(gameClockDelta)
    
    def draw(self, gameDisplay):
        if self.popup != None:
            self.popup.draw(gameDisplay)

    def handleTouchEvent(self, event):
        if self.popup != None and not(self.screenController.getFadingStatus()):
            self.popup.handleTouchEvent(event)
        else:
            return super().handleTouchEvent(event)