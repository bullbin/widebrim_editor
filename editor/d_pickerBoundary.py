from typing import Optional, Tuple
from .nopush_editor import PickerChangeBoundary
from pygame import Surface
from pygame.image import tostring
from wx import Bitmap, Pen, Brush, PENSTYLE_SOLID, BRUSHSTYLE_TRANSPARENT, BRUSHSTYLE_BDIAGONAL_HATCH ,IMAGE_QUALITY_NEAREST, BufferedPaintDC, Point, Rect, Image, Colour, ID_CANCEL, ID_OK, CallLater
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

    RADIUS_POINTS = 6

    def __init__(self, parent, bitmap : Bitmap, bitmapOverlay : Optional[Bitmap], boundary : BoundingBox, color : Tuple[int, int, int] = (255,0,0), highlightWidth : int = 4):
        super().__init__(parent)
        self._color = Colour(color[0], color[1], color[2])
        self._width = highlightWidth
        self._coordPin      : Point = Point(0,0)
        self._coordActive   : Point = Point(0,0)
        self._bitmap = bitmap
        self.__bitmapOverlay = bitmapOverlay

        self.btnSetBoundaryFromAnim.Hide()
        self.btnReset.Disable()
        self.Layout()

        self.__originalBounding = boundary
        self.__loadBoundary(boundary)

        self.__isDragging           = False
        self.__dragBoundary         = False
        self.__dragTopLeft          = False
        self.__dragTopRight         = False
        self.__dragBottomLeft       = False
        self.__dragBottomRight      = False
        self.__lastDragPos : Point  = Point(0,0)

        # Workaround - Remove handles
        self._showHandles = True
        self._clampToEdges = True

        # HACK - Without something to stop immediate event cue the last mouse movement is inputted into wx...
        self.__inputAllowed = False

        def enableInput():
            self.__inputAllowed = True

        self.__inputDisableCaller = CallLater(1000, enableInput)
        self.__inputDisableCaller.Start()

    def _isInputEnabled(self):
        return self.__inputAllowed

    def GetBounding(self) -> BoundingBox:
        smallActive = _scalePointDown(self._coordActive)
        smallPin = _scalePointDown(self._coordPin)
        minCoord    = (min(smallActive.x, smallPin.x), min(smallActive.y, smallPin.y))
        maxCoord    = (max(smallActive.x, smallPin.x), max(smallActive.y, smallPin.y))
        width       = maxCoord[0] - minCoord[0]
        height      = maxCoord[1] - minCoord[1]
        return BoundingBox(minCoord[0], minCoord[1], width, height)

    def __loadBoundary(self, boundary : BoundingBox):
        # TODO - Clamp if needed
        self._coordActive = _scalePointUp(Point(boundary.x, boundary.y))
        self._coordPin = _scalePointUp(Point(boundary.x + boundary.width, boundary.y + boundary.height))

    def _paintOutline(self, dc : BufferedPaintDC):
        self._paintLines(dc)
        self._paintInfill(dc)

    def _paintLines(self, dc : BufferedPaintDC):
        dc.SetPen(Pen(self._color, self._width, PENSTYLE_SOLID))
        dc.SetBrush(Brush(self._color, BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle(Rect(self._coordPin, self._coordActive))

    def _paintInfill(self, dc : BufferedPaintDC):
        dc.SetPen(Pen(self._color, self._width, PENSTYLE_SOLID))
        dc.SetBrush(Brush(self._color, BRUSHSTYLE_BDIAGONAL_HATCH))
        dc.DrawRectangle(Rect(self._coordPin, self._coordActive))

    def _paintHandles(self, dc : BufferedPaintDC):
        def drawHandleRectangle(pointAnchor : Point):
            topLeft = Point(pointAnchor.x - DialogChangeBoundary.RADIUS_POINTS, pointAnchor.y - DialogChangeBoundary.RADIUS_POINTS)
            bottomRight = Point(pointAnchor.x + DialogChangeBoundary.RADIUS_POINTS, pointAnchor.y + DialogChangeBoundary.RADIUS_POINTS)
            return Rect(topLeft, bottomRight)
        
        if self._showHandles:
            rectArea = Rect(self._coordActive, self._coordPin)
            dc.SetPen(Pen(self._color, self._width, PENSTYLE_SOLID))
            dc.SetBrush(Brush(self._color, BRUSHSTYLE_TRANSPARENT))
            dc.DrawRectangle(drawHandleRectangle(rectArea.GetBottomLeft()))
            dc.DrawRectangle(drawHandleRectangle(rectArea.GetBottomRight()))
            dc.DrawRectangle(drawHandleRectangle(rectArea.GetTopLeft()))
            dc.DrawRectangle(drawHandleRectangle(rectArea.GetTopRight()))

    def _paintBitmapOverlay(self, dc : BufferedPaintDC):
        if self.__bitmapOverlay != None:
            dc.DrawBitmap(self.__bitmapOverlay, 0, 0)

    def panelBitmapOnPaint(self, event):
        dc = BufferedPaintDC(self.panelBitmap)
        dc.Clear()
        dc.DrawBitmap(self._bitmap, 0, 0)
        self._paintInfill(dc)
        self._paintBitmapOverlay(dc)
        self._paintLines(dc)
        self._paintHandles(dc)
        return super().panelBitmapOnPaint(event)
    
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
    
    def btnCreateMidSizeOnButtonClick(self, event):
        size = self.panelBitmap.GetSize()
        quartX = size.x // 4
        quartY = size.y // 4
        self._coordActive.x = quartX
        self._coordActive.y = quartY
        self._coordPin.x = quartX * 3
        self._coordPin.y = quartY * 3
        self.panelBitmap.Refresh(eraseBackground=False)
        self.btnReset.Enable()
        return super().btnCreateMidSizeOnButtonClick(event)

    def panelBitmapOnLeftDown(self, event):
        
        def getHandleRect(pointCorner : Point) -> Rect:
            topLeft = Point(pointCorner.x - DialogChangeBoundary.RADIUS_POINTS, pointCorner.y - DialogChangeBoundary.RADIUS_POINTS)
            bottomRight = Point(pointCorner.x + DialogChangeBoundary.RADIUS_POINTS, pointCorner.y + DialogChangeBoundary.RADIUS_POINTS)
            return Rect(topLeft, bottomRight)

        def getBoundaryRect(baseRect : Rect) -> Rect:
            topLeft : Point = baseRect.GetTopLeft()
            bottomRight : Point = baseRect.GetBottomRight()
            topLeft.x += self._width
            topLeft.y += self._width
            bottomRight.x -= self._width
            bottomRight.y -= self._width
            return Rect(topLeft, bottomRight)

        if not(self._isInputEnabled()):
            return

        pos = event.GetPosition()
        rectArea = Rect(self._coordActive, self._coordPin)
        self.__lastDragPos = pos
        if self._showHandles:
            if getHandleRect(rectArea.GetTopLeft()).Contains(pos):
                self.__isDragging = True
                self.__dragTopLeft = True
            elif getHandleRect(rectArea.GetTopRight()).Contains(pos):
                self.__isDragging = True
                self.__dragTopRight = True
            elif getHandleRect(rectArea.GetBottomLeft()).Contains(pos):
                self.__isDragging = True
                self.__dragBottomLeft = True
            elif getHandleRect(rectArea.GetBottomRight()).Contains(pos):
                self.__isDragging = True
                self.__dragBottomRight = True
        if not(self.__isDragging) and getBoundaryRect(rectArea).Contains(pos):
            self.__isDragging = True
            self.__dragBoundary = True
        return
    
    def panelBitmapOnMotion(self, event):
        if self.__isDragging:
            deltaPos : Point = event.GetPosition() - self.__lastDragPos
            rectArea = Rect(self._coordActive, self._coordPin)
            if self.__dragBoundary:
                rectArea.Offset(deltaPos)
                self._coordActive = rectArea.GetTopLeft()
                self._coordPin = rectArea.GetBottomRight()
                if self._clampToEdges:
                    self._coordActive.x = max(min(self._coordActive.x, self.panelBitmap.GetSize().x), 0)
                    self._coordActive.y = max(min(self._coordActive.y, self.panelBitmap.GetSize().y), 0)
                    self._coordPin.x = max(min(self._coordPin.x, self.panelBitmap.GetSize().x), 0)
                    self._coordPin.y = max(min(self._coordPin.y, self.panelBitmap.GetSize().y), 0)
            elif self.__dragBottomLeft:
                self._coordActive = rectArea.GetTopLeft()
                self._coordActive.x += deltaPos.x
                self._coordPin = rectArea.GetBottomRight()
                self._coordPin.y += deltaPos.y
            elif self.__dragBottomRight:
                self._coordActive = rectArea.GetTopLeft()
                self._coordPin = rectArea.GetBottomRight()
                self._coordPin.x += deltaPos.x
                self._coordPin.y += deltaPos.y
            elif self.__dragTopLeft:
                self._coordActive = rectArea.GetTopLeft()
                self._coordPin = rectArea.GetBottomRight()
                self._coordActive.x += deltaPos.x
                self._coordActive.y += deltaPos.y
            elif self.__dragTopRight:
                self._coordActive = rectArea.GetTopLeft()
                self._coordPin = rectArea.GetBottomRight()
                self._coordActive.y += deltaPos.y
                self._coordPin.x += deltaPos.x

            self.panelBitmap.Refresh(eraseBackground=False)
            self.__lastDragPos = event.GetPosition()
            if not(self.btnReset.IsEnabled()):
                self.btnReset.Enable()
            if not(self.btnSetBoundaryFromAnim.IsEnabled()):
                self.btnSetBoundaryFromAnim.Enable()
        return
    
    def panelBitmapOnLeftUp(self, event):
        if self.__isDragging:
            self.__isDragging = False
            self.__dragBoundary = False
            self.__dragTopLeft = False
            self.__dragTopRight = False
            self.__dragBottomLeft = False
            self.__dragBottomRight = False
        return

class DialogChangeBoundaryPygame(DialogChangeBoundary):
    def __init__(self, parent, surface: Surface, boundary: BoundingBox, surfaceOverlay : Optional[Surface] = None, color : Tuple[int, int, int] = (255,0,0), highlightWidth : int = 4):
        if surfaceOverlay == None:
            super().__init__(parent, self.__convertPygameToBuffer(surface), None, boundary, color=color, highlightWidth=highlightWidth)
        else:
            super().__init__(parent, self.__convertPygameToBuffer(surface), self.__convertPygameToBuffer(surfaceOverlay, True), boundary, color=color, highlightWidth=highlightWidth)
    
    def __convertPygameToBuffer(self, surface : Surface, hasTransparency : bool = False) -> Bitmap:
        if hasTransparency:
            bitmap = Bitmap.FromBufferRGBA(surface.get_width(), surface.get_height(), tostring(surface, "RGBA"))
        else:
            bitmap = Bitmap.FromBuffer(surface.get_width(), surface.get_height(), tostring(surface, "RGB"))
        bitmap = _scaleBitmap(bitmap)
        return bitmap