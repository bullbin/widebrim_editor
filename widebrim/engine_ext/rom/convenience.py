from .banner import getBannerImageFromRom, getCodenameFromRom
from ...engine.config import ROM_LOAD_BANNER
from ...engine.file import FileInterface
from ...engine.convenience import initDisplay
import pygame

def applyPygameBannerTweaks():
    if ROM_LOAD_BANNER and FileInterface.isRunningFromRom():

        initDisplay()

        bannerImage = getBannerImageFromRom(FileInterface.getRom())
        # TODO - Does this need to be RGBA?
        bannerSurface = pygame.image.fromstring(bannerImage.convert("RGB").tobytes("raw", "RGB"), bannerImage.size, "RGB").convert()
        try:
            transparency = bannerImage.getpalette()[:3]
            transparency = (transparency[0], transparency[1], transparency[2])
            bannerSurface.set_colorkey(transparency)
        except IndexError:
            pass

        pygame.display.set_icon(bannerSurface)
        pygame.display.set_caption(getCodenameFromRom(FileInterface.getRom()))

        return True
    return False