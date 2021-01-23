from widebrim.engine.const import RESOLUTION_NINTENDO_DS
from .base import BaseQuestionObject
from ....madhatter.typewriter.stringsLt2 import OPCODES_LT2

class HandlerDivide(BaseQuestionObject):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, callbackOnTerminate)

        self._sizeBlock = 2
        self._colourLine = (0,0,0)
        self._colourPen = (0,0,0)
        
        if laytonState.getNazoData().idHandler == 15:
            self._isMovesLimited = True
        else:
            self._isMovesLimited = False

        self._limitMoves = 0
        self._countMoves = 0

        self._allowDiagonalMoves = False

        self._posGridCorner = (0,RESOLUTION_NINTENDO_DS[1])
        self._sizeGrid = (0,0)
        self._posTouchPoints = []
    
    def _doUnpackedCommand(self, opcode, operands):
        if opcode == OPCODES_LT2.SetNumTouch.value and len(operands) == 1:
            self._limitMoves = operands[0].value
        elif opcode == OPCODES_LT2.SetGridPosition.value and len(operands) == 2:
            self._posGridCorner = (operands[0].value, operands[1].value + RESOLUTION_NINTENDO_DS[1])
        elif opcode == OPCODES_LT2.SetGridSize.value and len(operands) == 2:
            self._sizeGrid = (operands[0].value, operands[1].value)
        elif opcode == OPCODES_LT2.SetBlockSize.value and len(operands) == 1:
            self._sizeBlock = operands[0].value
        elif opcode == OPCODES_LT2.SetLineColor.value and len(operands) == 3:
            self._colourLine = (operands[0].value, operands[1].value, operands[2].value)
        elif opcode == OPCODES_LT2.SetPenColor.value and len(operands) == 3:
            self._colourPen = (operands[0].value, operands[1].value, operands[2].value)
        elif opcode == OPCODES_LT2.EnableNaname.value and len(operands) == 0:
            self._allowDiagonalMoves = True
        elif opcode == OPCODES_LT2.AddTouchPoint.value and len(operands) == 2:
            self._posTouchPoints.append((operands[0].value, operands[1].value))
        else:
            return super()._doUnpackedCommand(opcode, operands)
        return True
    
    def drawPuzzleElements(self, gameDisplay):
        super().drawPuzzleElements(gameDisplay)
        for touchPointX, touchPointY in self._posTouchPoints:
            gameDisplay.set_at((touchPointX + self._posGridCorner[0], touchPointY + self._posGridCorner[1]), (0,0,0))
    
    def doOnComplete(self):
        self._sizeGrid = (self._sizeGrid[0] * self._sizeBlock, self._sizeGrid[0] * self._sizeBlock)
        for indexTouchPoint, touchPoint in enumerate(self._posTouchPoints):
            touchPointX, touchPointY = touchPoint
            self._posTouchPoints[indexTouchPoint] = (touchPointX * self._sizeBlock, touchPointY * self._sizeBlock)
        return super().doOnComplete()