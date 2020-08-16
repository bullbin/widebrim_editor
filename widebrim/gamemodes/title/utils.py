from ...engine.const import RESOLUTION_NINTENDO_DS
from ...engine.state.layer import ScreenLayerNonBlocking
from ...engine_ext.utils import getAnimFromPath as getAnimFromPathRaw

def getAnimFromPath(inPath, spawnAnimName="gfx", posVariable="pos"):

    # TODO - Where do buttons go if this is messed with?

    tempImage = getAnimFromPathRaw(inPath)
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