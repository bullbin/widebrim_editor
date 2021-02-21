from .base import BaseQuestionObject
from ....engine.const import RESOLUTION_NINTENDO_DS
from ....madhatter.typewriter.stringsLt2 import OPCODES_LT2
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, draw, Surface
from random import randint
from math import sqrt

# Up to 4 solutions
# each can have 24 trace points

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
        
        self._activeTraceZoneIndex = None
        self._traceZones = []
        self._colourLine = (0,0,0)
        self._colourKey = (0,0,0)

        self._penLastPoint = None
        self._penSurface = None

        # On reset, change back to false
        self._hasPenDrawn = False
        
        self._isPenDrawing = False
        self._tracePoints = []
    
    def _doUnpackedCommand(self, opcode, operands):
        if opcode == OPCODES_LT2.SetFontUserColor.value and len(operands) == 3:
            self._colourLine = (operands[0].value, operands[1].value, operands[2].value)
            while self._colourLine == self._colourKey:
                self._colourKey = (randint(0,256), randint(0,256), randint(0,256))
                
        elif opcode == OPCODES_LT2.AddTracePoint.value and len(operands) == 4:
            self._traceZones.append(TraceZone(operands[0].value, operands[1].value,
                                              operands[2].value, operands[3].value == "true"))
        else:
            return super()._doUnpackedCommand(opcode, operands)
    
    def doOnComplete(self):
        self._penSurface = Surface(RESOLUTION_NINTENDO_DS)
        self._penSurface.set_colorkey(self._colourKey)
        self._clearSurface()
        return super().doOnComplete()

    def _clearSurface(self):
        self._penSurface.fill(self._colourKey)

    def drawPuzzleElements(self, gameDisplay):
        gameDisplay.blit(self._penSurface, (0, RESOLUTION_NINTENDO_DS[1]))
        return super().drawPuzzleElements(gameDisplay)

    def handleTouchEventPuzzleElements(self, event):
        if event.type == MOUSEBUTTONDOWN:
            self._hasPenDrawn = True
            self._isPenDrawing = True
            self._clearSurface()
            self._penLastPoint = event.pos
            self._activeTraceZoneIndex = None
            for indexTarget, target in enumerate(self._traceZones):
                if target.wasPressed(event.pos):
                    self._activeTraceZoneIndex = indexTarget
                    break
        elif self._hasPenDrawn and self._isPenDrawing:
            if event.type == MOUSEMOTION:
                draw.line(self._penSurface, self._colourLine, self._penLastPoint, event.pos)
                self._penLastPoint = event.pos
                if self._activeTraceZoneIndex != None:
                    if not(self._traceZones[self._activeTraceZoneIndex].wasPressed(event.pos)):
                        self._activeTraceZoneIndex = None

            elif event.type == MOUSEBUTTONUP:
                self._isPenDrawing = False
                if self._penLastPoint != None:
                    draw.line(self._penSurface, self._colourLine, self._penLastPoint, event.pos)
                    self._penLastPoint = None
                if self._activeTraceZoneIndex != None:
                    if not(self._traceZones[self._activeTraceZoneIndex].wasPressed(event.pos)):
                        self._activeTraceZoneIndex = None
                    else:
                        print(self._activeTraceZoneIndex)
        
        return True