from typing import Optional, Tuple
from editor.generateFsTree import FolderTreeNode, generateFolderStructureFromRelativeRoot, populateTreeCtrlFromFolderTree
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.filesystem.compatibility import FusedFileInterface
from widebrim.madhatter.hat_io.asset import File
from .nopush_editor import PickerBgx
from widebrim.madhatter.hat_io.asset_image import StaticImage
from wx import TextEntryDialog, MessageDialog, ID_OK, FileDialog, FD_OPEN, FD_FILE_MUST_EXIST, ID_OK, ID_CANCEL, Bitmap
from PIL import Image as PilImage
from PIL.Image import Image as ImageType

# TODO - Image crop, resizing popup
# TODO - Slow to import big images, don't let the user do that

class DialogPickerBgx(PickerBgx):
    def __init__(self, parent, state : Layton2GameState, fusedFi : FusedFileInterface, pathRoot : str):
        super().__init__(parent)
        self.fusedFi = fusedFi
        self.__rootFolder, self.__folderLookup = generateFolderStructureFromRelativeRoot(fusedFi.fused, pathRoot)
        self.__pathOut = ""
        self.btnConfirmSelected.Disable()
        populateTreeCtrlFromFolderTree(self.treeFilesystem, self.__rootFolder)
    
    def __getSelectedFolder(self) -> str:
        selected = self.treeFilesystem.GetSelection()
        if not(selected.IsOk()):
            selected = self.__rootFolder.treeRef

        path = self.treeFilesystem.GetItemData(selected)
        if path not in self.__folderLookup:
            path = "/".join(path.split("/")[:-1])
        return path

    def __isInputGood(self, value) -> Tuple[bool, str]:
        try:
            value.encode("ascii")
        except UnicodeEncodeError:
            return (False, "Non-ascii characters are not permitted.")
        if "/" in value or "\\" in value:
            return (False, "Slashes are not permitted.")
        if len(value) == 0:
            return (False, "Value may not be empty.")
        if "?" in value or "*" in value or "&" in value:
            return (False, "Value may not contain special characters (?, *, &)")
        return (True, "")

    # Naming convention to match wx...
    def GetPath(self) -> str:
        languageString = "/%s/" % self.fusedFi.getLanguage().value
        if self.__pathOut.count(languageString) == 1:
            return self.__pathOut.replace(languageString, "/?/")
        return self.__pathOut

    def __doOnSuccessfulImage(self):
        self.EndModal(ID_OK)

    def treeFilesystemOnTreeItemActivated(self, event):
        selected = self.treeFilesystem.GetSelection()
        path = self.treeFilesystem.GetItemData(selected)
        if path in self.__folderLookup:
            return super().treeFilesystemOnTreeItemActivated(event)
        
        decompFile = File(data=self.fusedFi.getData(path))
        decompFile.decompress()
        previewImage = StaticImage.fromBytesArc(decompFile.data)
        if previewImage.getCountImages() != 1:
            return super().treeFilesystemOnTreeItemActivated(event)
        
        pillowImage = previewImage.getImage(0)
        pillowImage : ImageType
        self.bitmapPreviewBackground.SetBitmap(Bitmap.FromBuffer(pillowImage.size[0], pillowImage.size[1], pillowImage.convert("RGB").tobytes("raw", "RGB")))
        self.__pathOut = path
        self.btnConfirmSelected.Enable()
        return super().treeFilesystemOnTreeItemActivated(event)

    def btnConfirmSelectedOnButtonClick(self, event):
        if self.__pathOut != "":
            self.__doOnSuccessfulImage()
        return super().btnConfirmSelectedOnButtonClick(event)

    def btnImportImageOnButtonClick(self, event):       

        def getConvertableImage() -> Optional[ImageType]:
            """Grabs a functional image using a FileDialog.

            Returns:
                Optional[PIL.Image.Image]: Image if file was opened, None if operation cancelled.
            """
            doImport = True
            newImage : Optional[ImageType] = None
            while doImport:
                fileImportDialog = FileDialog(self, "Select a Background Image", style=FD_OPEN | FD_FILE_MUST_EXIST, wildcard="Images (*.bmp;*.png;*.jpg;*.jpeg)|*.bmp;*.png;*.jpg;*.jpeg")
                if fileImportDialog.ShowModal() == ID_OK:
                    try:
                        newImage = PilImage.open(fileImportDialog.GetPath())
                        doImport = False
                    except OSError:
                        MessageDialog(self, "Failed to open image file. Is this a valid image?", "Invalid Image").ShowModal()
                else:
                    doImport = False
            
            return newImage

        def getFilepath(rootPath : str) -> Optional[str]:

            def forceExtension(value : str) -> str:
                if len(value) > 4:
                    if value[-4:] == ".arc":
                        return value
                return value + ".arc"

            inputFilepath = "MyImage"
            doImport = True
            cancelString = False
            while doImport:
                textEntryDialog = TextEntryDialog(self, "Name your imported image.\n- The name can't be empty\n- The name can't contain slashes\n- The name must be in ASCII\n- The name can't refer to an existing file",
                                                "Enter an Image Name")
                textEntryDialog.SetValue(inputFilepath)
                if textEntryDialog.ShowModal() == ID_OK:
                    inputFilepath = textEntryDialog.GetValue()
                    isGood, errorMsg = self.__isInputGood(inputFilepath)
                    if not(isGood):
                        MessageDialog(self, errorMsg, "Invalid Name").ShowModal()
                    else:
                        testPath = rootPath + "/" + forceExtension(inputFilepath)
                        if self.fusedFi.doesFileExist(testPath):
                            MessageDialog(self, "Name refers to an existing file.", "Invalid Name").ShowModal()
                        else:
                            doImport = False
                else:
                    doImport = False
                    cancelString = True
            
            if cancelString:
                return None
            return rootPath + "/" + forceExtension(inputFilepath)

        image = getConvertableImage()
        if image == None:
            return super().btnImportImageOnButtonClick(event)
        
        path = self.__getSelectedFolder()
        folder = self.__folderLookup[path]
        filepath = getFilepath(path)
        if filepath == None:
            return super().btnImportImageOnButtonClick(event)

        packer = StaticImage()
        packer.addImage(image)
        packer = packer.toBytesArc()
        if len(packer) == 0 or len(packer) > 1:
            MessageDialog(self, "The image could not be converted successfully.", "Image Encoding Error").ShowModal()
            return super().btnImportImageOnButtonClick(event)
        packer = File(data=packer[0])
        packer.compress(addHeader=True)

        self.fusedFi.fused.addFile(filepath, packer.data)
        folder.files.append(filepath)
        self.__doOnSuccessfulImage()
        return super().btnImportImageOnButtonClick(event)

    def btnDeleteFolderOnButtonClick(self, event):
        path = self.__getSelectedFolder()
        
        if path == self.__rootFolder.path:
            MessageDialog(self, "The root folder cannot be deleted.", "Important Folder").ShowModal()
            return super().btnDeleteFolderOnButtonClick(event)

        if self.fusedFi.fused.getCountItemsInFolder(path) > 0:
            MessageDialog(self, "Deleting this folder may be harmful. To delete non-empty folders, use the Asset Management page.", "Folder not Empty").ShowModal()
            return super().btnDeleteFolderOnButtonClick(event)
        
        folder = self.__folderLookup[path]
        parentFolder = self.__folderLookup["/".join(path.split("/")[:-1])]
        parentFolder.folders.remove(folder)
    
        # Avoid doing an update, it's expensive
        self.treeFilesystem.DeleteChildren(folder.treeRef)
        self.treeFilesystem.Delete(folder.treeRef)
        folder.clearTreeReferencesForGc()
        self.fusedFi.fused.removeFolder(path)
        return super().btnDeleteFolderOnButtonClick(event)

    def btnAddFolderOnButtonClick(self, event):
        
        path = self.__getSelectedFolder()
        folder = self.__folderLookup[path]
        
        inputFilepath = "New Folder"
        doImport = True
        cancelString = False
        while doImport:
            textEntryDialog = TextEntryDialog(self, "Name your new folder\n- The name can't be empty\n- The name can't contain slashes\n- The name must be in ASCII\n- The name can't refer to an existing folder",
                                              "Enter a Folder Name")
            textEntryDialog.SetValue(inputFilepath)
            if textEntryDialog.ShowModal() == ID_OK:
                inputFilepath = textEntryDialog.GetValue()
                isGood, errorMsg = self.__isInputGood(inputFilepath)
                if not(isGood):
                    MessageDialog(self, errorMsg, "Invalid Name").ShowModal()
                else:
                    testPath = path + "/" + inputFilepath
                    if testPath in self.__folderLookup:
                        MessageDialog(self, "Name refers to an existing folder.", "Invalid Name").ShowModal()
                    else:
                        doImport = False
            else:
                doImport = False
                cancelString = True
        
        if not(cancelString):
            
            folderPath = path + "/" + inputFilepath
            newFolder = FolderTreeNode(folderPath)
            self.__folderLookup[folderPath] = newFolder

            if len(folder.folders) > 0:
                lastFolder = folder.folders[-1]
                newTreeRef = self.treeFilesystem.InsertItem(folder.treeRef, lastFolder.treeRef, inputFilepath, data=folderPath)
            else:
                if self.treeFilesystem.ItemHasChildren(folder.treeRef):
                    newTreeRef = self.treeFilesystem.PrependItem(folder.treeRef, inputFilepath, data=folderPath)
                else:
                    newTreeRef = self.treeFilesystem.AppendItem(folder.treeRef, inputFilepath, data=folderPath)
            newFolder.treeRef = newTreeRef

            folder.folders.append(newFolder)
            self.treeFilesystem.Refresh()
            # populateTreeCtrlFromFolderTree(self.treeFilesystem, self.__rootFolder)

        return super().btnAddFolderOnButtonClick(event)
