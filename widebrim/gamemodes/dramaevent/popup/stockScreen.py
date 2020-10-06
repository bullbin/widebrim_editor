# Notes

# Loads nazo_icon just for the popup, and positions it to 0x74, 0x3c

from .utils import FadingPopupAnimBackground
from ....engine_ext.utils import getTxt2String
from .const import NAME_POS_VARIABLE, ID_STOCK_SCREEN, POS_STOCK_SCREEN_NAZO_ICON
from ....engine.const import RESOLUTION_NINTENDO_DS

class StockPopup(FadingPopupAnimBackground):
    def __init__(self, laytonState, screenController, eventStorage):
        # cursorWait

        prizeWindow2 = eventStorage.getAssetPrizeWindow2()
        if prizeWindow2 != None:
            # TODO - Automagically set this in event storage so it doesn't have to be done for every item in every popup!
            prizeWindow2.setAnimationFromName("gfx")
            prizeWindow2Pos = prizeWindow2.getVariable(NAME_POS_VARIABLE)
            if prizeWindow2Pos != None:
                prizeWindow2.setPos((prizeWindow2Pos[0], prizeWindow2Pos[1] + RESOLUTION_NINTENDO_DS[1]))

        FadingPopupAnimBackground.__init__(self, laytonState, screenController, None, prizeWindow2)
        print(getTxt2String(ID_STOCK_SCREEN))