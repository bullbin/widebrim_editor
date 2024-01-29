from widebrim.engine.const import PATH_NAME_ROOT, PATH_ANI
from widebrim.gamemodes.dramaevent.const import PATH_BODY_ROOT, PATH_BODY_ROOT_LANG_DEP

from typing import Callable, List, Optional, Dict, Tuple, Union
from widebrim.engine.state.manager import Layton2GameState
from PIL.Image import Image as ImageType
from pygame import Surface

from widebrim.engine.anim.font.nftr_decode import Glyph
from widebrim.engine_ext.utils import getBottomScreenAnimFromPath

import pytesseract
from PIL.Image import Image as ImageType
from PIL import Image, ImageOps
from pygame.image import tostring
from statistics import mode

def _surfToPillow(surf : Surface) -> ImageType:
    """Converts a pygame surface to a PIL image. Any alpha is removed.

    Args:
        surf (Surface): Surface.

    Returns:
        ImageType: PIL Image.
    """
    data = tostring(surf, "RGB")
    image = Image.frombytes("RGB", (surf.get_width(), surf.get_height()), data, "raw")
    return image

def _nameSurfaceToPillow(surf : Surface) -> ImageType:
    """Prepares a nameplate surface for name recognition. The border is cropped out and text is reduced to pixel-thin lines. Output text is white on black.

    Args:
        surf (Surface): Nameplate surface.

    Returns:
        ImageType: PIL ready for processing.
    """
    border = 2
    image = _surfToPillow(surf)
    image = image.crop((border, border, surf.get_width() - border, surf.get_height() - border))
    image = ImageOps.grayscale(image)
    min, max = image.getextrema()
    for x in range(image.width):
        for y in range(image.height):
            if image.getpixel((x,y)) not in [min, max]:
                image.putpixel((x,y), 0)
            elif image.getpixel((x,y)) == min:
                image.putpixel((x,y), 0)
            else:
                image.putpixel((x,y), 255)
    return image

def _filterImage(surf : Surface) -> ImageType:
    """Prepares a surface for OCR. NDS fonts are low resolution which tends to perform poorly with OCR, so images will be scaled. The image will also be inverted so the text is black on white.

    Args:
        surf (Surface): Nameplate surface.

    Returns:
        ImageType: PIL image ready for OCR.
    """
    image = _nameSurfaceToPillow(surf)
    image = ImageOps.scale(image, 2)
    image = ImageOps.invert(image)
    return image

def _buildFontDb(state : Layton2GameState) -> Dict[bytearray, str]:
    output : Dict[bytearray, str] = {}
    for char in sorted(list(state.fontQ.glyphMap.keys()), reverse=True):
        glyph : Glyph = state.fontQ.glyphMap[char]
        
        if glyph.image == None:
            continue

        # HACK - Skip numbers
        if char.isdigit():
            continue

        glyphImage = _surfToPillow(glyph.image)
        glyphImage = glyphImage.crop(glyphImage.getbbox())
        glyphImage = ImageOps.grayscale(glyphImage)
        output[glyphImage.tobytes()] = char
    return output

