from ...madhatter.hat_io.asset_sav import Layton2SaveSlot
from .enum_mode import GAMEMODES
from ..const import LANGUAGES

class Layton2GameState():
    def __init__(self, language=LANGUAGES.Japanese):
        
        # Save header is unused during gameplay
        self.saveSlot       = Layton2SaveSlot()

        self.language       = language

        self.gameMode       = GAMEMODES.INVALID
        self.gameModeNext   = GAMEMODES.INVALID

        self.idEvent        = -1
        self.idMovieNum     = -1
        
        self.namePlace      = ""

        self.isFirstTouchEnabled = True

        # Safe to assume always loaded
        self.dbPlaceFlag        = None
        self.dbStoryFlag        = None
        self.dbAutoEvent        = None

        # Loaded and unloaded where required
        self._dbChapterInfo      = None
        self._dbSubmapInfo       = None
        self._dbGoalInfo         = None
        self._dbSoundSetList     = None
        self._dbEventInfo        = None
        self._dbEventBaseList    = None
        self._dbPuzzleInfo       = None
        self._dbSubPhoto         = None
        self._dbTeaElement       = None
        self._dbTeaRecipe        = None
        self._dbTeaEventInfo     = None
        self._dbTeaTalk          = None

        self.entryEvInfo    = None
        self.entryNzList    = None
    
    def getEventInfoEntry(self, idEvent):
        if self._dbEventInfo == None:
            # TODO : Load event info
            pass
        
        indexEntry = self._dbEventInfo.searchForEntry(idEvent)
        if indexEntry != None:
            return self._dbEventInfo.getEntry(indexEntry)

        return None

    def setEventId(self, idEvent):
        entry = self.getEventInfoEntry(idEvent)
        if entry != None:
            self.idEvent = idEvent
            self.entryEvInfo = entry
            return True
        return False
    
    def clearEventId(self):
        self.eventId = -1