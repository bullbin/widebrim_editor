from .utils import MainScreenPopup
from ..title.utils import getAnimFromPath
from ...engine.config import PATH_SAVE
from ...engine.anim.button import AnimatedButton
from .const import PATH_BG_FILELOAD, PATH_ANI_BTN_BACK

# Maybe not accurate to game behaviour? In main engine overlay so acts differently

# How text writing works
# Middle text starts at 0x2f, top text at 0x25 and bottom text at 0x39
# To calculate center of box offset, do 0x8a - ((length of text * 7) / 2)

# Boxes are staggered by 0x2e

class SaveLoadScreenPopup(MainScreenPopup):
    def __init__(self, laytonState, screenController, bgIndex, callbackOnTerminate, callbackOnSave):
        MainScreenPopup.__init__(self, callbackOnTerminate)

        # TODO - Make class variable
        self.buttonBack = AnimatedButton(getAnimFromPath(PATH_ANI_BTN_BACK % laytonState.language.value), "on", "off", callback=callbackOnTerminate)

        screenController.setBgMain(PATH_BG_FILELOAD % (laytonState.language.value, bgIndex + 1))
        screenController.fadeInMain()
    
    def draw(self, gameDisplay):
        self.buttonBack.draw(gameDisplay)
    
    def update(self, gameClockDelta):
        self.buttonBack.update(gameClockDelta)
    
    def handleTouchEvent(self, event):
        self.buttonBack.handleTouchEvent(event)