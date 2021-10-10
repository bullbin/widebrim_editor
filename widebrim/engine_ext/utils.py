from __future__ import annotations
from typing import Callable, Optional, TYPE_CHECKING, Tuple, Union
if TYPE_CHECKING:
    from widebrim.engine.state.state import Layton2GameState
    from PIL.Image import Image as ImageType

from widebrim.engine.anim.button import AnimatedButton, AnimatedClickableButton, StaticButton
from ..madhatter.hat_io.asset_image import StaticImage
from ..engine.const import PATH_BG_ROOT, PATH_ANI, PATH_FACE_ROOT, RESOLUTION_NINTENDO_DS
from ..engine.file import FileInterface
from ..madhatter.hat_io.asset_image import AnimatedImage
from ..madhatter.hat_io.asset import LaytonPack
from ..engine.anim.image_anim import AnimatedImageObject, AnimatedImageObjectWithSubAnimation
from ..engine.const import PATH_PACK_TXT2, PATH_PACK_TXT
from .const import PATH_TEMP

from os import makedirs
from shutil import rmtree

from pygame import image, Surface

def substituteLanguageString(laytonState : Layton2GameState, string : str) -> str:
    """Get substituted strings for a given path. Will substitute language if there is one missing string or a "?" symbol.

    Args:
        laytonState (Layton2GameState): Game state used for language substitution
        string (str): Any path

    Returns:
        str: Path with language substituted or original if substitution not possible
    """
    if "?" in string:
        string = string.replace("?", laytonState.language.value)
    elif string.count("%s") == 1:
        string = string.replace("%s", laytonState.language.value)
    return string

def getFormatString(path : str, extension : str) -> str:
    if len(path) >= len(extension):
        return path[0:- len(extension)] + extension
    return path

def doesAnimExist(laytonState : Layton2GameState, pathAnim : str) -> bool:
    """Check for presence of file with anim extension in animation folder. Will substitute language if there is one missing string or a "?" symbol. Does not guarentee file is of anim type or can be read.

    Args:
        laytonState (Layton2GameState): Game state used for language substitution
        pathAnim (str): Path to animation. Extension included but root anim path excluded

    Returns:
        bool: True if file exists, may not be anim
    """
    if ".spr" in pathAnim:
        pathAnim = getFormatString(pathAnim, "arc")
    elif ".sbj" in pathAnim:
        pathAnim = getFormatString(pathAnim, "arj")
    else: # yes this will maybe cause bugs but the game really doesn't care about last 3 digits
        pathAnim = getFormatString(pathAnim, "arc")
    
    return FileInterface.doesFileExist(substituteLanguageString(laytonState, PATH_ANI % pathAnim))

def doesImageExist(laytonState : Layton2GameState, pathBg : str) -> bool:
    """Check for presence of file with image extension in background folder. Will substitute language if there is one missing string or a "?" symbol. Does not guarentee file is of image type or can be read.

    Args:
        laytonState (Layton2GameState): Game state used for language substitution
        pathBg (str): Path to background. Extension included but root background path excluded

    Returns:
        bool: True if file exists, may not be image
    """
    return FileInterface.doesFileExist(substituteLanguageString(laytonState, PATH_BG_ROOT % getFormatString(pathBg, "arc")))

def getImageFromPath(laytonState : Layton2GameState, pathBg : str) -> Optional[Surface]:
    """Get Surface representing some background image at the given path. Will substitute language if there is one missing string or a "?" symbol.

    Args:
        laytonState (Layton2GameState): Game state used for language substitution
        pathBg (str): Path to background. Extension included but root background path excluded

    Returns:
        Optional[Surface]: Surface if image was readable, else None
    """
    def fetchBgxImage(path) -> Optional[ImageType]:
        # TODO - Fix unwanted behaviour with reading null-terminated strings, where a null character is left at the end
        imageFile = FileInterface.getData(PATH_BG_ROOT % substituteLanguageString(laytonState, getFormatString(path, "arc")))
        if imageFile != None:
            try:
                imageFile = StaticImage.fromBytesArc(imageFile)
                return imageFile.getImage(0)
            except:
                return None
        return imageFile

    if (bg := fetchBgxImage(pathBg)) != None:
        # HACK - Reword transparencies to support colormasking
        output = image.fromstring(bg.convert("RGB").tobytes("raw", "RGB"), bg.size, "RGB").convert()
        if bg.mode == "P":
            output.set_colorkey(bg.getpalette()[0:3])
        return output

