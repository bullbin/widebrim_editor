from typing import List, Optional, Tuple
from editor.e_script.get_input_popup import getDialogForType
from editor.gui.command_annotator.default_value import getDefaultValue
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from widebrim.engine.const import PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C, PATH_PACK_EVENT_DAT, PATH_PACK_EVENT_SCR, RESOLUTION_NINTENDO_DS
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine.state.manager import Layton2GameState
from widebrim.engine_ext.utils import getBottomScreenAnimFromPath
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.gamemodes.dramaevent.const import PATH_BODY_ROOT, PATH_BODY_ROOT_LANG_DEP
from widebrim.madhatter.common import logSevere
from widebrim.madhatter.hat_io.asset_dat.event import EventData
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2

from ..nopush_editor import editorScript
from .opcode_translation import MAP_OPCODE_TO_FRIENDLY, getInstructionName
from wx import ID_ANY, DefaultPosition, Size, TAB_TRAVERSAL, EmptyString, NOT_FOUND

from widebrim.madhatter.hat_io.asset_script import GdScript, Instruction, Operand
from editor.gui.command_annotator.bank import Context, OperandCompatibility, OperandType, ScriptVerificationBank
from pygame import Surface
from pygame.transform import flip
from pygame.image import tostring
from wx import Bitmap, TreeEvent, TreeItemId, SingleChoiceDialog, ID_OK

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

# TODO - Bugfix, scrollbar not resizing on minimize

def getOperandName(opcode : bytes, operand : Operand) -> str:
    return str(operand.value)

# TODO - Eventually build into vfs by modifying script editing to generate build commands instead of modifying file
# TODO - Prevent interaction with widebrim while event is being edited - can lead to major desync!

