from ...engine.const import PATH_ANI, RESOLUTION_NINTENDO_DS
from ...engine.file import FileInterface
from ...engine.state.layer import ScreenLayerNonBlocking
from ...madhatter.hat_io.asset_image import AnimatedImage
from ...engine.anim.image_anim import AnimatedImageObject

def getAnimFromPath(inPath):
    tempAsset = FileInterface.getData(PATH_ANI % inPath)
    tempImage = AnimatedImageObject.fromMadhatter(AnimatedImage.fromBytesArc(tempAsset))
    tempImage.setAnimationFromName("gfx")
    if tempImage.getVariable("pos") != None:
        tempImage.setPos((tempImage.getVariable("pos")[0],
                          tempImage.getVariable("pos")[1] + RESOLUTION_NINTENDO_DS[1]))
    else:
        tempImage.setPos((0, RESOLUTION_NINTENDO_DS[1]))
    return tempImage

class TitlePlayerBottomScreenOverlay(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController, routineTitleScreen, routineNewGame, routineContinue, routineBonus):
        ScreenLayerNonBlocking.__init__(self)