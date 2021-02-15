# 10 points each
# SetTraceCorrectZone unused

from ....engine_ext.utils import getAnimFromPath
from ....engine.anim.fader import Fader
from ....engine.anim.button import StaticButton
from ....engine.const import RESOLUTION_NINTENDO_DS
from ....madhatter.typewriter.stringsLt2 import OPCODES_LT2

from .base import BaseQuestionObject
from pygame import Surface
from pygame.draw import polygon

# Points in LAYTON2 appear to already be pre-sorted,
#     so no convex hull is calculated

class HandlerTraceOnly(BaseQuestionObject):

    MAX_COUNT_POINTS = 10

    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, callbackOnTerminate)
        self._surfaceSolution = Surface(RESOLUTION_NINTENDO_DS)
        self._surfaceSolution.fill((0,0,0))
        self._surfaceSolution.set_alpha(128)
        
        # TODO - Solution bounding rect, intersect on complete
        # TODO - Is solution used? Game leaves it alone after init
        self._pointsIn = []
        self._pointsOut = []

    def _doUnpackedCommand(self, opcode, operands):
        if opcode == OPCODES_LT2.AddInPoint.value and len(operands) == 2:
            if len(self._pointsIn) < HandlerTraceOnly.MAX_COUNT_POINTS:
                self._pointsIn.append((operands[0].value, operands[1].value))
        elif opcode == OPCODES_LT2.AddOutPoint.value and len(operands) == 2:
            if len(self._pointsOut) < HandlerTraceOnly.MAX_COUNT_POINTS:
                self._pointsOut.append((operands[0].value, operands[1].value))
        else:
            return super()._doUnpackedCommand(opcode, operands)
        return True
    
    def doOnComplete(self):
        # TODO - Do the lengths of points in and out need to be the same? Solution algorithm
        # TODO - I think it checks lines between two points as a checkpoint mechanism for checking
        polygon(self._surfaceSolution, (255,255,255), self._pointsOut)
        polygon(self._surfaceSolution, (0,0,0), self._pointsIn)
        return super().doOnComplete()

    def drawPuzzleElements(self, gameDisplay):
        gameDisplay.blit(self._surfaceSolution, (0,RESOLUTION_NINTENDO_DS[1]))
        for point in self._pointsIn:
            x,y = point
            y += RESOLUTION_NINTENDO_DS[1]
            gameDisplay.set_at((x,y), (255,0,0))
        for point in self._pointsOut:
            x,y = point
            y += RESOLUTION_NINTENDO_DS[1]
            gameDisplay.set_at((x,y), (0,255,0))

        return super().drawPuzzleElements(gameDisplay)