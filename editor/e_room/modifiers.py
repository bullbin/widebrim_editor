from typing import Optional, Tuple
from pygame import Surface
from editor.d_pickerAnim import DialogPickerLimitedAnim
from editor.d_pickerBoundary import DialogChangeBoundaryPygame
from editor.d_pickerBoundaryAnim import DialogChangeBoundaryWithSpritePositioning
from editor.d_pickerEvent import DialogEvent
from editor.d_pickerMoveAnim import DialogSpriteReposition
from editor.e_script.get_input_popup import VerifiedDialog, rangeIntCheckFunction
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.engine_ext.utils import getBottomScreenAnimFromPath, getTopScreenAnimFromPath
from widebrim.madhatter.hat_io.asset_dat.place import BoundingBox
from wx import ID_OK, Window, TextEntryDialog
from re import match

def modifyEventSelection(parent : Window, state : Layton2GameState, idEvent : int) -> int:
    print("Modify called on", idEvent)
    dlg = DialogEvent(parent, state)
    if dlg.ShowModal() == ID_OK:
        return dlg.GetSelection()
    return idEvent

def modifyPosition(parent : Window, pos : Tuple[int,int]):
    print("Modify pos called on", pos)
    dlg = VerifiedDialog(TextEntryDialog(parent, "Enter the X co-ordinate"), rangeIntCheckFunction(-(2 ** 31), (2 ** 31) - 1))
    newX = dlg.do(str(pos[0]))
    if newX == None:
        return pos

    dlg = VerifiedDialog(TextEntryDialog(parent, "Enter the Y co-ordinate"), rangeIntCheckFunction(-(2 ** 31), (2 ** 31) - 1))
    newY = dlg.do(str(pos[1]))
    if newY == None:
        return pos
    return (newX, newY)

def modifySpritePosition(parent : Window, state : Layton2GameState, background : Surface, pathSprite : str, pos : Tuple[int,int], color : Tuple[int,int,int], foreground : Optional[Surface]=None) -> Tuple[int,int]:
    """Brings up a dialog to modify a position that is connected to a sprite. If no sprite could be loaded, the default position editing dialog will be presented instead.

    Args:
        parent (Window): wx dialog parent.
        state (Layton2GameState): Game state used for file access.
        background (Surface): Background preview used in dialog renderer.
        pathSprite (str): Path to sprite associated with the sprite.
        pos (Tuple[int,int]): Sprite position.
        foreground (Optional[Surface]): Surface to overlay onto preview. Defaults to None.

    Returns:
        Tuple[int,int]: Sprite position.
    """
    isTopScreenSprite = len(pathSprite) >= 4 and pathSprite[-4:] == ".sbj"
    if isTopScreenSprite:
        anim = getTopScreenAnimFromPath(state, pathSprite)
    else:
        anim = getBottomScreenAnimFromPath(state, pathSprite)
    if anim.getActiveFrame() == None:
        return modifyPosition(parent, pos)
    print("Modify spritepos called on", pos)
    dlg = DialogSpriteReposition(parent, background, anim, pos=pos, color=color, surfaceOverlay=foreground)
    if dlg.ShowModal() == ID_OK:
        return dlg.GetPos()
    return pos

def modifySpritePath(parent : Window, state : Layton2GameState, pathSprite : str, reMatchString : str = ".+.arc", pathRoot : str = "/data_lt2/ani", allowEmptyImage=False) -> str:
    dlg = DialogPickerLimitedAnim(parent, state, state.getFileAccessor(), pathRoot, reMatchString=reMatchString, defaultPathRelative=pathSprite, allowEmptyImage=allowEmptyImage)
    dlg.ShowModal()
    outPath = dlg.GetPath()
    try:
        groupingMatch = match(reMatchString, outPath)
        return groupingMatch.group(1)
    except IndexError:
        return dlg.GetPath()
    except AttributeError:
        return dlg.GetPath()

def modifySpriteBoundary(parent : Window, state : Layton2GameState, background : Surface, boundary : BoundingBox, color : Tuple[int,int,int], spritePath : str, foreground : Optional[Surface] = None) -> bool:
    """Brings up a dialog to modify a boundary that is connected to another sprite. If no sprite could be loaded, the default boundary dialog will be presented instead.

    Args:
        parent (Window): wx dialog parent.
        state (Layton2GameState): Game state used for file access.
        background (Surface): Background preview used in dialog renderer.
        boundary (BoundingBox): Boundary being edited in-place.
        color (Tuple[int,int,int]): Line color for outlining boundary.
        spritePath (str): Path to sprite associated with the boundary.
        foreground (Optional[Surface]): Surface to overlay onto preview. Defaults to None.

    Returns:
        bool: True if boundary was modified.
    """
    anim = getBottomScreenAnimFromPath(state, spritePath)
    if anim.getActiveFrame() != None:
        dlg = DialogChangeBoundaryWithSpritePositioning(parent, background, anim, boundary, color=color, surfaceOverlay=foreground)
    else:
        dlg = DialogChangeBoundaryPygame(parent, background, boundary, color=color, surfaceOverlay=foreground)
    if dlg.ShowModal() == ID_OK:
        newBoundary = dlg.GetBounding()
        output = (boundary.x != newBoundary.x) or (boundary.y != newBoundary.y) or (boundary.width != newBoundary.width) or (boundary.height != newBoundary.height)
        boundary.x = newBoundary.x
        boundary.y = newBoundary.y
        boundary.width = newBoundary.width
        boundary.height = newBoundary.height
        return output
    return False

def modifyBoundary(parent : Window, state : Layton2GameState, background : Surface, boundary : BoundingBox, color : Tuple[int,int,int], foreground : Optional[Surface] = None) -> bool:
    """Brings up a dialog to modify a boundary.

    Args:
        parent (Window): wx dialog parent.
        state (Layton2GameState): Game state used for file access.
        background (Surface): Background preview used in dialog renderer.
        boundary (BoundingBox): Boundary being edited in-place.
        color (Tuple[int,int,int]): Line color for outlining boundary.
        foreground (Optional[Surface]): Surface to overlay onto preview. Defaults to None.

    Returns:
        bool: True if boundary was modified.
    """
    dlg = DialogChangeBoundaryPygame(parent, background, boundary, color=color, surfaceOverlay=foreground)
    if dlg.ShowModal() == ID_OK:
        newBoundary = dlg.GetBounding()
        output = (boundary.x != newBoundary.x) or (boundary.y != newBoundary.y) or (boundary.width != newBoundary.width) or (boundary.height != newBoundary.height)
        boundary.x = newBoundary.x
        boundary.y = newBoundary.y
        boundary.width = newBoundary.width
        boundary.height = newBoundary.height
        return output
    return False

def modifyTxt2String(parent : Window, state : Layton2GameState, id : int) -> int:
    print("Modify called on a txt2 string")
    return id