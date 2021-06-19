from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

class TargettedButton():
    def __init__(self, callbackOnPressed, callbackOnTargetted, callbackOnUntargetted):
        self._isTargetted = False
        self.callbackOnPressed = callbackOnPressed
        self.callbackOnTargetted = callbackOnTargetted
        self.callbackOnUntargetted = callbackOnUntargetted
    
    def setTargettedState(self, newState):
        if self._isTargetted != newState:
            if newState:
                if callable(self.callbackOnTargetted):
                    self.callbackOnTargetted()
                self.doOnMouseTargetting()
            else:
                if callable(self.callbackOnUntargetted):
                    self.callbackOnUntargetted()
                self.doOnMouseAwayFromTarget()

        self._isTargetted = newState

    def doOnMouseTargetting(self):
        pass

    def doOnMouseAwayFromTarget(self):
        pass

    def doBeforePressedCallback(self):
        pass

    def getTargettedState(self):
        return self._isTargetted

    def wasPressed(self, pos):
        return False

    def handleTouchEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.wasPressed(event.pos):
                self.setTargettedState(True)
                return True
            else:
                self.setTargettedState(False)

        elif event.type == MOUSEMOTION:
            if self.getTargettedState():
                if self.wasPressed(event.pos):
                    self.doOnMouseTargetting()
                else:
                    self.doOnMouseAwayFromTarget()
                return True

        elif event.type == MOUSEBUTTONUP:
            if self.getTargettedState() and self.wasPressed(event.pos):
                self.doBeforePressedCallback()
                if callable(self.callbackOnPressed):
                    self.callbackOnPressed()

                self.setTargettedState(False)
                return True

            self.setTargettedState(False)
        
        return False

class NullButton(TargettedButton):
    def __init__(self, pos, posEnd, callback=None):
        TargettedButton.__init__(self, callback, None, None)
        self._posTl = pos
        self._posBr = posEnd
        self.setPos(pos)
    
    def getPos(self):
        return self._posTl

    def setPos(self, newPos):
        length = (self._posBr[0] - self._posTl[0], self._posBr[1] - self._posTl[1])
        self._posTl = newPos
        self._posBr = (newPos[0] + length[0], newPos[1] + length[1])

    def wasPressed(self, pos):
        if pos[0] >= self._posTl[0] and pos[1] >= self._posTl[1]:
            if pos[0] <= self._posBr[0] and pos[1] <= self._posBr[1]:
                return True
        return False

class StaticButton(NullButton):
    def __init__(self, pos, surfaceButton, callback=None, targettedOffset=(0,0)):
        self._image = surfaceButton
        self._offset = targettedOffset
        self._imageBlitPos = (0,0)
        self._offsetBlitPos = (0,0)
        NullButton.__init__(self, pos, (pos[0] + surfaceButton.get_width(), pos[1] + surfaceButton.get_height()), callback=callback)
    
    def setPos(self, newPos):
        super().setPos(newPos)
        self._imageBlitPos = self._posTl
        self._offsetBlitPos = (self._imageBlitPos[0] + self._offset[0], self._imageBlitPos[1] + self._offset[1])

    def doOnMouseTargetting(self):
        self._imageBlitPos = self._offsetBlitPos

    def doOnMouseAwayFromTarget(self):
        self._imageBlitPos = self._posTl
    
    def draw(self, gameDisplay):
        gameDisplay.blit(self._image, self._imageBlitPos)

class AnimatedButton(TargettedButton):

    # TODO - Unify drawables to have a draw method
    def __init__(self, image, animNamePressed, animNameUnpressed, callback=None):
        TargettedButton.__init__(self, callback, None, None)
        self._animNamePressed = animNamePressed
        self._animNameUnpressed = animNameUnpressed
        self.image = image
        self.image.setAnimationFromName(self._animNameUnpressed)
        self.__customDimensions = None
    
    def update(self, gameClockDelta):
        self.image.update(gameClockDelta)
    
    def setDimensions(self, dimensions):
        # TODO - Check and add to targetted button.
        self.__customDimensions = dimensions

    def draw(self, gameDisplay):
        self.image.draw(gameDisplay)

    def doOnMouseTargetting(self):
        if self.image.animActive != None and self.image.animActive.name != self._animNamePressed:
            self.image.setAnimationFromName(self._animNamePressed)
    
    def doOnMouseAwayFromTarget(self):
        if self.image.animActive != None and self.image.animActive.name != self._animNameUnpressed:
            self.image.setAnimationFromName(self._animNameUnpressed)
    
    def wasPressed(self, pos):
        if self.__customDimensions != None:
            if pos[0] >= self.image.getPos()[0] and pos[1] >= self.image.getPos()[1]:
                if pos[0] <= (self.image.getPos()[0] + self.__customDimensions[0]) and pos[1] <= (self.image.getPos()[1] + self.__customDimensions[1]):
                    return True
            return False
        return self.image.wasPressed(pos)