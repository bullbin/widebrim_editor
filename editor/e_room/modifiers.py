from typing import Tuple
from pygame import Surface
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.madhatter.hat_io.asset_dat.place import BoundingBox

def modifyEventSelection(parent, state : Layton2GameState, idEvent : int) -> int:
    print("Modify called on", idEvent)
    return idEvent

def modifySpritePosition(parent, state : Layton2GameState, background : Surface, sprite : Surface, originalPos : Tuple[int,int]) -> Tuple[int,int]:
    print("Modify called on", originalPos)
    return originalPos

def modifySpritePath(parent, state : Layton2GameState, background : Surface, pathSprite : str) -> str:
    print("Modify called on", pathSprite)
    return pathSprite

def modifyBoundary(parent, state : Layton2GameState, background : Surface, boundary : BoundingBox):
    print("Modify called a boundary")
    pass

def modifyTxt2String(parent, state : Layton2GameState, id : int) -> int:
    print("Modify called on a txt2 string")
    return id