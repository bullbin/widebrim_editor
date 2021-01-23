from ....madhatter.hat_io.asset_image import Animation
from ...const import TIME_FRAMECOUNT_TO_MILLISECONDS
from ...convenience import initDisplay

# TODO - Fix imports for only image
import pygame
initDisplay()

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
        if self.isActive and self._indexFrame < len(self.keyframes):
            return self.keyframes[self._indexFrame].indexFrame
        return None

    def updateCurrentFrame(self, gameClockDelta):
        if self.isActive:
            self._elapsedFrame += gameClockDelta
            previousFrame = self._indexFrame
            while self._indexFrame < len(self.keyframes) and self.keyframes[self._indexFrame].duration <= self._elapsedFrame and self.isActive:
                nextFrameIndex = (self._indexFrame + 1) % len(self.keyframes)
                if nextFrameIndex < self._indexFrame and not(self.isLooping):
                    self.isActive = False
                else:
                    self._elapsedFrame -= self.keyframes[self._indexFrame].duration
                    self._indexFrame = nextFrameIndex
            return previousFrame != self._indexFrame
        return False

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
        self._variables = {}
        self._frames = []
        self._animations = {}
        self._indexToAnimationMap = {}
        self.subAnimation = None

        self.animActive = None
        self._pos = (0,0)
        self._offset = (0,0)

        # Not guarenteed reliable, workaround for alignment techniques since measuring the surface would be annoying
        self._dimensions = (0,0)

        # TODO - Add alpha
        # TODO - Don't use composed frame since that preblends alpha which causes every surface to require alpha drawing instead of alpha mask
        # TODO - Support multiple animations running simultaneously (used in LAYTON3)
        # TODO - Add alignment options, primarily for characters

    @staticmethod
    def fromMadhatter(assetData):

        # TODO - Break dependencies on original file so it can be reused (or implement multi-animation support)

        def convertPilRgbaToPygame(imageIn):
            return pygame.image.fromstring(imageIn.tobytes("raw", "RGBA"), imageIn.size, "RGBA").convert_alpha()

        output = AnimatedImageObject()
        output.setVariables(assetData.variables)
        tempDimensions = (0,0)
        for frame in assetData.frames:
            tempPygameFrame = convertPilRgbaToPygame(frame.getComposedFrame())
            output._frames.append(tempPygameFrame)
            tempDimensions = (max(tempPygameFrame.get_width(), tempDimensions[0]),
                              max(tempPygameFrame.get_height(), tempDimensions[1]))

        output.setDimensions(tempDimensions)

        for anim in assetData.animations:
            output._addAnimation(AnimationSequence.fromMadhatter(anim))
        
        if assetData.subAnimation != None:
            output.subAnimation = AnimatedImageObject.fromMadhatter(assetData.subAnimation)
        
        return output

    def setVariables(self, variableDict):
        if len(variableDict) == 16:
            self._variables = variableDict

    def getVariable(self, name):
        if name in self._variables:
            return self._variables[name]
        return None

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

        def searchFirstNullTerminatedString(inString):
            # Catches b2 normal on Layton.
            # TODO - Check string compare function
            # TODO - Check if anim reset if same anim set twice
            inString = inString.split("\x00")[0]
            for key in self._animations:
                lengthShortest = min(len(name), len(key))
                if key[0:lengthShortest] == inString[0:lengthShortest]:
                    return self._animations[key]
            return None 

        if name in self._animations:
            self.animActive = self._animations[name]
        elif type(name) == str:
            self.animActive = searchFirstNullTerminatedString(name)
        self._setAnimationFromActive()
        return not(self.animActive == None)
    
    def setDimensions(self, dimensions):
        self._dimensions = dimensions
    
    def getDimensions(self):
        return self._dimensions

    def setAnimationFromIndex(self, index):
        if index in self._indexToAnimationMap:
            self.animActive = self._indexToAnimationMap[index]
        else:
            self.animActive = None
        self._setAnimationFromActive()
        return not(self.animActive == None)

    def setPos(self, pos):
        self._pos = pos
        if self.subAnimation != None:
            self.subAnimation.setPos(pos)
    
    def getPos(self):
        return self._pos

    def getActiveFrame(self):
        if self.animActive != None:
            activeFrame = self.animActive.getActiveKeyframe()
            if activeFrame != None:
                if 0 <= activeFrame < len(self._frames):
                    return self._frames[activeFrame]
        return None
    
    def wasPressed(self, cursorPos):
        if self._pos[0] <= cursorPos[0] and self._pos[1] <= cursorPos[1]:
            if (self._pos[0] + self._dimensions[0]) >= cursorPos[0] and (self._pos[1] + self._dimensions[1]) >= cursorPos[1]:
                return True
        return False

    def update(self, gameClockDelta):
        hasMainFrameChanged = False
        hasSubFrameChanged = False
        if self.animActive != None:
            hasMainFrameChanged = self.animActive.updateCurrentFrame(gameClockDelta)
        if self.subAnimation != None:
            hasSubFrameChanged = self.subAnimation.update(gameClockDelta)
        return hasMainFrameChanged or hasSubFrameChanged

    def draw(self, gameDisplay):
        
        surface = self.getActiveFrame()
        if surface != None:
            offset = (self._pos[0] + self._offset[0], self._pos[1] + self._offset[1])
            gameDisplay.blit(surface, offset)

        if self.subAnimation != None:
            self.subAnimation.draw(gameDisplay)