from widebrim.engine_ext.utils import getAnimFromPath
from widebrim.gamemodes.dramaevent.popup.utils import PrizeWindow2PopupWithCursor

class ItemAddPopup(PrizeWindow2PopupWithCursor):
    def __init__(self, laytonState, screenController, eventStorage, idChar : int):
        PrizeWindow2PopupWithCursor.__init__(self, laytonState, screenController, eventStorage)
        self.__animParty = None