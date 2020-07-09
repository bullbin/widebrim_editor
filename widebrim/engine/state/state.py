from ...madhatter.hat_io.asset_sav import Layton2SaveSlot
from ...madhatter.hat_io.asset_dlz.ev_inf2 import EventInfoList
from ...madhatter.hat_io.asset_placeflag import PlaceFlag
from ...madhatter.hat_io.asset_storyflag import StoryFlag
from ...madhatter.hat_io.asset_autoevent import AutoEvent
from ...madhatter.hat_io.asset_dlz.goal_inf import GoalInfo
from ...madhatter.hat_io.asset import LaytonPack, File
from ..const import LANGUAGES, EVENT_ID_START_PUZZLE, EVENT_ID_START_TEA, PATH_DB_EV_INF2, PATH_PROGRESSION_DB, PATH_DB_RC_ROOT, PATH_DB_GOAL_INF
from ..exceptions import FileInvalidCritical
from ..file import FileInterface
from .enum_mode import GAMEMODES

class Layton2GameState():
    def __init__(self, language=LANGUAGES.Japanese):
        
        # Save header is unused during gameplay
        self.saveSlot       = Layton2SaveSlot()

        self.language       = language

        # TODO - Don't make these public so dbs can be dynamically loaded
        self._gameMode       = GAMEMODES.INVALID
        self._gameModeNext   = GAMEMODES.INVALID

        self.gameModeRestartRequired = False

        self._idEvent       = -1
        self.idMovieNum     = -1
        
        self.namePlace      = ""

        self.isFirstTouchEnabled = True

        self.dbPlaceFlag        = PlaceFlag()
        self.dbStoryFlag        = StoryFlag()
        self.dbAutoEvent        = AutoEvent()

        # Safe to assume always loaded
        try:
            packedProgressionDbs = LaytonPack()
            packedProgressionDbs.load(FileInterface.getData(PATH_PROGRESSION_DB))

            self.dbPlaceFlag.load(packedProgressionDbs.getFile("placeflag.dat"))
            self.dbStoryFlag.load(packedProgressionDbs.getFile("storyflag2.dat"))
            self.dbAutoEvent.load(packedProgressionDbs.getFile("autoevent2.dat"))

        except:
            raise FileInvalidCritical()

        # Loaded and unloaded where required
        # TODO - Do this by gamemode
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
    
    def setGameMode(self, newGameMode):
        if newGameMode == self._gameMode:
            self.gameModeRestartRequired = True
        self._gameMode = newGameMode
    
    def getGameMode(self):
        return self._gameMode
    
    def setGameModeNext(self, newGameMode):
        self._gameModeNext = newGameMode
    
    def getGameModeNext(self):
        return self._gameModeNext

    def getEventInfoEntry(self, idEvent):
        if self._dbEventInfo == None:
            # TODO : Load event info
            print("Bad: Event Info should have been loaded sooner!")
            self._dbEventInfo = EventInfoList()
            self._dbEventInfo.load(FileInterface.getData(PATH_DB_EV_INF2 % self.language.value))
        
        indexEntry = self._dbEventInfo.searchForEntry(idEvent)
        if indexEntry != None:
            return self._dbEventInfo.getEntry(indexEntry)

        return None

    def setEventId(self, idEvent):
        if idEvent == -1:
            self.clearEventId()
            return True

        entry = self.getEventInfoEntry(idEvent)
        if entry != None:
            self._idEvent = idEvent
            self.entryEvInfo = entry
            return True
        return False
    
    def getEventId(self):

        def getOffsetIdWasViewed():
            if self.entryEvInfo.indexEventViewedFlag != None:
                if self.saveSlot.eventViewed.getSlot(self.entryEvInfo.indexEventViewedFlag):
                    return self._idEvent + 1
            return self._idEvent

        def getOffsetIdPuzzle():
            # Initial solved and quit not included as these seem to be the result of the puzzle handler
            # These will not be modified however
            if self.entryEvInfo.dataPuzzle != None:
                entryPuzzle = self.saveSlot.puzzleData.getPuzzleData(self.entryEvInfo.dataPuzzle)
                if entryPuzzle.wasSolved:
                    return self._idEvent + 3
                elif entryPuzzle.wasEncountered:
                    return self._idEvent + 1
                else:
                    return getOffsetIdWasViewed()
            return self._idEvent
        
        def getOffsetIdLimit():
            countSolved, countEncountered = self.saveSlot.getSolvedAndEncounteredPuzzleCount()
            if countSolved >= self.entryEvInfo.dataPuzzle:
                return self._idEvent + 2
            return getOffsetIdWasViewed()

        if self.entryEvInfo == None:
            return self._idEvent

        if self.entryEvInfo.indexStoryFlag != None:
            self.saveSlot.storyFlag.setSlot(True, self.entryEvInfo.indexStoryFlag)
        
        if self._idEvent >= EVENT_ID_START_TEA:
            # Tea Event
            # TODO - Figure out progression on these
            return self._idEvent
        
        elif self._idEvent >= EVENT_ID_START_PUZZLE:
            # Puzzle Event (designated IDs)
            return getOffsetIdPuzzle()

        else:
            # Drama Event
            if self.entryEvInfo.typeEvent == 5:
                return getOffsetIdLimit()
            elif self.entryEvInfo.typeEvent == 3: # Seems to be autoevents, which do not have any branching available
                if getOffsetIdWasViewed() != self._idEvent:
                    self.clearEventId()
                return self._idEvent
            else:
                # TODO - Research remaining types 0,1,2,3,4
                return getOffsetIdWasViewed()
    
    def clearEventId(self):
        self._idEvent = -1
        self.entryEvInfo = None
    
    def setPuzzleId(self, idPuzzle):
        # Load nz info entry, set id
        pass

    def getGoalInfEntry(self):
        if self._dbGoalInfo == None:
             # TODO : Load goal info
            print("Bad: Goal Info should have been loaded sooner!")
            self._dbGoalInfo = GoalInfo()

            # Temporary workaround
            tempFile = File(data=FileInterface.getData(PATH_DB_RC_ROOT % PATH_DB_GOAL_INF))
            tempFile.decompressLz10()

            self._dbGoalInfo.load(tempFile.data)

        # TODO - Add madhatter search for goal_inf (why was this missing??)
        for indexEntry in range(self._dbGoalInfo.getCountEntries()):
            entry = self._dbGoalInfo.getEntry(indexEntry)

            # TODO - Does this use calculated ID?
            if entry.idEvent == self._idEvent:
                return entry
        return None