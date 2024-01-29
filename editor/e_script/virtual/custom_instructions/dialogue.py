from typing import Any, List, Optional, Union
from editor.e_script.virtual.custom import VirtualInstructionGenerator
from widebrim.madhatter.common import log, logSevere
from .const import OFFSET_VIRTUAL_INSTRUCTION
from editor.bank.command_annotator.bank import Context, InstructionDescription, OperandDescription, OperandType
from widebrim.engine.const import PATH_PACK_TALK
from filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.madhatter.hat_io.asset_script import GdScript, Instruction, Operand
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2
from re import match
# TODO - How best to structure this?

class DialogueInstructionDescription(InstructionDescription):

    TARGET_OPERAND = OPCODES_LT2.TextWindow.value + OFFSET_VIRTUAL_INSTRUCTION

    def __init__(self):
        self.opcode         = DialogueInstructionDescription.TARGET_OPERAND
        self.name           = "Dialogue"
        self.description    = "Virtual Instruction.\n\nBrings up the text box for dialogue in events. Script execution is paused while dialogue is playing back."
        self.contextValid   = [Context.DramaEvent]
        self.isUsed         = True
        self.permittedOperandTypes = [OperandDescription(OperandType.InternalCharacterId, "Character index from event data, starting at 0 and reading top to bottom."),
                                      OperandDescription(OperandType.StringTalkScript, "Spoken dialogue sequence."),
                                      OperandDescription(OperandType.StringCharAnim, "Animation called on the character when dialogue starts. 'NONE' will leave the character alone."),
                                      OperandDescription(OperandType.StringCharAnim, "Animation called on the character when dialogue ends. 'NONE' will leave the character alone."),
                                      OperandDescription(OperandType.IndexVoiceId, "ID for the sound of voiceline to play when this dialogue starts."),
                                      OperandDescription(OperandType.Pitch, "Unvoiced speech sound effect pitch. 1 is lowest and default.")]

class InstructionTalkScriptContainer(Instruction):
    def __init__(self, idxTalkscript : Optional[int] = None):
        super().__init__()
        self.idxTalkscript : Optional[int] = idxTalkscript

