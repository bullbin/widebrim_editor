from .utils import PrizeWindow2PopupWithCursor
from ....engine_ext.utils import getTxt2String, getAnimFromPath
from ....engine.const import RESOLUTION_NINTENDO_DS, PATH_TEXT_GENERIC
from ....engine.anim.font.staticFormatted import StaticTextHelper
from .const import ID_STOCK_SCREEN, PATH_ANIM_NAZO_ICON, POS_STOCK_SCREEN_NAZO_ICON, NAME_AUTO_ANIM, POS_TEXT_STOCK_SCREEN_Y

class StockPopup(PrizeWindow2PopupWithCursor):
    def __init__(self, laytonState, screenController, eventStorage):
        PrizeWindow2PopupWithCursor.__init__(self, laytonState, screenController, eventStorage)

        self._nazoIcon = getAnimFromPath(PATH_ANIM_NAZO_ICON)
        if self._nazoIcon != None:
            self._nazoIcon.setPos((POS_STOCK_SCREEN_NAZO_ICON[0], POS_STOCK_SCREEN_NAZO_ICON[1] + RESOLUTION_NINTENDO_DS[1]))
            self._nazoIcon.setAnimationFromName(NAME_AUTO_ANIM)

        try:
            tempPromptText = getTxt2String(laytonState, PATH_TEXT_GENERIC % ID_STOCK_SCREEN)
            tempPromptText = tempPromptText % (laytonState.entryNzList.idExternal, laytonState.entryNzList.name)
        except:
            tempPromptText = ""
        
        self.promptText = StaticTextHelper(laytonState.fontEvent)
        self.promptText.setPos((RESOLUTION_NINTENDO_DS[0] // 2, POS_TEXT_STOCK_SCREEN_Y + RESOLUTION_NINTENDO_DS[1]))
        self.promptText.setText(tempPromptText)
    
    def updateForegroundElements(self, gameClockDelta):
        if self._nazoIcon != None:
            self._nazoIcon.update(gameClockDelta)
        return super().updateForegroundElements(gameClockDelta)

    def drawForegroundElements(self, gameDisplay):
        if self._nazoIcon != None:
            self._nazoIcon.draw(gameDisplay)
        self.promptText.drawXYCenterPoint(gameDisplay)
        return super().drawForegroundElements(gameDisplay)