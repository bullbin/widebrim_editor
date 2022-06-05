from typing import List, Optional
from editor.gui.command_annotator.bank import InstructionDescription
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.madhatter.hat_io.asset_script import GdScript

class VirtualInstructionDefinition(InstructionDescription):
    pass

class VirtualInstructionGenerator():
    def __init__(self, filesystem : WriteableFilesystemCompatibilityLayer, packTalkScript : LaytonPack, idEvent : Optional[int]):
        self.packTalkScript = packTalkScript
        self.filesystem = filesystem
        self.idMainEvent = idEvent // 1000
        self.idSubEvent = idEvent % 1000

    def replaceInScript(self, script : GdScript):
        pass