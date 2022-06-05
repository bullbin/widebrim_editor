from typing import List

from widebrim.filesystem.builder.builder import BuildCommand
from widebrim.filesystem.fused import FusedFilesystem

class ScriptBuilder():
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
    
    def reset(self):
        self.__commands = []
        self.__data = b''