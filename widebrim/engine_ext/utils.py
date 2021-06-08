from __future__ import annotations
from typing import Callable, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from widebrim.engine.state.state import Layton2GameState

from widebrim.engine.anim.button import AnimatedButton, StaticButton
from ..madhatter.hat_io.asset_image import StaticImage
from ..engine.const import PATH_BG_ROOT, PATH_ANI, PATH_FACE_ROOT, RESOLUTION_NINTENDO_DS
from ..engine.file import FileInterface
from ..madhatter.hat_io.asset_image import AnimatedImage
from ..madhatter.hat_io.asset import LaytonPack
from ..engine.anim.image_anim import AnimatedImageObject
from ..engine.const import PATH_PACK_TXT2, PATH_PACK_TXT

from pygame import image, Surface

def getImageFromPath(laytonState, pathBg) -> Optional[Surface]:

    def fetchBgxImage(path):
        # TODO - Fix unwanted behaviour with reading null-terminated strings, where a null character is left at the end
        if "bgx" in path:
            tempPath = path.split(".")
            path = ".".join(tempPath[:-1]) + ".arc"

        imageFile = FileInterface.getData(PATH_BG_ROOT % path)
        if imageFile != None:
            try:
                imageFile = StaticImage.fromBytesArc(imageFile)
                return imageFile.getImage(0)
            except:
                return None
        return imageFile

    if type(pathBg) == str:
        if "?" not in pathBg:
            langPath = pathBg.split("/")
            langPath.insert(-1, laytonState.language.value)
            langPath = '/'.join(langPath)
        else:
            langPath = pathBg.replace("?", laytonState.language.value)

        bg = fetchBgxImage(langPath)
        if bg == None:
            bg = fetchBgxImage(pathBg)
        
        if bg != None:
            return image.fromstring(bg.convert("RGB").tobytes("raw", "RGB"), bg.size, "RGB").convert()
    return None

def getPackedData(pathPack, nameItem) -> Optional[bytes]:
    pack = LaytonPack()
    pack.load(FileInterface.getData(pathPack))
    return pack.getFile(nameItem)

def getPackedString(pathPack, nameString) -> str:
    # TODO - Maybe decoding using substiter
    # TODO - sp... substituter
    tempString = getPackedData(pathPack, nameString)
    try:
        return tempString.decode('shift-jis')
    except:
        return ""

def getTxtString(laytonState, nameString) -> str:
    return getPackedString(PATH_PACK_TXT % laytonState.language.value, nameString)

def getTxt2String(laytonState, nameString) -> str:
    return getPackedString(PATH_PACK_TXT2 % laytonState.language.value, nameString)

def getButtonFromPath(laytonState : Layton2GameState, inPath : str, callback : Optional[Callable] = None, animOff : str="off", animOn : str="on", pos=(0,0), namePosVariable=None) -> Optional[AnimatedButton]:
    """Returns an image-based button from path. Note that by default, this button will be offset onto the bottom screen already.

    Args:
        laytonState (Layton2GameState): Game state
        inPath (str): Path to image asset, relative from master animation path
        callback (Optional[Callable], optional): Callback when button is pressed. Defaults to None.
        animOff (str, optional): Name of animation when button is idle. Defaults to "off".
        animOn (str, optional): Name of animation when button is targetted. Defaults to "on".
        pos (tuple, optional): Position. Defaults to (0,0) and overriden by variable.
        namePosVariable ([type], optional): Name of variable storing position. Defaults to None, 'pos' will be used instead.

    Returns:
        Optional[AnimatedButton]: Image-based button
    """

    # TODO - Support click image
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

def getAnimFromPath(inPath, spawnAnimName=None, pos=(0,0)) -> Optional[AnimatedImageObject]:

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

        tempImage = AnimatedImageObject.fromMadhatter(tempImage)
        tempImage.setPos(pos)
        if type(spawnAnimName) == str:
            tempImage.setAnimationFromName(spawnAnimName)
        return tempImage
    return tempAsset

def getAnimFromPathWithAttributes(inPath, spawnAnimName="gfx", posVariable="pos") -> Optional[AnimatedImageObject]:
    tempImage = getAnimFromPath(inPath, spawnAnimName=spawnAnimName)
    if tempImage != None:
        if tempImage.getVariable(posVariable) != None:
            tempImage.setPos((tempImage.getVariable(posVariable)[0],
                            tempImage.getVariable(posVariable)[1] + RESOLUTION_NINTENDO_DS[1]))
        else:
            tempImage.setPos((0, RESOLUTION_NINTENDO_DS[1]))
    return tempImage