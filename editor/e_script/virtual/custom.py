from typing import List, Optional
from editor.bank.command_annotator.bank import InstructionDescription
from filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.madhatter.hat_io.asset_script import GdScript

class VirtualInstructionDefinition(InstructionDescription):
    pass

class VirtualInstructionGenerator():
    def __init__(self, filesystem : WriteableFilesystemCompatibilityLayer, packTalkScript : LaytonPack, idEvent : Optional[int]):
        self.pathTalkScript = packTalkScript
        self.filesystem = filesystem
        self.idMainEvent = idEvent // 1000
        self.idSubEvent = idEvent % 1000

    def _convertToOriginalInternal(self, script : GdScript):
        pass

    def convertToVirtual(self, script : GdScript):
        """Concatenates original instruction sequences into virtualized, smaller representations. This operation is lossless, but needs to be converted back before using in-game.

        Args:
            script (GdScript): Script containing virtual instructions.
        """
        pass

    def convertToOriginal(self, script : GdScript, ensureClean : bool = False):
        """Converts any virtual instructions of this generator type back to their original counterparts. Non-virtual instructions will be unaffected.

        Args:
            script (GdScript): Script containing virtual instructions.
            ensureClean (bool, optional): Force another pass for the generator to catch any instructions that could have been virtualized. May reduce errors. Defaults to False.
        """
        if ensureClean:
            self.convertToVirtual(script)
        self._convertToOriginalInternal(script)