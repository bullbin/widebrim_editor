from typing import Dict, List, Optional
from widebrim.engine.const import PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C
from widebrim.engine.file import FileInterface, VirtualArchive
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine.state.state import Layton2GameState
from widebrim.gamemodes.core_popup.script import ScriptPlayer
from widebrim.gamemodes.dramaevent import EventPlayer
from widebrim.gamemodes.dramaevent.dramaevent import CharacterController
from widebrim.gamemodes.dramaevent.storage import EventStorage
from widebrim.madhatter.hat_io.asset_script import GdScript
from widebrim.madhatter.hat_io.asset_dat.event import EventData

class ModifiedEventPlayer(EventPlayer):
    def __init__(self, laytonState : Layton2GameState, screenController, script : GdScript, eventData : EventData, spawnId : int):
        ScriptPlayer.__init__(self, laytonState, screenController, GdScript())
        
        def substituteEventPath(inPath, inPathA, inPathB, inPathC):

            def trySubstitute(path, lang, evId):
                try:
                    return path % (lang, evId)
                except TypeError:
                    return path % evId

            if self._idMain != 24:
                return trySubstitute(inPath, self.laytonState.language.value, self._idMain)
            elif self._idSub < 300:
                return trySubstitute(inPathA, self.laytonState.language.value, self._idMain)
            elif self._idSub < 600:
                return trySubstitute(inPathB, self.laytonState.language.value, self._idMain)
            else:
                return trySubstitute(inPathC, self.laytonState.language.value, self._idMain)

        def getEventTalkPath():
            return substituteEventPath(PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C)

        self.laytonState.setGameMode(GAMEMODES.Room)
        self._packEventTalk : Optional[VirtualArchive] = FileInterface.getPack(getEventTalkPath())
        
        self._id = spawnId
        self._idMain = spawnId // 1000
        self._idSub = spawnId % 1000

        self.talkScript     = GdScript()

        self.characters : List[CharacterController] = []
        self.nameCharacters = []
        self.characterSpawnIdToCharacterMap : Dict[int, CharacterController] = {}

        self._sharedImageHandler = EventStorage()

        self._doGoalSet = True

        self._loadEventAndScriptData(script, eventData)
    
    def doOnComplete(self):
        if self._doGoalSet:
            goalInfoEntry = self.laytonState.getGoalInfEntry(self._id)
            if goalInfoEntry != None:
                self._makeActive()
                self.laytonState.saveSlot.goal = goalInfoEntry.goal
                self._doGoalSet = False
                self.__doMokutekiWindow(goalInfoEntry.type, goalInfoEntry.goal)
        # Don't allow calling the kill command