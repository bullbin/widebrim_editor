from widebrim.madhatter.hat_io.asset_script import GdScript
from .defined import *

HEURISTIC_PASSES = [DialogueInstruction,
                    FadeInstruction,
                    ShowHideCharacterInstruction,
                    PauseInstruction,
                    SwitchGameModeInstruction]

def convertToVirtual(script : GdScript) -> GdScript:
    pass