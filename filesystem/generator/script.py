from typing import List
from filesystem.builder.builder import BuildCommand
from filesystem.generator.base import FileRepresentationBuilt, FileRepresentationRaw
from widebrim.madhatter.hat_io.asset_script import GdScript, Instruction

class ScriptRepresentationRaw(FileRepresentationRaw):
    def __init__(self) -> None:
        super().__init__()
        self._script = GdScript()
    
    def load(self, data : bytes, isTalkScript = False):
        self._script.load(data, isTalkscript=isTalkScript)

    def insertInstruction(self, instruction : Instruction):
        self._hasBeenModified = True

    def moveInstructionUp(self, idxInstruction : int):
        self._hasBeenModified = True

    def moveInstructionDown(self, idxInstruction : int):
        self._hasBeenModified = True
    
    def getData(self) -> bytes:
        self._script.save()
        return self._script.data

class ScriptRepresentationBuilt(ScriptRepresentationRaw, FileRepresentationBuilt):
    def __init__(self) -> None:
        ScriptRepresentationRaw.__init__(self)
        self._buildCommands = []
    
    def load(self, buildCommands : List[BuildCommand]):
        pass

    def isBuiltAsset(self):
        return True