import ndspy.rom
from ..madhatter.hat_io import binary, asset
from .config import PATH_ROM
from os import path
from .exceptions import PathInvalidRom, RomInvalid

# TODO - Patch support
# TODO - Clean exit

class FileInterface():

    _rom = None

    if path.isfile(PATH_ROM):
        try:
            _rom = ndspy.rom.NintendoDSRom.fromFile(PATH_ROM)
        except:
            raise RomInvalid
        
        if _rom.name != bytearray(b'LAYTON2') or _rom.idCode[:3] != bytearray(b'YLT'):
            raise RomInvalid
    else:
        raise PathInvalidRom

    @staticmethod
    def _isPathAvailableRom(filepath):
        # debugSeverePrint("RomCheck", resolveFilepath(filepath))
        if FileInterface._rom.filenames.idOf(filepath) != None:
            return True
        return False

    @staticmethod
    def _dataFromRom(filepath):
        if FileInterface._isPathAvailableRom(filepath):
            testFile = asset.File(data=FileInterface._rom.getFileByName(filepath))
            testFile.decompress()
            #debugPrint("RomGrab", resolveFilepath(filepath))
            return testFile.data
        #debugErrorPrint("RomGrabFailed", resolveFilepath(filepath))
        return None

    @staticmethod
    def doesFileExist(filepath):
        return FileInterface._isPathAvailableRom(filepath)

    @staticmethod
    def getData(filepath):
        return FileInterface._dataFromRom(filepath)
    
    @staticmethod
    def isRunningFromRom():
        return True
    
    @staticmethod
    def getRom():
        if FileInterface.isRunningFromRom():
            return FileInterface._rom
        return None