from .nopush_editor import ImportBackground
from wx import FileDialog, FD_OPEN, FD_FILE_MUST_EXIST, ID_CANCEL, BitmapFromBuffer
from widebrim.madhatter.hat_io.asset_image import StaticImage
from PIL import Image, UnidentifiedImageError
from widebrim.madhatter.hat_io.asset import File

class DialogueImportBackground(ImportBackground):
    def __init__(self, parent):
        self.__newImage     = StaticImage()
        self.__previewImage = StaticImage()
        super().__init__(parent)
    
    def bitmapBeforeOnLeftDClick(self, event):
        with FileDialog(self, "Open Image", wildcard="Images (*.jpeg,*.jpg,*.png,*.bmp)|*.jpeg;*.jpg;*.png;*.bmp", style=FD_OPEN|FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() != ID_CANCEL:
                filepath = fileDialog.GetPath()
                try:
                    newImage = Image.open(filepath)
                    self.__newImage.addImage(newImage)
                    for _indexImage in range(self.__newImage.getCountImages() - 1):
                        self.__newImage.removeImage(0)
                except UnidentifiedImageError:
                    pass
        
        self.__updateView()
        return super().bitmapBeforeOnLeftDClick(event)
    
    def __updateView(self):
        if self.__newImage.getCountImages() > 0:
            original = self.__newImage.getImage(0)
            self.__previewImage = StaticImage.fromBytesArc(self.__newImage.toBytesArc()[0])
            tempData = File(name="FML", data=self.__newImage.toBytesArc()[0], extension=".arc")
            tempData.compress(addHeader=True)
            tempData.export("fml.arc")
            quantized = self.__previewImage.getImage(0)
            self.bitmapBefore.SetBitmap(BitmapFromBuffer(original.size[0], original.size[1], original.convert("RGB").tobytes("raw", "RGB")))
            self.bitmapAfter.SetBitmap(BitmapFromBuffer(quantized.size[0], quantized.size[1], quantized.convert("RGB").tobytes("raw", "RGB")))