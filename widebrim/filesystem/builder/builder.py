from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional
from widebrim.filesystem.fusedError import BuilderRomAssetNotAvailable
from widebrim.madhatter.hat_io.asset import File
from shlex import split as splitQuote

if TYPE_CHECKING:
    from widebrim.filesystem.fused import FusedFilesystem

class BuildCommand():
    
    @staticmethod
    def fromString(string : str) -> BuildCommand:
        """Get the command represented by a string.

        Args:
            string (str): String representation of command.

        Returns:
            BuildCommand: Command. NO-OP BuildCommand class if the string could not be decoded.
        """
        stringSplit = splitQuote(string)
        if len(stringSplit) > 0:
            command = _operatorToCommand(stringSplit[0])
            if command != None:
                command = command.processKeyString(stringSplit[1:])
                if command != None:
                    return command
        return BuildCommand()
    
    @staticmethod
    def processKeyString(splitArgs : List[str]) -> Optional[BuildCommand]:
        """Instanciate a command using an input string and get the resulting command.

        Args:
            splitArgs (List[str]): List of argument strings after opcode.

        Returns:
            Optional[BuildCommand]: Command. None if the string could not be decoded for this class.
        """
        return None
    
    def apply(self, filesystem: FusedFilesystem, data: bytes) -> bytes:
        """Applies the command to the working data.

        Args:
            filesystem (FusedFilesystem): Source filesystem.
            data (bytes): Working data.

        Returns:
            bytes: Working data after command application.
        """
        return data
    
    def __str__(self) -> str:
        return "FATAL"

class BuildLoadFromSource(BuildCommand):
    def __init__(self, pathRom : str):
        """Command to refresh the entire contents of the built file with a file extracted from ROM.

        Args:
            pathRom (str): [description]
        """
        self.__pathAsset = pathRom
    
    @staticmethod
    def processKeyString(splitArgs) -> Optional[BuildCommand]:
        if len(splitArgs) > 0:
            return BuildLoadFromSource(splitArgs[0])
        return None

    def apply(self, filesystem: FusedFilesystem, data: bytes) -> bytes:
        data = filesystem.getFile(self.__pathAsset, forceRom = True)
        if data == None:
            raise BuilderRomAssetNotAvailable()
        return data
    
    def __str__(self) -> str:
        return "GEN_ROMLOAD " + '"' + self.__pathAsset + '"'

class BuildInsertIntoRaw(BuildCommand):
    def __init__(self, absoluteOffset : int, insertion : bytes):
        self.__offsetAbsolute = absoluteOffset
        self.__insertion = insertion

class BuildDecompress(BuildCommand):
    def __init__(self):
        """Command to decompress the file for the rest of the remaining command stack.
        """
        pass

    def apply(self, filesystem: FusedFilesystem, data: bytes) -> bytes:
        tempDecomp = File(data=data)
        tempDecomp.decompress()
        return tempDecomp.data
    
    def __str__(self) -> str:
        return "GEN_DECOMP DETECT"

class BuildCompress(BuildCommand):
    def __init__(self):
        """Command to compress the file for the rest of the remaining command stack.
        """
        # TODO - Add header
        pass

    def apply(self, filesystem: FusedFilesystem, data: bytes) -> bytes:
        tempDecomp = File(data=data)
        tempDecomp.compress()
        return tempDecomp.data
    
    def __str__(self) -> str:
        return "GEN_COMP BEST"

# TODO - Will eventually have to deal with situation where ROM duplicates files...
#        Cyclical dependencies, so would need to build dependency tree.
COMMAND_TO_CODE = {"GEN_ROMLOAD" : BuildLoadFromSource,
                   "GEN_COMP" : BuildCompress,
                   "GEN_DECOMP" : BuildDecompress}
COMMAND_ELIMINATES_HISTORY = [BuildLoadFromSource]

def _operatorToCommand(operator : str) -> Optional[BuildCommand]:
    if operator in COMMAND_TO_CODE:
        return COMMAND_TO_CODE[operator]
    return None

# Command list -> files

class GeneralFileBuilder():
    def __init__(self, filesystem : FusedFilesystem):
        self.__commands : List[BuildCommand] = [] 
        self.__data = b''
        self.__filesystem = filesystem
    
    def rebuild(self):
        self.data = b''
        for command in self.__commands:
            self.__data = command.apply(self.__filesystem, self.__data)
    
    def getData(self, forceRebuild = True) -> bytes:
        if forceRebuild:
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