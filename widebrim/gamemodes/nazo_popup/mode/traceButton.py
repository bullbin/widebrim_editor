from .base import BaseQuestionObject
from ....engine.const import RESOLUTION_NINTENDO_DS
from ....engine_ext.utils import getAnimFromPath, getAnimFromPathWithAttributes
from ....madhatter.typewriter.stringsLt2 import OPCODES_LT2
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, draw, Surface
from random import randint
from math import sqrt

# Up to 4 solutions
# TODO - Puzzle specific behaviour - a bunch of unimplemented animation names?

# TODO - Put these constants somewhere
PATH_ANI_RETRY = "nazo/tracebutton/%s/retry_trace.spr"
PATH_ANI_POINT = "nazo/tracebutton/point_trace.spr"
WIDTH_PEN = 3

class TraceZone():
    def __init__(self, x, y, diameter, isSolution):
        self.x = x
        self.y = y + RESOLUTION_NINTENDO_DS[1]
        self.radius = diameter / 2
        self.isSolution = isSolution
    
    def wasPressed(self, pos):
        distance = sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
        return distance <= self.radius

class HandlerTraceButton(BaseQuestionObject):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, callbackOnTerminate)
        
        self._traceZones = []
        self._colourLine = (0,0,0)
        self._colourKey = (0,0,0)

        # TODO - getAnimFromPath set animation on spawn

        self._animNoTargetFound = getAnimFromPathWithAttributes(PATH_ANI_RETRY % laytonState.language.value)
        self._animPoint         = getAnimFromPath(PATH_ANI_POINT)

        if self._animPoint != None:
            self._animPoint.setAnimationFromName("gfx")

        self._penLastPoint = None
        self._penSurface = None

        self._hasPenDrawn = False
        self._isPenDrawing = False

        # TODO - Maybe do rolling average to prevent this from being able to get stupidly big
        self._tracePointsTotal = (0,0)
        self._tracePointsCount = 0
        self._tracePointTargetted = None
    
    def _doUnpackedCommand(self, opcode, operands):
        if opcode == OPCODES_LT2.SetFontUserColor.value and len(operands) == 3:
            self._colourLine = (operands[0].value, operands[1].value, operands[2].value)
                
        elif opcode == OPCODES_LT2.AddTracePoint.value and len(operands) == 4:
            if len(self._traceZones) < 24:
                self._traceZones.append(TraceZone(operands[0].value, operands[1].value,
                                                operands[2].value, operands[3].value == "true"))
        else:
            return super()._doUnpackedCommand(opcode, operands)
        return True
    
    def doOnComplete(self):
        self._penSurface = Surface(RESOLUTION_NINTENDO_DS)
        while self._colourLine == self._colourKey:
            self._colourKey = (randint(0,256), 0, 0)
        self._penSurface.set_colorkey(self._colourKey)
        self._clearSurface()
        return super().doOnComplete()

    def _clearSurface(self):
        # TODO - Disable pointing overlay, clear targetted point
        self._tracePointsTotal = (0,0)
        self._tracePointsCount = 0
        self._penSurface.fill(self._colourKey)
    
    def _wasAnswerSolution(self):
        return self._tracePointTargetted != None and self._tracePointTargetted.isSolution

    def _doReset(self):
        self._hasPenDrawn = False
        self._tracePointTargetted = None
        self._clearSurface()
    
    def _addLastPoint(self):
        self._tracePointsCount += 1
        self._tracePointsTotal = (self._tracePointsTotal[0] + self._penLastPoint[0], self._tracePointsTotal[1] + self._penLastPoint[1])
    
    def _drawLineToCurrentPoint(self, pos):
        offsetLastPoint = (self._penLastPoint[0], self._penLastPoint[1] - RESOLUTION_NINTENDO_DS[1])
        offsetPos = (pos[0], pos[1] - RESOLUTION_NINTENDO_DS[1])
        draw.line(self._penSurface, self._colourLine, offsetLastPoint, offsetPos, width=WIDTH_PEN)
    
    def _updatePenTarget(self):

        def setPointPositionFromTarget(target):
            if self._animPoint != None and self._animPoint.getActiveFrame() != None:
                y = target.y - (self._animPoint.getActiveFrame().get_height())
                self._animPoint.setPos((target.x,y))

        self._tracePointTargetted = None
        if self._tracePointsCount > 0:
            targetPos = (round(self._tracePointsTotal[0] / self._tracePointsCount), round(self._tracePointsTotal[1] / self._tracePointsCount))
            for target in self._traceZones:
                if target.wasPressed(targetPos):
                    self._tracePointTargetted = target
                    setPointPositionFromTarget(target)
                    break

    def drawPuzzleElements(self, gameDisplay):
        gameDisplay.blit(self._penSurface, (0, RESOLUTION_NINTENDO_DS[1]))
        # TODO - Implement top screen/bottom screen for clipping purposes
        if self._tracePointTargetted != None:
            # Draw arrow
            if self._animPoint != None:
                self._animPoint.draw(gameDisplay)
        elif self._hasPenDrawn and not(self._isPenDrawing):
            # Draw retry trace screen
            if self._animNoTargetFound != None:
                self._animNoTargetFound.draw(gameDisplay)

        return super().drawPuzzleElements(gameDisplay)

    def handleTouchEventPuzzleElements(self, event):
        if event.type == MOUSEBUTTONDOWN:
            self._hasPenDrawn = True
            self._isPenDrawing = True
            self._tracePointTargetted = None
            self._clearSurface()
            self._penLastPoint = event.pos

        elif self._hasPenDrawn and self._isPenDrawing:
            if event.type == MOUSEMOTION:
                draw.line(self._penSurface, self._colourLine, self._penLastPoint, event.pos)
                self._drawLineToCurrentPoint(event.pos)
                self._addLastPoint()
                self._penLastPoint = event.pos

            elif event.type == MOUSEBUTTONUP:
                self._isPenDrawing = False
                if self._penLastPoint != None:
                    self._drawLineToCurrentPoint(event.pos)
                    self._addLastPoint()
                    self._updatePenTarget()
                    self._penLastPoint = None
        return True