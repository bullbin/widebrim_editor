from widebrim.engine.anim.font.staticFormatted import StaticTextHelper
from widebrim.engine.const import PATH_TEXT_GENERIC, RESOLUTION_NINTENDO_DS
from widebrim.gamemodes.dramaevent.popup.const import ID_FLORA_LEAVE_PARTY, PATH_ANIM_PARTY, POS_PARTY_SCREEN_NAZO_ICON, POS_PHOTO_PIECE_TEXT
from widebrim.engine_ext.utils import getAnimFromPath, getTxt2String
from widebrim.gamemodes.dramaevent.popup.utils import PrizeWindow2PopupWithCursor

class DoOutPartyPopup(PrizeWindow2PopupWithCursor):
    def __init__(self, laytonState, screenController, eventStorage):
        PrizeWindow2PopupWithCursor.__init__(self, laytonState, screenController, eventStorage)
        self.__animParty = getAnimFromPath(PATH_ANIM_PARTY)
        if self.__animParty != None:
            self.__animParty.setAnimationFromIndex(3)
            self.__animParty.setPos((POS_PARTY_SCREEN_NAZO_ICON[0], POS_PARTY_SCREEN_NAZO_ICON[1] + RESOLUTION_NINTENDO_DS[1]))
    
        self._prompt = StaticTextHelper(laytonState.fontEvent)
        self._prompt.setText(getTxt2String(laytonState, PATH_TEXT_GENERIC % ID_FLORA_LEAVE_PARTY))
        self._prompt.setPos((POS_PHOTO_PIECE_TEXT[0], POS_PHOTO_PIECE_TEXT[1] + RESOLUTION_NINTENDO_DS[1]))
    
    def drawForegroundElements(self, gameDisplay):
        if self.__animParty != None:
            self.__animParty.draw(gameDisplay)
        self._prompt.drawXYCenterPoint(gameDisplay) # TODO - bias?
        return super().drawForegroundElements(gameDisplay)
    
    def updateForegroundElements(self, gameClockDelta):
        if self.__animParty != None:
            self.__animParty.update(gameClockDelta)
        return super().updateForegroundElements(gameClockDelta)