def getPackedData(pathPack, nameItem) -> Optional[bytes]:
    pack = LaytonPack()
    pack.load(FileInterface.getData(pathPack))
    return pack.getFile(nameItem)

def getPackedString(pathPack, nameString) -> str:
    # TODO - Maybe decoding using substituter
    tempString = getPackedData(pathPack, nameString)
    try:
        return tempString.decode('shift-jis')
    except:
        return ""

# TODO - Use in above commands
def decodeArchiveString(pack : LaytonPack, nameString) -> Optional[str]:
    if (stringData := pack.getFile(nameString)) != None:
        try:
            return stringData.decode('shift-jis')
        except UnicodeDecodeError:
            return ""
    return None

def getTxtString(laytonState, nameString) -> str:
    return getPackedString(PATH_PACK_TXT % laytonState.language.value, nameString)

def getTxt2String(laytonState, nameString) -> str:
    return getPackedString(PATH_PACK_TXT2 % laytonState.language.value, nameString)

def getButtonFromPath(laytonState : Layton2GameState, inPath : str, callback : Optional[Callable] = None, animOff : str="off", animOn : str="on", pos=(0,0), customDimensions=None, namePosVariable=None) -> Optional[AnimatedButton]:
    """Returns an image-based button from path. Note that by default, this button will be offset onto the bottom screen already. Language strings will be substituted where possible.

    Args:
        laytonState (Layton2GameState): Game state
        inPath (str): Path to image asset, relative from master animation path
        callback (Optional[Callable], optional): Callback when button is pressed. Defaults to None.
        animOff (str, optional): Name of animation when button is idle. Defaults to "off".
        animOn (str, optional): Name of animation when button is targetted. Defaults to "on".
        pos (tuple, optional): Position. Defaults to (0,0) and overriden by variable.
        customDimensions (tuple, optional): Size of interactable area. Defaults to None, which means the maximum dimensions of the animation is used.
        namePosVariable ([type], optional): Name of variable storing position. Defaults to None, 'pos' will be used instead.

    Returns:
        Optional[AnimatedButton]: Image-based button
    """

    if "?" in inPath:
        inPath = inPath.replace("?", laytonState.language.value)
    elif "%s" in inPath:
        inPath = inPath.replace("%s", laytonState.language.value)
    
    if (anim := getAnimFromPathWithAttributes(inPath)) != None:
        anim : AnimatedImageObject
        anim.setPos((pos[0], pos[1] + RESOLUTION_NINTENDO_DS[1]))
        # Verified behaviour
        if namePosVariable == None:
            namePosVariable = "pos"

        if anim.getVariable(namePosVariable) != None:
            anim.setPos((anim.getVariable(namePosVariable)[0],
                         anim.getVariable(namePosVariable)[1] + RESOLUTION_NINTENDO_DS[1]))
        
        if customDimensions != None:
            anim.setDimensions(customDimensions)

        return AnimatedButton(anim, animOn, animOff, callback=callback)
    return None

def getStaticButtonFromAnim(anim : Optional[AnimatedImage], spawnAnimName : str, callback : Optional[Callable] = None, pos=(0,0), namePosVariable=None, clickOffset=(0,0)) -> Optional[StaticButton]:
    if anim != None:
        anim : AnimatedImageObject
        anim.setPos((pos[0], pos[1] + RESOLUTION_NINTENDO_DS[1]))
        if namePosVariable == None:
            namePosVariable = "pos"

        if anim.getVariable(namePosVariable) != None:
            anim.setPos((anim.getVariable(namePosVariable)[0],
                         anim.getVariable(namePosVariable)[1] + RESOLUTION_NINTENDO_DS[1]))
        
        if anim.setAnimationFromName(spawnAnimName):
            return StaticButton(anim.getPos(), anim.getActiveFrame(), callback=callback, targettedOffset=clickOffset)
    return None