class DialogueInstructionGenerator(VirtualInstructionGenerator):

    LOG_MODULE_NAME = "ViDiag"

    # TODO - Fix talkscript type
    def __init__(self, filesystem : WriteableFilesystemCompatibilityLayer, pathTalkScript : LaytonPack, idEvent : Optional[int]):
        super().__init__(filesystem, pathTalkScript, idEvent)

    def _convertToOriginalInternal(self, script: GdScript):

        class DialogContainer():
            def __init__(self, instruction : Union[InstructionTalkScriptContainer, Instruction], idxInstruction : int) -> None:

                def getOperandValueIfMatches(idxOperand : int, defaultValue : Any) -> Any:
                    if 0 <= idxOperand < len(instruction.operands):
                        operand = instruction.operands[idxOperand]
                        if type(operand.value) == type(defaultValue):
                            return operand.value
                        logSevere("Missing part of operand!", name=DialogueInstructionGenerator.LOG_MODULE_NAME)
                    return defaultValue

                self.idxInstruction = idxInstruction

                self.idxChar    : int = getOperandValueIfMatches(0, 0)
                self.textDialog : str = getOperandValueIfMatches(1, "")
                self.animStart  : str = getOperandValueIfMatches(2, "NONE")
                self.animEnd    : str = getOperandValueIfMatches(3, "NONE")
                self.idVoice    : Optional[int] = getOperandValueIfMatches(4, -1)
                self.pitch      : int = getOperandValueIfMatches(5, 1)
                self.preferId   : Optional[int] = None

                if self.idVoice == -1:
                    self.idVoice = None
                if type(instruction) == InstructionTalkScriptContainer:
                    self.preferId = instruction.idxTalkscript
        
        class DialogNumGen():

            GAP_VALUE = 100
            INFILL_BETWEEN = True

            def __init__(self, listUnique : List[int]):
                self.__listUnique = listUnique
                if DialogNumGen.INFILL_BETWEEN or len(self.__listUnique) == 0:
                    self.__lastValue = 100
                else:
                    self.__listUnique.sort()
                    self.__lastValue = ((self.__listUnique[-1] // 100) + 1) * 100

            def getNextValue(self) -> int:
                while self.__lastValue in self.__listUnique:
                    self.__lastValue += DialogNumGen.GAP_VALUE
                self.__listUnique.append(self.__lastValue)
                return self.__lastValue

        pack = self.filesystem.getPack(self.pathTalkScript)

        def addTalkScript(dialog : DialogContainer):
            outScript = GdScript()
            outScript.name = PATH_PACK_TALK % (self.idMainEvent, self.idSubEvent, dialog.preferId)
            instruction = Instruction()
            instruction.opcode = b'\xff\xff'
            instruction.operands.append(Operand(1, dialog.idxChar))
            instruction.operands.append(Operand(3, dialog.animStart))
            instruction.operands.append(Operand(3, dialog.animEnd))
            instruction.operands.append(Operand(1, dialog.pitch))
            instruction.operands.append(Operand(3, dialog.textDialog))
            outScript.addInstruction(instruction)
            outScript.save(isTalkscript=True)
            pack.files.append(outScript)

        # Remove all talkscripts for this event (including unused)
        matchFilter = "t%i_%.3i_([0-9]+).gds" % (self.idMainEvent, self.idSubEvent)
        for file in reversed(pack.files):
            if match(matchFilter, file.name) != None:
                pack.files.remove(file)

        # Build list of commands to convert - this is sorted by index command, so reverse when removing
        preprocessCommands : List[DialogContainer] = []
        preprocessIndicies : List[int] = []
        for idxInstruction in range(script.getInstructionCount()):
            instruction = script.getInstruction(idxInstruction)
            if int.from_bytes(instruction.opcode, byteorder='little') == DialogueInstructionDescription.TARGET_OPERAND:
                preprocessCommands.append(DialogContainer(instruction, idxInstruction))

                # Remove non-unique preferred IDs
                if preprocessCommands[-1].preferId != None:
                    if preprocessCommands[-1].preferId in preprocessIndicies:
                        log("Remapped dialog due to conflict!", name=DialogueInstructionGenerator.LOG_MODULE_NAME)
                        preprocessCommands[-1].preferId = None
                    else:
                        preprocessIndicies.append(preprocessCommands[-1].preferId)
        
        # Forward pass - want the indices to be in order where possible
        numGen = DialogNumGen(preprocessIndicies)
        for command in preprocessCommands:
            if command.preferId == None:
                command.preferId = numGen.getNextValue()

        # Backward pass - start modifying original script
        for command in reversed(preprocessCommands):
            script.removeInstruction(command.idxInstruction)
            
            genIns = Instruction()
            genIns.opcode = OPCODES_LT2.TextWindow.value.to_bytes(2, byteorder='little')
            genIns.operands.append(Operand(1, command.preferId))
            script.insertInstruction(command.idxInstruction, genIns)

            if command.idVoice != None:
                genIns = Instruction()
                genIns.opcode = OPCODES_LT2.SetVoiceID.value.to_bytes(2, byteorder='little')
                genIns.operands.append(Operand(1, command.idVoice))
                script.insertInstruction(command.idxInstruction, genIns)
            
            addTalkScript(command)
        
        # Restoration complete, now we save the talkscript pack
        # TODO - Header?
        pack.save()
        pack.compress()
        if not(self.filesystem.writeableFs.replaceFile(self.pathTalkScript, pack.data)):
            logSevere("Failed to overwrite TalkScript pack!", name=DialogueInstructionGenerator.LOG_MODULE_NAME)

        return super()._convertToOriginalInternal(script)

    def convertToVirtual(self, script: GdScript):

        def createDialogueInstruction(idxChar : int, animStart : str, animEnd : str, pitch : int, text : str, idVoice : int, idTalkScript : int) -> Instruction:
            output = InstructionTalkScriptContainer(idTalkScript)
            output.opcode = (DialogueInstructionDescription.TARGET_OPERAND).to_bytes(2, byteorder='little')
            output.operands.append(Operand(1, idxChar))
            output.operands.append(Operand(3, text))
            output.operands.append(Operand(3, animStart))
            output.operands.append(Operand(3, animEnd))
            output.operands.append(Operand(1, idVoice))
            output.operands.append(Operand(1, pitch))
            return output

        # TODO - Make internal
        packTalkScript = self.filesystem.getPack(self.pathTalkScript)

        idxPop = []
        nextVoiceLine = -1
        # TODO - Does match description would be a great method here...
        for idxInstruction in range(script.getInstructionCount()):
            instruction = script.getInstruction(idxInstruction)
            opcode = int.from_bytes(instruction.opcode, byteorder = 'little')

            if opcode == OPCODES_LT2.SetVoiceID.value:
                if len(instruction.operands) > 0 and type(instruction.operands[0].value) == int:
                    nextVoiceLine = instruction.operands[0].value
                    idxPop.append(idxInstruction)

            if opcode == OPCODES_LT2.TextWindow.value:
                useVoiceLine = nextVoiceLine
                nextVoiceLine = -1
                if len(instruction.operands) > 0 and type(instruction.operands[0].value) == int:
                    talkScriptPath = PATH_PACK_TALK % (self.idMainEvent, self.idSubEvent, instruction.operands[0].value)
                    if (data := packTalkScript.getFile(talkScriptPath)) != None:
                        talkScript = GdScript()
                        talkScript.load(data, isTalkscript=True)
                        if talkScript.getInstructionCount() < 1:
                            continue
                        talkScript = talkScript.getInstruction(0)
                        if len(talkScript.operands) < 5:
                            continue
                        talkScript = talkScript.operands
                        if type(talkScript[0].value) == int and type(talkScript[1].value) == str and type(talkScript[2].value) == str and type(talkScript[3].value) == int and type(talkScript[4].value) == str:
                            repDiag = createDialogueInstruction(talkScript[0].value, talkScript[1].value, talkScript[2].value, talkScript[3].value, talkScript[4].value, useVoiceLine, instruction.operands[0].value)
                            script.insertInstruction(idxInstruction, repDiag)
                            script.removeInstruction(idxInstruction + 1)
                    else:
                        continue
        
        idxPop.sort(reverse=True)
        for idxToPop in idxPop:
            script.removeInstruction(idxToPop)