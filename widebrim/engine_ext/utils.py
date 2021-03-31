from ..madhatter.hat_io.asset_image import StaticImage
from ..engine.const import PATH_BG_ROOT, PATH_ANI, RESOLUTION_NINTENDO_DS
from ..engine.file import FileInterface
from ..madhatter.hat_io.asset_image import AnimatedImage
from ..madhatter.hat_io.asset import LaytonPack
from ..engine.anim.image_anim import AnimatedImageObject
from ..engine.const import PATH_PACK_TXT2, PATH_PACK_TXT
from typing import Optional
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

def getPackedString(pathPack, nameString) -> str:
    # TODO - Maybe decoding using substiter
    # TODO - sp... substituter
    textPack = LaytonPack()
    textPack.load(FileInterface.getData(pathPack))
    tempString = textPack.getFile(nameString)
    try:
        return tempString.decode('shift-jis')
    except:
        return ""

def getTxtString(laytonState, nameString) -> str:
    return getPackedString(PATH_PACK_TXT % laytonState.language.value, nameString)

def getTxt2String(laytonState, nameString) -> str:
    return getPackedString(PATH_PACK_TXT2 % laytonState.language.value, nameString)

def getAnimFromPath(inPath, spawnAnimName=None, pos=(0,0)) -> Optional[AnimatedImageObject]:
    if ".spr" in inPath:
        inPath = inPath.split(".spr")[0] + ".arc"
    elif ".sbj" in inPath:
        inPath = inPath.split(".sbj")[0] + ".arj"
    
    if (tempAsset := FileInterface.getData(PATH_ANI % inPath)) != None:
        if ".arj" in inPath:
            tempImage = AnimatedImage.fromBytesArj(tempAsset)
        else:
            tempImage = AnimatedImage.fromBytesArc(tempAsset)

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