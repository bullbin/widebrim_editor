from typing import Literal, Optional, Union
from ndspy.rom import NintendoDSRom
from widebrim.engine.const import ADDRESS_ARM9_POINTER_FUNC_LANGUAGE, DICT_ID_TO_LANGUAGE, LANGUAGES
from widebrim.engine_ext.utils import decodeStringFromPack

from widebrim.filesystem.fused import FusedFilesystem
from widebrim.madhatter.common import log, logSevere
from widebrim.madhatter.hat_io.asset import File, LaytonPack

# TODO - Remove usePatch, to be removed from mainline anyway

class FusedFileInterface():
    def __init__(self, rom : NintendoDSRom, pathFused : str, generateNewFs : bool = True):
        """Compatibility layer for Fused Filesystem access on prior FileInterface calls

        Args:
            rom (NintendoDSRom): ROM for NDS filesystem
            pathFused (str): Path for Native filesystem
            generateNewFs (bool, optional): Treat Native filesystem as new (empty) and generate file references. Defaults to True.
        """

        # TODO - ROM should ideally not be exposed
        self.rom = rom
        self.fused = FusedFilesystem(rom, pathFused, generateNewFs)

    def doesFileExist(self, filepath : str, usePatch=True) -> bool:
        """Checks if there is a file available for given filepath. Does not ensure file is valid or readable.

        Args:
            filepath (str): Full filepath for data
            usePatch (bool, optional): Allow patch data to be referenced if found instead of ROM data. Defaults to True.

        Returns:
            bool: True if file reference could be found
        """
        return self.fused.doesFileExist(filepath)

    def getData(self, filepath : str, usePatch=True) -> Optional[bytearray]:
        """Gets data stored at filepath if it exists and could be opened. Does not ensure file pertains to any particular format.

        Args:
            filepath (str): Full filepath for data
            usePatch (bool, optional): Allow patch data to be returned if found instead of ROM data. Defaults to True.

        Returns:
            Optional[bytearray]:  Raw bytearray of contents if file exists, else None
        """
        if (compFile := self.fused.getFile(filepath)) != None:
            decompFile = File(data=compFile)
            decompFile.decompress()
            return decompFile.data
        return None
        
    def getPack(self, filepath : str, usePatch=True) -> LaytonPack:
        """Get an archive object representing files stored in the pack at the given filepath.

        Args:
            filepath (str): Full filepath for LPCK archive
            usePatch (bool, optional): Allow patch data to be returned if found instead of ROM data. Defaults to True.

        Returns:
            LaytonPack: Archive object regardless of if filepath exists or not
        """
        archive = LaytonPack()
        if (data := self.getData(filepath)) != None:
            archive.load(data)
        return archive
    
    def getPackedData(self, pathPack : str, filename : str, usePatch=True) -> Optional[bytearray]:
        """Get uncompressed data for some file stored inside an archive at the given filepath.

        Args:
            pathPack (str): Full filepath for LPCK archive
            filename (str): Filename for desired file inside archive
            usePatch (bool, optional): Allow patch data to be returned if found instead of ROM data. Defaults to True.

        Returns:
            Optional[bytearray]: Raw bytearray of contents if file exists, else None
        """
        return self.getPack(pathPack, usePatch=usePatch).getFile(filename)
    
    def getPackedString(self, pathPack : str, filename : str, usePatch=True) -> Optional[str]:
        """Get raw string contents for some file stored inside an archive at the given filepath.

        Args:
            pathPack (str): Full filepath for LPCK archive
            filename (str): Filename for desired file inside archive
            usePatch (bool, optional): Allow patch data to be returned if found instead of ROM data. Defaults to True.

        Returns:
            Optional[str]: Unicode string contents if file exists and could be decoded, else None
        """
        return decodeStringFromPack(self.getPack(pathPack, usePatch=usePatch), filename)
    
    def isRunningFromRom(self) -> bool:
        """Returns whether widebrim's filesystem has access to some LAYTON2 ROM.

        Returns:
            bool: True if there is a ROM loaded for widebrim to access
        """
        return True
    
    def getRom(self) -> Optional[NintendoDSRom]:
        """Gets the loaded ROM being accessed by widebrim. Not recommended since usage of this object may interfere with widebrim's operation.

        Returns:
            Optional[ndspy.rom.NintendoDSRom]: ROM object if loaded, else None
        """
        # TODO - bad
        return self.rom

    def getLanguage(self) -> Optional[Union[Literal[LANGUAGES.Chinese], Literal[LANGUAGES.Dutch], Literal[LANGUAGES.English], Literal[LANGUAGES.French], Literal[LANGUAGES.German], Literal[LANGUAGES.Italian], Literal[LANGUAGES.Japanese], Literal[LANGUAGES.Korean]]]:
        """Attempts to get language from loaded LAYTON2 ROM. Will not recognise (regional, unmodified) Japanese ROM due to changes interfering with language heuristic.

        Returns:
            Optional[Union[Literal[LANGUAGES.Chinese], Literal[LANGUAGES.Dutch], Literal[LANGUAGES.English], Literal[LANGUAGES.French], Literal[LANGUAGES.German], Literal[LANGUAGES.Italian], Literal[LANGUAGES.Japanese], Literal[LANGUAGES.Korean]]]: Returns LANGUAGES Enum member if language could be found, else None
        """
        arm9 = self.rom.loadArm9()
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