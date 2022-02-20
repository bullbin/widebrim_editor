from typing import List, Optional
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from widebrim.engine.const import PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C, PATH_PACK_EVENT_DAT, PATH_PACK_EVENT_SCR, RESOLUTION_NINTENDO_DS
from widebrim.engine.file import FileInterface
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine.state.state import Layton2GameState
from widebrim.engine_ext.utils import getAnimFromPath
from widebrim.gamemodes.dramaevent.const import PATH_BODY_ROOT, PATH_BODY_ROOT_LANG_DEP
from widebrim.madhatter.hat_io.asset_dat.event import EventData

from nopush_editor import editorScript
from wx import ID_ANY, DefaultPosition, Size, TAB_TRAVERSAL, EmptyString, NOT_FOUND

from widebrim.madhatter.hat_io.asset_script import GdScript, Operand
from widebrim.gui.command_annotator import Context
from pygame import Surface
from pygame.transform import flip
from pygame.image import tostring
from wx import BitmapFromBufferRGBA, EmptyBitmapRGBA

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

def getInstructionName(opcode : bytes):
    return str(opcode)

def getOperandName(opcode : bytes, operand : Operand):
    return str(operand.value)

class FrameScriptEditor(editorScript):

    SLOT_OFFSET = {0:0x30,     1:0x80,
                   2:0xd0,     3:0x20,
                   4:0x58,     5:0xa7,
                   6:0xe0}
    SLOT_LEFT  = [0,3,4]    # Left side characters need flipping

    def __init__(self, parent, idEvent : int, state : Layton2GameState, id=ID_ANY, pos=DefaultPosition, size=Size(640, 640), style=TAB_TRAVERSAL, name=EmptyString):
        super().__init__(parent, id, pos, size, style, name)

        self.__state = state
        self.__context = None
        self.__eventData :  Optional[EventData] = None
        self.__eventScript : Optional[GdScript] = None

        self.__backgroundWidebrim = Surface(RESOLUTION_NINTENDO_DS).convert_alpha()
        self.__backgroundWidebrim.fill((0,0,0,1))

        self.__eventCharacters : List[AnimatedImageObject] = []
        self.__idEvent = idEvent
        self.__idMain = self.__idEvent // 1000
        self.__idSub = self.__idEvent % 1000
        # self.__state.dbAutoEvent
        self.__mapActiveCharacterIndexToRealIndex = {}
        self.__activeCharacterImage : Optional[AnimatedImageObject] = None
        self.__setContext(Context.DramaEvent)

        self._refresh()
        if self.__eventScript != None:
            self.__generateScriptingTree(self.__eventScript)
    
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
        self.__eventData = None
        self.__eventScript = None
        if entry == None:
            return
        
        if self.__context == Context.DramaEvent:
            
            if (data := FileInterface.getPackedData(getEventScriptPath(), PATH_PACK_EVENT_DAT % (self.__idMain, self.__idSub))) != None:
                eventData = EventData()
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
            
            if (data := FileInterface.getPackedData(getEventScriptPath(), PATH_PACK_EVENT_SCR % (self.__idMain, self.__idSub))) != None:
                eventScript = GdScript()
                eventScript.load(data)
                self.__eventScript = eventScript

    def __setContext(self, context : Context):
        self.__context = context
        self.textScriptingContext.SetLabel(str(context)[8:])
        if context != Context.DramaEvent:
            self.staticTextBranchingWarning.Destroy()
            self.panelStateControls.Destroy()
            self.paneCharacters.Destroy()
            self.Layout()

    def __getCharacter(self, indexCharacter : int) -> Optional[AnimatedImageObject]:
        if indexCharacter == 86 or indexCharacter == 87:
            return getAnimFromPath((PATH_BODY_ROOT_LANG_DEP % indexCharacter).replace("?", self.__state.language.value), enableSubAnimation=True)
        return getAnimFromPath(PATH_BODY_ROOT % indexCharacter, enableSubAnimation=True)

    def __generateAnimCheckboxes(self):

        def isNameGood(name) -> bool:
            if len(name) > 0:
                if name[0] != "*" and name != "Create an Animation":
                    return True
            return False

        self.choiceCharacterAnimStart.Clear()
            
        # TODO - access to animation details, dunno if this is accurate tbh
        # TODO - Awful, requires subanimation (not guarenteed!!!)
        selection = self.listAllCharacters.GetSelection()
        if 0 <= selection < len(self.__eventCharacters) and self.__eventData != None:
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
        if self.__eventData.charactersShown[self.listAllCharacters.GetSelection()]:
            slot = self.__eventData.charactersPosition[self.listAllCharacters.GetSelection()]
            if slot in FrameScriptEditor.SLOT_OFFSET:
                offset = FrameScriptEditor.SLOT_OFFSET[slot]
            else:
                # TODO - Test invalid slot, iirc it's the middle
                slot = 1
                offset = FrameScriptEditor.SLOT_OFFSET[1]

            variableOffset = getImageOffset(self.__activeCharacterImage)

            if slot in FrameScriptEditor.SLOT_LEFT:
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
        
        self.bitmapRenderCharacterPreview.SetBitmap(BitmapFromBufferRGBA(RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1], tostring(self.__backgroundWidebrim, "RGBA")))

    def __generateScriptingTree(self, script : GdScript):
        self.treeScript.DeleteAllItems()
        rootId = self.treeScript.GetRootItem()
        if not(rootId.IsOk()):
            rootId = self.treeScript.AddRoot("Root")
        for indexInstruction in range(script.getInstructionCount()):
            instruction = script.getInstruction(indexInstruction)
            commandRoot = self.treeScript.AppendItem(parent=rootId, text=getInstructionName(instruction.opcode), data=instruction.opcode)
            for operand in instruction.operands:
                self.treeScript.AppendItem(parent=commandRoot, text=getOperandName(instruction.opcode, operand), data=operand)

    def __updateCharacterSelection(self):
        selection = self.listAllCharacters.GetSelection()
        if selection == NOT_FOUND:
            return

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
    
    def choiceCharacterSlotOnChoice(self, event):
        selection = self.listAllCharacters.GetSelection()
        if 0 <= selection < len(self.__eventCharacters):
            slot = MAP_POS_TO_INGAME[self.choiceCharacterSlot.GetSelection()]
            self.__eventData.charactersPosition[selection] = slot
            self.__generateCharacterPreview()

        return super().choiceCharacterSlotOnChoice(event)

    def choiceCharacterAnimStartOnChoice(self, event):
        selection = self.choiceCharacterAnimStart.GetSelection()
        indexAnim = self.__mapActiveCharacterIndexToRealIndex[selection]
        selection = self.listAllCharacters.GetSelection()
        self.__eventData.charactersInitialAnimationIndex[selection] = indexAnim
        if self.__activeCharacterImage != None:
            # TODO - Will probably fail with initial anim
            self.__activeCharacterImage.setAnimationFromIndex(indexAnim)
            self.__generateCharacterPreview()

        return super().choiceCharacterAnimStartOnChoice(event)

    def checkDisableCharacterVisibilityOnCheckBox(self, event):
        selection = self.listAllCharacters.GetSelection()
        self.__eventData.charactersShown[selection] = not(self.checkDisableCharacterVisibility.GetValue())
        if self.__activeCharacterImage != None:
            self.__generateCharacterPreview()
        return super().checkDisableCharacterVisibilityOnCheckBox(event)

    def prepareWidebrimState(self):
        self.__state.setEventId(self.__idEvent)
        return GAMEMODES.DramaEvent
            
    def listAllCharactersOnListBoxDClick(self, event):
        self.__updateCharacterSelection()
        return super().listAllCharactersOnListBoxDClick(event)
    
    def checkDisableBadAnimsOnCheckBox(self, event):
        self.__generateAnimCheckboxes()
        return super().checkDisableBadAnimsOnCheckBox(event)
    
    def paneCharactersOnCollapsiblePaneChanged(self, event):
        self.paneCharacters.GetParent().Layout()
        return super().paneCharactersOnCollapsiblePaneChanged(event)