from typing import Optional, Tuple
from editor.e_script.get_input_popup import getDialogForType
from editor.gui.command_annotator.default_value import getDefaultValue
from widebrim.engine.state.manager import Layton2GameState

from widebrim.madhatter.common import logSevere, logVerbose
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2

from ..nopush_editor import editorScript
from .opcode_translation import MAP_OPCODE_TO_FRIENDLY, getInstructionName

from widebrim.madhatter.hat_io.asset_script import GdScript, Instruction, Operand
from editor.gui.command_annotator.bank import Context, OperandCompatibility, OperandType, ScriptVerificationBank
from wx import TreeEvent, TreeItemId, SingleChoiceDialog, ID_OK, Window

# TODO - Bugfix, scrollbar not resizing on minimize

# TODO - Eventually build into vfs by modifying script editing to generate build commands instead of modifying file
# TODO - Prevent interaction with widebrim while event is being edited - can lead to major desync!

# TODO - Add method for custom instruction (operand and name...)

# TODO - Generate script from tree - this is really convoluted for no reason

class FrameScriptEditor(editorScript):

    LOG_MODULE_NAME = "ScriptEdit"

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

    def __init__(self, parent : Window, state : Layton2GameState, bankInstructions : ScriptVerificationBank, script : Optional[GdScript], context : Context = Context.Base):
        super().__init__(parent)
        self._bankInstructions : ScriptVerificationBank = bankInstructions
        self.__context      : Context = None

        self._state         : Layton2GameState = state
        self._loaded        : bool = False

        if script != None:
            self._eventScript : GdScript = script
        else:
            self._eventScript : GdScript = GdScript()

        self.__setContext(context)
    
    def ensureLoaded(self):
        if not(self._loaded):
            self.Freeze()
            self._refresh()
            self._loaded = True
            self.Thaw()

    def syncChanges(self):
        logSevere("No method provided to sync changes!", name=FrameScriptEditor.LOG_MODULE_NAME)

    def _refresh(self):
        self.__generateScriptingTree(self._eventScript)
    
    def __setContext(self, context : Context):
        self.__context = context
        self.textScriptingContext.SetLabel(str(context)[8:])
        if context != Context.DramaEvent:
            self.staticTextBranchingWarning.Destroy()
            self.panelStateControls.Destroy()
            self.paneCharacters.Destroy()
            self.Layout()

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
            self._eventScript.removeInstruction(instructionDetails[0])
            if isInstruction:
                self.treeScript.Delete(itemId)
            else:
                self.treeScript.Delete(self.treeScript.GetItemParent(itemId))
        return super().buttonDeleteInstructionOnButtonClick(event)

    def getNameForOperandType(self, operandType : OperandType, operand : Operand) -> Optional[str]:
        """Called unless getOperandTreeValue was overridden. Should return the tree label given for an operand of a particular type.

        Args:
            operandType (OperandType): Operand type for filtering.
            operand (Operand): Operand storing type and value.

        Returns:
            Optional[str]: String representing operand, or None if not available.
        """
        return str(operandType) + ": " + str(operand.value)

    def getOperandTreeValue(self, instruction : Instruction, idxOperand : int) -> str:
        definition = self._bankInstructions.getInstructionByOpcode(int.from_bytes(instruction.opcode, byteorder='little'))
        operand = instruction.operands[idxOperand]
        if definition != None:
            if (operandDef := definition.getOperand(idxOperand)) != None:
                if (name := self.getNameForOperandType(operandDef.operandType, operand)) != None:
                    return name 
                return str(operandDef.operandType) + ": " + str(operand.value)
        try:
            return str(FrameScriptEditor.CONVERSION_OPERAND_TO_COMPATIBILITY[operand.type]) + ": " + str(operand.value)
        except KeyError:
            if operand.type == 0xc:
                return "Breakpoint - end execution after this instruction"
            return "Unknown: " + str(operand.value)

    def __getPopupForOperandType(self, instruction : Instruction, idxOperand : int, treeItem : TreeItemId) -> None:

        operand = instruction.operands[idxOperand]
        if operand.type not in FrameScriptEditor.CONVERSION_OPERAND_TO_COMPATIBILITY:
            return None
        
        baseType    = FrameScriptEditor.CONVERSION_OPERAND_TO_COMPATIBILITY[operand.type]
        baseValue   = operand.value

        definition = self._bankInstructions.getInstructionByOpcode(int.from_bytes(instruction.opcode, byteorder='little'))
        if definition != None:
            if (operandDef := definition.getOperand(idxOperand)) != None:
                if operandDef.isBaseTypeCompatible(baseType):
                    logVerbose(baseType, "->", operandDef.operandType, name=FrameScriptEditor.LOG_MODULE_NAME)
                    baseType = operandDef.operandType
                else:
                    logSevere("Incompatible", baseType, "->", operandDef.operandType, name=FrameScriptEditor.LOG_MODULE_NAME)
            else:
                logSevere("Missing definition for operand", name=FrameScriptEditor.LOG_MODULE_NAME)
        else:
            logSevere("Missing instruction definition", name=FrameScriptEditor.LOG_MODULE_NAME)
        
        dialog = getDialogForType(self, self._state, self._state.getFileAccessor(), baseType)
        if dialog != None:
            newVal = dialog.do(str(baseValue))
            if newVal != None:
                operand.value = newVal
                self.treeScript.SetItemText(treeItem, self.getOperandTreeValue(instruction, idxOperand))
                
    def treeScriptOnTreeItemActivated(self, event : TreeEvent):
        isInstruction, instructionDetails = self.__decodeTreeItem(event.GetItem())
        if isInstruction:
            return super().treeScriptOnTreeItemActivated(event)
        else:
            self.__getPopupForOperandType(self._eventScript.getInstruction(instructionDetails[0]), instructionDetails[1], event.GetItem())
            event.Skip()

    def __generateScriptingTree(self, script : GdScript):
        self.treeScript.DeleteAllItems()
        rootId = self.treeScript.GetRootItem()
        if not(rootId.IsOk()):
            rootId = self.treeScript.AddRoot("Root")
        for indexInstruction in range(script.getInstructionCount()):
            instruction = script.getInstruction(indexInstruction)
            commandRoot = self.treeScript.AppendItem(parent=rootId, text=getInstructionName(instruction.opcode), data=instruction)
            for indexOperand in range(len(instruction.operands)):
                self.treeScript.AppendItem(parent=commandRoot, text=self.getOperandTreeValue(instruction, indexOperand), data=instruction.operands[indexOperand])

    def __getNewInstruction(self) -> Optional[Instruction]:

        def doDialog() -> Optional[int]:
            filteredOpcodes = []
            strings = []
            for opcode in self._bankInstructions.getAllInstructionOpcodes():
                description = self._bankInstructions.getInstructionByOpcode(opcode)
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
        description = self._bankInstructions.getInstructionByOpcode(newOpcode)
        for idxOperand in range(description.getCountOperands()):
            descOperand = description.getOperand(idxOperand)
            baseType = OperandCompatibility[descOperand.operandType.name]
            if baseType not in FrameScriptEditor.CONVERSION_COMPATIBILITY_TO_OPERAND:
                logSevere("No base type for " + descOperand.operandType.name, name=FrameScriptEditor.LOG_MODULE_NAME)
                return None
            
            defaultValue = getDefaultValue(descOperand.operandType)
            if defaultValue == None:
                logSevere("No default value for " + descOperand.operandType.name, name=FrameScriptEditor.LOG_MODULE_NAME)
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
            self._eventScript.addInstruction(command)
        else:
            idxInstruction, idxOperand = instructionDetails
            operandRoot = self.treeScript.InsertItem(self.treeScript.GetRootItem(),
                                                     self.__getTreeItemForInstruction(idxInstruction),
                                                     getInstructionName(command.opcode),
                                                     data=command.opcode)
            # TODO - why does this add before...?
            self._eventScript.insertInstruction(idxInstruction + 1, command)

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
            self._eventScript.addInstruction(command)
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
            self._eventScript.insertInstruction(idxInstruction, command)

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
            instruction = self._eventScript.getInstruction(idxInstruction)
            treeItem = self.__getTreeItemForInstruction(idxInstruction)

            newItem = self.__insertAbove(instruction, self.__getTreeItemForInstruction(idxInstruction - 1))
            self._eventScript.removeInstruction(idxInstruction + 1)
            
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
        if idxInstruction < self._eventScript.getInstructionCount() - 1:
            # Can move down
            instruction = self._eventScript.getInstruction(idxInstruction)
            treeItem = self.__getTreeItemForInstruction(idxInstruction)

            newItem = self.__insertBelow(instruction, self.__getTreeItemForInstruction(idxInstruction + 1))
            self._eventScript.removeInstruction(idxInstruction)
            
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
        treeRef = self.__insertBelow(self._eventScript.getInstruction(idxInstruction), self.__getTreeItemForInstruction(idxInstruction))
        if isExpanded:
            self.treeScript.Expand(treeRef)
        return super().buttonCopyOnButtonClick(event)