from time import perf_counter
from typing import Any, Optional
from editor.d_pickerBgx import DialogPickerBgx
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from widebrim.engine.state.manager.state import Layton2GameState
from filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.common import logSevere
from widebrim.madhatter.hat_io.asset_image.image import AnimatedImage

from pygame.image import tostring
from pygame import Surface
from wx import Bitmap, Timer, EVT_TIMER, NullBitmap, EVT_CLOSE

# TODO - Basic image import (really needs widebrim anim module rewrite...)
# TODO - Will this crash on the close button? What is triggered?

class DialogPickerLimitedAnim(DialogPickerBgx):
    def __init__(self, parent, state : Layton2GameState, fileAccessor : WriteableFilesystemCompatibilityLayer, pathRoot : str, reMatchString : Optional[str] = None, defaultPathRelative : Optional[str] = None, allowEmptyImage=False):
        super().__init__(parent, state, fileAccessor, pathRoot, reMatchString=reMatchString, defaultPathRelative=None)
        self.SetTitle("Change Animation")
        if allowEmptyImage:
            self.btnRemoveImage.Show()
            self.Layout()
        
        self.timerAnimationLastUpdateTime   = 0
        self.timerAnimation                 = Timer(self)
        self.Bind(EVT_TIMER, self.__updateActiveAnimation, self.timerAnimation)
        self.Bind(EVT_CLOSE, self.__onClose)

        self.activeAnimation                : Optional[AnimatedImageObject] = None
        self.activeAnimationFrame           : Optional[Surface]             = None
        
        if defaultPathRelative != None:
            self.setDefaultRelativePath(defaultPathRelative)
    
    def __updateActiveAnimation(self, event : Optional[Any]):
        if self.activeAnimation == None:
            if self.activeAnimationFrame != None:
                self.activeAnimationFrame = None
                self.bitmapPreviewBackground.SetBitmap(NullBitmap)
            return
        
        updateTime = perf_counter()
        self.activeAnimation.update((updateTime - self.timerAnimationLastUpdateTime) * 1000)
        self.timerAnimationLastUpdateTime = updateTime
        if (newFrame := self.activeAnimation.getActiveFrame()) != self.activeAnimationFrame:
            self.activeAnimationFrame = newFrame
        else:
            return
        
        if self.activeAnimationFrame == None:
            self.bitmapPreviewBackground.SetBitmap(NullBitmap)
        else:
            bitmap = Bitmap.FromBufferRGBA(self.activeAnimationFrame.get_width(), self.activeAnimationFrame.get_height(), tostring(self.activeAnimationFrame, "RGBA"))
            self.bitmapPreviewBackground.SetBitmap(bitmap)
        
        if event != None:
            event.Skip()

    def __onClose(self, event):
        self.timerAnimation.Stop()
        event.Skip()

    def _doOnSuccessfulImage(self):
        self.timerAnimation.Stop()
        return super()._doOnSuccessfulImage()

    def btnCancelOnButtonClick(self, event):
        self.timerAnimation.Stop()
        return super().btnCancelOnButtonClick(event)

    def btnRemoveImageOnButtonClick(self, event):
        self._pathOut = ""
        self._doOnSuccessfulImage()
        return super().btnRemoveImageOnButtonClick(event)

    def _pathExternalToInternal(self, value: str):
        subsPath = value.replace("/?/", "/" + self.fileAccessor.getLanguage().value + "/")
        if len(subsPath) > 4 and subsPath[-4:] == ".spr":
            subsPath = subsPath[:-4] + ".arc"
        return subsPath

    def _updatePreviewImage(self, path) -> bool:
        # TODO - Can we allow subanimation?
        # TODO - Top screen animation
        # TODO - wx timer for anim (forseeing flicker)
        dataAnim = self.fileAccessor.getData(path)
        if dataAnim == None:
            logSevere("Failed", path)
            return False

        
        tempImage = AnimatedImage.fromBytesArc(dataAnim)
        self.activeAnimation = AnimatedImageObject.fromMadhatter(tempImage)

        # TODO - This or gfx?
        self.activeAnimation.setAnimationFromIndex(1)
        self.timerAnimation.Stop()
        self.timerAnimationLastUpdateTime = perf_counter()

        self.__updateActiveAnimation(None)
        self.timerAnimation.Start(1000//60, False)
        self._pathOut = path
        self.btnConfirmSelected.Enable()
        return True

    def btnImportImageOnButtonClick(self, event):
        pass