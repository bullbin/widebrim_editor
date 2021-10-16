from __future__ import annotations

from typing import Literal, Optional, Union
import ndspy.rom
from widebrim.madhatter.hat_io import asset
from widebrim.madhatter.common import log, logSevere
from widebrim.engine.config import DEBUG_ALLOW_WIDEBRIM_NO_ROM, FILE_USE_PATCH, PATH_PATCH, PATH_ROM
from os import path

from widebrim.madhatter.hat_io.const import ENCODING_DEFAULT_STRING
from .exceptions import PathInvalidRom, RomInvalid
from widebrim.engine.const import ADDRESS_ARM9_POINTER_FUNC_LANGUAGE, DICT_ID_TO_LANGUAGE, LANGUAGES

# TODO - Improved patch support (file excluding for replacement)
# TODO - Madhatter magic checks, file checks (there will be errors once patching starts...)

def _getResolvedPatchPath(inPath : str) -> str:
    if len(inPath) > 0 and (inPath[0] == "/" or inPath[0] == "\\"):
        if inPath[0] == "/":
            return inPath.lstrip("/")
        elif inPath[0] == "\\":
            return inPath.lstrip("\\")
    return inPath

class VirtualArchive():

    def __init__(self, pathPack : str, usePatch=True):
        self.__romArchive = asset.LaytonPack()
        if (data := FileInterface.getData(pathPack, usePatch=False)) != None:
            self.__romArchive.load(data)
        
        self.__allowPatch       = usePatch and FILE_USE_PATCH
        self.__pathPatchArchive = pathPack
    
    def getData(self, nameFile : str) -> Optional[bytes]:
        if self.__allowPatch:
            namePath = path.join(PATH_PATCH, _getResolvedPatchPath(self.__pathPatchArchive), nameFile)
            if path.isfile(namePath):
                try:
                    with open(namePath, 'rb') as patchData:
                        data = patchData.read()
                        log("PatchGrabArchive", self.__pathPatchArchive, "->", nameFile)
                        return data
                except OSError:
                    pass
        return self.__romArchive.getFile(nameFile)

    def getString(self, nameFile : str) -> Optional[str]:
        data = self.getData(nameFile)
        if data != None:
            try:
                return data.decode(ENCODING_DEFAULT_STRING)
            except UnicodeDecodeError:
                pass
        return None

