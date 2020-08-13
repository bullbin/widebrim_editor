from ...engine.const import PATH_ANI, RESOLUTION_NINTENDO_DS
from ...engine.file import FileInterface
from ...engine.state.layer import ScreenLayerNonBlocking
from ...madhatter.hat_io.asset_image import AnimatedImage
from ...engine.anim.image_anim import AnimatedImageObject

def getAnimFromPath(inPath, spawnAnimName="gfx", posVariable="pos"):

    # TODO - Where do buttons go if this is messed with?

    tempAsset = FileInterface.getData(PATH_ANI % inPath)
    tempImage = AnimatedImageObject.fromMadhatter(AnimatedImage.fromBytesArc(tempAsset))
    tempImage.setAnimationFromName(spawnAnimName)
    if tempImage.getVariable(posVariable) != None:
        tempImage.setPos((tempImage.getVariable(posVariable)[0],
                          tempImage.getVariable(posVariable)[1] + RESOLUTION_NINTENDO_DS[1]))
    else:
        tempImage.setPos((0, RESOLUTION_NINTENDO_DS[1]))
    return tempImage

class TitlePlayerBottomScreenOverlay(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController, saveData, routineTitleScreen, routineContinue, routineBonus, routineTerminate):
        ScreenLayerNonBlocking.__init__(self)
        self.screenController = screenController
        self.laytonState = laytonState