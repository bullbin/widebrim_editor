from .utils import PrizeWindow2PopupWithCursor
from ....engine_ext.utils import getTxtString
from ....engine.anim.font.staticFormatted import StaticTextHelper

class ItemAddPopup(PrizeWindow2PopupWithCursor):
    def __init__(self, laytonState, screenController, eventStorage, itemIndex):
        PrizeWindow2PopupWithCursor.__init__(self, laytonState, screenController, eventStorage)

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