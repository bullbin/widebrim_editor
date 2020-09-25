from .utils import FadingPopupAnimBackground
from .const import NAME_POS_VARIABLE
from ....engine.const import RESOLUTION_NINTENDO_DS

class ItemPopup(FadingPopupAnimBackground):
    def __init__(self, laytonState, screenController, eventStorage, itemIndex):
        # cursorWait

        prizeWindow2 = eventStorage.getAssetPrizeWindow2()
        if prizeWindow2 != None:
            # TODO - Automagically set this in event storage so it doesn't have to be done for every item in every popup!
            prizeWindow2.setAnimationFromName("gfx")
            prizeWindow2Pos = prizeWindow2.getVariable(NAME_POS_VARIABLE)
            if prizeWindow2Pos != None:
                prizeWindow2.setPos((prizeWindow2Pos[0], prizeWindow2Pos[1] + RESOLUTION_NINTENDO_DS[1]))

        FadingPopupAnimBackground.__init__(self, laytonState, screenController, None, prizeWindow2)

        self.itemIcon = eventStorage.getAssetItemIcon()
        if self.itemIcon != None:
            self.itemIcon.setAnimationFromName(str(itemIndex + 1))
    
    def drawForegroundElements(self, gameDisplay):
        if self.itemIcon != None:
            self.itemIcon.draw(gameDisplay)
        return super().drawForegroundElements(gameDisplay)
    
    def updateForegroundElements(self, gameClockDelta):
        if self.itemIcon != None:
            self.itemIcon.update(gameClockDelta)
        return super().updateForegroundElements(gameClockDelta)