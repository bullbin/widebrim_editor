from __future__ import annotations
from typing import List, TYPE_CHECKING
from widebrim.filesystem.fusedError import BuilderRomAssetNotAvailable

if TYPE_CHECKING:
    from widebrim.filesystem.fused import FusedFilesystem

class BuildCommand():
    
    def apply(self, filesystem : FusedFilesystem, data : bytes) -> bytes:
        return data

    @staticmethod
    def fromFile(*args):
        return BuildCommand()

class BuildLoadFromSource(BuildCommand):
    def __init__(self, pathRom : str):
        """Command to refresh the entire contents of the built file with a file extracted from ROM.

        Args:
            pathRom (str): [description]
        """
        self.__pathAsset = pathRom
    
    def apply(self, filesystem: FusedFilesystem, data: bytes) -> bytes:
        data = filesystem.getFile(self.__pathAsset, forceRom = True)
        if data == None:
            raise BuilderRomAssetNotAvailable()
        return data

class BuildInsertIntoRaw(BuildCommand):
    def __init__(self, absoluteOffset : int, insertion : bytes):
        self.__offsetAbsolute = absoluteOffset
        self.__insertion = insertion

class BuildDecompress(BuildCommand):
    pass

class BuildCompress(BuildCommand):
    def __init__(self, compressionMethod=None, addHeader=True):
        pass

# TODO - Will eventually have to deal with situation where ROM duplicates files...
#        Cyclical dependencies, so would need to build dependency tree.
COMMAND_TO_CODE = {"ROMLOAD" : BuildLoadFromSource}
COMMAND_ELIMINATES_HISTORY = [BuildLoadFromSource]

# Command list -> files

class GeneralFileBuilder():
    def __init__(self, filesystem : FusedFilesystem):
        self.__commands : List[BuildCommand] = [] 
        self.__data = b''
        self.__filesystem = filesystem
    
    def rebuild(self):
        for command in self.__commands:
            command.apply(self.__filesystem, self.__data)
    
    def getData(self, forceRebuild = True) -> bytes:
        self.rebuild()
        return self.__data
    
    def getScript(self) -> str:
        output = ""
        for indexCommand, command in enumerate(self.__commands):
            if indexCommand > 0:
                output += "\n"
            output += str(command)
        return output
    
    def addCommand(self, command : BuildCommand):
        if type(command) in COMMAND_ELIMINATES_HISTORY:
            self.reset()
        self.__commands.append(command)
    
    def reset(self):
        self.__commands = []
        self.__data = b''