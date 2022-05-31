from typing import List, Optional
from editor.gui.command_annotator.bank import InstructionDescription
from widebrim.filesystem.compatibility import FusedFileInterface
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.madhatter.hat_io.asset_script import GdScript

class VirtualInstructionDefinition(InstructionDescription):
    pass

class VirtualInstructionGenerator():
    def __init__(self, fusedFi : FusedFileInterface, packTalkScript : LaytonPack, idEvent : Optional[int]):
        self.packTalkScript = packTalkScript
        self.fusedFi = fusedFi
        self.idMainEvent = idEvent // 1000
        self.idSubEvent = idEvent % 1000

    def replaceInScript(self, script : GdScript):
        pass