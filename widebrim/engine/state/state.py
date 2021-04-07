from typing import Optional

from ...madhatter.hat_io.asset_sav import Layton2SaveSlot
from ...madhatter.hat_io.asset_dlz.ev_inf2 import DlzEntryEvInf2, EventInfoList
from ...madhatter.hat_io.asset_dlz.sm_inf import DlzEntrySubmapInfo, SubmapInfo
from ...madhatter.hat_io.asset_placeflag import PlaceFlag
from ...madhatter.hat_io.asset_storyflag import StoryFlag
from ...madhatter.hat_io.asset_autoevent import AutoEvent
from ...madhatter.hat_io.asset_dlz.goal_inf import GoalInfo
from ...madhatter.hat_io.asset_dlz.nz_lst import NazoList
from ...madhatter.hat_io.asset_dlz.chp_inf import ChapterInfo
from ...madhatter.hat_io.asset_dlz.tm_def import TimeDefinitionInfo
from ...madhatter.hat_io.asset import LaytonPack, File
from ...madhatter.hat_io.asset_dat.nazo import NazoData

from ..const import LANGUAGES, EVENT_ID_START_PUZZLE, EVENT_ID_START_TEA, PATH_DB_EV_INF2, PATH_DB_SM_INF, PATH_PROGRESSION_DB, PATH_DB_RC_ROOT, PATH_DB_GOAL_INF, PATH_DB_NZ_LST, PATH_DB_TM_DEF, PATH_DB_RC_ROOT_LANG, PATH_DB_CHP_INF, PATH_PUZZLE_SCRIPT
from ..const import PATH_NAZO_A, PATH_NAZO_B, PATH_NAZO_C, PATH_PACK_NAZO
from ..exceptions import FileInvalidCritical
from ..file import FileInterface

from ...engine.anim.font.nftr_decode import NftrTiles

from time import time
from math import floor

from .enum_mode import GAMEMODES

