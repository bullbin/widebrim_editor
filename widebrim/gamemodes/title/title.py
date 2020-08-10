from ...engine.state.layer import ScreenLayerNonBlocking
from ...engine.anim.fader import Fader
from .const import PATH_BG_TITLE_SUB
from .main_title import MenuScreen

class TitlePlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)

        self.popup = None

        def switchPopup(newOverlay):
            self.popup = newOverlay(laytonState, screenController,
                                    callbackSpawnTitle, callbackSpawnNewGame,
                                    callbackSpawnContinue, callbackSpawnBonus)
            screenController.fadeInMain()

        def callbackSpawnTitle():
            screenController.fadeOutMain(callback=switchPopup(MenuScreen))

        def callbackSpawnNewGame():
            callbackSpawnTitle()
        
        def callbackSpawnContinue():
            callbackSpawnTitle()
        
        def callbackSpawnBonus():
            callbackSpawnTitle()

        def callbackStartMainScreenAnim():
            switchPopup(MenuScreen)

        self.screenController = screenController
        self.laytonState = laytonState
        self.logoAlphaFader = Fader(1000, initialActiveState=False, callbackOnDone=callbackStartMainScreenAnim)

        def callbackStartLogoAnim():
            self.logoAlphaFader.setActiveState(True)
        
        self.screenController.setBgSub(PATH_BG_TITLE_SUB)
        self.screenController.fadeInSub(duration=3600, callback=callbackStartLogoAnim)

    def update(self, gameClockDelta):
        self.logoAlphaFader.update(gameClockDelta)
        if self.popup != None and not(self.screenController.getFadingStatus()):
            self.popup.update(gameClockDelta)
    
    def draw(self, gameDisplay):
        if self.popup != None:
            self.popup.draw(gameDisplay)

    def handleTouchEvent(self, event):
        if self.popup != None and not(self.screenController.getFadingStatus()):
            self.popup.handleTouchEvent(event)
        else:
            return super().handleTouchEvent(event)