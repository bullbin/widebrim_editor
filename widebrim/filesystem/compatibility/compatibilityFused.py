from typing import Optional
from ndspy.rom import NintendoDSRom
from widebrim.engine.const import ADDRESS_ARM9_POINTER_FUNC_LANGUAGE, DICT_ID_TO_LANGUAGE, LANGUAGES
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer

from widebrim.filesystem.fused import FusedFilesystem
from widebrim.madhatter.common import log, logSevere

class WriteableFusedFileInterface(WriteableFilesystemCompatibilityLayer):

    def __init__(self, rom : NintendoDSRom, pathFused : str, generateNewFs : bool = True):
        """Compatibility layer for Fused Filesystem access on prior FileInterface calls.

        Args:
            rom (NintendoDSRom): ROM for NDS filesystem
            pathFused (str): Path for Native filesystem
            generateNewFs (bool, optional): Treat Native filesystem as new (empty) and generate file references. Defaults to True.
        """

        # TODO - ROM should ideally not be exposed
        self.rom = rom
        super().__init__(FusedFilesystem(rom, pathFused, generateNewFs))
    
    def isRunningFromRom(self) -> bool:
        return True
    
    def getRom(self) -> Optional[NintendoDSRom]:
        return self.rom

    def getLanguage(self) -> Optional[LANGUAGES]:
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