from typing import Optional, Tuple
from PIL.Image import Image as ImageType
from PIL import Image
from wx import Bitmap, ImageList
from widebrim.engine.const import PATH_ANI
from filesystem.compatibility.compatibilityBase import ReadOnlyFileInterface
from widebrim.madhatter.hat_io.asset_image.image import AnimatedImage, getTransparentLaytonPaletted

def pillowToWx(image : ImageType, resize : Optional[Tuple[int,int]] = None) -> Bitmap:
    if resize != None:
        image = image.resize(resize)
    
    output = Bitmap.FromBufferRGBA(image.width, image.height, image.tobytes())
    return output

def getFrameOfImage(filesystem : ReadOnlyFileInterface, aniPath : str, frameIndex=0) -> Optional[ImageType]:
    if (data := filesystem.getData(PATH_ANI % aniPath)) != None:
        if len(aniPath) > 3:
            if aniPath[-3:] == "arc":
                image = AnimatedImage.fromBytesArc(data)
            else:
                image = AnimatedImage.fromBytesArj(data)

            if image != None and len(image.frames) > frameIndex and frameIndex >= 0:
                image = image.frames[frameIndex].getComposedFrame()
                if image.mode != "RGBA":
                    image = getTransparentLaytonPaletted(image)
                    if image.width != image.height:
                        dim = max(image.width, image.height)
                        output = Image.new("RGBA", (dim,dim))
                        marginLeft = (dim - image.width) // 2
                        marginUp = (dim - image.height) // 2
                        output.paste(image, (marginLeft, marginUp))
                        image = output
                return image
    return None

def getThumbnailImage(filesystem : ReadOnlyFileInterface, aniPath : str, resize=(16,16), forceImageIndex=0) -> Optional[Bitmap]:
    image = getFrameOfImage(filesystem, aniPath, frameIndex=forceImageIndex)
    if image != None:
        image = pillowToWx(image, resize=resize)
        return image
    return None

def getImageAndSetVariable(filesystem : ReadOnlyFileInterface, aniPath : str, iconDest : ImageList, resize=(16,16), forceImageIndex=0) -> int:
    image = getThumbnailImage(filesystem, aniPath, resize, forceImageIndex)
    if image != None:
        iconDest.Add(image)
        return iconDest.GetImageCount() - 1
    return -1