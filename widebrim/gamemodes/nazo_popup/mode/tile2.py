from .base import BaseQuestionObject
from ....engine_ext.utils import getAnimFromPath
from ....madhatter.typewriter.stringsLt2 import OPCODES_LT2

# 2 types - Type 18, puzzle 1,2  Rotatable, plus Elysian Box puzzle
#           Type 26, puzzle 4    Movable

class HandlerTile2(BaseQuestionObject):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, callbackOnTerminate)

        self._canTilesBeSwapped = False
        if laytonState.getNazoData().idHandler == 18:
            self._canTilesBeRotated = True
        else:
            self._canTilesBeRotated = False
        
        self._resources = {}
        self._resourcesLastIndex = 0
        
    def _doUnpackedCommand(self, opcode, operands):
        if opcode == OPCODES_LT2.Tile2_AddSprite.value and len(operands) == 1:

            self._resourcesLastIndex += 1
        elif opcode == OPCODES_LT2.Tile2_SwapOn.value and len(operands) == 0:
            self._canTilesBeSwapped = True
        else:
            return super()._doUnpackedCommand(opcode, operands)
        return True