from ...engine_ext.utils import getAnimFromPathWithAttributes
from ...engine_ext.utils import getImageFromPath
from .const import PATH_ANIM_SENRO, PATH_ANIM_TRAIN, PATH_ANIM_WAKU, PATH_BG_TITLE, PATH_BUTTON_NEW_GAME, PATH_BUTTON_CONTINUE, PATH_BUTTON_BONUS
from ...engine.const import RESOLUTION_NINTENDO_DS
from ...engine.state.layer import ScreenLayerNonBlocking
from ...engine.state.enum_mode import GAMEMODES
from ...engine.anim.button import AnimatedButton

class TitlePlayerBottomScreenOverlay(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController, saveData, routineTitleScreen, routineContinue, routineBonus, routineTerminate):
        ScreenLayerNonBlocking.__init__(self)
        self.screenController = screenController
        self.laytonState = laytonState

class MenuScreen(TitlePlayerBottomScreenOverlay):

    ANIM_TRAIN  = getAnimFromPathWithAttributes(PATH_ANIM_TRAIN)
    ANIM_SENRO  = getAnimFromPathWithAttributes(PATH_ANIM_SENRO)
    ANIM_WAKU   = getAnimFromPathWithAttributes(PATH_ANIM_WAKU)

    BUTTON_NEW      = None
    BUTTON_CONT     = None
    BUTTON_BONUS    = None

    BACKGROUND_SPEED_MULTIPLIER = 0.0666
    BACKGROUND_SPEED_MULTIPLIER = 2/30
    FOREGROUND_SPEED_MULTIPLIER = 1/5

    def __init__(self, laytonState, screenController, saveData, routineTitleScreen, routineContinue, routineBonus, routineTerminate):
        TitlePlayerBottomScreenOverlay.__init__(self, laytonState, screenController, saveData, routineTitleScreen, routineContinue, routineBonus, routineTerminate)
        screenController.setBgMain(PATH_BG_TITLE)

        # TODO - Redundancy if None
        self.background = getImageFromPath(laytonState, PATH_BG_TITLE)
        self.backgroundX = 0
        self.senroX = MenuScreen.ANIM_SENRO.getPos()[0]

        screenController.fadeInMain()

        self.routineTerminate = routineTerminate
        self.routineContinue = routineContinue
        self.routineBonus = routineBonus
        self.isActive = False
        for slotIndex in range(3):
            self.isActive = self.isActive or saveData.getSlotData(slotIndex).isActive
        
        def callbackOnNewGame():
            self.laytonState.setGameMode(GAMEMODES.Name)
            self.routineTerminate()

        if MenuScreen.BUTTON_BONUS == None:
            MenuScreen.BUTTON_BONUS = AnimatedButton(getAnimFromPathWithAttributes(PATH_BUTTON_BONUS % laytonState.language.value), "on", "off", callback=routineBonus)

        if MenuScreen.BUTTON_NEW == None:
            if self.isActive:
                MenuScreen.BUTTON_NEW = AnimatedButton(getAnimFromPathWithAttributes(PATH_BUTTON_NEW_GAME % laytonState.language.value), "on", "off", callback=callbackOnNewGame)
            else:
                MenuScreen.BUTTON_NEW = AnimatedButton(getAnimFromPathWithAttributes(PATH_BUTTON_NEW_GAME % laytonState.language.value, posVariable="pos2"), "on", "off", callback=callbackOnNewGame)

        if MenuScreen.BUTTON_CONT == None:
            MenuScreen.BUTTON_CONT = AnimatedButton(getAnimFromPathWithAttributes(PATH_BUTTON_CONTINUE % laytonState.language.value), "on", "off", callback=routineContinue)
    
    def update(self, gameClockDelta):

        self.backgroundX    = (self.backgroundX + gameClockDelta * MenuScreen.BACKGROUND_SPEED_MULTIPLIER) % RESOLUTION_NINTENDO_DS[0]
        self.senroX         = (self.senroX + gameClockDelta * MenuScreen.FOREGROUND_SPEED_MULTIPLIER) % RESOLUTION_NINTENDO_DS[0]

        MenuScreen.ANIM_SENRO.update(gameClockDelta)
        MenuScreen.ANIM_TRAIN.update(gameClockDelta)
        MenuScreen.ANIM_WAKU.update(gameClockDelta)

        if self.isActive:
            MenuScreen.BUTTON_BONUS.update(gameClockDelta)
            MenuScreen.BUTTON_CONT.update(gameClockDelta)
        MenuScreen.BUTTON_NEW.update(gameClockDelta)

    def draw(self, gameDisplay):

        gameDisplay.blit(self.background, (self.backgroundX, RESOLUTION_NINTENDO_DS[1]))
        gameDisplay.blit(self.background, (self.backgroundX - self.background.get_width(), RESOLUTION_NINTENDO_DS[1]))

        # TODO - What happens with subanimations? Maybe safer to change position each time.
        if MenuScreen.ANIM_SENRO.getActiveFrame() != None:
            gameDisplay.blit(MenuScreen.ANIM_SENRO.getActiveFrame(), (self.senroX, MenuScreen.ANIM_SENRO.getPos()[1]))
            gameDisplay.blit(MenuScreen.ANIM_SENRO.getActiveFrame(), (self.senroX - RESOLUTION_NINTENDO_DS[0], MenuScreen.ANIM_SENRO.getPos()[1]))

        MenuScreen.ANIM_TRAIN.draw(gameDisplay)
        MenuScreen.ANIM_WAKU.draw(gameDisplay)

        if self.isActive:
            MenuScreen.BUTTON_BONUS.draw(gameDisplay)
            MenuScreen.BUTTON_CONT.draw(gameDisplay)
        MenuScreen.BUTTON_NEW.draw(gameDisplay)
    
    def handleTouchEvent(self, event):

        MenuScreen.BUTTON_NEW.handleTouchEvent(event)
        if self.isActive:
            MenuScreen.BUTTON_CONT.handleTouchEvent(event)
            MenuScreen.BUTTON_BONUS.handleTouchEvent(event)

        return super().handleTouchEvent(event)