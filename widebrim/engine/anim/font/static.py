from pygame import Surface

def generateImageFromString(font, inString):

    chars = []

    for letter in inString:
        if letter in font.glyphMap:
            chars.append(font.glyphMap[letter])
            
    dimensions = (0,0)
    for glyph in chars:
        dimensions = (dimensions[0] + glyph.getWidth(), max(dimensions[1], glyph.image.get_height()))
    
    output = Surface(dimensions).convert()
    output.set_colorkey((0,0,0))
    xOffset = 0
    for glyph in chars:
        output.blit(glyph.image, (xOffset,0))
        xOffset += glyph.getWidth()

    return output