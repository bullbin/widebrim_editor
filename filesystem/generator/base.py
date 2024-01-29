from typing import List, Optional
from filesystem.builder.builder import BuildCommand

class FileRepresentationRaw():
    
    def __init__(self) -> None:
        self._hasBeenModified = False

    def hasBeenModified(self):
        return self._hasBeenModified

    def isBuiltAsset(self):
        return False

    def getData(self) -> bytes:
        return b''

    def getRecipe(self) -> Optional[List[BuildCommand]]:
        return []

class FileRepresentationBuilt(FileRepresentationRaw):
    
    def __init__(self) -> None:
        super().__init__()