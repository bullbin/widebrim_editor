from ..madhatter.hat_io.asset_image import StaticImage
from ..engine.const import PATH_BG_ROOT
from ..engine.file import FileInterface
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

    if "?" not in pathBg:
        langPath = pathBg.split("/")
        langPath.insert(-1, laytonState.language.value)
        langPath = '/'.join(langPath)
    else:
        langPath = pathBg.replace("?", laytonState.language.value)

    bg = fetchBgxImage(langPath)
    if bg == None:
        bg = fetchBgxImage(pathBg)
    
    if bg == None:
        return bg
    return image.fromstring(bg.convert("RGB").tobytes("raw", "RGB"), bg.size, "RGB").convert()