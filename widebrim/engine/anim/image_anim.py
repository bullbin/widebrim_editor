from ...madhatter.hat_io.asset_image import Animation
from ..const import TIME_FRAMECOUNT_TO_MILLISECONDS

# TODO - Fix imports for only image
import pygame
# TODO - Init display centrally elsewhere
pygame.display.set_mode((256, 384))

class AnimationSequence(Animation):
    def __init__(self):
        Animation.__init__(self)
        self.isLooping  = True
        self.isActive   = True
        # TODO - This can be carried into AnimatedImageObject to reduce overlap between anims
        self._indexFrame = 0
        self._elapsedFrame = 0
    
    def reset(self):
        self._indexFrame = 0
        self._elapsedFrame = 0
    
    def getActiveKeyframe(self):
        if self.isActive:
            return self.keyframes[self._indexFrame].indexFrame
        return None

    def updateCurrentFrame(self, gameClockDelta):
        if self.isActive:
            self._elapsedFrame += gameClockDelta
            while self.keyframes[self._indexFrame].duration <= self._elapsedFrame and self.isActive:
                nextFrameIndex = (self._indexFrame + 1) % len(self.keyframes)
                if nextFrameIndex < self._indexFrame and not(self.isLooping):
                    self.isActive = False
                else:
                    self._elapsedFrame -= self.keyframes[self._indexFrame].duration
                    self._indexFrame = nextFrameIndex

    @staticmethod
    def fromMadhatter(inAnim):
        output = AnimationSequence()
        output.name = inAnim.name
        output.keyframes = inAnim.keyframes
        for keyframe in output.keyframes:
            keyframe.duration *= TIME_FRAMECOUNT_TO_MILLISECONDS
        output.subAnimationIndex = inAnim.subAnimationIndex
        output.subAnimationOffset = inAnim.subAnimationOffset
        return output

class AnimatedImageObject():
    def __init__(self):
        self._frames = []
        self._animations = {}
        self._indexToAnimationMap = {}
        self.subAnimation = None

        self.animActive = None
        self._pos = (0,0)
        self._offset = (0,0)

        # TODO - Add alpha
        # TODO - Don't use composed frame since that preblends alpha which causes every surface to require alpha drawing instead of alpha mask
        # TODO - Support multiple animations running simultaneously (used in LAYTON3)

    @staticmethod
    def fromMadhatter(assetData):

        # TODO - Break dependencies on original file so it can be reused (or implement multi-animation support)

        def convertPilRgbaToPygame(imageIn):
            return pygame.image.fromstring(imageIn.tobytes("raw", "RGBA"), imageIn.size, "RGBA").convert_alpha()

        output = AnimatedImageObject()
        for frame in assetData.frames:
            output._frames.append(convertPilRgbaToPygame(frame.getComposedFrame()))

        for anim in assetData.animations:
            output._addAnimation(AnimationSequence.fromMadhatter(anim))
        
        if assetData.subAnimation != None:
            output.subAnimation = AnimatedImageObject.fromMadhatter(assetData.subAnimation)
        
        return output

    def _addAnimation(self, animation):
        self._indexToAnimationMap[len(self._animations)] = animation
        self._animations[animation.name] = animation

    def _setAnimationFromActive(self):
        if self.animActive == None:
            if self.subAnimation != None:
                self.subAnimation.setAnimationFromName(None)
                self.subAnimation._offset = (0,0)
        else:
            self.animActive.reset()
            if self.subAnimation != None:
                self.subAnimation.setAnimationFromIndex(self.animActive.subAnimationIndex)
                self.subAnimation._offset = self.animActive.subAnimationOffset

    def setAnimationFromName(self, name):
        if name in self._animations:
            self.animActive = self._animations[name]
        else:
            self.animActive = None
        self._setAnimationFromActive()
    
    def setAnimationFromIndex(self, index):
        if index in self._indexToAnimationMap:
            self.animActive = self._indexToAnimationMap[index]
        else:
            self.animActive = None
        self._setAnimationFromActive()

    def setPos(self, pos):
        self._pos = pos
        if self.subAnimation != None:
            self.subAnimation.setPos(pos)

    def _getActiveFrame(self):
        if self.animActive != None:
            activeFrame = self.animActive.getActiveKeyframe()
            if activeFrame != None:
                if 0 <= activeFrame < len(self._frames):
                    return self._frames[activeFrame]
        return None

    def update(self, gameClockDelta):
        if self.animActive != None:
            self.animActive.updateCurrentFrame(gameClockDelta)
        if self.subAnimation != None:
            self.subAnimation.update(gameClockDelta)

    def draw(self, gameDisplay):
        
        surface = self._getActiveFrame()
        if surface != None:
            offset = (self._pos[0] + self._offset[0], self._pos[1] + self._offset[1])
            gameDisplay.blit(surface, offset)

        if self.subAnimation != None:
            self.subAnimation.draw(gameDisplay)