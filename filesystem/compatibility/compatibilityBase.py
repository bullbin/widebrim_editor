from typing import Optional
from widebrim.engine.file.base import ReadOnlyFileInterface
from widebrim.engine_ext.utils import decodeStringFromPack

from filesystem.low_level.fs_template import Filesystem
from widebrim.madhatter.hat_io.asset import File, LaytonPack

class WriteableFilesystemCompatibilityLayer(ReadOnlyFileInterface):
    def __init__(self, filesystem : Filesystem):
        """Compatibility layer for converting FileInterface calls to Filesystem calls

        Args:
            filesystem (Filesystem): Filesystem for data access.
        """
        super().__init__()
        self.writeableFs = filesystem

    def doesFileExist(self, filepath : str) -> bool:
        return self.writeableFs.doesFileExist(filepath)

    def getData(self, filepath : str) -> Optional[bytearray]:
        if (compFile := self.writeableFs.getFile(filepath)) != None:
            decompFile = File(data=compFile)
            decompFile.decompress()
            return decompFile.data
        return None
        
    def getPack(self, filepath : str) -> LaytonPack:
        archive = LaytonPack()
        if (data := self.getData(filepath)) != None:
            archive.load(data)
        return archive
    
    def getPackedData(self, pathPack : str, filename : str) -> Optional[bytearray]:
        return self.getPack(pathPack).getFile(filename)
    
    def getPackedString(self, pathPack : str, filename : str) -> Optional[str]:
        return decodeStringFromPack(self.getPack(pathPack), filename)