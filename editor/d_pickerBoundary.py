from typing import Tuple
from .nopush_editor import PickerChangeBoundary
from pygame import Surface
from pygame.image import tostring
from wx import Bitmap, Pen, Brush, PENSTYLE_SOLID, BRUSHSTYLE_TRANSPARENT, IMAGE_QUALITY_NEAREST, BufferedPaintDC, Point, Rect, Image, Colour, ID_CANCEL, ID_OK
from widebrim.madhatter.hat_io.asset_dat.place import BoundingBox

def _scaleBitmap(bitmap : Bitmap):
    image : Image = bitmap.ConvertToImage()
    image = image.Scale(512, 384, IMAGE_QUALITY_NEAREST)
    return image.ConvertToBitmap()

def _scalePointUp(point : Point) -> Point:
    return Point(round(point.x * 2), round(point.y * 2))

def _scalePointDown(point : Point) -> Point:
    return Point(round(point.x / 2), round(point.y / 2))

class DialogChangeBoundary(PickerChangeBoundary):
    def __init__(self, parent, bitmap : Bitmap, boundary : BoundingBox, color : Tuple[int, int, int] = (255,0,0), highlightWidth : int = 4):
        super().__init__(parent)
        self.__color = Colour(color[0], color[1], color[2])
        self.__width = highlightWidth
        self.__coordPin = Point(0,0)
        self.__coordActive = Point(0,0)
        self.__drawing = False
        self.__bitmap = bitmap

        self.btnReset.Disable()
        self.__originalBounding = boundary
        self.__loadBoundary(boundary)

    def __toBoundary(self) -> BoundingBox:
        smallActive = _scalePointDown(self.__coordActive)
        smallPin = _scalePointDown(self.__coordPin)
        minCoord    = (min(smallActive.x, smallPin.x), min(smallActive.y, smallPin.y))
        maxCoord    = (max(smallActive.x, smallPin.x), max(smallActive.y, smallPin.y))
        width       = maxCoord[0] - minCoord[0]
        height      = maxCoord[1] - minCoord[1]
        return BoundingBox(minCoord[0], minCoord[1], width, height)

    def __loadBoundary(self, boundary : BoundingBox):
        self.__coordActive = _scalePointUp(Point(boundary.x, boundary.y))
        self.__coordPin = _scalePointUp(Point(boundary.x + boundary.width, boundary.y + boundary.height))

    def panelBitmapOnPaint(self, event):
        dc = BufferedPaintDC(self.panelBitmap)
        dc.Clear()
        dc.DrawBitmap(self.__bitmap, 0, 0)
        if _scalePointDown(self.__coordActive) != _scalePointDown(self.__coordPin):
            dc.SetPen(Pen(self.__color, self.__width, PENSTYLE_SOLID))
            dc.SetBrush(Brush(self.__color, BRUSHSTYLE_TRANSPARENT))
            dc.DrawRectangle(Rect(self.__coordPin, self.__coordActive))
        return super().panelBitmapOnPaint(event)
    
    def panelBitmapOnLeftDown(self, event):
        self.__coordPin = event.GetPosition()
        self.__coordActive = self.__coordPin
        self.__drawing = True
        return super().panelBitmapOnLeftDown(event)

    def panelBitmapOnLeftUp(self, event):
        if not(self.btnReset.IsEnabled()):
            self.btnReset.Enable()

        self.__coordActive = event.GetPosition()
        self.__drawing = False
        self.panelBitmap.Refresh(eraseBackground=False)
        return super().panelBitmapOnLeftUp(event)

    def panelBitmapOnMotion(self, event):
        if self.__drawing:
            self.__coordActive = event.GetPosition()
            self.panelBitmap.Refresh(eraseBackground=False)
        return super().panelBitmapOnMotion(event)
    
    def btnResetOnButtonClick(self, event):
        self.__loadBoundary(self.__originalBounding)
        self.btnReset.Disable()
        self.panelBitmap.Refresh(eraseBackground=False)
        return super().btnResetOnButtonClick(event)
    
    def btnCancelOnButtonClick(self, event):
        self.EndModal(ID_CANCEL)
        return super().btnCancelOnButtonClick(event)
    
    def btnAgreeOnButtonClick(self, event):
        self.EndModal(ID_OK)
        return super().btnAgreeOnButtonClick(event)
    
    def GetBounding(self):
        return self.__toBoundary()

class DialogChangeBoundaryPygame(DialogChangeBoundary):
    def __init__(self, parent, surface: Surface, boundary: BoundingBox, color : Tuple[int, int, int] = (255,0,0), highlightWidth : int = 4):
        super().__init__(parent, self.__convertPygameToBuffer(surface), boundary, color=color, highlightWidth=highlightWidth)
    
    def __convertPygameToBuffer(self, surface : Surface) -> Bitmap:
        bitmap = Bitmap.FromBuffer(surface.get_width(), surface.get_height(), tostring(surface, "RGB"))
        bitmap = _scaleBitmap(bitmap)
        return bitmap