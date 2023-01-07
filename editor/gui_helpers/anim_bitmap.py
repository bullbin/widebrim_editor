from time import perf_counter
from typing import Optional
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from wx import StaticBitmap, Bitmap
from pygame import Surface
from pygame.image import tostring

class AnimationUpdater():
    def __init__(self, image : Optional[AnimatedImageObject], destBitmap : Optional[StaticBitmap]):
        """GUI handler that converts an in-engine animated image to a StaticBitmap element.
        For this to animate, the update() method must be routinely called. No timer is provided to reduce chance of crashing.

        Args:
            image (Optional[AnimatedImageObject]): Input in-engine image. If no image is provided, the output bitmap will be cleared.
            destBitmap (Optional[StaticBitmap]): Destination wxStaticBitmap element. If no image is provided, the animation will not be rendered.
        """
        self.__activeAnimation      : Optional[AnimatedImageObject] = image
        self.__bitmap               : Optional[StaticBitmap] = destBitmap
        
        self.__lastUpdateTime       : float     = perf_counter()

        if image != None:
            self.__activeSurf           : Surface   = Surface(image.getDimensions()).convert_alpha()
        else:
            self.__activeSurf           : Surface   = Surface((1,1)).convert_alpha()

        self.__queueRedraw          : bool      = False
        self.__hidden               : bool      = False

        self.__activeSurf.fill((0,0,0,0))

    def changeBitmap(self, destBitmap : Optional[StaticBitmap]):
        """Changes render target to another bitmap.

        Args:
            destBitmap (Optional[StaticBitmap]): wxStaticBitmap for destination blit. If no image is provided, the animation will not be rendered.
        """
        self.__bitmap = destBitmap
        self.__queueRedraw = True

    def setAnimationFromName(self, name : str) -> bool:
        """Changes the active animation by name.

        Args:
            name (str): Name of new animation.

        Returns:
            bool: True if animation is now that corresponding to the name.
        """
        if self.__activeAnimation == None:
            return False

        # TODO - Bugfix, we want True even on changing to same anim (unlike game...)
        self.__activeAnimation.setAnimationFromName(name)
        self.__queueRedraw = True

        output = True
        if self.__activeAnimation.animActive == None:
            output = False
        elif self.__activeAnimation.animActive.name != name:
            output = False
        else:
            # We have changed the animation, update the frame
            self.update()

        self.__hidden = not(output)
        return output
    
    def setAnimationFromIndex(self, idx : int) -> bool:
        """Changes the active animation by index. The logic of this is different to setAnimationByName.

        Args:
            idx (int): Index of animation.

        Returns:
            bool: True if there is an animation to be displayed.
        """
        if self.__activeAnimation == None:
            return False

        self.__queueRedraw = True
        self.__hidden = not(self.__activeAnimation.setAnimationFromIndex(idx))
        if not(self.__hidden):
            self.update()

        # TODO - Replicate above path
        return not(self.__hidden)

    def triggerRedraw(self, reset_timer : bool = False):
        """Triggers the attached bitmap to be redrawn with the active animation.

        Args:
            reset_timer (bool, optional): Resets accumulated time, preventing animations from jumping forward. Defaults to False.
        """
        self.__queueRedraw = True
        if reset_timer:
            self.__lastUpdateTime = perf_counter()
        self.update()

    def update(self):
        """Updates and renders the active animation. If no animation is loaded, a blank image will be rendered.
        This method must be called periodically.
        """
        if self.__bitmap == None or self.__activeAnimation == None:
            self.__lastUpdateTime = perf_counter()
            if self.__bitmap != None and self.__activeAnimation == None:
                bitmap = Bitmap.FromBufferRGBA(self.__activeSurf.get_width(), self.__activeSurf.get_height(), tostring(self.__activeSurf, "RGBA"))
                self.__bitmap.SetBitmap(bitmap)
            self.__queueRedraw = False
            return

        updateTime = perf_counter()
        if self.__activeAnimation.update((updateTime - self.__lastUpdateTime) * 1000) or self.__queueRedraw:
            self.__activeSurf.fill((0,0,0,1))
            if not(self.__hidden):
                prevPos = self.__activeAnimation.getPos()
                self.__activeAnimation.setPos((0,0))
                self.__activeAnimation.draw(self.__activeSurf)
                self.__activeAnimation.setPos(prevPos)

            bitmap = Bitmap.FromBufferRGBA(self.__activeSurf.get_width(), self.__activeSurf.get_height(), tostring(self.__activeSurf, "RGBA"))
            self.__bitmap.SetBitmap(bitmap)
            self.__queueRedraw = False
        self.__lastUpdateTime = updateTime