def _heuristicNameSearch(state : Layton2GameState, image : ImageType, fontDb : Dict[bytearray, str]) -> List[Union[bytearray, str]]:

    # Detect subshapes inside by using X discontinuity
    def getSubCrop(image : ImageType, start : int, end : int):
        
        # TODO - optimize
        def sampleKernel(image : ImageType, center : Tuple[int,int]):
            output = 0
            if image.getpixel(center) != 255:
                return 0
            for y in range(center[1] - 1, center[1] + 2):
                for x in range(center[0] - 1, center[0] + 2):
                    if 0 <= y < image.height:
                        if 0 <= x < image.width:
                            value = image.getpixel((x,y))
                            if value == 255:
                                if x < center[0]:
                                    if output == 1:
                                        return 0
                                    output = -1
                                elif x > center[0]:
                                    if output == -1:
                                        return 0
                                    output = 1
            return output

        crop = image.copy()
        crop = image.crop((start, 0, end, crop.height))
        
        velocities : List[List[int]] = []
        for y in range(crop.height):
            velocities.append([])
            for x in range(crop.width):
                velocities[y].append(0)
        
        if crop.width > 5:
            for y in range(crop.height):
                for x in range(crop.width):
                    velocities[y][x] = sampleKernel(crop, (x,y))
                test = ""
                for val in velocities[y]:
                    test += str(val) + "\t"
        
            lastColumn = [0]
            for x in range(crop.width):
                column = []
                for y in range(crop.height):
                    val = velocities[y][x]
                    column.append(val)
                
                if min(lastColumn) == -1 and max(column) == 1:
                    return start + x

                lastColumn = column
        return end

    image = image.crop((0, 0, image.width, 10))

    def cutShape(image : ImageType, xStart : int) -> Tuple[Optional[ImageType], int, int]:
        startFound = False
        start = xStart
        end = image.width
        for x in range(xStart, image.width):
            lightInRow = False
            for y in range(0, image.height):
                if image.getpixel((x,y)) == 255:
                    lightInRow = True
                    break
            if lightInRow:
                if not(startFound):
                    startFound = True
                    start = x
            else:
                if startFound:
                    end = x
                    break
        
        if startFound:
            end = getSubCrop(image, start, end)
            output = image.crop((start, 0, end, image.height))
        else:
            output = None
        return (output, start, end)

    def recogniseShape(image : ImageType) -> Union[bytearray, str]:
        
        image = image.crop(image.getbbox())
        data = image.tobytes()
        if data in fontDb:
            if fontDb[data] != "":
                return fontDb[data]
        else:
            fontDb[data] = ""
        return data

    output = []
    lastStart = 0
    nextStart = 0
    while True:
        letter, trueStart, nextStart = cutShape(image, nextStart)
        
        if letter == None:
            break
        
        if lastStart != 0:
            if (trueStart - lastStart) > 3:
                output.append(" ")

        output.append(recogniseShape(letter))
        lastStart = nextStart

    return output

class CharacterEntry():
    def __init__(self, index : int, pathImage : str, pathName : Optional[str]):
        self._index : int = index
        self._pathImage = pathImage
        self._pathName : Optional[str] = pathName
    
    def __str__(self):
        return str(self._index) + "\n" + str(self._pathImage) + "\n" + str(self._pathName)
    
    def getPathName(self) -> Optional[str]:
        return self._pathName
    
    def getPathImage(self) -> str:
        return self._pathImage
    
    def getIndex(self) -> int:
        return self._index

def getCharacters(laytonState : Layton2GameState) -> List[CharacterEntry]:
    """Returns a list of all character assets accessible from the ROM.
    Asset order is given by ID ascending. While all characters are accessible from events, not all will be visible from the character bonus screen.

    Args:
        laytonState (Layton2GameState): State for filesystem access.

    Returns:
        List[CharacterEntry]: List of entries with character animation paths.
    """
    output = []
    for charIndex in range(1,256):
        if charIndex == 86 or charIndex == 87:
            pathAsset = PATH_BODY_ROOT_LANG_DEP.replace("?", laytonState.language.value)
        else:
            pathAsset =  PATH_BODY_ROOT
        pathAsset = PATH_ANI % pathAsset
        if laytonState.getFileAccessor().doesFileExist(pathAsset % charIndex):
            if laytonState.getFileAccessor().doesFileExist(PATH_ANI % (PATH_NAME_ROOT % (laytonState.language.value, charIndex))):
                output.append(CharacterEntry(charIndex, pathAsset % charIndex, PATH_ANI % (PATH_NAME_ROOT % (laytonState.language.value, charIndex))))
            else:
                output.append(CharacterEntry(charIndex, pathAsset % charIndex, None))
    return output

