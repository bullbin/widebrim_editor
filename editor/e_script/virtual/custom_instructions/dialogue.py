from typing import Optional
from editor.e_script.virtual.custom import VirtualInstructionGenerator
from editor.gui.command_annotator.bank import Context, InstructionDescription, OperandDescription, OperandType
from widebrim.engine.const import PATH_PACK_TALK
from widebrim.filesystem.compatibility import FusedFileInterface
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.madhatter.hat_io.asset_script import GdScript, Instruction, Operand
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2
# TODO - How best to structure this?

class DialogueInstructionDescription(InstructionDescription):
    def __init__(self):
        self.opcode         = OPCODES_LT2.TextWindow.value + 0x0100
        self.description    = "Virtual Instruction\nBrings up the text box for dialogue in events. Script execution is paused while dialogue is playing back."
        self.contextValid   = [Context.DramaEvent]
        self.isUsed         = True
        self.permittedOperandTypes = [OperandDescription(OperandType.IndexEventDataCharacter, "Character index from event data, starting at 0 and reading top to bottom."),
                                      OperandDescription(OperandType.StringTalkScript, "Spoken dialogue sequence."),
                                      OperandDescription(OperandType.StringCharAnim, "Animation called on the character when dialogue starts. 'NONE' will leave the character alone."),
                                      OperandDescription(OperandType.StringCharAnim, "Animation called on the character when dialogue ends. 'NONE' will leave the character alone."),
                                      OperandDescription(OperandType.IndexVoiceId, "ID for the sound of voiceline to play when this dialogue starts."),
                                      OperandDescription(OperandType.Integer8, "Unvoiced speech sound effect pitch. 1 is lowest and default.")]

class DialogueInstructionGenerator(VirtualInstructionGenerator):

    def __init__(self, fusedFi : FusedFileInterface, packTalkScript : LaytonPack, idEvent : Optional[int]):
        super().__init__(fusedFi, packTalkScript, idEvent)

    def replaceInScript(self, script: GdScript):

        def createDialogueInstruction(idxChar : int, animStart : str, animEnd : str, pitch : int, text : str, idVoice : int) -> Instruction:
            output = Instruction()
            output.opcode = (OPCODES_LT2.TextWindow.value + 0x0100).to_bytes(2, byteorder='little')
            output.operands.append(Operand(1, idxChar))
            output.operands.append(Operand(3, text))
            output.operands.append(Operand(3, animStart))
            output.operands.append(Operand(3, animEnd))
            output.operands.append(Operand(1, idVoice))
            output.operands.append(Operand(1, pitch))
            return output

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
                    if (data := self.packTalkScript.getFile(talkScriptPath)) != None:
                        talkScript = GdScript()
                        talkScript.load(data, isTalkscript=True)
                        if talkScript.getInstructionCount() < 1:
                            continue
                        talkScript = talkScript.getInstruction(0)
                        if len(talkScript.operands) < 5:
                            continue
                        talkScript = talkScript.operands
                        if type(talkScript[0].value) == int and type(talkScript[1].value) == str and type(talkScript[2].value) == str and type(talkScript[3].value) == int and type(talkScript[4].value) == str:
                            repDiag = createDialogueInstruction(talkScript[0].value, talkScript[1].value, talkScript[2].value, talkScript[3].value, talkScript[4].value, useVoiceLine)
                            script.insertInstruction(idxInstruction, repDiag)
                            script.removeInstruction(idxInstruction + 1)
                    else:
                        continue
        
        idxPop.sort(reverse=True)
        for idxToPop in idxPop:
            script.removeInstruction(idxToPop)