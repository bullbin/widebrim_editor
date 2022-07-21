from typing import Optional, Tuple

from pygame import Surface
from editor.d_pickerBoundaryAnim import DialogChangeBoundaryWithSpritePositioning
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from widebrim.madhatter.hat_io.asset_dat.place import BoundingBox

class DialogSpriteReposition(DialogChangeBoundaryWithSpritePositioning):
    def __init__(self, parent, bitmap: Surface, animation: AnimatedImageObject, pos : Tuple[int,int], surfaceOverlay : Optional[Surface], color: Tuple[int, int, int] = (255,255,255), highlightWidth: int = 4):
        super().__init__(parent, bitmap, animation, BoundingBox(pos[0],pos[1],animation.getDimensions()[0],animation.getDimensions()[1]), color=color, highlightWidth=highlightWidth, surfaceOverlay=surfaceOverlay)
        self.SetTitle("Change Position")
        self.btnCreateMidSize.SetLabelText("Recenter")
        self._showHandles = False
        self._clampToEdges = False
        self.btnSetBoundaryFromAnim.Hide()
        self.Layout()
        self.panelBitmap.Refresh(eraseBackground=False)
        # TODO - unify this
        self.__centerX = 256 - animation.getDimensions()[0]
        self.__centerY = 192 - animation.getDimensions()[1]
    
    def btnCreateMidSizeOnButtonClick(self, event):
        self._coordActive.x = self.__centerX
        self._coordActive.y = self.__centerY
        self._coordPin.x = self.__centerX + 1
        self._coordPin.y = self.__centerY + 1
        self._setBoundsFromAnim()
        self.panelBitmap.Refresh(eraseBackground=False)
        event.Skip()

    def GetPos(self) -> Tuple[int,int]:
        bounding = self.GetBounding()
        return (bounding.x, bounding.y)