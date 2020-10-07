# Notes

# Loads nazo_icon just for the popup, and positions it to 0x74, 0x3c

from .utils import PrizeWindow2PopupWithCursor
from ....engine_ext.utils import getTxt2String
from .const import ID_STOCK_SCREEN

class StockPopup(PrizeWindow2PopupWithCursor):
    def __init__(self, laytonState, screenController, eventStorage):
        PrizeWindow2PopupWithCursor.__init__(self, laytonState, screenController, eventStorage)
        print(getTxt2String(laytonState, ID_STOCK_SCREEN))