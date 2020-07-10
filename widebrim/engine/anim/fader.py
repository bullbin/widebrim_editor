class Fader():

    # Transitions from 0 to 1 over time

    def __init__(self, durationHighToLow, initialActiveState=True, invertOutput = False):
        self._duration = durationHighToLow
        self._isActive = initialActiveState
        self._timeElapsed = 0
        self._inverted = invertOutput
    
    def update(self, gameClockDelta):
        if self._isActive:
            self._timeElapsed += gameClockDelta
            if self._timeElapsed > self._duration:
                self._timeElapsed = self._duration
                self._isActive = False
    
    def setDuration(self, duration):

        # Change the duration of the fader. Will also reset the timer.

        self._duration = duration
        self.reset()
    
    def setInvertedState(self, isInverted):
        self._inverted = isInverted

    def setActiveState(self, isActive):
        self._isActive = isActive
    
    def getActiveState(self):
        return self._isActive

    def reset(self):
        self._timeElapsed = 0
        self._isActive = True
    
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