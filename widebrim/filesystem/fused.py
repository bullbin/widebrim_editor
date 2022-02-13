# TODO - Filesystem for PLZ?
from os.path import splitext
from typing import List, Optional
from ndspy.rom import NintendoDSRom
from widebrim.filesystem.builder import BuildLoadFromSource, GeneralFileBuilder
from widebrim.filesystem.const import EXTENSION_FILE_NEEDS_BUILDING
from widebrim.filesystem.fusedError import FusedPatchFailedToInitialise, FusedPatchFolderNotEmpty, FusedPatchOperationInvalid, FusedPatchOperationInvalidatesFilesystem, FusedPatchRenameOperationExtensionNotPreserved
from widebrim.filesystem.low_level import FilesystemNative, FilesystemNds
from widebrim.filesystem.low_level.fs_template import Filesystem

# TODO - PLZ filtering, directory filtering

class FusedFilesystem(Filesystem):
    def __init__(self, rom : NintendoDSRom, pathFused : str, generateNewFs : bool = True):
        self.__fsRom    = FilesystemNds(rom)
        self.__fsPatch  = FilesystemNative(pathFused)

        if generateNewFs:
            # TODO - Could be dangerous since we're modifying the object we're in
            #        As long as we're only generating ROM copy commands this should be fine
            builder = GeneralFileBuilder(self)
            for filepath in self.__fsRom.getFilepathsInFolder("/"):
                if self.__fsPatch.getFile(filepath) != None:
                    raise FusedPatchFolderNotEmpty()
                else:
                    builder.reset()
                    builder.addCommand(BuildLoadFromSource(filepath))
                    script = builder.getScript()
                    # TODO - Unicode support...?
                    script = script.encode("utf-8")
                    if not(self.__fsPatch.addFile(filepath + EXTENSION_FILE_NEEDS_BUILDING, script)):
                        raise FusedPatchFailedToInitialise()

    def __compileAsset(self, pathAssetRecipe : str) -> bytes:
        assetExtension = splitext(splitext(pathAssetRecipe)[0])[1]
        return b''

    def __resolvePath(self, filepath : str) -> Optional[str]:
        if self.__fsPatch.doesFileExist(filepath):
            return filepath
        if self.__fsPatch.doesFileExist(filepath + EXTENSION_FILE_NEEDS_BUILDING):
            return filepath + EXTENSION_FILE_NEEDS_BUILDING
        return None

    def __checkIfExtensionPreserved(self, filepath1 : str, filepath2 : str) -> bool:
        # TODO - Will error even if file doesn't exist, could be a little annoying
        return splitext(filepath1)[1] == splitext(filepath2)[1]

    def addFile(self, filepath: str, file: bytes, overwriteIfExists: bool = True) -> bool:
        """[summary]

        Args:
            filepath (str): [description]
            file (bytes): [description]
            overwriteIfExists (bool, optional): [description]. Defaults to True.

        Returns:
            bool: [description]
        """
        dupFilepath = self.__resolvePath(filepath)
        if dupFilepath != None:
            if overwriteIfExists:
                if not(self.__fsPatch.removeFile(dupFilepath)):
                    return False
            else:
                return False
        return self.__fsPatch.addFile(filepath, file, overwriteIfExists)
    
    def addFileBuilt(self, filepath : str, file : bytes) -> bool:
        """Add file directly to patch filesystem. Bypasses checks for recipes, etc, so can conflict with internal patching system.
        Use this only to add built assets - there is no reason to use it otherwise. All built assets must be marked with the extension.

        Args:
            filepath (str): [description]
            file (bytes): [description]

        Returns:
            bool: [description]
        """
        if splitext(filepath)[1] != EXTENSION_FILE_NEEDS_BUILDING:
            raise FusedPatchOperationInvalidatesFilesystem("FusedFilesystem.addFileBuilt only supports asset recipes to ensure the filesystem stays valid. Use FusedFilesystem.addFile instead.")
        return self.__fsPatch.addFile(filepath, file, True)

    def addFolder(self, folderPath: str) -> bool:
        return self.__fsPatch.addFolder(folderPath)
    
    def doesFileExist(self, filepath: str) -> bool:
        return self.__resolvePath(filepath) != None
    
    def doesFolderExist(self, folderPath: str) -> bool:
        return self.__fsPatch.doesFolderExist(folderPath)
    
    def getFile(self, filepath: str, forceRom : bool = False) -> Optional[bytes]:
        if forceRom:
            return self.__fsRom.getFile(filepath)
        filepath = self.__resolvePath()
        if splitext(filepath)[1] == EXTENSION_FILE_NEEDS_BUILDING:
            return self.__compileAsset(filepath)
        return self.__fsPatch.getFile(filepath)
    
    def getFilepathsInFolder(self, folderPath: str, sorted=True, hideUncompiled:bool = True) -> List[str]:
        if hideUncompiled:
            return self.__fsPatch.getFilepathsInFolder(folderPath, sorted)
        else:
            output = self.__fsPatch.getFilepathsInFolder(folderPath, sorted)
            for indexPath, filepath in enumerate(output):
                filepathNoExt, extension = splitext(filepath)
                if extension == EXTENSION_FILE_NEEDS_BUILDING:
                    output[indexPath] = filepathNoExt
            return output
    
    def getCountItemsInFolder(self, folderPath: str) -> int:
        return self.__fsPatch.getCountItemsInFolder(folderPath)
    
    def moveFile(self, filepathSource: str, filepathDest: str, overwriteIfExists: bool = True) -> bool:
        if not(self.__checkIfExtensionPreserved(filepathSource, filepathDest)):
            raise FusedPatchRenameOperationExtensionNotPreserved()

        filepathSource = self.__resolvePath(filepathSource)
        extension = splitext(filepathSource)[1]
        if extension == EXTENSION_FILE_NEEDS_BUILDING:
            filepathDest += EXTENSION_FILE_NEEDS_BUILDING
        return self.__fsPatch.moveFile(filepathSource, filepathDest, overwriteIfExists)
    
    def moveFolderContents(self, folderPathSource: str, folderPathDest: str, overwriteIfExists: bool = True) -> bool:
        return self.__fsPatch.moveFolderContents(folderPathSource, folderPathDest, overwriteIfExists)
    
    def removeFile(self, filepath: str) -> bool:
        filepath = self.__resolvePath(filepath)
        if filepath == None:
            return True
        return self.__fsPatch.removeFile(filepath)
    
    def removeFolder(self, folderPath: str, removeIfFull: bool = True) -> bool:
        return self.__fsPatch.removeFolder(folderPath, removeIfFull)
    
    def renameFile(self, filepath: str, filenameRename: str, overwriteIfExists=True) -> bool:
        if not(self.__checkIfExtensionPreserved(filepath, filenameRename)):
            raise FusedPatchRenameOperationExtensionNotPreserved()

        filepath = self.__resolvePath(filepath)
        extension = splitext(filepath)[1]
        if extension == EXTENSION_FILE_NEEDS_BUILDING:
            filenameRename += EXTENSION_FILE_NEEDS_BUILDING
        return self.__fsPatch(filepath, filenameRename, overwriteIfExists)
    
    def renameFolder(self, folderPath: str, folderName: str, mergeIfExists: bool = True) -> bool:
        return self.__fsPatch.renameFolder(folderPath, folderName, mergeIfExists)
    
    def replaceFile(self, filepath: str, file: bytes, createIfNotExists: bool = True) -> bool:
        if splitext(filepath)[1] == EXTENSION_FILE_NEEDS_BUILDING:
            raise FusedPatchOperationInvalid("FusedFilesystem.replaceFile only supports compiled assets to ensure the filesystem stays valid. Use FusedFilesystem.replaceFileBuilt instead.")

        previousFilepath = self.__resolvePath(filepath)
        if previousFilepath != None:
            self.__fsPatch.removeFile(previousFilepath)
        return self.__fsPatch.replaceFile(filepath, file, createIfNotExists)
    
    def replaceFileBuilt(self, filepath: str, file: bytes) -> bool:
        """Replace files within the patch filesystem. Bypasses checks for recipes, etc, so can conflict with internal patching system.
        Use this only to replace asset recipes with other asset recipes. All built assets must be marked with the extension.

        Args:
            filepath (str): [description]
            file (bytes): [description]

        Returns:
            bool: [description]
        """
        if splitext(filepath)[1] != EXTENSION_FILE_NEEDS_BUILDING:
            raise FusedPatchOperationInvalidatesFilesystem("FusedFilesystem.replaceFileBuilt only supports asset recipes to ensure the filesystem stays valid. Use FusedFilesystem.replaceFile instead.")
        return self.__fsPatch.replaceFile(filepath, file, False)