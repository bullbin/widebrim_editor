from __future__ import annotations
from typing import TYPE_CHECKING

from pygame.constants import MOUSEBUTTONUP
if TYPE_CHECKING:
    from widebrim.engine.state.state import Layton2GameState
    from widebrim.engine_ext.state_game import ScreenController

from widebrim.engine.anim.button import AnimatedButton
from widebrim.engine_ext.utils import getAnimFromPathWithAttributes

from widebrim.gamemodes.core_popup.utils import FullScreenPopup
from ....engine.anim.font.scrolling import ScrollingFontHelper
from widebrim.engine.const import RESOLUTION_NINTENDO_DS
from .const import *
from ...nazo_popup.mode.base import BaseQuestionObject

class QuestionEndPopup(FullScreenPopup):
    def __init__(self, laytonState : Layton2GameState, screenController : ScreenController, callbackOnTerminate):
        super().__init__(callbackOnTerminate)

        # TODO - cleanup all these variables lmao
        self.laytonState = laytonState

        self.__buttons = []
        self.__isOnButtonScreen = False
        self._callbackOnTerminate = callbackOnTerminate

        # TODO - From base
        def getButtonObject(pathAnim, callback=None):
            if "?" in pathAnim:
                pathAnim = pathAnim.replace("?", laytonState.language.value)
            elif "%s" in pathAnim:
                pathAnim = pathAnim % laytonState.language.value

            image = getAnimFromPathWithAttributes(pathAnim)
            if image != None:
                return AnimatedButton(image, "on", "off", callback=callback)
            return None
        
        def addIfNotNone(button):
            if button != None:
                self.__buttons.append(button)

        self._textScroller = ScrollingFontHelper(laytonState.fontQ, yBias=2)
        self._textScroller.setPos((BaseQuestionObject.POS_QUESTION_TEXT[0],
                                   BaseQuestionObject.POS_QUESTION_TEXT[1] + RESOLUTION_NINTENDO_DS[1]))

        self.screenController = screenController
        entryPuzzle = laytonState.saveSlot.puzzleData.getPuzzleData(laytonState.getCurrentNazoListEntry().idExternal - 1)

        if laytonState.wasPuzzleSolved:
            # TODO - When is encountered flag set?
            # TODO - Set reward flag
            entryPuzzle.wasSolved = True
            screenController.setBgMain(PATH_BG_PASS % laytonState.getNazoData().getBgSubIndex())
            if laytonState.getNazoData().isBgLanguageDependent():
                screenController.setBgSub(PATH_BG_ANSWER_LANG % laytonState.getNazoData().getBgMainIndex())
            else:
                screenController.setBgSub(PATH_BG_ANSWER % laytonState.getNazoData().getBgMainIndex())
            self._textScroller.setText(laytonState.getNazoData().getTextCorrect())
            screenController.fadeIn()
        else:
            if not(entryPuzzle.wasSolved):
                entryPuzzle.incrementDecayStage()

            screenController.setBgMain(PATH_BG_FAIL % laytonState.getNazoData().getBgSubIndex())
            self._textScroller.setText(laytonState.getNazoData().getTextIncorrect())
            screenController.fadeInMain()

            addIfNotNone(getButtonObject(PATH_ANI_TRY_AGAIN, callback=self.__callbackOnTryAgain))
            addIfNotNone(getButtonObject(PATH_ANI_VIEW_HINT))
            addIfNotNone(getButtonObject(PATH_ANI_QUIT, callback=self.__callbackOnQuit))
        
    def update(self, gameClockDelta):
        if not(self.screenController.getFadingStatus()):
            self._textScroller.update(gameClockDelta)
    
    def draw(self, gameDisplay):
        if self.__isOnButtonScreen:
            for button in self.__buttons:
                button.draw(gameDisplay)
        else:
            self._textScroller.draw(gameDisplay)

    # TODO - same as base
    def __callbackOnQuit(self):
        self.laytonState.wasPuzzleSkipped = True
        self.screenController.fadeOut(callback=self._callbackOnTerminate)
    
    def __callbackOnTryAgain(self):
        self.laytonState.wasPuzzleRestarted = True
        self.screenController.fadeOut(callback=self._callbackOnTerminate)

    def __switchToButtonMode(self):
        self.__isOnButtonScreen = True
        self.screenController.setBgMain(PATH_BG_RETRY)
        self.screenController.fadeInMain()
    
    def handleTouchEvent(self, event):
        # TODO - Hint popup
        if not(self.screenController.getFadingStatus()):
            # TODO - Unify hiding fading status
            if self.__isOnButtonScreen:
                for button in self.__buttons:
                    button.handleTouchEvent(event)
            else:
                if not(self._textScroller.getActiveState()):
                    # Update buttons
                    # TODO - Touch overlay - hide it
                    if event.type == MOUSEBUTTONUP:
                        if self.laytonState.wasPuzzleSolved:
                            self.screenController.fadeOut(callback=self._callbackOnTerminate)
                        else:
                            self.screenController.fadeOutMain(callback=self.__switchToButtonMode)
                else:
                    if event.type == MOUSEBUTTONUP:
                        self._textScroller.skip()

        return super().handleTouchEvent(event)