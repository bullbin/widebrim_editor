# Centralises assets used in an event so they can be reused
# This reduces asset duplication, as the structure of events
#     mean that the same asset won't be reused in the same
#     frame anyway

# TODO - Figure out remaining data left in event structure
#        Not everything is needed (eg keeping a save screen
#        in memory at all times) but critical images are a must

# TODO - Everything has init positions. Add them where required.

from ...engine_ext.utils import getAnimFromPath
from ...engine.file import FileInterface
from ...engine.const import RESOLUTION_NINTENDO_DS
from .const import PATH_PRIZE_WINDOW, PATH_CURSOR_WAIT, PATH_ITEM_ICON, PATH_PIECE_ICON, POS_ITEM_ICON_Y

class EventStorage():
    def __init__(self):
        self.__prizeWindow2 = None
        self.__rewardWindow = None
        self.__cursor_wait  = None
        self.__item_icon    = None
        self.__piece_icon   = None

    def getAssetPrizeWindow2(self):
        if self.__prizeWindow2 == None:
            self.__prizeWindow2 = getAnimFromPath(PATH_PRIZE_WINDOW)
        return self.__prizeWindow2
    
    def getAssetCursorWait(self):
        if self.__cursor_wait == None:
            self.__cursor_wait = getAnimFromPath(PATH_CURSOR_WAIT)
        return self.__cursor_wait
    
    def getAssetItemIcon(self):
        if self.__item_icon == None:
            self.__item_icon = getAnimFromPath(PATH_ITEM_ICON)
            self.__item_icon.setPos(((RESOLUTION_NINTENDO_DS[0] - self.__item_icon.getDimensions()[0]) // 2, POS_ITEM_ICON_Y + RESOLUTION_NINTENDO_DS[1]))
        return self.__item_icon
    
    def getAssetPieceIcon(self):
        if self.__piece_icon == None:
            self.__piece_icon = getAnimFromPath(PATH_PIECE_ICON)
        return self.__piece_icon