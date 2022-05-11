from editor.e_script.virtual.converter import VirtualInstruction

class FadeInstruction(VirtualInstruction):
    pass

class DialogueInstruction(VirtualInstruction):
    def __init__(self):
        super().__init__()
        self.__idCharacter          = 0
        self.__text                 = ""
        self.__pitchText            = 1
        self.__characterStartAnim   = "NONE"
        self.__characterEndAnim     = "NONE"
        self.__idVoiceClip          = -1

class ShowHideCharacterInstruction(VirtualInstruction):
    pass

class PauseInstruction(VirtualInstruction):
    pass