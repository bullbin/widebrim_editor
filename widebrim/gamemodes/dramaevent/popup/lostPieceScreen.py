from .utils import PrizeWindow2PopupWithCursor
from .const import POS_LOST_SCREEN_PIECE_ICON, ID_LOST_SCREEN, NAME_AUTO_ANIM
from ....engine_ext.utils import getTxt2String
from ....engine.const import RESOLUTION_NINTENDO_DS

class LostPiecePopup(PrizeWindow2PopupWithCursor):
    def __init__(self, laytonState, screenController, eventStorage):
        PrizeWindow2PopupWithCursor.__init__(self, laytonState, screenController, eventStorage)

        self.pieceIcon = eventStorage.getAssetPieceIcon()
        if self.pieceIcon != None:
            self.pieceIcon.setAnimationFromName(NAME_AUTO_ANIM)
            posPieceIcon = (RESOLUTION_NINTENDO_DS[0] - self.pieceIcon.getDimensions[0] // 2,
                            POS_LOST_SCREEN_PIECE_ICON[1] + RESOLUTION_NINTENDO_DS[1])
            self.pieceIcon.setPos(posPieceIcon)
        print(getTxt2String(laytonState, ID_LOST_SCREEN))
    
    def drawForegroundElements(self, gameDisplay):
        if self.pieceIcon != None:
            self.pieceIcon.draw(gameDisplay)
        return super().drawForegroundElements(gameDisplay)
    
    def updateForegroundElements(self, gameClockDelta):
        if self.pieceIcon != None:
            self.pieceIcon.update(gameClockDelta)
        return super().updateForegroundElements(gameClockDelta)