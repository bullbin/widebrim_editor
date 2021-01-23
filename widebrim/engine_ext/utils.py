from ..madhatter.hat_io.asset_image import StaticImage
from ..engine.const import PATH_BG_ROOT, PATH_ANI, RESOLUTION_NINTENDO_DS
from ..engine.file import FileInterface
from ..madhatter.hat_io.asset_image import AnimatedImage
from ..madhatter.hat_io.asset import LaytonPack
from ..engine.anim.image_anim import AnimatedImageObject
from ..engine.const import PATH_PACK_TXT2, PATH_PACK_TXT
from pygame import image

def getImageFromPath(laytonState, pathBg):

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

def getPackedString(pathPack, nameString):
    # TODO - Maybe decoding using substiter
    # TODO - sp... substituter
    textPack = LaytonPack()
    textPack.load(FileInterface.getData(pathPack))
    tempString = textPack.getFile(nameString)
    try:
        return tempString.decode('shift-jis')
    except:
        return ""

def getTxtString(laytonState, nameString):
    return getPackedString(PATH_PACK_TXT % laytonState.language.value, nameString)

def getTxt2String(laytonState, nameString):
    return getPackedString(PATH_PACK_TXT2 % laytonState.language.value, nameString)

def getAnimFromPath(inPath):
    if ".spr" in inPath:
        inPath = inPath.split("spr")[0] + "arc"
    tempAsset = FileInterface.getData(PATH_ANI % inPath)
    if tempAsset != None:
        tempImage = AnimatedImageObject.fromMadhatter(AnimatedImage.fromBytesArc(tempAsset))
        return tempImage
    return tempAsset

def getAnimFromPathWithAttributes(inPath, spawnAnimName="gfx", posVariable="pos"):
    tempImage = getAnimFromPath(inPath)
    tempImage.setAnimationFromName(spawnAnimName)
    if tempImage.getVariable(posVariable) != None:
        tempImage.setPos((tempImage.getVariable(posVariable)[0],
                          tempImage.getVariable(posVariable)[1] + RESOLUTION_NINTENDO_DS[1]))
    else:
        tempImage.setPos((0, RESOLUTION_NINTENDO_DS[1]))
    return tempImage