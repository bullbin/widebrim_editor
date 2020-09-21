from ...core_popup.utils import MainScreenPopup
from ....engine.anim.fader import Fader

# TODO - Popups and characters all share the same layers, so alpha transitions cause colours to immediately bleed.
# What is the best way to mimick this behaviour?

class FadingPopup(MainScreenPopup):

    DURATION_FADE = 300

    def __init__(self, laytonState, screenController, callbackOnTerminate, bgSurface, bgSurfacePos):
        MainScreenPopup.__init__(self, callbackOnTerminate)
        self.__alphaFader = Fader(FadingPopup.DURATION_FADE)
        self._surfaceBackground = bgSurface
        self._surfaceBackgroundPos = bgSurfacePos
        self._surfaceBackground.set_alpha(0)
    
    def updateForegroundElements(self, gameClockDelta):
        pass
    
    def drawForegroundElements(self, gameDisplay):
        pass

    def handleTouchEventForegroundElements(self, event):
        # Return True if the touch event was used in the popup, meaning termination is not required.
        return False

    def draw(self, gameDisplay):
        gameDisplay.blit(self._surfaceBackground, self._surfaceBackgroundPos)
        if self.__alphaFader.getStrength():
            self.drawForegroundElements(gameDisplay)

    def update(self, gameClockDelta):
        self.__alphaFader.update(gameClockDelta)
        
        # TODO - Only update surface where required
        self._surfaceBackground.set_alpha(round(self.__alphaFader.getStrength() * 255))

        if self.__alphaFader.getStrength():
            self.updateForegroundElements(gameClockDelta)
    
    def handleTouchEvent(self, event):
        if self.__alphaFader.getStrength():
            if not(self.handleTouchEventForegroundElements(event)):
                self.__alphaFader.setInvertedState(True)
                self.__alphaFader.reset()
                self.__alphaFader.setCallback(self.doOnKill)