class FileInterface():

    _rom = None

    if path.isfile(PATH_ROM):
        try:
            _rom = ndspy.rom.NintendoDSRom.fromFile(PATH_ROM)
        except:
            if not(DEBUG_ALLOW_WIDEBRIM_NO_ROM):
                raise RomInvalid
        
        if _rom != None and not(DEBUG_ALLOW_WIDEBRIM_NO_ROM) and _rom.name != bytearray(b'LAYTON2') or not((_rom.idCode[:3] != bytearray(b'YLT') or _rom.idCode[:3] != bytearray(b'Y6Z'))):
            raise RomInvalid
    
    if _rom == None and not(DEBUG_ALLOW_WIDEBRIM_NO_ROM):
        raise PathInvalidRom

    @staticmethod
    def _isPathAvailableRom(filepath) -> bool:
        try:
            if FileInterface._rom.filenames.idOf(filepath) != None:
                return True
            return False
        except:
            return False

    @staticmethod
    def _dataFromRom(filepath) -> Optional[bytearray]:
        if FileInterface._isPathAvailableRom(filepath):
            testFile = asset.File(data=FileInterface._rom.getFileByName(filepath))
            testFile.decompress()
            log("RomGrab", filepath)
            return testFile.data
        logSevere("RomGrabFailed", filepath)
        return None

    @staticmethod
    def _isPathAvailablePatch(filepath) -> bool:
        return FILE_USE_PATCH and path.exists(path.join(PATH_PATCH, _getResolvedPatchPath(filepath)))
    
    @staticmethod
    def _dataFromPatch(filepath) -> Optional[bytearray]:
        if FileInterface._isPathAvailablePatch(filepath):
            try:
                with open(path.join(PATH_PATCH, _getResolvedPatchPath(filepath)), 'rb') as patchData:
                    data = patchData.read()
                    log("PatchGrab", filepath)
                    return data
            except OSError:
                pass
        return None

    @staticmethod
    def _langFromRom() -> Optional[Union[Literal[LANGUAGES.Chinese], Literal[LANGUAGES.Dutch], Literal[LANGUAGES.English], Literal[LANGUAGES.French], Literal[LANGUAGES.German], Literal[LANGUAGES.Italian], Literal[LANGUAGES.Japanese], Literal[LANGUAGES.Korean]]]:
        if FileInterface._rom != None:
            arm9 = FileInterface._rom.loadArm9()
            startAddress = arm9.ramAddress
            dataArm9 = arm9.save()

            def is32BitGrabValid(address : int):
                return 0 <= address and address + 4 <= len(dataArm9)

            # Not emulating any registers, so relying on heuristics to detect correct MOV instruction. Assumes r0 will be used, so rest of engine not touched

            targetInstructionPointer = ADDRESS_ARM9_POINTER_FUNC_LANGUAGE - startAddress    # Find pointer to next big function after entry
            
            if is32BitGrabValid(targetInstructionPointer):
                targetInstructionPointer = int.from_bytes(dataArm9[targetInstructionPointer:targetInstructionPointer + 4], byteorder='little') - startAddress
                if is32BitGrabValid(targetInstructionPointer):
                    targetInstructionPointer += 4 * 33                      # Seek forward 33 instructions into the function (mov)
                    if is32BitGrabValid(targetInstructionPointer):
                        languageInstruction = int.from_bytes(dataArm9[targetInstructionPointer : targetInstructionPointer + 4], byteorder = 'little')
                        if languageInstruction & 0xffffff00 == 0xe3a00000:  # Check for proper MOV instruction to r0 with immediate language operand
                            languageInstruction = languageInstruction & 0x000000ff
                            if languageInstruction in DICT_ID_TO_LANGUAGE:
                                log("Detected language", DICT_ID_TO_LANGUAGE[languageInstruction].value)
                                return DICT_ID_TO_LANGUAGE[languageInstruction]
        logSevere("Failed to detect language!")
        return None

    @staticmethod
    def doesFileExist(filepath : str, usePatch=True) -> bool:
        """Checks if there is a file available for given filepath. Does not ensure file is valid or readable.

        Args:
            filepath (str): Full filepath for data
            usePatch (bool, optional): Allow patch data to be referenced if found instead of ROM data. Defaults to True.

        Returns:
            bool: True if file reference could be found
        """
        if usePatch and FileInterface._isPathAvailablePatch(filepath):
            return True
        return FileInterface._isPathAvailableRom(filepath)

    @staticmethod
    def getData(filepath : str, usePatch=True) -> Optional[bytearray]:
        """Gets data stored at filepath if it exists and could be opened. Does not ensure file pertains to any particular format.

        Args:
            filepath (str): Full filepath for data
            usePatch (bool, optional): Allow patch data to be returned if found instead of ROM data. Defaults to True.

        Returns:
            Optional[bytearray]:  Raw bytearray of contents if file exists, else None
        """
        if usePatch and (data := FileInterface._dataFromPatch(filepath)) != None:
            return data
        return FileInterface._dataFromRom(filepath)
    
    @staticmethod
    def getPack(filepath : str, usePatch=True) -> VirtualArchive:
        """Get an archive object representing files stored in the pack at the given filepath.

        Args:
            filepath (str): Full filepath for LPCK archive
            usePatch (bool, optional): Allow patch data to be returned if found instead of ROM data. Defaults to True.

        Returns:
            VirtualArchive: Archive object regardless of if filepath exists or not
        """
        return VirtualArchive(filepath, usePatch=usePatch)
    
    @staticmethod
    def getPackedData(pathPack : str, filename : str, usePatch=True) -> Optional[bytearray]:
        """Get uncompressed data for some file stored inside an archive at the given filepath.

        Args:
            pathPack (str): Full filepath for LPCK archive
            filename (str): Filename for desired file inside archive
            usePatch (bool, optional): Allow patch data to be returned if found instead of ROM data. Defaults to True.

        Returns:
            Optional[bytearray]: Raw bytearray of contents if file exists, else None
        """
        return FileInterface.getPack(pathPack, usePatch=usePatch).getData(filename)
    
    @staticmethod
    def getPackedString(pathPack : str, filename : str, usePatch=True) -> Optional[str]:
        """Get raw string contents for some file stored inside an archive at the given filepath.

        Args:
            pathPack (str): Full filepath for LPCK archive
            filename (str): Filename for desired file inside archive
            usePatch (bool, optional): Allow patch data to be returned if found instead of ROM data. Defaults to True.

        Returns:
            Optional[str]: Unicode string contents if file exists and could be decoded, else None
        """
        return FileInterface.getPack(pathPack, usePatch=usePatch).getString(filename)
    
    @staticmethod
    def isRunningFromRom() -> bool:
        """Returns whether widebrim's filesystem has access to some LAYTON2 ROM.

        Returns:
            bool: True if there is a ROM loaded for widebrim to access
        """
        return FileInterface._rom != None
    
    @staticmethod
    def getRom() -> Optional[ndspy.rom.NintendoDSRom]:
        """Gets the loaded ROM being accessed by widebrim. Not recommended since usage of this object may interfere with widebrim's operation.

        Returns:
            Optional[ndspy.rom.NintendoDSRom]: ROM object if loaded, else None
        """
        if FileInterface.isRunningFromRom():
            return FileInterface._rom
        return None

    @staticmethod
    def getLanguage() -> Optional[Union[Literal[LANGUAGES.Chinese], Literal[LANGUAGES.Dutch], Literal[LANGUAGES.English], Literal[LANGUAGES.French], Literal[LANGUAGES.German], Literal[LANGUAGES.Italian], Literal[LANGUAGES.Japanese], Literal[LANGUAGES.Korean]]]:
        """Attempts to get language from loaded LAYTON2 ROM. Will not recognise (regional, unmodified) Japanese ROM due to changes interfering with language heuristic.

        Returns:
            Optional[Union[Literal[LANGUAGES.Chinese], Literal[LANGUAGES.Dutch], Literal[LANGUAGES.English], Literal[LANGUAGES.French], Literal[LANGUAGES.German], Literal[LANGUAGES.Italian], Literal[LANGUAGES.Japanese], Literal[LANGUAGES.Korean]]]: Returns LANGUAGES Enum member if language could be found, else None
        """
        if FileInterface.isRunningFromRom():
            return FileInterface._langFromRom()
        return None