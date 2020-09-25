from .utils import FadingPopupAnimBackground

from .const import NAME_POS_VARIABLE, PATH_ANIM_BUTTON_YES, PATH_ANIM_BUTTON_NO, ID_SAVE_NOT_COMPLETE, POS_TEXT_SAVE_Y
from ....engine.const import RESOLUTION_NINTENDO_DS, PATH_TEXT_GENERIC
from ....engine.anim.button import AnimatedButton
from ....engine.anim.font.static import generateImageFromString
from ....engine_ext.utils import getAnimFromPathWithAttributes, getTxt2String

from pygame import BLEND_RGB_SUB

# TODO - Reuse me for overwrite save confirmation window
# TODO - Add text support

class SaveButtonPopup(FadingPopupAnimBackground):
    def __init__(self, laytonState, screenController, eventStorage, callbackOnDoSave, callbackOnSkipSave):
        # cursorWait

        prizeWindow2 = eventStorage.getAssetPrizeWindow2()
        if prizeWindow2 != None:
            # TODO - Automagically set this in event storage so it doesn't have to be done for every item in every popup!
            prizeWindow2.setAnimationFromName("gfx")
            prizeWindow2Pos = prizeWindow2.getVariable(NAME_POS_VARIABLE)
            if prizeWindow2Pos != None:
                prizeWindow2.setPos((prizeWindow2Pos[0], prizeWindow2Pos[1] + RESOLUTION_NINTENDO_DS[1]))

        self._callbackOnDoSave = callbackOnDoSave
        self._callbackOnSkippedSave = callbackOnSkipSave

        def callbackOnYes():
            self._callbackOnTerminate = self._callbackOnDoSave
            self.startTerminateBehaviour()
        
        def callbackOnNo():
            self._callbackOnTerminate = self._callbackOnSkippedSave
            self.startTerminateBehaviour()

        FadingPopupAnimBackground.__init__(self, laytonState, screenController, None, prizeWindow2)

        # TODO - What is the pos name here?
        self._prompt = generateImageFromString(laytonState.fontEvent, getTxt2String(laytonState, PATH_TEXT_GENERIC % ID_SAVE_NOT_COMPLETE))
        self._promptPos = ((RESOLUTION_NINTENDO_DS[0] - self._prompt.get_width()) // 2, POS_TEXT_SAVE_Y + RESOLUTION_NINTENDO_DS[1])
        self.buttonYes = AnimatedButton(getAnimFromPathWithAttributes(PATH_ANIM_BUTTON_YES % laytonState.language.value, posVariable="win_p"), "on", "off", callback=callbackOnYes)
        self.buttonNo = AnimatedButton(getAnimFromPathWithAttributes(PATH_ANIM_BUTTON_NO % laytonState.language.value, posVariable="win_p"), "on", "off", callback=callbackOnNo)
    
    def updateForegroundElements(self, gameClockDelta):
        self.buttonYes.update(gameClockDelta)
        self.buttonNo.update(gameClockDelta)

    def drawForegroundElements(self, gameDisplay):
        gameDisplay.blit(self._prompt, self._promptPos, special_flags=BLEND_RGB_SUB)
        self.buttonYes.draw(gameDisplay)
        self.buttonNo.draw(gameDisplay)

    def handleTouchEventForegroundElements(self, event):
        self.buttonYes.handleTouchEvent(event)
        self.buttonNo.handleTouchEvent(event)
        return True