def computeCharacterNames(state : Layton2GameState, characterEntries : List[CharacterEntry],
                          funcConfirmPrediction : Optional[Callable[[ImageType, List[ImageType], str], str]] = None,
                          forceOcr : bool = False, ocrLang : str = "eng", maxOcr : int = 3) -> List[Optional[str]]:
    """Derives character names from nameplates using a matching font. Where impossible, OCR will be used to recognise individual characters.

    This operation is expensive - related animations must be loaded and processed. Multiple passes occur with the heuristics.

    If the nameplates aren't designed like the original game, this function may fail. English is supported best - if the results are poor, force OCR instead.

    Args:
        state (Layton2GameState): State used for filesystem and font access.
        characterEntries (List[CharacterEntry]): List of character entries where names will be derived.
        funcConfirmPrediction (Optional[Callable[[ImageType, List[ImageType], str], str]], optional): Function called when the heuristic fails for a character. None disables feedback.
        
        Args: First image is of the character, other images are for uses of the character. The given string is the suggested result.
        Return a single character for the image.
        
        Defaults to None.

        forceOcr (bool, optional): Bypass font-based detection in favor of OCR-only. Slower and less accurate but can predict font-mismatched characters. Defaults to False.
        ocrLang (str, optional): OCR language. Refer to the tesseract documentation. Defaults to "eng".
        maxOcr (int, optional): Performance-related. Controls number of entries per unrecognised character will be sent for OCR. Disabled when OCR is forced. Defaults to 3.

    Returns:
        List[Optional[str]]: List of strings for character names. Where no nameplate is available, None is returned.
    """
     
    def countBad(encoded : List[Union[str, bytearray]]) -> int:
        output = 0
        for val in encoded:
            if type(val) != str:
                output += 1
        return output
    
    def printName(encoded : List[Union[str, bytearray]]) -> str:
        output = ""
        for val in encoded:
            if type(val) == str:
                output += val
            else:
                output += "?"
        return output

    tempCharNames           : Dict[CharacterEntry, List[Union[bytearray, str]]] = {}
    charRepass              : List[CharacterEntry] = []
    missingCharToCharMap    : Dict[bytearray, List[CharacterEntry]] = {}
    fontDb = _buildFontDb(state)

    # TODO - Multithread
    if forceOcr:
        output = []
        for entry in characterEntries:
            if entry.getPathName() != None:
                anim = getBottomScreenAnimFromPath(state, entry.getPathName()[14:])
                if (surf := anim.getActiveFrame()) != None:
                    image = _filterImage(surf)
                    ocrName : str = pytesseract.image_to_string(image, config=("--psm 7 -l " + ocrLang))
                    output.append(ocrName.strip())
                else:
                    output.append(None)
            else:
                output.append(None)
        return output

    # Start with initial heuristic pass - this will reveal most letters. Capture any missing characters
    for entry in characterEntries:
        if entry.getPathName() != None:
            anim = getBottomScreenAnimFromPath(state, entry.getPathName()[14:])
            if (surf := anim.getActiveFrame()) != None:
                image = _nameSurfaceToPillow(surf)
                value = _heuristicNameSearch(state, image, fontDb)
                for item in value:
                    if type(item) != str:
                        charRepass.append(entry)
                        break
                tempCharNames[entry] = value
    
    # Build faster map to map missing characters to related entries
    for char in charRepass:
        value = tempCharNames[char]
        for item in value:
            if type(item) != str:
                if item not in missingCharToCharMap:
                    missingCharToCharMap[item] = []
                if char not in missingCharToCharMap[item]:
                    missingCharToCharMap[item].append(char)

    # Sort the missing character map by the amount of entries
    for item in sorted(list(missingCharToCharMap.keys()), key=lambda x: len(missingCharToCharMap[x]), reverse=True):

        # For each missing character, sort by the words with fewest missing characters
        charsMissing = sorted(missingCharToCharMap[item], key=lambda x: countBad(tempCharNames[x]))

        countConsider = min(maxOcr, len(charsMissing))
        considerReplacement = []
        for idxChar in range(countConsider):
            char = charsMissing[idxChar]

            # TODO - Persist
            anim = getBottomScreenAnimFromPath(state, char.getPathName()[14:])
            surf = anim.getActiveFrame()
            image = _filterImage(surf)

            ocrName : str = pytesseract.image_to_string(image, config="--psm 7 -l eng").strip()
            if len(ocrName) == len(tempCharNames[char]):
                # TODO - Check similarity
                for idxValue, value in enumerate(tempCharNames[char]):
                    if value == item:
                        considerReplacement.append(ocrName[idxValue])
        
        if len(considerReplacement) > 0:
            newValue = mode(considerReplacement)

            # TODO - Reencode image, will need to track or derive dimensions
            #if funcConfirmPrediction != None:
            #    funcConfirmPrediction(Image.frombytes("L", ))

            for char in missingCharToCharMap[item]:
                for idxEncodedVal, encodedVal in enumerate(tempCharNames[char]):
                    if encodedVal == item:
                        tempCharNames[char][idxEncodedVal] = newValue
            del missingCharToCharMap[item]

    output = []
    for char in characterEntries:
        if char in tempCharNames:
            output.append(printName(tempCharNames[char]))
        else:
            output.append(None)
    return output