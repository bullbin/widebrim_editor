from widebrim.madhatter.hat_io.asset_script import GdScript
from .custom_instructions import *

HEURISTIC_PASSES = [DialogueInstructionGenerator]

def convertToVirtual(script : GdScript) -> GdScript:
    for stage in HEURISTIC_PASSES:
        pass