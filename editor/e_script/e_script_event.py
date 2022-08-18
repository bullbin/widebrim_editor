from typing import Dict, List, Optional
from editor.asset_management.character import CharacterEntry
from editor.e_script.virtual.custom_instructions.dialogue import DialogueInstructionDescription, DialogueInstructionGenerator
from editor.gui.command_annotator.bank import Context, OperandType, ScriptVerificationBank
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from widebrim.engine.const import PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C, PATH_PACK_EVENT_SCR, RESOLUTION_NINTENDO_DS, PATH_PACK_EVENT_DAT
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.madhatter.common import logSevere
from widebrim.madhatter.hat_io.asset_dat.event import EventData
from widebrim.madhatter.hat_io.asset_script import GdScript, Operand
from .e_script_generic import FrameScriptEditor
from wx import Bitmap, NOT_FOUND, Window
from pygame import Surface
from pygame.transform import flip
from pygame.image import tostring

from widebrim.gamemodes.dramaevent.const import PATH_BODY_ROOT, PATH_BODY_ROOT_LANG_DEP
from widebrim.engine_ext.utils import getBottomScreenAnimFromPath

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

class FrameEventEditor(FrameScriptEditor):

    SLOT_OFFSET = {0:0x30,     1:0x80,
                   2:0xd0,     3:0x20,
                   4:0x58,     5:0xa7,
                   6:0xe0}
    SLOT_LEFT  = [0,3,4]    # Left side characters need flipping

    def __init__(self, parent : Window, state: Layton2GameState, bankInstructions: ScriptVerificationBank, idEvent: int, characters : List[CharacterEntry], characterNames : List[Optional[str]]):

        self._idEvent = idEvent
        self._idMain = idEvent // 1000
        self._idSub = idEvent % 1000

        self.__eventData        : Optional[EventData] = None
        self.__eventCharacters  : List[AnimatedImageObject] = []

        self.__idToCharacter : Dict[int, Optional[str]] = {}
        for char, name in zip(characters, characterNames):
            self.__idToCharacter[char.getIndex()] = name

        self.__backgroundWidebrim = Surface(RESOLUTION_NINTENDO_DS).convert_alpha()
        self.__backgroundWidebrim.fill((0,0,0,1))

        self.__mapActiveCharacterIndexToRealIndex = {}
        self.__activeCharacterImage : Optional[AnimatedImageObject] = None
        self.__selectedCharacterIndex : Optional[int] = None

        super().__init__(parent, state, bankInstructions, None, context=Context.DramaEvent)
    
    def prepareWidebrimState(self):
        # Hopefully don't need to call sync here - hope that the state was loaded properly
        # Calling sync here causes changes to ROM under current heuristic which is no good
        # TODO - Maybe detect state before so we can sync anyway without changes
        self._state.setEventId(self._idEvent)
        return GAMEMODES.DramaEvent

    def _substituteEventPath(self, inPath, inPathA, inPathB, inPathC):

        def trySubstitute(path, lang, evId):
            try:
                return path % (lang, evId)
            except TypeError:
                return path % evId

        # TODO - Update this in widebrim too
        if self._idMain != 24:
            return trySubstitute(inPath, self._state.language.value, self._idMain)
        elif self._idSub < 300:
            return trySubstitute(inPathA, self._state.language.value, self._idMain)
        elif self._idSub < 600:
            return trySubstitute(inPathB, self._state.language.value, self._idMain)
        else:
            return trySubstitute(inPathC, self._state.language.value, self._idMain)

    def _getEventTalkPath(self):
        return self._substituteEventPath(PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C)

    def _getEventScriptPath(self):
        return self._substituteEventPath(PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C)

    def _getExportScript(self) -> GdScript:
        exportScript = GdScript()
        self._eventScript.save()
        exportScript.load(self._eventScript.data)

        generator = DialogueInstructionGenerator(self._state.getFileAccessor(), self._getEventTalkPath(), self._idEvent)
        generator.convertToOriginal(exportScript)
        return exportScript
    
    def _getCharacterName(self, idChar : int) -> str:
        if idChar in self.__idToCharacter:
            if self.__idToCharacter[idChar] == None:
                return "%i" % idChar
            return "%s" % self.__idToCharacter[idChar]
        if idChar == 0:
            return "Hidden"
        return "Unrecognized, %i" % idChar

    def getNameForOperandType(self, operandType: OperandType, operand: Operand) -> Optional[str]:
        if operandType == OperandType.InternalCharacterId:
            idChar = operand.value
            return "Character: %s" % self._getCharacterName(idChar)
        elif operandType == OperandType.IndexEventDataCharacter:
            value = operand.value
            if 0 <= value < len(self.__eventData.characters):
                idChar = self.__eventData.characters[value]
                return "Character: %s" % self._getCharacterName(idChar)
            return "Character: Affects invalid character slot!"
        return super().getNameForOperandType(operandType, operand)

    def __getCharacterAnim(self, indexChar : int) -> Optional[AnimatedImageObject]:
        if indexChar == 86 or indexChar == 87:
            return getBottomScreenAnimFromPath(self._state, (PATH_BODY_ROOT_LANG_DEP % indexChar), enableSubAnimation=True)
        return getBottomScreenAnimFromPath(self._state, PATH_BODY_ROOT % indexChar, enableSubAnimation=True)

    def _refresh(self):

        def loadScript() -> GdScript:
            if (data := self._state.getFileAccessor().getPackedData(self._getEventScriptPath(), PATH_PACK_EVENT_SCR % (self._idMain, self._idSub))) != None:
                eventScript = GdScript()
                eventScript.load(data)

                if self._bankInstructions.getInstructionByOpcode(DialogueInstructionDescription.TARGET_OPERAND) == None:
                    self._bankInstructions.addInstruction(DialogueInstructionDescription())

                generator = DialogueInstructionGenerator(self._state.getFileAccessor(), self._getEventTalkPath(), self._idEvent)
                generator.convertToVirtual(eventScript)
                return eventScript
            return GdScript()

        def loadEventData() -> EventData:
            if (data := self._state.getFileAccessor().getPackedData(self._getEventScriptPath(), PATH_PACK_EVENT_DAT % (self._idMain, self._idSub))) != None:
                eventData = EventData()
                eventData.load(data)
                newItems = []
                for character in eventData.characters:
                    newItems.append(self._getCharacterName(character))
                    self.__eventCharacters.append(self.__getCharacterAnim(character))
                    self.__eventCharacters[-1].setPos((0,0))
                self.listAllCharacters.AppendItems(newItems)
                if len(eventData.characters) > 0:
                    self.listAllCharacters.SetSelection(0)
                    
                return eventData
            return EventData()

        self._eventScript = loadScript()
        self.__eventData = loadEventData()
        self.__updateCharacterSelection()
        return super()._refresh()

    def _getExportScript(self) -> GdScript:
        exportScript = GdScript()
        self._eventScript.save()
        exportScript.load(self._eventScript.data)
        generator = DialogueInstructionGenerator(self._state.getFileAccessor(), self._getEventTalkPath(), self._idEvent)
        generator.convertToOriginal(exportScript)
        return exportScript

    def syncChanges(self):
        # TODO - Compile with file builders
        packEvent = self._state.getFileAccessor().getPack(self._getEventScriptPath())

        filenameScript = PATH_PACK_EVENT_SCR % (self._idMain, self._idSub)
        filenameData = PATH_PACK_EVENT_DAT % (self._idMain, self._idSub)

        exportScript = self._getExportScript()
        exportScript.save()
        self.__eventData.save()

        # TODO - Madhatter archive support rewrite, this is terrible syntax. Could break very, very easily
        # TODO - Is it possible for either to be missing?
        for file in packEvent.files:
            if file.name == filenameScript:
                file.data = exportScript.data
            elif file.name == filenameData:
                file.data = self.__eventData.data

        packEvent.save()
        packEvent.compress()
        self._state.getFileAccessor().writeableFs.replaceFile(self._getEventScriptPath(), packEvent.data)
        print("synced?")

    def __updateCharacterSelection(self):
        selection = self.listAllCharacters.GetSelection()
        if selection == NOT_FOUND:
            return
        else:
            self.__selectedCharacterIndex = selection

        character = self.__eventCharacters[selection]
        
        if character != None:
            if self.__activeCharacterImage != character:
                self.__activeCharacterImage = character
                self.__generateCharacterPreview()

            if self.__eventData.charactersPosition[selection] not in MAP_INGAME_TO_POS:
                # Force invalidate it
                self.__eventData.charactersPosition[selection] = 7
            
            self.choiceCharacterSlot.SetSelection(MAP_INGAME_TO_POS[self.__eventData.charactersPosition[selection]])
            self.__generateAnimCheckboxes()

    def __generateAnimCheckboxes(self):

        def isNameGood(name) -> bool:
            if len(name) > 0:
                if name[0] != "*" and name != "Create an Animation":
                    return True
            return False

        self.choiceCharacterAnimStart.Clear()
            
        # TODO - access to animation details, dunno if this is accurate tbh
        # TODO - Awful, requires subanimation (not guarenteed!!!)
        selection = self.__selectedCharacterIndex
        if selection != None and self.__eventData != None:
            self.checkDisableCharacterVisibility.SetValue(not(self.__eventData.charactersShown[selection]))
            character = self.__eventCharacters[selection]
            if character != None:
                newAnims = []
                for indexAnim in range(256):
                    if character.setAnimationFromIndex(indexAnim):
                        newAnims.append(character.getAnimationName())
                    else:
                        break

                if self.__eventData.charactersInitialAnimationIndex[selection] >= len(newAnims):
                    print("Invalid animation index!!!")
                    # If initial animation index is bad, override it to zero (which is invalid, but invisible so who cares)
                    self.__eventData.charactersInitialAnimationIndex[selection] = 0
                
                addToList = []
                target : Optional[int] = None
                self.__mapActiveCharacterIndexToRealIndex = {}
                for idxAnim, newAnim in enumerate(newAnims):
                    if (self.checkDisableBadAnims.IsChecked() and (idxAnim == self.__eventData.charactersInitialAnimationIndex[selection] or isNameGood(newAnim))) or not(self.checkDisableBadAnims.IsChecked()):
                        if idxAnim == self.__eventData.charactersInitialAnimationIndex[selection]:
                            target = len(addToList)
                        self.__mapActiveCharacterIndexToRealIndex[len(self.__mapActiveCharacterIndexToRealIndex.keys())] = idxAnim
                        addToList.append(newAnim)
                
                self.choiceCharacterAnimStart.AppendItems(addToList)
                self.choiceCharacterAnimStart.SetSelection(target)
            else:
                print("FAILED TO LOAD CHARACTER...")

    def __generateCharacterPreview(self):
        def getImageOffset(imageCharacter : AnimatedImageObject):
            offset = imageCharacter.getVariable("drawoff")
            if offset != None:
                return (offset[0], abs(offset[1]))
            else:
                return (0,0)

        self.__backgroundWidebrim.fill((0,0,0,1))
        if self.__activeCharacterImage == None:
            self.__backgroundWidebrim.fill((0,0,0,1))
        if self.__eventData.charactersShown[self.__selectedCharacterIndex]:

            self.__activeCharacterImage.setAnimationFromIndex(self.__eventData.charactersInitialAnimationIndex[self.__selectedCharacterIndex])
            slot = self.__eventData.charactersPosition[self.__selectedCharacterIndex]
            if slot in FrameEventEditor.SLOT_OFFSET:
                offset = FrameEventEditor.SLOT_OFFSET[slot]
            else:
                # TODO - Test invalid slot, iirc it's the middle
                slot = 1
                offset = FrameEventEditor.SLOT_OFFSET[1]

            variableOffset = getImageOffset(self.__activeCharacterImage)

            if slot in FrameEventEditor.SLOT_LEFT:
                characterIsFlipped = True
                drawLocation = (offset - (self.__activeCharacterImage.getDimensions()[0] // 2) - variableOffset[0], RESOLUTION_NINTENDO_DS[1] - variableOffset[1] - self.__activeCharacterImage.getDimensions()[1])
            else:
                characterIsFlipped = False
                drawLocation = (offset - (self.__activeCharacterImage.getDimensions()[0] // 2) + variableOffset[0], RESOLUTION_NINTENDO_DS[1] - variableOffset[1] - self.__activeCharacterImage.getDimensions()[1])
            
            characterFlippedSurface = Surface(self.__activeCharacterImage.getDimensions()).convert_alpha()
            characterFlippedSurface.fill((0,0,0,0))
            self.__activeCharacterImage.draw(characterFlippedSurface)
            if characterIsFlipped:
                characterFlippedSurface = flip(characterFlippedSurface, True, False)
            
            self.__backgroundWidebrim.blit(characterFlippedSurface, drawLocation)
        
        self.bitmapRenderCharacterPreview.SetBitmap(Bitmap.FromBufferRGBA(RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1], tostring(self.__backgroundWidebrim, "RGBA")))

    def __shiftEventData(self, newId : int):
        idChar = self.__eventData.characters[self.__selectedCharacterIndex]

        remapIndices : List[int] = []
        for indexChar, char in enumerate(self.__eventData.characters):
            remapIndices.append(indexChar)

        # Shift related components down
        remapIndices.insert(newId, remapIndices.pop(self.__selectedCharacterIndex))
        self.__eventData.characters.insert(newId, self.__eventData.characters.pop(self.__selectedCharacterIndex))
        self.__eventData.charactersPosition.insert(newId, self.__eventData.charactersPosition.pop(self.__selectedCharacterIndex))
        self.__eventData.charactersInitialAnimationIndex.insert(newId, self.__eventData.charactersInitialAnimationIndex.pop(self.__selectedCharacterIndex))
        self.__eventData.charactersShown.insert(newId, self.__eventData.charactersShown.pop(self.__selectedCharacterIndex))
        self.__eventCharacters.insert(newId, self.__eventCharacters.pop(self.__selectedCharacterIndex))

        self.listAllCharacters.Delete(self.__selectedCharacterIndex)
        self.listAllCharacters.Insert(self._getCharacterName(idChar), newId)

        self.__selectedCharacterIndex = newId
        self.listAllCharacters.SetSelection(self.__selectedCharacterIndex)

        for idxInstruction in range(self._eventScript.getInstructionCount()):
            instruction = self._eventScript.getInstruction(idxInstruction)
            definition = self._bankInstructions.getInstructionByOpcode(int.from_bytes(instruction.opcode, byteorder='little'))
            if definition != None:
                for idxOperand, operand in enumerate(instruction.getFilteredOperands()):
                    if (operandDef := definition.getOperand(idxOperand)) != None:
                        if operandDef.operandType == OperandType.IndexEventDataCharacter:
                            operand : Operand
                            if 0 <= operand.value < len(remapIndices):
                                operand.value = remapIndices[operand.value]
                            else:
                                logSevere("Failed to remap index", operand.value, name=FrameEventEditor.LOG_MODULE_NAME)

    def btnCharMoveUpOnButtonClick(self, event):
        if self.__selectedCharacterIndex != None and self.__selectedCharacterIndex > 0:
            self.__shiftEventData(self.__selectedCharacterIndex - 1)
        return super().btnCharMoveUpOnButtonClick(event)
    
    def btnCharMoveDownOnButtonClick(self, event):
        if self.__selectedCharacterIndex != None and self.__selectedCharacterIndex < len(self.__eventCharacters) - 1:
            self.__shiftEventData(self.__selectedCharacterIndex + 1)
        return super().btnCharMoveDownOnButtonClick(event)

    def choiceCharacterSlotOnChoice(self, event):
        if self.__selectedCharacterIndex != None:
            slot = MAP_POS_TO_INGAME[self.choiceCharacterSlot.GetSelection()]
            self.__eventData.charactersPosition[self.__selectedCharacterIndex] = slot
            self.__generateCharacterPreview()
        return super().choiceCharacterSlotOnChoice(event)

    def choiceCharacterAnimStartOnChoice(self, event):
        if self.__selectedCharacterIndex != None:
            selection = self.choiceCharacterAnimStart.GetSelection()
            indexAnim = self.__mapActiveCharacterIndexToRealIndex[selection]
            self.__eventData.charactersInitialAnimationIndex[self.__selectedCharacterIndex] = indexAnim
            if self.__activeCharacterImage != None:
                # TODO - Will probably fail with initial anim
                # self.__activeCharacterImage.setAnimationFromIndex(indexAnim)
                self.__generateCharacterPreview()

        return super().choiceCharacterAnimStartOnChoice(event)

    def checkDisableCharacterVisibilityOnCheckBox(self, event):
        if self.__selectedCharacterIndex != None:
            self.__eventData.charactersShown[self.__selectedCharacterIndex] = not(self.checkDisableCharacterVisibility.GetValue())
            if self.__activeCharacterImage != None:
                self.__generateCharacterPreview()
        return super().checkDisableCharacterVisibilityOnCheckBox(event)
       
    def listAllCharactersOnListBoxDClick(self, event):
        self.__updateCharacterSelection()
        return super().listAllCharactersOnListBoxDClick(event)
    
    def checkDisableBadAnimsOnCheckBox(self, event):
        self.__generateAnimCheckboxes()
        return super().checkDisableBadAnimsOnCheckBox(event)
    
    def paneCharactersOnCollapsiblePaneChanged(self, event):
        self.paneCharacters.GetParent().Layout()
        return super().paneCharactersOnCollapsiblePaneChanged(event)