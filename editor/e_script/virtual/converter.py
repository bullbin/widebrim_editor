from typing import List
from editor.gui.command_annotator.bank import InstructionDescription
from widebrim.madhatter.hat_io.asset_script import Instruction

class VirtualInstructionDefinition(InstructionDescription):
    pass

class VirtualInstruction(InstructionDescription):
    def __init__(self):
        super().__init__(self)

    def generateScriptMarkers(self):
        pass

    def toInstructions(self) -> List[Instruction]:
        return []