# TODO - Add mode which forces fader to have strength grabbed first before it terminates
# Due to clock desyncs with inexact timing, faders can sometimes not fully obscure the screen, which allows various jumps to be seen

class Fader():

    # Transitions from 0 to 1 over time

    def __init__(self, durationHighToLow, initialActiveState=True, invertOutput = False, callbackOnDone=None, callbackClearOnDone=True):
        self._duration = durationHighToLow
        self._isActive = initialActiveState
        self._timeElapsed = 0
        self._inverted = invertOutput
        self._callback = callbackOnDone
        self._callbackClearOnDone = callbackClearOnDone
    
    def update(self, gameClockDelta):
        if self.getActiveState():
            self._timeElapsed += gameClockDelta
            if self._timeElapsed > self._duration:
                self.skip()
    
    def skip(self):
        if self.getActiveState():
            self._timeElapsed = self._duration
            self.setActiveState(False)
            self._doCallback()

    def setDuration(self, duration):

        # Change the duration of the fader. Will also reset the timer.

        self._duration = duration
        self.reset()
    
    def setCallback(self, callback):
        self._callback = callback

    def _doCallback(self):
        if callable(self._callback):
            self._callback()
            if self._callbackClearOnDone:
                self.setCallback(None)

    def setInvertedState(self, isInverted):
        self._inverted = isInverted

    def setActiveState(self, isActive):
        self._isActive = isActive
    
    def getActiveState(self):
        return self._isActive

    def reset(self):
        self._timeElapsed = 0
        self.setActiveState(True)
    
    def _calcStrength(self):
        try:
            return self._timeElapsed / self._duration
        except ZeroDivisionError:
            return 1
    
    def getStrength(self):
        strength = self._calcStrength()
        if self._inverted:
            return 1 - strength
        return strength