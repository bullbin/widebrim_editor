from typing import Tuple
from pygame import Surface
from editor.d_pickerBoundary import DialogChangeBoundaryPygame
from editor.d_pickerEvent import DialogEvent
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.madhatter.hat_io.asset_dat.place import BoundingBox
from wx import ID_OK

def modifyEventSelection(parent, state : Layton2GameState, idEvent : int) -> int:
    print("Modify called on", idEvent)
    dlg = DialogEvent(parent, state)
    if dlg.ShowModal() == ID_OK:
        pass
    return idEvent

def modifySpritePosition(parent, state : Layton2GameState, background : Surface, sprite : Surface, originalPos : Tuple[int,int]) -> Tuple[int,int]:
    print("Modify called on", originalPos)
    return originalPos

def modifySpritePath(parent, state : Layton2GameState, background : Surface, pathSprite : str) -> str:
    print("Modify called on", pathSprite)
    return pathSprite

def modifyBoundary(parent, state : Layton2GameState, background : Surface, boundary : BoundingBox, color : Tuple[int,int,int]):
    print("Modify called a boundary")
    dlg = DialogChangeBoundaryPygame(parent, background, boundary, color=color)
    if dlg.ShowModal() == ID_OK:
        newBoundary = dlg.GetBounding()
        boundary.x = newBoundary.x
        boundary.y = newBoundary.y
        boundary.width = newBoundary.width
        boundary.height = newBoundary.height

def modifyTxt2String(parent, state : Layton2GameState, id : int) -> int:
    print("Modify called on a txt2 string")
    return id