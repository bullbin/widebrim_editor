from typing import Optional, Tuple
from pygame import Surface, Rect
from pygame.draw import rect as drawRectangle

from widebrim.madhatter.hat_io.asset_dat.place import BoundingBox

def getShortenedString(text : str, maxChars=36, extra="(...)", addSpace=True) -> str:
    """Shorten string to fit character length.

    Args:
        text (str): Input string.
        maxChars (int, optional): Max character count to shorten to, including extension. Defaults to 36.
        extra (str, optional): Extension to fit to long strings. Defaults to "(...)".
        addSpace (bool, optional): Add space before extension. Defaults to True.

    Returns:
        str: Shortened string.
    """
    text = " ".join(text.split("\n"))
    if len(text) <= maxChars:
        return text
    else:
        if addSpace:
            extra = " " + extra

        text = text[:maxChars - len(extra)]

        # Rewind to space before last cutoff word
        while len(text) > 0 and text[-1] != " ":
            text = text[:-1]

        # Rewind to word before spaces
        while len(text) > 0 and text[-1] == " ":
            text = text[:-1]

        text = text + extra
        if addSpace:
            checkLen = len(extra) + 1
            if len(text) >= checkLen:
                if text[-checkLen] == " ":
                    return text[:-checkLen] + extra[1:]

        return text
    
def blitBoundingLine(dest : Surface, bounding : BoundingBox, color : Tuple[int,int,int], width : int = 2):
    drawRectangle(dest, color, Rect(bounding.x, bounding.y, bounding.width, bounding.height), width=width, border_radius=0)

def getBoundingFromSurface(inSurf : Optional[Surface], pos : Tuple[int,int]) -> BoundingBox:
    if inSurf == None:
        return BoundingBox(pos[0], pos[1], 0, 0)
    return BoundingBox(pos[0], pos[1], inSurf.get_width(), inSurf.get_height())

def blitBoundingAlphaFill(dest : Surface, bounding : BoundingBox, color : Tuple[int,int,int], alpha : int = 120, noBlend : bool = True):
    lenX = bounding.width
    lenY = bounding.height
    if lenX == 0 or lenY == 0:
        return
    
    # TODO - Change code to show only hittable hitboxes
    if noBlend:
        for x in range(lenX):
            for y in range(lenY):
                dest.set_at((bounding.x + x, bounding.y + y), (color[0], color[1], color[2], alpha))
    else:
        tempRect = Surface((lenX, lenY)).convert_alpha()
        tempRect.fill((color[0], color[1], color[2], alpha))
        dest.blit(tempRect, (bounding.x, bounding.y))