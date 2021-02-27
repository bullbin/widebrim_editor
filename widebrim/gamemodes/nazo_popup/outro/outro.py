from widebrim.engine.const import RESOLUTION_NINTENDO_DS
from ...core_popup.utils import FullScreenPopup
from ....engine.anim.fader import Fader
from ....engine_ext.utils import getImageFromPath
from ....engine.state.enum_mode import GAMEMODES
from .const import *
from .end import QuestionEndPopup

# TODO - Refer to annotated function to finish implementing this...
#        DO NOT FORGET TO MARK PUZZLES AS SOLVED BY USING THE VARIABLE IN LAYTONSTATE

# TODO - 27_Question - remember to set solved and decay flags, reward

class JudgementPopup(FullScreenPopup):
    # Note that this popup is an exception to the general rule that every popup should end with both faders activated
    # This is because its replacing a shared function in the game to do the judgement animation, which ends with a correct
    #     or failed screen at the top

    # TODO - Cache all images at start, since that is causing stutter

    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(callbackOnTerminate)
        self.laytonState = laytonState
        self.screenController = screenController

        self.screenController.setBgMain(None)
        self.screenController.setBgSub(None)

        if self.laytonState.wasPuzzleSolved:
            self._indexImages = JUDGE_INDEX_PASS
        else:
            self._indexImages = JUDGE_INDEX_FAIL
        
        if self.laytonState.getNazoData() != None:
            if self.laytonState.getNazoData().isAltCharacterUsed():
                self._charCharacter = CHAR_CHARACTER_1
            else:
                self._charCharacter = CHAR_CHARACTER_0
        else:
            self._charCharacter = CHAR_CHARACTER_0
    
        self._indexFrame = -1
        self._indexWait = 0
        self._indexImage = 0

        self.screenController.fadeIn(callback=self._triggerFadeOutIfLate)
        self._animTimer = Fader(0, initialActiveState=False)
        self._prepareNextFrame()

        self._surfScrollingScreen = None
        self._isScrollingPopup = False

        # TODO - unify setting callback
        self._callback = callbackOnTerminate
        self._waitingToSetBgAndEnd = False

    def update(self, gameClockDelta):
        self._animTimer.update(gameClockDelta)
        if self._waitingToSetBgAndEnd:
            self._waitingToSetBgAndEnd = False
            self.screenController.setBgSub(self._getFramePath())
            if callable(self._callback):
                self.screenController.fadeOutMain(0)
                self._callback()
                self._callback = None

    def draw(self, gameDisplay):
        if self._isScrollingPopup:
            if self._surfScrollingScreen != None:
                # don't invert for ease of reading
                y = round(RESOLUTION_NINTENDO_DS[1] * (1 - self._animTimer.getStrength()))
                gameDisplay.blit(self._surfScrollingScreen, (0,y))

            # Done like this to prevent hung frame at end while next popup is loading
            if self._animTimer.getStrength() == 1.0:
                self._waitingToSetBgAndEnd = True
                self._isScrollingPopup = False

    def _triggerFadeOutIfLate(self):
        if self._indexImages[self._indexFrame] == 0:
            self._doWaitBetweenFades()

    def _prepareNextFrame(self):
        if self._indexFrame < len(self._indexImages) - 1:
            self._indexFrame += 1
            if self._indexImages[self._indexFrame] == 0:
                if not(self.screenController.getFadingStatus()):
                    self._doWaitBetweenFades()
            else:
                self._applyFrame()
                self._startNextTimer()
        else:
            self._surfScrollingScreen = getImageFromPath(self.laytonState, self._getFramePath())
            if self._surfScrollingScreen == None:
                # Missed the frame, so immediately start callback
                self._waitingToSetBgAndEnd = True
            else:
                self.screenController.setBgMain(None)
                self._isScrollingPopup = True
                self._animTimer.setDuration(250)
                # TODO - Wait before fade out

    def _doWaitBetweenFades(self):
        self._animTimer.setDurationInFrames(6)
        self._animTimer.setCallback(self._doFadeOutFrame)

    def _doFadeOutFrame(self):
        self.screenController.fadeOutMain(callback=self._doWaitBeforeFadeIn)
    
    def _doWaitBeforeFadeIn(self):
        self._animTimer.setDurationInFrames(JUDGE_PARAM_WAIT[self._indexWait])
        self._animTimer.setCallback(self._doFadeInFrame)
        self._indexWait += 1

    def _doFadeInFrame(self):
        self.screenController.fadeInMain(callback=self._triggerFadeOutIfLate)
        self._prepareNextFrame()

    def _startNextTimer(self):
        self._animTimer.setDurationInFrames(JUDGE_PARAM_DEFAULT[self._indexImage])
        self._indexImage += 1
        self._animTimer.setCallback(self._prepareNextFrame)

    def _getFramePath(self):
        if self._indexImages[self._indexFrame] in INDEX_IMAGE_FINAL:
            return PATH_BG_LANGUAGE % (self._charCharacter, self._indexImages[self._indexFrame])
        return PATH_BG % (self._charCharacter, self._indexImages[self._indexFrame])

    def _applyFrame(self):
        self.screenController.setBgMain(self._getFramePath())

class OutroLayer(FullScreenPopup):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        FullScreenPopup.__init__(self, callbackOnTerminate)
        # Does the outro animation, and then displays either the fail screen or correct screen when done
        # DoFailHantei, DoCorrectHantei

        #     So when are picarats reduced?
        # If hint button pressed, a hint screen is attached and drawn over current state.
        self._callbackOnTerminate = callbackOnTerminate
        self.laytonState = laytonState
        self.screenController = screenController
        self._popup = JudgementPopup(laytonState, screenController, self._getNextPopup)
    
    def _getNextPopup(self):
        entryPuzzle = self.laytonState.saveSlot.puzzleData.getPuzzleData(self.laytonState.getCurrentNazoListEntry().idExternal - 1)
        if self.laytonState.wasPuzzleSolved:
            if not(entryPuzzle.wasSolved):
                if self.laytonState.getGameModeNext() != GAMEMODES.Jiten1 and self.laytonState.getCurrentNazoListEntry().idInternal != 0xce:
                    # TODO - Set picarats better lol
                    picaratsGained = self.laytonState.getNazoData().getPicaratStage(entryPuzzle.levelDecay)
                    self.laytonState.saveSlot.picarats += picaratsGained
                    # TODO - Picarats add screen
            self.screenController.fadeOut(callback=self._switchToModeEnd)
        else:
            self.screenController.fadeOutMain(callback=self._switchToModeEnd)

    # TODO - Reward, see question end stuff
    def _switchToModeEnd(self):
        # If it wasn't solved, add a callback to a handler with the retry buttons.
        # If solved, jump to another handler with the congratulations message
        self._popup = QuestionEndPopup(self.laytonState, self.screenController, self._callbackOnTerminate)

    def update(self, gameClockDelta):
        if self._popup != None:
            self._popup.update(gameClockDelta)
    
    def draw(self, gameDisplay):
        if self._popup != None:
            self._popup.draw(gameDisplay)
    
    def handleTouchEvent(self, event):
        if self._popup != None:
            return self._popup.handleTouchEvent(event)
        return super().handleTouchEvent(event)