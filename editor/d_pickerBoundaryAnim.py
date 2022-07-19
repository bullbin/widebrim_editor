from time import perf_counter
from editor.d_pickerBoundary import DialogChangeBoundaryPygame
from wx import Bitmap, BufferedPaintDC, NullBitmap, EVT_TIMER, Timer, Image, IMAGE_QUALITY_NEAREST, Rect, Point
from typing import Any, Optional, Tuple
from pygame import Surface
from pygame.image import tostring
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from widebrim.madhatter.hat_io.asset_dat.place import BoundingBox

# TODO - Sort out imports
# TODO - Handle case with no bounds (handles will be impossible to grab!)
def _scaleBitmap(bitmap : Bitmap):
    image : Image = bitmap.ConvertToImage()
    image = image.Scale(bitmap.GetWidth() * 2, bitmap.GetHeight() * 2, IMAGE_QUALITY_NEAREST)
    return image.ConvertToBitmap()

class DialogChangeBoundaryWithSpritePositioning(DialogChangeBoundaryPygame):

    def __init__(self, parent, bitmap: Surface, animation : AnimatedImageObject, boundary: BoundingBox, color: Tuple[int, int, int] = (255,0,0), highlightWidth: int = 4):
        super().__init__(parent, bitmap, boundary, color, highlightWidth)
        self.__animPreview : AnimatedImageObject = animation
        self.__timerAnimationLastUpdateTime   = perf_counter()
        self.__animPreview.update(0)

        self.__timerAnimation                 = Timer(self)
        self.Bind(EVT_TIMER, self.__updateActiveAnimation, self.__timerAnimation)
        self._lastPaintedFrame : Optional[Surface] = None
        self._lastPaintedBitmap : Optional[Bitmap] = None
        self._bitmapCache = {}
        self.__timerAnimation.Start(1000//60, False)
        self.btnSetBoundaryFromAnim.Show()
        self.Layout()

    def __updateActiveAnimation(self, event : Optional[Any]):
        currentTime = perf_counter()
        self.__animPreview.update((currentTime - self.__timerAnimationLastUpdateTime) * 1000)
        self.__timerAnimationLastUpdateTime = currentTime
        if self._lastPaintedFrame != self.__animPreview.getActiveFrame():
            self.panelBitmap.Refresh(eraseBackground=False)
        
        if event != None:
            event.Skip()

    def btnAgreeOnButtonClick(self, event):
        self.__timerAnimation.Stop()
        return super().btnAgreeOnButtonClick(event)

    def btnCancelOnButtonClick(self, event):
        self.__timerAnimation.Stop()
        return super().btnCancelOnButtonClick(event)

    def panelBitmapOnPaint(self, event):

        dc = BufferedPaintDC(self.panelBitmap)
        dc.Clear()

        def drawCharBitmap():
            activeFrame = self.__animPreview.getActiveFrame()
            if activeFrame != self._lastPaintedFrame:
                if activeFrame != None:
                    if activeFrame not in self._bitmapCache:
                        self._bitmapCache[activeFrame] = _scaleBitmap(Bitmap.FromBufferRGBA(activeFrame.get_width(), activeFrame.get_height(), tostring(activeFrame, "RGBA")))
                    self._lastPaintedBitmap = self._bitmapCache[activeFrame]
                else:
                    self._lastPaintedBitmap = NullBitmap
                self._lastPaintedFrame = activeFrame
            
            minPinX = min(self._coordPin.x, self._coordActive.x)
            minPinY = min(self._coordPin.y, self._coordActive.y)
            dc.DrawBitmap(self._lastPaintedBitmap, minPinX, minPinY, useMask=True)

        dc.DrawBitmap(self._bitmap, 0, 0)
        self._paintOutline(dc)
        drawCharBitmap()
        self._paintHandles(dc)

    def _setBoundsFromAnim(self):
        # TODO - Unify scale
        sizeX, sizeY = self.__animPreview.getDimensions()
        rectArea = Rect(self._coordActive, self._coordPin)
        topLeft = rectArea.GetTopLeft()
        bottomRight = Point(topLeft.x + (sizeX * 2), topLeft.y + (sizeY * 2))
        self._coordActive = topLeft
        self._coordPin = bottomRight
        self._coordActive.x = max(min(self._coordActive.x, self.panelBitmap.GetSize().x), 0)
        self._coordActive.y = max(min(self._coordActive.y, self.panelBitmap.GetSize().y), 0)
        self._coordPin.x = max(min(self._coordPin.x, self.panelBitmap.GetSize().x), 0)
        self._coordPin.y = max(min(self._coordPin.y, self.panelBitmap.GetSize().y), 0)

    def btnSetBoundaryFromAnimOnButtonClick(self, event):
        self._setBoundsFromAnim()
        self.panelBitmap.Refresh(eraseBackground=False)
        return super().btnSetBoundaryFromAnimOnButtonClick(event)