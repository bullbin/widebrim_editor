from .base import BaseQuestionObject
from ....engine_ext.utils import getAnimFromPath
from ....engine.const import RESOLUTION_NINTENDO_DS
from ....madhatter.typewriter.stringsLt2 import OPCODES_LT2
from .const import PATH_ANI_TILE2, PATH_ANI_TILE

from pygame import Rect, draw

# Tile2_AddCheckRotate
# IndexTile, IndexPoint, Direction (0-3)

# Tile2_AddCheckNormal
# IndexTile, IndexPoint

class Tile():
    def __init__(self, resource, offsetX, offsetY, animNameSpawn, animNameTouch, animNameIdle, indexSpawnPoint, allowRotation):
        self.allowRotation = allowRotation == True
        self.indexSpawnPoint = indexSpawnPoint
        self.resource = resource

        # custom center point
        self.offset = (offsetX, offsetY)
        if resource != None:
            self.resource.setAnimationFromName(animNameSpawn)
        else:
            print("Failed to grab resource!")
        
        self.rectsMovement = []
        self.rectsRotation = []

    def setMovementRegion(self, cornerBottomLeft, dimensions):
        self.rectsMovement.append(Rect(cornerBottomLeft, dimensions))

    def setRotationRegion(self, cornerBottomLeft, dimensions):
        self.rectsRotation.append(Rect(cornerBottomLeft, dimensions))

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
        self._points = []
        self._tiles = []
    
    def hasMemoButton(self):
        return self.laytonState.getCurrentNazoListEntry().idInternal != 203
    
    def hasQuitButton(self):
        if self.laytonState.getCurrentNazoListEntry().idInternal != 203:
            return True
        else:
            # Has checks for 2 gamemodes
            return False

    def hasSubmitButton(self):
        return self.laytonState.getCurrentNazoListEntry().idInternal != 2 and self.laytonState.getCurrentNazoListEntry().idInternal != 203

    def hasRestartButton(self):
        return self.laytonState.getCurrentNazoListEntry().idInternal != 203

    def drawPuzzleElements(self, gameDisplay):
        for tile in self._tiles:
            if tile.resource != None:
                frame = tile.resource.getActiveFrame()
                if frame != None:
                    indexPoint = tile.indexSpawnPoint
                    if 0 <= indexPoint < len(self._points):
                        x, y = self._points[indexPoint]
                        y += RESOLUTION_NINTENDO_DS[1]

                        # TODO - Why is the center point behaviour changed for this variant?
                        if self._canTilesBeRotated:
                            x -= (frame.get_width()) // 2
                            y -= (frame.get_height()) // 2

                        gameDisplay.blit(frame, (x,y))
                        for tileMoveRect in tile.rectsMovement:
                            moveRect = tileMoveRect.copy()
                            moveRect.move_ip((x,y))
                            draw.rect(gameDisplay, (255,0,0), moveRect)

        return super().drawPuzzleElements(gameDisplay)
        
    def _doUnpackedCommand(self, opcode, operands):
        # TODO - Check if order of operands matters - it probably very much does
        if opcode == OPCODES_LT2.Tile2_AddSprite.value and len(operands) == 1:
            if self._canTilesBeRotated:
                animResource = PATH_ANI_TILE2 % operands[0].value
            else:
                animResource = PATH_ANI_TILE % operands[0].value
            self._resources[self._resourcesLastIndex] = animResource
            self._resourcesLastIndex += 1
        elif opcode == OPCODES_LT2.Tile2_AddPoint.value and len(operands) == 2:
            self._points.append((operands[0].value, operands[1].value))
        elif opcode == OPCODES_LT2.Tile2_AddObjectNormal.value and len(operands) == 7:
            if len(self._tiles) < 32:
                tile = Tile(self._getCopyOfResource(operands[0].value),
                            operands[1].value, operands[2].value,
                            operands[3].value, operands[5].value, operands[6].value, 
                            operands[6].value, self._canTilesBeRotated)
                self._tiles.append(tile)
        elif opcode == OPCODES_LT2.Tile2_AddObjectRotate.value and len(operands) == 8:
            if len(self._tiles) < 32:
                # TODO - Add rotation param (last operand)
                tile = Tile(self._getCopyOfResource(operands[0].value),
                            operands[1].value, operands[2].value,
                            operands[3].value, operands[5].value, operands[6].value, 
                            operands[6].value, self._canTilesBeRotated)
                self._tiles.append(tile)
        elif opcode == OPCODES_LT2.Tile2_AddObjectRange.value and len(operands) == 4:
            if len(self._tiles) > 0:
                if self._canTilesBeRotated:
                    self._tiles[-1].setRotationRegion((operands[0].value, operands[1].value),
                                                      (operands[2].value, operands[3].value))
                else:
                    self._tiles[-1].setMovementRegion((operands[0].value, operands[1].value),
                                                      (operands[2].value, operands[3].value))
        elif opcode == OPCODES_LT2.Tile2_AddObjectRange2.value and len(operands) == 4:
            if len(self._tiles) > 0:
                if self._canTilesBeRotated:
                    self._tiles[-1].setMovementRegion((operands[0].value, operands[1].value),
                                                      (operands[2].value, operands[3].value))
        elif opcode == OPCODES_LT2.Tile2_SwapOn.value and len(operands) == 0:
            self._canTilesBeSwapped = True
        else:
            return super()._doUnpackedCommand(opcode, operands)
        return True

    def _getCopyOfResource(self, indexResource):
        # Duplicate resource for tile
        # TODO - Create a way to copy anim or have duplicates playing to reduce memory usage
        if indexResource in self._resources:
            return getAnimFromPath(self._resources[indexResource])
        return None