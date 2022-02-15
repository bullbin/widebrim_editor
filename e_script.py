from typing import List, Optional
from widebrim.engine.anim.image_anim.image import AnimatedImageObject, AnimatedImageObjectWithSubAnimation
from widebrim.engine.const import PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C, PATH_PACK_EVENT_DAT
from widebrim.engine.file import FileInterface
from widebrim.engine.state.state import Layton2GameState
from widebrim.engine_ext.utils import getAnimFromPath, getBottomScreenAnimFromPath
from widebrim.gamemodes.dramaevent.const import PATH_BODY_ROOT, PATH_BODY_ROOT_LANG_DEP
from widebrim.madhatter.hat_io.asset_dat.event import EventData

from nopush_editor import editorScript
from wx import ID_ANY, DefaultPosition, Size, TAB_TRAVERSAL, EmptyString, NOT_FOUND

MAP_POS_TO_INGAME = {0:0,
                     1:3,
                     2:4,
                     3:1,
                     4:2,
                     5:5,
                     6:6,
                     7:7}
MAP_INGAME_TO_POS = {0:0,
                     3:1,
                     4:2,
                     1:3,
                     2:4,
                     5:5,
                     6:6,
                     7:7}
MAP_CHAR_ID_TO_NAME = {1:"Layton",
                       2:"Luke",
                       3:"Dr. Schrader"}

class FrameScriptEditor(editorScript):
    def __init__(self, parent, idEvent : int, state : Layton2GameState, id=ID_ANY, pos=DefaultPosition, size=Size(500, 550), style=TAB_TRAVERSAL, name=EmptyString):
        super().__init__(parent, id, pos, size, style, name)

        self.__state = state
        self.__eventData :  Optional[EventData] = None
        self.__eventCharacters : List[AnimatedImageObject] = []
        self.__idEvent = idEvent
        self.__idMain = self.__idEvent // 1000
        self.__idSub = self.__idEvent % 1000
        # self.__state.dbAutoEvent
        self.__mapActiveCharacterIndexToRealIndex = {}
        self._refresh()
    
    def _refresh(self):

        def substituteEventPath(inPath, inPathA, inPathB, inPathC):

            def trySubstitute(path, lang, evId):
                try:
                    return path % (lang, evId)
                except TypeError:
                    return path % evId

            # TODO - Update this in widebrim too
            if self.__idMain != 24:
                return trySubstitute(inPath, self.__state.language.value, self.__idMain)
            elif self.__idSub < 300:
                return trySubstitute(inPathA, self.__state.language.value, self.__idMain)
            elif self.__idSub < 600:
                return trySubstitute(inPathB, self.__state.language.value, self.__idMain)
            else:
                return trySubstitute(inPathC, self.__state.language.value, self.__idMain)

        def getEventTalkPath():
            return substituteEventPath(PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C)

        def getEventScriptPath():
            return substituteEventPath(PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C)

        entry = self.__state.getEventInfoEntry(self.__idEvent)
        if entry == None:
            return
        
        eventData = EventData()
        if (data := FileInterface.getPackedData(getEventScriptPath(), PATH_PACK_EVENT_DAT % (self.__idMain, self.__idSub))) != None:
            eventData.load(data)
            self.__eventData = eventData
            newItems = []
            for character in eventData.characters:
                if character in MAP_CHAR_ID_TO_NAME:
                    newItems.append(MAP_CHAR_ID_TO_NAME[character])
                else:
                    newItems.append(str(character))
                self.__eventCharacters.append(self.__getCharacter(character))
            self.listAllCharacters.AppendItems(newItems)
            if len(eventData.characters) > 0:
                self.listAllCharacters.SetSelection(0)
                self.__updateCharacterSelection()

    def __getCharacter(self, indexCharacter : int) -> Optional[AnimatedImageObject]:
        if indexCharacter == 86 or indexCharacter == 87:
            return getAnimFromPath((PATH_BODY_ROOT_LANG_DEP % indexCharacter).replace("?", self.__state.language.value), enableSubAnimation=True)
        return getAnimFromPath(PATH_BODY_ROOT % indexCharacter, enableSubAnimation=True)

    def __generateAnimCheckboxes(self):

        def isNameGood(name) -> bool:
            #if self.chec
            if len(name) > 0:
                if name[0] != "*":
                    return True
            return False

        self.choiceCharacterAnimStart.Clear()
            
        # TODO - access to animation details, dunno if this is accurate tbh
        # TODO - Awful, requires subanimation (not guarenteed!!!)
        selection = self.listAllCharacters.GetSelection()
        character = self.__eventCharacters[selection]
        if character != None:
            newAnims = []
            for indexAnim in range(256):
                if character.setAnimationFromIndex(indexAnim):
                    newAnims.append(character.getAnimationName())
                else:
                    break

            if self.__eventData.charactersInitialAnimationIndex[selection] >= len(newAnims):
                # If initial animation index is bad, override it to zero (which is invalid, but invisible so who cares)
                self.__eventData.charactersInitialAnimationIndex[selection] = 0
            
            # TODO - Not working lol
            addToList = []
            target : Optional[int] = None
            for idxAnim, newAnim in enumerate(newAnims):
                if idxAnim == 0 or not(isNameGood(newAnim)):
                    if idxAnim == self.__eventData.charactersInitialAnimationIndex[selection]:
                        target = len(self.__mapActiveCharacterIndexToRealIndex.keys())
                        self.__mapActiveCharacterIndexToRealIndex[len(self.__mapActiveCharacterIndexToRealIndex.keys())] = idxAnim
                        
                        addToList.append(newAnim)
                else:
                    if idxAnim == self.__eventData.charactersInitialAnimationIndex[selection]:
                        target = len(self.__mapActiveCharacterIndexToRealIndex.keys())
                    self.__mapActiveCharacterIndexToRealIndex[len(self.__mapActiveCharacterIndexToRealIndex.keys())] = idxAnim
                    addToList.append(newAnim)
                    
            self.choiceCharacterAnimStart.AppendItems(addToList)
            if target != None:
                self.choiceCharacterAnimStart.SetSelection(target)

    def __updateCharacterSelection(self):
        selection = self.listAllCharacters.GetSelection()
        if selection == NOT_FOUND:
            return
        # TODO - Update bitmap

        character = self.__eventCharacters[selection]
        if character != None:
            if self.__eventData.charactersPosition[selection] not in MAP_INGAME_TO_POS:
                # Force invalidate it
                self.__eventData.charactersPosition[selection] = 7
            
            self.choiceCharacterSlot.SetSelection(MAP_INGAME_TO_POS[self.__eventData.charactersPosition[selection]])
            
            self.__generateAnimCheckboxes()

            if character.setAnimationFromIndex(self.__eventData.charactersInitialAnimationIndex[selection]):
                # TODO - set bitmap
                self.choiceCharacterAnimStart.SetSelection(self.__eventData.charactersInitialAnimationIndex[selection])
                pass
            else:
                pass
            
    def listAllCharactersOnListBoxDClick(self, event):
        self.__updateCharacterSelection()
        return super().listAllCharactersOnListBoxDClick(event)