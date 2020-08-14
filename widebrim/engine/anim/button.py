from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

class NullButton():
    def __init__(self, pos, posEnd, callback=None):
        self._posTl = pos
        self._posBr = posEnd
        self._callback = callback
    
    def handleTouchEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.pos[0] >= self._posTl[0] and event.pos[1] >= self._posTl[1]:
                if event.pos[0] <= self._posBr[0] and event.pos[1] <= self._posBr[1]:
                    if callable(self._callback):
                        self._callback()

class AnimatedButton():
    def __init__(self, image, animNamePushed, animNameUnpushed, callback=None):
        self.image = image
        self._animNamePushed    = animNamePushed
        self._animNameUnpushed  = animNameUnpushed
        self.image.setAnimationFromName(self._animNameUnpushed)

        self._isTargetted = False
        self._callback = callback
    
    def update(self, gameClockDelta):
        self.image.update(gameClockDelta)
    
    def draw(self, gameDisplay):
        self.image.draw(gameDisplay)
    
    def handleTouchEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # If the button was pressed, start the pressed animation
            if self.image.wasPressed(event.pos):
                self._isTargetted = True
                self.image.setAnimationFromName(self._animNamePushed)
            else:
                if self._isTargetted:
                    self.image.setAnimationFromName(self._animNameUnpushed)
                self._isTargetted = False

        elif event.type == MOUSEMOTION:
            # Judder between pressed and unpressed as mouse hovers over button
            if self._isTargetted:
                if self.image.wasPressed(event.pos):
                    if self.image.animActive != None and self.image.animActive.name != self._animNamePushed:
                        self.image.setAnimationFromName(self._animNamePushed)

                elif self.image.animActive != None and self.image.animActive.name != self._animNameUnpushed:
                    self.image.setAnimationFromName(self._animNameUnpushed)
        
        elif event.type == MOUSEBUTTONUP:
            # When mouse is released and the button was being targetted, do the callback.
            if self._isTargetted and self.image.wasPressed(event.pos):
                self.image.setAnimationFromName(self._animNameUnpushed)
                if callable(self._callback):
                    self._callback()
            self._isTargetted = False