from __future__ import annotations

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from widebrim.engine.string.cmp import strCmp
from ....madhatter.hat_io.asset_image import Animation, getTransparentLaytonPaletted
from ...const import TIME_FRAMECOUNT_TO_MILLISECONDS
from ...convenience import initDisplay

if TYPE_CHECKING:
    from widebrim.madhatter.hat_io.asset_image.image import AnimatedImage


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
        self.isActive   = True
    
    def getActiveKeyframe(self) -> Optional[int]:
        if self.isActive and self._indexFrame < len(self.keyframes):
            return self.keyframes[self._indexFrame].indexFrame
        return None

    def updateCurrentFrame(self, gameClockDelta) -> bool:
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
    def fromMadhatter(inAnim : Animation) -> AnimationSequence:
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
        self._variables : Dict[str, List[int]]                      = {}
        self._frames : List[pygame.Surface]                         = []
        self._animations : Dict[str, AnimationSequence]             = {}
        self._indexToAnimationMap : Dict[int, AnimationSequence]    = {}

        self.subAnimation : Optional[AnimatedImageObject]   = None
        self.animActive : Optional[AnimationSequence]       = None

        self._pos : Tuple[int,int]          = (0,0)
        self._offset : Tuple[int,int]       = (0,0)
        self._dimensions : Tuple[int,int]   = (0,0) # Not guarenteed reliable, workaround for alignment techniques since measuring the surface would be annoying

        # TODO - Add alpha
        # TODO - Don't use composed frame since that preblends alpha which causes every surface to require alpha drawing instead of alpha mask

    @staticmethod
    def fromMadhatter(assetData : AnimatedImage) -> AnimatedImageObject:

        # TODO - Break dependencies on original file so it can be reused (or implement multi-animation support)

        def convertPilRgbaToPygame(imageIn):
            targetImage = imageIn
            if imageIn.mode == "P":
                targetImage = getTransparentLaytonPaletted(imageIn)
            else:
                targetImage = imageIn.convert("RGBA")
            return pygame.image.fromstring(targetImage.tobytes("raw", "RGBA"), imageIn.size, "RGBA").convert_alpha()

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

    def setVariables(self, variableDict : Dict[str, List[int]]) -> bool:
        if len(variableDict) == 16:
            self._variables = variableDict
            return True
        return False

    def getVariable(self, name) -> Optional[List[int]]:
        for key in self._variables:
            if strCmp(name, key):
                return self._variables[key]
        return None

    def _addAnimation(self, animation : AnimationSequence):
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

    def setAnimationFromIndex(self, index : int) -> bool:
        if index in self._indexToAnimationMap:  # TODO - index > 0 is given but leads to bad rendering
            if self.animActive != self._indexToAnimationMap[index]:
                self.animActive = self._indexToAnimationMap[index]
                self._setAnimationFromActive()
            return True
        return False

    def setAnimationFromName(self, name : str) -> bool:
        indexAnim = 0
        for idxAnim, key in enumerate(self._animations):
            if strCmp(name, key):
                indexAnim = idxAnim
                break
        return self.setAnimationFromIndex(indexAnim)
    
    def setCurrentAnimationLoopStatus(self, isLooping : bool) -> bool:
        if self.animActive != None:
            self.animActive.isLooping = isLooping
            return True
        return False

    def setDimensions(self, dimensions : Tuple[int,int]):
        self._dimensions = dimensions
    
    def getDimensions(self) -> Tuple[int,int]:
        return self._dimensions

    def setPos(self, pos : Tuple[int,int]):
        self._pos = pos
        if self.subAnimation != None:
            self.subAnimation.setPos(pos)
    
    def getPos(self) -> Tuple[int,int]:
        return self._pos

    def getPosWithOffset(self) -> Tuple[int,int]:
        return self._pos[0] + self._offset[0], self._pos[1] + self._offset[1]

    def getActiveFrame(self) -> Optional[pygame.Surface]:
        if self.animActive != None:
            activeFrame = self.animActive.getActiveKeyframe()
            if activeFrame != None:
                if 0 <= activeFrame < len(self._frames):
                    return self._frames[activeFrame]
        return None
    
    def wasPressed(self, cursorPos : Tuple[int,int]) -> bool:
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
            # TODO - would really like to integrate offset in (getPosWithOffset) but unsure if safe
            offset = (self._pos[0] + self._offset[0], self._pos[1] + self._offset[1])
            gameDisplay.blit(surface, offset)

        if self.subAnimation != None:
            self.subAnimation.draw(gameDisplay)