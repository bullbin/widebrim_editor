from typing import Literal, Optional, Union
import ndspy.rom
from widebrim.madhatter.hat_io import asset
from widebrim.madhatter.common import log, logSevere
from widebrim.engine.config import PATH_ROM
from os import path
from .exceptions import PathInvalidRom, RomInvalid
from widebrim.engine.const import ADDRESS_ARM9_POINTER_FUNC_LANGUAGE, DICT_ID_TO_LANGUAGE, LANGUAGES

# TODO - Patch support

class FileInterface():

    _rom = None

    if path.isfile(PATH_ROM):
        try:
            _rom = ndspy.rom.NintendoDSRom.fromFile(PATH_ROM)
        except:
            raise RomInvalid
        
        if _rom.name != bytearray(b'LAYTON2') or not((_rom.idCode[:3] != bytearray(b'YLT') or _rom.idCode[:3] != bytearray(b'Y6Z'))):
            raise RomInvalid
    else:
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
                                return DICT_ID_TO_LANGUAGE[languageInstruction]
        return None

    @staticmethod
    def doesFileExist(filepath) -> bool:
        return FileInterface._isPathAvailableRom(filepath)

    @staticmethod
    def getData(filepath) -> Optional[bytearray]:
        return FileInterface._dataFromRom(filepath)
    
    @staticmethod
    def isRunningFromRom() -> bool:
        return True
    
    @staticmethod
    def getRom() -> Optional[ndspy.rom.NintendoDSRom]:
        if FileInterface.isRunningFromRom():
            return FileInterface._rom
        return None

    @staticmethod
    def getLanguage() -> Optional[Union[Literal[LANGUAGES.Chinese], Literal[LANGUAGES.Dutch], Literal[LANGUAGES.English], Literal[LANGUAGES.French], Literal[LANGUAGES.German], Literal[LANGUAGES.Italian], Literal[LANGUAGES.Japanese], Literal[LANGUAGES.Korean]]]:
        if FileInterface.isRunningFromRom():
            return FileInterface._langFromRom()
        return None