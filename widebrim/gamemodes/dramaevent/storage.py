# Centralises assets used in an event so they can be reused
# This reduces asset duplication, as the structure of events
#     mean that the same asset won't be reused in the same
#     frame anyway

# TODO - Figure out remaining data left in event structure
#        Not everything is needed (eg keeping a save screen
#        in memory at all times) but critical images are a must

from ...engine_ext.utils import getAnimFromPath
from ...engine.file import FileInterface
from .const import PATH_PRIZE_WINDOW, PATH_CURSOR_WAIT, PATH_ITEM_ICON

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
        return self.__item_icon