class Layton2GameState():
    def __init__(self, language=LANGUAGES.Japanese):
        
        # Save header is unused during gameplay
        self.saveSlot       = Layton2SaveSlot()

        self.language       = language

        self._gameMode       = GAMEMODES.INVALID
        self._gameModeNext   = GAMEMODES.INVALID

        self._idEvent       = -1
        self._idMovieNum    = -1
        
        self.namePlace      = ""

        self.isFirstTouchEnabled    = False
        self.wasPuzzleSkipped       = False
        self.wasPuzzleSolved        = False
        self.wasPuzzleRestarted     = False
        self.puzzleLastReward       = -1

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
        self._dbChapterInfo     = None
        self._dbSubmapInfo      = None
        self._dbGoalInfo        = None
        self._dbSoundSetList    = None
        self._dbEventInfo       = None
        self._dbEventBaseList   = None
        self._dbPuzzleInfo      = None
        self._dbSubPhoto        = None
        self._dbTeaElement      = None
        self._dbTeaRecipe       = None
        self._dbTeaEventInfo    = None
        self._dbTeaTalk         = None
        self._dbNazoList        = None
        self._dbSubmapInfo      = None

        # TODO - Add to const
        try:
            self.font18             = NftrTiles(FileInterface.getData("/data_lt2/font/font18.NFTR"))
            self.fontEvent          = NftrTiles(FileInterface.getData("/data_lt2/font/fontevent.NFTR"))
            self.fontQ              = NftrTiles(FileInterface.getData("/data_lt2/font/fontq.NFTR"))
            self._dbNazoList        = NazoList()
            self._dbNazoList.load(FileInterface.getData(PATH_DB_RC_ROOT_LANG % (self.language.value, PATH_DB_NZ_LST)))
            self._dbTimeDef         = TimeDefinitionInfo()
            self._dbTimeDef.load(FileInterface.getData(PATH_DB_RC_ROOT % (PATH_DB_TM_DEF)))
        except:
            raise FileInvalidCritical()

        self.entryEvInfo : Optional[DlzEntryEvInf2] = None
        self.entryNzList    = None
        self._entryNzData    = None

        self.__isTimeStarted = False
        self.__timeStarted = 0

        # Not accurate, but used to centralise event behaviour between room and event
        self._wasLastEventIdBranching = False
        self.timeStartTimer()

    def timeGetStartedState(self):
        return self.__isTimeStarted

    def timeStartTimer(self):
        self.__isTimeStarted = True
        self.__timeStarted = time()

    def timeUpdateStoredTime(self):
        if self.timeGetStartedState():
            # TODO - Access method which changes the header time and save slot time simulataneously
            # This is only used to verify whether the save was tampered with which isn't that accuracy anyway
            # TODO - Is the padding after the time variable actually where the counting time is stored?
            self.saveSlot.timeElapsed = self.timeGetRunningTime()
            self.__timeStarted = time()

    def timeGetRunningTime(self):
        return max(floor(time() - self.__timeStarted), 0) + self.saveSlot.timeElapsed

    def setMovieNum(self, movieNum):
        self._idMovieNum = movieNum
    
    def getMovieNum(self):
        return self._idMovieNum

    def setPlaceNum(self, placeNum):
        if self.saveSlot.roomIndex != placeNum:
            self.saveSlot.idHeldAutoEvent = -1
        self.saveSlot.roomIndex = placeNum
    
    def getPlaceNum(self):
        return self.saveSlot.roomIndex

    def setGameMode(self, newGameMode):
        self._gameMode = newGameMode
    
    def getGameMode(self):
        return self._gameMode
    
    def setGameModeNext(self, newGameMode):
        self._gameModeNext = newGameMode
    
    def getGameModeNext(self):
        return self._gameModeNext

    def getTimeDefinitionEntry(self, idTime):
        indexEntry = self._dbTimeDef.searchForEntry(idTime)
        if indexEntry != None:
            return self._dbTimeDef.getEntry(indexEntry)
        return None

    def getEventInfoEntry(self, idEvent) -> Optional[DlzEntryEvInf2]:
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
        # As evidenced by event 15000, the game will accept events which are not inside
        # any event database and simply void out its own cached entry in RAM.
        # Without this behaviour implemented, 14510 will loop as it tries to connect to
        # 15000.
        entry = self.getEventInfoEntry(idEvent)
        self._idEvent = idEvent
        self.entryEvInfo = entry
        self._wasLastEventIdBranching = False
        return True
    
    def setEventIdBranching(self, idEvent):
        self.setEventId(idEvent)
        self._wasLastEventIdBranching = True
        return True
    
    def getEventId(self):

        if not(self._wasLastEventIdBranching):
            return self._idEvent

        def getOffsetIdWasViewed():
            if self.entryEvInfo.indexEventViewedFlag != None:
                if self.saveSlot.eventViewed.getSlot(self.entryEvInfo.indexEventViewedFlag):
                    return self._idEvent + 1
            return self._idEvent

        def getOffsetIdPuzzle():
            # Initial solved and quit not included as these seem to be the result of the puzzle handler
            # These will not be modified however
            if self.entryEvInfo.dataPuzzle != None:
                nazoListEntry = self.getNazoListEntry(self.entryEvInfo.dataPuzzle)
                if nazoListEntry != None:
                    entryPuzzle = self.saveSlot.puzzleData.getPuzzleData(nazoListEntry.idExternal - 1)
                    if entryPuzzle.wasSolved:
                        return self._idEvent + 2
                    elif entryPuzzle.wasEncountered:
                        return self._idEvent + 1
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
            elif self.entryEvInfo.typeEvent == 2:
                return getOffsetIdWasViewed()
            else:
                return self._idEvent
    
    def clearEventId(self):
        self._idEvent = -1
        self.entryEvInfo = None
    
    def setPuzzleId(self, idInternal):
        # Load nz info entry, set id
        self.entryNzList = self.getNazoListEntry(idInternal)
        if self.entryNzList == None:
            print("Failed to update entry!")

    def getCurrentNazoListEntry(self):
        return self.entryNzList

    def getNazoListEntry(self, idInternal):
        idEntry = self._dbNazoList.searchForEntry(idInternal)
        if idEntry != None:
            return self._dbNazoList.getEntry(idEntry)
        return None
    
    def getNazoListEntryByExternal(self, idExternal):
        for indexEntry in range(self._dbNazoList.getCountEntries()):
            entry = self._dbNazoList.getEntry(indexEntry)
            if entry.idExternal == idExternal:
                return entry
        return None

    def loadCurrentNazoData(self):
        if self.getCurrentNazoListEntry() != None:
            indexPuzzle = self.getCurrentNazoListEntry().idInternal
            # TODO - Store this max somewhere, it's already a save field
            if type(indexPuzzle) == int and 0 <= indexPuzzle < 216:
                if indexPuzzle < 60:
                    pathNazo = PATH_NAZO_A
                elif indexPuzzle < 120:
                    pathNazo = PATH_NAZO_B
                else:
                    pathNazo = PATH_NAZO_C
                
                packPuzzleData = FileInterface.getData(pathNazo % self.language.value)
                
                if packPuzzleData != None:
                    tempPackPuzzle = LaytonPack()
                    tempPackPuzzle.load(packPuzzleData)
                    packPuzzleData = tempPackPuzzle.getFile(PATH_PACK_NAZO % indexPuzzle)
                    if packPuzzleData != None:
                        self._entryNzData = NazoData()
                        if self._entryNzData.load(packPuzzleData):
                            return True

        self._entryNzData = None
        return False
    
    def getNazoData(self):
        return self._entryNzData

    def unloadCurrentNazoData(self):
        pass

    def loadChapterInfoDb(self):
        # TODO - What if this returns None
        self._dbChapterInfo = ChapterInfo()
        self._dbChapterInfo.load(FileInterface.getData(PATH_DB_RC_ROOT % PATH_DB_CHP_INF))

    def unloadChapterInfoDb(self):
        del self._dbChapterInfo
        self._dbChapterInfo = None

    def getChapterInfEntry(self):
        if self._dbChapterInfo == None:
            print("Bad: Chapter Info should have been loaded sooner!")
            self.loadChapterInfoDb()

        for indexEntry in range(self._dbChapterInfo.getCountEntries()):
            entry = self._dbChapterInfo.getEntry(indexEntry)
            if entry.chapter == self.saveSlot.chapter:
                return entry
        return None

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
    
    def loadSubmapInfo(self):
        if self._dbSubmapInfo == None:
            if (submapData := FileInterface.getData(PATH_DB_RC_ROOT % PATH_DB_SM_INF)) != None:
                self._dbSubmapInfo = SubmapInfo()
                self._dbSubmapInfo.load(submapData)
                return True
        return False

    def unloadSubmapInfo(self):
        del self._dbSubmapInfo
        self._dbSubmapInfo = None

    def getSubmapInfoEntry(self, indexEventViewed) -> Optional[DlzEntrySubmapInfo]:
        if indexEventViewed == 0 or self.saveSlot.eventViewed.getSlot(indexEventViewed):
            if self._dbSubmapInfo == None:
                self.loadSubmapInfo()
                print("Bad: Goal Info should have been loaded sooner!")

            if self._dbSubmapInfo != None:
                return self._dbSubmapInfo.searchForEntry(indexEventViewed, self.saveSlot.roomIndex, self.saveSlot.chapter)
        return None
    
    # TODO - Merge into madhatter, simpler
    def isAnthonyDiaryEnabled(self) -> bool:
        for indexFlag in range(16):
            if self.saveSlot.anthonyDiaryState.flagEnabled.getSlot(indexFlag):
                return True
        return False
    
    def isCameraAvailable(self) -> bool:
        return int.from_bytes(self.saveSlot.minigameCameraState.getCameraAvailableBytes(), byteorder = 'little') != 0
    
    def isCameraAssembled(self) -> bool:
        # Don't know best way to do this yet :(
        return False
    
    def isHamsterUnlocked(self) -> bool:
        return self.saveSlot.minigameHamsterState.isEnabled
    
    def isHamsterCompleted(self) -> bool:
        return self.saveSlot.minigameHamsterState.level == 0
    
    def isTeaEnabled(self) -> bool:
        for indexElement in range(self.saveSlot.minigameTeaState.flagElements.getLength()):
            if self.saveSlot.minigameTeaState.flagElements.getSlot(indexElement):
                return True
        return False

    def isTeaCompleted(self) -> bool:
        # TODO - More to this, maybe reserved bit elsewhere
        for indexElement in range(self.saveSlot.minigameTeaState.flagCorrect.getLength()):
            if not(self.saveSlot.minigameTeaState.flagCorrect.getSlot(indexElement)):
                return False
        return True