class FrameScriptEditor(editorScript):

    SLOT_OFFSET = {0:0x30,     1:0x80,
                   2:0xd0,     3:0x20,
                   4:0x58,     5:0xa7,
                   6:0xe0}
    SLOT_LEFT  = [0,3,4]    # Left side characters need flipping

    CONVERSION_OPERAND_TO_COMPATIBILITY = {1:OperandType.StandardS32,
                                           2:OperandType.StandardF32,
                                           3:OperandType.StandardString,
                                           4:OperandType.StandardU16,
                                           6:OperandType.StandardS32,
                                           7:OperandType.StandardS32}
    CONVERSION_COMPATIBILITY_TO_OPERAND = {OperandType.StandardS32:1,
                                           OperandType.StandardF32:2,
                                           OperandType.StandardString:3,
                                           OperandType.StandardU16:4}

    def __init__(self, parent,  filesystem : WriteableFilesystemCompatibilityLayer, bankInstructions : ScriptVerificationBank, idEvent : int, state : Layton2GameState, id=ID_ANY, pos=DefaultPosition, size=Size(640, 640), style=TAB_TRAVERSAL, name=EmptyString):
        super().__init__(parent, id, pos, size, style, name)

        self.__bankInstructions = bankInstructions
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
        self.__selectedCharacterIndex : Optional[int] = None

        self._filesystem = filesystem
        self._loaded = False
    
    def substituteEventPath(self, inPath, inPathA, inPathB, inPathC):

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

    def getEventTalkPath(self):
        return self.substituteEventPath(PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C)

    def getEventScriptPath(self):
        return self.substituteEventPath(PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C)
    
    def ensureLoaded(self):
        if not(self._loaded):
            self.Freeze()
            self._refresh()
            if self.__eventScript != None:
                self.__generateScriptingTree(self.__eventScript)
            self._loaded = True
            self.Thaw()
    
    def __decodeTreeItem(self, itemId) -> Tuple[bool, Optional[Tuple[int, int]]]:

        def getItemIndex(itemId):
            indexItem = 0
            while True:
                itemId = self.treeScript.GetPrevSibling(itemId)
                if itemId.IsOk():
                    indexItem += 1
                else:
                    break
            return indexItem

        if not(itemId.IsOk()):
            return (False, None)

        isInstruction = False
        indexInstruction = 0
        indexOperand = 0
        if self.treeScript.GetItemParent(itemId) == self.treeScript.GetRootItem():
            isInstruction = True
            indexInstruction = getItemIndex(itemId)
        else:
            indexInstruction = getItemIndex(self.treeScript.GetItemParent(itemId))
            indexOperand = getItemIndex(itemId)
        return (isInstruction, (indexInstruction, indexOperand))

    def buttonDeleteInstructionOnButtonClick(self, event):
        # TODO - VFS insert and delete for less dangerous effects on sync.
        itemId = self.treeScript.GetSelection()
        isInstruction, instructionDetails = self.__decodeTreeItem(itemId)
        if instructionDetails != None:
            self.__eventScript.removeInstruction(instructionDetails[0])
            if isInstruction:
                self.treeScript.Delete(itemId)
            else:
                self.treeScript.Delete(self.treeScript.GetItemParent(itemId))
        return super().buttonDeleteInstructionOnButtonClick(event)

    def __getAbstractionLevel(self):
        return 1

    # TODO - Respect abstraction level
    def getOperandTreeValue(self, instruction : Instruction, idxOperand : int) -> str:
        definition = self.__bankInstructions.getInstructionByOpcode(int.from_bytes(instruction.opcode, byteorder='little'))
        operand = instruction.operands[idxOperand]
        if definition != None:
            if (operandDef := definition.getOperand(idxOperand)) != None:
                return str(operandDef.operandType) + ": " + str(operand.value)
        try:
            return str(FrameScriptEditor.CONVERSION_OPERAND_TO_COMPATIBILITY[operand.type]) + ": " + str(operand.value)
        except KeyError:
            if operand.type == 0xc:
                return "Breakpoint - end execution after this instruction"
            return "Unknown: " + str(operand.value)

    def getOperandDescription(self, instruction : Instruction, idxOperand):
        pass

    def __getPopupForOperandType(self, instruction : Instruction, idxOperand : int, treeItem : TreeItemId) -> None:

        operand = instruction.operands[idxOperand]
        if operand.type not in FrameScriptEditor.CONVERSION_OPERAND_TO_COMPATIBILITY:
            return None
        
        baseType    = FrameScriptEditor.CONVERSION_OPERAND_TO_COMPATIBILITY[operand.type]
        baseValue   = operand.value

        if self.__getAbstractionLevel() != 0:
            definition = self.__bankInstructions.getInstructionByOpcode(int.from_bytes(instruction.opcode, byteorder='little'))
            if definition != None:
                if (operandDef := definition.getOperand(idxOperand)) != None:
                    if operandDef.isBaseTypeCompatible(baseType):
                        print(baseType, "->", operandDef.operandType)
                        baseType = operandDef.operandType
                    else:
                        print("Incompatible", baseType, "->", operandDef.operandType)
                else:
                    print("Missing definition for operand")
            else:
                print("Missing instruction definition")
        
        dialog = getDialogForType(self, self.__state, self.__state.getFileAccessor(), baseType)
        if dialog != None:
            newVal = dialog.do(str(baseValue))
            if newVal != None:
                operand.value = newVal
                self.treeScript.SetItemText(treeItem, self.getOperandTreeValue(instruction, idxOperand))
                
    def treeScriptOnTreeItemActivated(self, event : TreeEvent):
        isInstruction, instructionDetails = self.__decodeTreeItem(event.GetItem())
        if isInstruction:
            print("Instruction", instructionDetails[0])
            return super().treeScriptOnTreeItemActivated(event)
        else:
            print("Instruction", instructionDetails[0], "Operand", instructionDetails[1])
            self.__getPopupForOperandType(self.__eventScript.getInstruction(instructionDetails[0]), instructionDetails[1], event.GetItem())
            event.Skip()

    def syncChanges(self):
        # TODO - Compile with file builders
        print("attempt sync operation...")
        packEvent = self._filesystem.getPack(self.getEventScriptPath())

        # TODO - Virtual scripting
        filenameScript = PATH_PACK_EVENT_SCR % (self.__idMain, self.__idSub)
        filenameData = PATH_PACK_EVENT_DAT % (self.__idMain, self.__idSub)
        self.__eventScript.save()
        self.__eventData.save()

        # TODO - Madhatter archive support rewrite, this is terrible syntax. Could break very, very easily
        for file in packEvent.files:
            if file.name == filenameScript:
                file.data = self.__eventScript.data
            elif file.name == filenameData:
                file.data = self.__eventData.data

        packEvent.save()
        packEvent.compress()
        self._filesystem.writeableFs.replaceFile(self.getEventScriptPath(), packEvent.data)
        print("synced?")

    def _refresh(self):
        entry = self.__state.getEventInfoEntry(self.__idEvent)
        self.__eventData = None
        self.__eventScript = None
        if entry == None:
            return
        
        if self.__context == Context.DramaEvent:
            
            if (data := self._filesystem.getPackedData(self.getEventScriptPath(), PATH_PACK_EVENT_DAT % (self.__idMain, self.__idSub))) != None:
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
                    self.__eventCharacters[-1].setPos((0,0))
                self.listAllCharacters.AppendItems(newItems)
                if len(eventData.characters) > 0:
                    self.listAllCharacters.SetSelection(0)
                    self.__updateCharacterSelection()
            
            if (data := self._filesystem.getPackedData(self.getEventScriptPath(), PATH_PACK_EVENT_SCR % (self.__idMain, self.__idSub))) != None:
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
            return getBottomScreenAnimFromPath(self.__state, (PATH_BODY_ROOT_LANG_DEP % indexCharacter), enableSubAnimation=True)
        return getBottomScreenAnimFromPath(self.__state, PATH_BODY_ROOT % indexCharacter, enableSubAnimation=True)

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
        
        self.bitmapRenderCharacterPreview.SetBitmap(Bitmap.FromBufferRGBA(RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1], tostring(self.__backgroundWidebrim, "RGBA")))

    def __generateScriptingTree(self, script : GdScript):
        self.treeScript.DeleteAllItems()
        rootId = self.treeScript.GetRootItem()
        if not(rootId.IsOk()):
            rootId = self.treeScript.AddRoot("Root")
        for indexInstruction in range(script.getInstructionCount()):
            instruction = script.getInstruction(indexInstruction)
            commandRoot = self.treeScript.AppendItem(parent=rootId, text=getInstructionName(instruction.opcode), data=instruction.opcode)
            for indexOperand in range(len(instruction.operands)):
                self.treeScript.AppendItem(parent=commandRoot, text=self.getOperandTreeValue(instruction, indexOperand), data=instruction.operands[indexOperand])

    def __getNewInstruction(self) -> Optional[Instruction]:

        def doDialog() -> Optional[int]:
            filteredOpcodes = []
            strings = []
            for opcode in self.__bankInstructions.getAllInstructionOpcodes():
                description = self.__bankInstructions.getInstructionByOpcode(opcode)
                if self.__context in description.contextValid or self.__context == None:
                    if Context.Stubbed not in description.contextValid:
                        try:
                            friendlyString = MAP_OPCODE_TO_FRIENDLY[OPCODES_LT2(opcode)]
                            if friendlyString == None:
                                friendlyString = "(No helper) " + OPCODES_LT2(opcode).name
                            strings.append(friendlyString)
                        except:
                            strings.append("(No rename) Instruction " + str(opcode))
                        filteredOpcodes.append(opcode)

            dlg = SingleChoiceDialog(self, "Select an instruction to add...", "Add New Instruction", strings)
            confirm = dlg.ShowModal()
            if confirm == ID_OK:
                return filteredOpcodes[dlg.GetSelection()]
            return None
        
        newOpcode = doDialog()
        if newOpcode == None:
            return None
        
        output = Instruction()
        output.opcode = newOpcode.to_bytes(2, byteorder = 'little')
        description = self.__bankInstructions.getInstructionByOpcode(newOpcode)
        for idxOperand in range(description.getCountOperands()):
            descOperand = description.getOperand(idxOperand)
            baseType = OperandCompatibility[descOperand.operandType.name]
            if baseType not in FrameScriptEditor.CONVERSION_COMPATIBILITY_TO_OPERAND:
                logSevere("[GDSEDT - D ] No base type for " + descOperand.operandType.name)
                return None
            
            defaultValue = getDefaultValue(descOperand.operandType)
            if defaultValue == None:
                logSevere("[GDSEDT - D ] No default value for " + descOperand.operandType.name)
                return None

            tempOperand = Operand(FrameScriptEditor.CONVERSION_COMPATIBILITY_TO_OPERAND[baseType], defaultValue)
            output.operands.append(tempOperand)
        return output

    def __getTreeItemForInstruction(self, idxInstruction):
        item, cookie = self.treeScript.GetFirstChild(self.treeScript.GetRootItem())
        for _idxMove in range(idxInstruction):
            item, cookie = self.treeScript.GetNextChild(self.treeScript.GetRootItem(), cookie)
        return item

    def __insertBelow(self, command : Instruction, reference : TreeItemId) -> TreeItemId:
        isInstruction, instructionDetails = self.__decodeTreeItem(reference)
        if instructionDetails == None:
            # Tree item was not valid, so we are the first item
            operandRoot = self.treeScript.AppendItem(self.treeScript.GetRootItem(),
                                                     getInstructionName(command.opcode),
                                                     data=command.opcode)
            self.__eventScript.addInstruction(command)
        else:
            idxInstruction, idxOperand = instructionDetails
            operandRoot = self.treeScript.InsertItem(self.treeScript.GetRootItem(),
                                                     self.__getTreeItemForInstruction(idxInstruction),
                                                     getInstructionName(command.opcode),
                                                     data=command.opcode)
            # TODO - why does this add before...?
            self.__eventScript.insertInstruction(idxInstruction + 1, command)

        for indexOperand, operand in enumerate(command.operands):
            self.treeScript.AppendItem(parent=operandRoot, text=self.getOperandTreeValue(command, indexOperand), data=operand)
        return operandRoot

    def __insertAbove(self, command : Instruction, reference : TreeItemId) -> TreeItemId:
        isInstruction, instructionDetails = self.__decodeTreeItem(reference)
        if instructionDetails == None:
            # Tree item was not valid, so we are the first item
            operandRoot = self.treeScript.AppendItem(self.treeScript.GetRootItem(),
                                                     getInstructionName(command.opcode),
                                                     data=command.opcode)
            self.__eventScript.addInstruction(command)
        else:
            idxInstruction, idxOperand = instructionDetails
            if idxInstruction == 0:
                # If this is the topmost instruction, use prepend instead to add at top
                operandRoot = self.treeScript.PrependItem(self.treeScript.GetRootItem(),
                                                          getInstructionName(command.opcode),
                                                          data=command.opcode)
            else:
                # Else we know there is an item above it which we can add below
                operandRoot = self.treeScript.InsertItem(self.treeScript.GetRootItem(),
                                                         self.__getTreeItemForInstruction(idxInstruction - 1),
                                                         getInstructionName(command.opcode),
                                                         data=command.opcode)
            # TODO - Insert below...
            self.__eventScript.insertInstruction(idxInstruction, command)

        for indexOperand, operand in enumerate(command.operands):
            self.treeScript.AppendItem(parent=operandRoot, text=self.getOperandTreeValue(command, indexOperand), data=operand)
        return operandRoot

    def buttonInsertBelowOnButtonClick(self, event):
        # TODO - Dialogue has bad operand count!
        # TODO - Make use of focused consistent, we want focused, not selected

        command = self.__getNewInstruction()
        if command == None:
            return super().buttonInsertBelowOnButtonClick(event)

        self.__insertBelow(command, self.treeScript.GetFocusedItem())

        # TODO - Hook to script generator for file building
        # TODO - Write a subclass that manages this (redirects insert to custom command)
        return super().buttonInsertBelowOnButtonClick(event)

    def buttonInsertAboveOnButtonClick(self, event):
        # TODO - see above
        isInstruction, instructionDetails = self.__decodeTreeItem(self.treeScript.GetFocusedItem())
        command = self.__getNewInstruction()
        if command == None:
            return super().buttonInsertAboveOnButtonClick(event)

        self.__insertAbove(command, self.treeScript.GetFocusedItem())
        return super().buttonInsertAboveOnButtonClick(event)

    def buttonMoveUpOnButtonClick(self, event):
        isInstruction, instructionDetails = self.__decodeTreeItem(self.treeScript.GetFocusedItem())
        if instructionDetails == None:
            return super().buttonMoveUpOnButtonClick(event)
        
        idxInstruction, idxOperand = instructionDetails
        if idxInstruction > 0:
            # Can move up
            instruction = self.__eventScript.getInstruction(idxInstruction)
            treeItem = self.__getTreeItemForInstruction(idxInstruction)

            newItem = self.__insertAbove(instruction, self.__getTreeItemForInstruction(idxInstruction - 1))
            self.__eventScript.removeInstruction(idxInstruction + 1)
            
            isExpanded = self.treeScript.IsExpanded(treeItem)
            
            self.treeScript.DeleteChildren(treeItem)
            self.treeScript.Delete(treeItem)

            if isExpanded:
                self.treeScript.Expand(newItem)

            self.treeScript.SetFocusedItem(newItem)
        return super().buttonMoveUpOnButtonClick(event)

    def buttonMoveDownOnButtonClick(self, event):
        isInstruction, instructionDetails = self.__decodeTreeItem(self.treeScript.GetFocusedItem())
        if instructionDetails == None:
            return super().buttonMoveDownOnButtonClick(event)
        
        idxInstruction, idxOperand = instructionDetails
        if idxInstruction < self.__eventScript.getInstructionCount() - 1:
            # Can move down
            instruction = self.__eventScript.getInstruction(idxInstruction)
            treeItem = self.__getTreeItemForInstruction(idxInstruction)

            newItem = self.__insertBelow(instruction, self.__getTreeItemForInstruction(idxInstruction + 1))
            self.__eventScript.removeInstruction(idxInstruction)
            
            isExpanded = self.treeScript.IsExpanded(treeItem)
            
            self.treeScript.DeleteChildren(treeItem)
            self.treeScript.Delete(treeItem)

            if isExpanded:
                self.treeScript.Expand(newItem)

            self.treeScript.SetFocusedItem(newItem)
        return super().buttonMoveDownOnButtonClick(event)

    def buttonCopyOnButtonClick(self, event):
        isInstruction, instructionDetails = self.__decodeTreeItem(self.treeScript.GetFocusedItem())
        if instructionDetails == None:
            return super().buttonCopyOnButtonClick(event)
        idxInstruction, _idxOperand = instructionDetails
        treeRef = self.__getTreeItemForInstruction(idxInstruction)
        isExpanded = self.treeScript.IsExpanded(treeRef)
        treeRef = self.__insertBelow(self.__eventScript.getInstruction(idxInstruction), self.__getTreeItemForInstruction(idxInstruction))
        if isExpanded:
            self.treeScript.Expand(treeRef)
        return super().buttonCopyOnButtonClick(event)

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
    
    def btnCharMoveUpOnButtonClick(self, event):
        if self.__selectedCharacterIndex != None and self.__selectedCharacterIndex > 0:
            pass
        return super().btnCharMoveUpOnButtonClick(event)
    
    def btnCharMoveDownOnButtonClick(self, event):
        if self.__selectedCharacterIndex != None and self.__selectedCharacterIndex < len(self.__eventCharacters) - 1:
            pass
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

    def prepareWidebrimState(self):
        # Hopefully don't need to call sync here - hope that the state was loaded properly
        # Calling sync here causes changes to ROM under current heuristic which is no good
        # TODO - Maybe detect state before so we can sync anyway without changes
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