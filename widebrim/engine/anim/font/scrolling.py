from pygame import Surface, BLEND_RGB_MULT
from ...const import RESOLUTION_NINTENDO_DS, TIME_FRAMECOUNT_TO_MILLISECONDS
from .const import BLEND_MAP
from ...string import getSubstitutedString

from ...convenience import initDisplay

initDisplay()

class ScrollingFontHelper():
    def __init__(self, font, yBias = 4, durationPerCharacter=TIME_FRAMECOUNT_TO_MILLISECONDS):
        self._font = font
        self._yBias = font.dimensions[1] + yBias
        self._xMax = font.dimensions[0]

        self._outputLineSurfaces = []
        self._workingLineSurfaceIndex = 0
        self._workingLineXOffset = 0

        self._pos = (0,0)
        self._color = (0,0,0)
        self._tintSurface = Surface(font.dimensions)

        self._text = ""
        self._offsetText = 0
        self._hasCharsRemaining = False

        self._durationPerChar = TIME_FRAMECOUNT_TO_MILLISECONDS
        self._durationCarried = 0
        self._durationWaiting = 0

        self.setDurationPerCharacter(durationPerCharacter)
        self._isWaitingForTap = False
    
    def setDurationPerCharacter(self, duration : float):
        if self._durationPerChar >= 0:
            self._durationPerChar = duration

    def setPos(self, pos):
        self._pos = pos

    def setColor(self, triplet):
        self._color = triplet
        self._tintSurface.fill(triplet)

    def _reset(self):
        self._outputLineSurfaces = []
        self._workingLineSurfaceIndex = 0
        self._workingLineXOffset = 0
        self._offsetText = 0
        self._hasCharsRemaining = False
        self._durationCarried = 0
        self._durationWaiting = 0
        self._isWaitingForTap = False

    def setText(self, text):
        # Clear current stored text
        self._reset()
        self._text = getSubstitutedString(text)
        self._hasCharsRemaining = True

        lineWidths = []

        # Remove any sequences to do with changing anims, etc
        removedControlledCharString = []
        for indexLine, line in enumerate(self._text.split("&")):
            if not(indexLine % 2):
                removedControlledCharString.append(line)
        removedControlledCharString = ''.join(removedControlledCharString)

        # Account for control characters, line breaks and text clearing to calculate the maximum length of each line
        for clearParagraph in removedControlledCharString.split("@c"):
            indexLine = 0
            for line in clearParagraph.split("@B"):
                for subLine in line.split("\n"):
                    controlChars = subLine.count("@") + subLine.count("#")
                    if len(lineWidths) > indexLine:
                        lineWidths[indexLine] = max(lineWidths[indexLine], len(subLine) - (controlChars * 2))
                    else:
                        lineWidths.append(len(subLine) - (controlChars * 2))
                    indexLine += 1
            
        # Finally create the blank buffer surfaces for text to be written to
        for indexLine, width in enumerate(lineWidths):
            self._outputLineSurfaces.append(Surface((int(self._font.dimensions[0] * width), int(self._font.dimensions[1]))).convert_alpha())
            self._outputLineSurfaces[indexLine].fill((0,0,0,0))

    def _getNextChar(self):
        # Returns next character (control included) from input string
        # If no character is available, None is returned
        # Control characters are given in full, including their identifiers.

        if self._offsetText >= len(self._text):
            self._hasCharsRemaining = False
            return None
        else:
            # TODO - Check error hasn't occured
            if self._text[self._offsetText] == "@" or self._text[self._offsetText] == "#":
                self._offsetText += 2
                return self._text[self._offsetText - 2:self._offsetText]
            elif self._text[self._offsetText] == "&":
                output = "&"
                while self._text[self._offsetText + 1] != "&":
                    output += self._text[self._offsetText + 1]
                    self._offsetText += 1
                self._offsetText += 2
                return output + "&"
            else:
                self._offsetText += 1
                return self._text[self._offsetText - 1]

    def _addCharacterToDrawBuffer(self, character):
        if character in self._font.glyphMap:
            glyph = self._font.glyphMap[character]
            self._outputLineSurfaces[self._workingLineSurfaceIndex].blit(glyph.image, (self._workingLineXOffset, 0))
            self._outputLineSurfaces[self._workingLineSurfaceIndex].blit(self._tintSurface, (self._workingLineXOffset, 0), special_flags=BLEND_RGB_MULT)
            self._workingLineXOffset += glyph.getWidth()

    def _clearBufferAndResetLineCounter(self):
        for buffer in self._outputLineSurfaces:
            buffer.fill((0,0,0,0))
        self._workingLineSurfaceIndex = 0
        self._workingLineXOffset = 0

    def _updateTextChar(self):
        # Returns True if the character contributed graphically
        nextChar = self._getNextChar()
        while nextChar != None and self._hasCharsRemaining and not(self.isWaiting()):
            # Newline character added for puzzles - cannot be used in events
            if nextChar == "\n":
                self._workingLineSurfaceIndex += 1
                self._workingLineXOffset = 0
            elif len(nextChar) == 1:
                self._addCharacterToDrawBuffer(nextChar)
                return True 
            else:
                if nextChar[0] == "@":
                    # Control character
                    if nextChar[1] == "p":      # Wait until touch
                        self._isWaitingForTap = True

                    elif nextChar[1] == "w":    # Wait during text
                        self._durationCarried -= 500

                    elif nextChar[1] == "c":    # Clear the screen
                        self._clearBufferAndResetLineCounter()

                    elif nextChar[1] == "B":    # Line break
                        self._workingLineSurfaceIndex += 1
                        self._workingLineXOffset = 0
                
                elif nextChar[0] == "#":
                    # Color character
                    if nextChar[1] in BLEND_MAP:
                        self.setColor(BLEND_MAP[nextChar[1]])
                    else:
                        print("Missing color", nextChar[1])

                else:
                    # TODO - Command characters
                    print("TODO - Encountered anim command :: ", nextChar)
                    pass

            return False

    def isWaiting(self):
        return self._isWaitingForTap
    
    def setTap(self):
        self._isWaitingForTap = False
    
    def getActiveState(self):
        return self._hasCharsRemaining
    
    def skip(self):
        while self._hasCharsRemaining and not(self.isWaiting()):
            self._updateTextChar()

    def update(self, gameClockDelta):
        if self._hasCharsRemaining and not(self.isWaiting()):
            self._durationCarried += gameClockDelta
            while self._durationCarried >= self._durationPerChar and self._hasCharsRemaining and not(self.isWaiting()):
                if self._updateTextChar():
                    self._durationCarried -= self._durationPerChar

    def draw(self, gameDisplay):
        yBias = self._pos[1]
        for buffer in self._outputLineSurfaces[0:self._workingLineSurfaceIndex + 1]:
            gameDisplay.blit(buffer, (self._pos[0], yBias))
            yBias += self._yBias
    
    def drawCentered(self, gameDisplay):
        # Bugfix - Will not draw centered as width is not aligned with buffer. Fixed in static, see to check tracking actual width
        yBias = self._pos[1]
        for buffer in self._outputLineSurfaces[0:self._workingLineSurfaceIndex + 1]:
            gameDisplay.blit(buffer, ((RESOLUTION_NINTENDO_DS[0] - buffer.get_width()) // 2, yBias))
            yBias += self._yBias