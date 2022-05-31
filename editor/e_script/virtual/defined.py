from editor.e_script.virtual.custom import VirtualInstructionGenerator
from editor.gui.command_annotator.bank import InstructionDescription

class FadeInstruction(InstructionDescription, VirtualInstructionGenerator):
    pass

class DialogueInstruction(InstructionDescription, VirtualInstructionGenerator):
    def __init__(self):
        super().__init__()
        self.__idCharacter          = 0
        self.__text                 = ""
        self.__pitchText            = 1
        self.__characterStartAnim   = "NONE"
        self.__characterEndAnim     = "NONE"
        self.__idVoiceClip          = -1

class ShowHideCharacterInstruction(InstructionDescription, VirtualInstructionGenerator):
    pass

class PauseInstruction(InstructionDescription, VirtualInstructionGenerator):
    pass

class SwitchGameModeInstruction(InstructionDescription, VirtualInstructionGenerator):
    pass