from pygame.display import set_mode, set_caption
from .config import WINDOW_DEFAULT_NAME
from .const import RESOLUTION_NINTENDO_DS

_HAS_CAPTION_BEEN_SET = False

def initDisplay():
    global _HAS_CAPTION_BEEN_SET
    output = set_mode((RESOLUTION_NINTENDO_DS[0], int(RESOLUTION_NINTENDO_DS[1] * 2)))
    if not(_HAS_CAPTION_BEEN_SET):
        set_caption(WINDOW_DEFAULT_NAME)
        _HAS_CAPTION_BEEN_SET = True
    return output