def getStaticButtonFromPath(laytonState : Layton2GameState, inPath : str, spawnAnimName : str, callback : Optional[Callable] = None, pos=(0,0), namePosVariable=None, clickOffset=(0,0)) -> Optional[StaticButton]:
    """Returns a surface-based button from path. Note that by default, this button will be offset onto the bottom screen already.

    Args:
        laytonState (Layton2GameState): Game state
        inPath (str): Path to image asset, relative from master animation path
        spawnAnimName (str): Name of animation
        callback (Optional[Callable], optional): Callback when button is pressed. Defaults to None.
        pos (tuple, optional): Position. Defaults to (0,0) and overriden by variable.
        namePosVariable ([type], optional): Name of variable storing position. Defaults to None, 'pos' will be used instead.
        clickOffset (tuple, optional): Position offset when button is targetted. Defaults to (0,0).

    Returns:
        Optional[StaticButton]: Surface-based button
    """

    # TODO - Replace calls to static button to this constructor instead
    if (button := getButtonFromPath(laytonState, inPath, callback=callback, animOff=spawnAnimName, animOn=spawnAnimName, pos=pos, namePosVariable=namePosVariable)) != None:
        if button.image.getActiveFrame() != None:
            return StaticButton(button.image.getPos(), button.image.getActiveFrame(), callback=callback, targettedOffset=clickOffset)
    return None

def getClickableButtonFromPath(laytonState : Layton2GameState, inPath : str, callback : Optional[Callable], animOff : str = "off", animOn : str = "on", animClick : str = "click", pos=(0,0), customDimensions=None, namePosVariable=None, unclickOnCallback=True) -> Optional[AnimatedClickableButton]:
    button = getButtonFromPath(laytonState, inPath, callback, animOff, animOn, pos, customDimensions, namePosVariable)
    if button != None:
        button = button.asClickable(animClick, unclickOnCallback)
    return button

# TODO - Swith anim name to anim index, more accurate and faster (index 1 will be target in 99% of cases)
def getAnimFromPath(inPath, spawnAnimName=None, pos=(0,0), enableSubAnimation=False) -> Optional[Union[AnimatedImageObject, AnimatedImageObjectWithSubAnimation]]:

    def functionGetAnimationFromName(name):
        name = name.split(".")[0] + ".arc"
        resolvedPath = PATH_FACE_ROOT % name
        return FileInterface.getData(resolvedPath)

    if ".spr" in inPath:
        inPath = inPath.split(".spr")[0] + ".arc"
    elif ".sbj" in inPath:
        inPath = inPath.split(".sbj")[0] + ".arj"
    
    if (tempAsset := FileInterface.getData(PATH_ANI % inPath)) != None:
        if ".arj" in inPath:
            tempImage = AnimatedImage.fromBytesArj(tempAsset, functionGetFileByName=functionGetAnimationFromName)
        else:
            tempImage = AnimatedImage.fromBytesArc(tempAsset, functionGetFileByName=functionGetAnimationFromName)

        if enableSubAnimation:
            tempImage = AnimatedImageObjectWithSubAnimation.fromMadhatter(tempImage)
        else:
            tempImage = AnimatedImageObject.fromMadhatter(tempImage)
        tempImage.setPos(pos)
        if type(spawnAnimName) == str:
            tempImage.setAnimationFromName(spawnAnimName)
        return tempImage
    return tempAsset

# TODO - This is the more accurate function... by default, game will use position given by value. If that is 0,0, it will use the pos variable
def getAnimFromPathWithAttributes(inPath, spawnAnimName="gfx", posVariable="pos", enableSubAnimation=False) -> Optional[Union[AnimatedImageObject, AnimatedImageObjectWithSubAnimation]]:
    tempImage = getAnimFromPath(inPath, spawnAnimName=spawnAnimName, enableSubAnimation=enableSubAnimation)
    if tempImage != None:
        if tempImage.getVariable(posVariable) != None:
            tempImage.setPos((tempImage.getVariable(posVariable)[0],
                            tempImage.getVariable(posVariable)[1] + RESOLUTION_NINTENDO_DS[1]))
        else:
            tempImage.setPos((0, RESOLUTION_NINTENDO_DS[1]))
    return tempImage

# TODO - Remove this HACK (and use it wherever possible)
def offsetVectorToSecondScreen(inPos : Tuple[int,int]):
    return (inPos[0], inPos[1] + RESOLUTION_NINTENDO_DS[1])

def ensureTempFolder():
    try:
        makedirs(PATH_TEMP, exist_ok=True)
    except OSError:
        return False
    return True

def cleanTempFolder():
    try:
        rmtree(PATH_TEMP)
    except:
        return False
    return True