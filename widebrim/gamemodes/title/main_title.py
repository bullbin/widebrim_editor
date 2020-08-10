from .utils import getAnimFromPath, TitlePlayerBottomScreenOverlay
from .const import PATH_ANIM_SENRO, PATH_ANIM_TRAIN, PATH_ANIM_WAKU, PATH_BG_TITLE
from ...engine.state.layer import ScreenLayerNonBlocking

class MenuScreen(TitlePlayerBottomScreenOverlay):

    ANIM_TRAIN  = getAnimFromPath(PATH_ANIM_TRAIN)
    ANIM_SENRO  = getAnimFromPath(PATH_ANIM_SENRO)
    ANIM_WAKU   = getAnimFromPath(PATH_ANIM_WAKU)

    def __init__(self, laytonState, screenController, routineTitleScreen, routineNewGame, routineContinue, routineBonus):
        TitlePlayerBottomScreenOverlay.__init__(self, laytonState, screenController, routineTitleScreen, routineNewGame, routineContinue, routineBonus)
        screenController.setBgMain(PATH_BG_TITLE)
    
    def update(self, gameClockDelta):
        MenuScreen.ANIM_SENRO.update(gameClockDelta)
        MenuScreen.ANIM_TRAIN.update(gameClockDelta)
        MenuScreen.ANIM_WAKU.update(gameClockDelta)

    def draw(self, gameDisplay):
        MenuScreen.ANIM_SENRO.draw(gameDisplay)
        MenuScreen.ANIM_TRAIN.draw(gameDisplay)
        MenuScreen.ANIM_WAKU.draw(gameDisplay)