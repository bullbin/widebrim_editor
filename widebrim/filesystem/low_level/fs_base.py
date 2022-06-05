from typing import List, Optional, Tuple
from os.path import relpath, join, split

from widebrim.filesystem.low_level.fs_template import Filesystem

# TODO - Method for copy
# TODO - Unify delimiter (forward slash and backslash) to fix trailing join, etc

class FilesystemBase(Filesystem):
    """Class for lowest level abstraction of filesystem access.
    """
    def __init__(self) -> None:
        super().__init__()
        self._wasModified = False

    # These methods are needed to get the filesystem functional
    def _requiredGetFile(self, filepath : str) -> Optional[bytes]:
        """Reimplement this in your filesystem. This is expected to run on any path and return the file data if it exists.

        NOTE: The default implementation of _doesFileExist calls this method indirectly. Be careful using _doesFileExist here as it may lead to an infinite loop.
        If _doesFileExist is no longer dependent on this method then _getFile will only be ran on valid paths which could be faster.

        Args:
            filepath (str): Filepath with extension.

        Returns:
            Optional[bytes]: None if the file doesn't exist, bytes otherwise.
        """
        return None

    def _requiredDoesFolderExist(self, folderPath : str) -> bool:
        """Reimplement this in your filesystem. This is expected to run on any path but only return True if the folder path is valid and accessible.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            bool: True if the folder exists and is accessible.
        """
        return False

    def _requiredAddNewFileToExistentFolder(self, filepath : str, file : bytes) -> bool:
        """Reimplement this in your filesystem. This method may be called on any filepath that locates to an existing folder.
        This is expected to perform simple file addition to a known good folder path.

        Args:
            filepath (str): Folder path without any extension.
            file (bytes): File contents as raw data.

        Returns:
            bool: True if the file addition operation was successful.
        """
        return False
    
    def _requiredRemoveExistentFile(self, filepath : str) -> bool:
        """Reimplement this in your filesystem. This method may be called on any existent filepath.
        This is expected to fully remove a file from the filesystem such that it will not be detectable by any other public methods.

        Args:
            filepath (str): Folder path without any extension.

        Returns:
            bool: True if the file removal operation was successful.
        """
        return False

    def _requiredAddNewFolderNested(self, folderPath : str) -> bool:
        """Reimplement this in your filesystem. This method may be called on any non-existent folder path.
        This is expected to handle both nested and simple folder addition.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            bool: True if the folder was added successfully. False may leave fragments of the operation.
        """
        return False

    def _requiredRemoveFolderNested(self, folderPath : str) -> bool:
        """Reimplement this in your filesystem. This method may be called on any existed folder path.
        This is expected to handle both nested and simple folder removal, as well as deletion of any contents.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            bool: True if the folder was removed successfully. False may leave fragments of the operation.
        """
        return False
    
    def _requiredGetFilepathsInFolder(self, folderPath : str) -> List[str]:
        """Reimplement this in your filesystem. This method may be called on any existent folder path.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            List[str]: List of absolute (to filesystem) paths for any files inside the folder, including nested directories. Empty if folder has no contents.
        """
        return []
    


    # May need to be changed depending on the pathing behaviour of your filesystem
    def _sensitiveFsSplit(self, filepath : str) -> Tuple[str, str]:
        """May need to be reimplemented in your filesystem. Should take a filename and split it into (folderPath, filename) on output

        Args:
            filepath (str): Filepath with extension.

        Returns:
            Tuple[str, str]: Folder path followed by filename.
        """
        return split(filepath)
    
    def _sensitiveFsRelpath(self, filepath : str, folderPath : str) -> str:
        """May need to be reimplemented in your filesystem. Should take a filepath and folder path and return the relative path from the folder to reach that file.

        Args:
            filepath (str): Filepath with extension.
            folderPath (str): Folder path without any extension.

        Returns:
            str: Path from folder to file (including filename).
        """
        # TODO - Bugs will happen if . is returned
        return relpath(filepath, folderPath)
    
    def _sensitiveFsJoin(self, x : str, y : str) -> str:
        """May need to be reimplemented in your filesystem. Should take two paths and join them by the filesystem's native slash character.

        Args:
            x (str): Path 1.
            y (str): Path 2.

        Returns:
            str: Path 1 joined by path 2.
        """
        return join(x,y)



    # Can be reimplemented, but these methods should already provide functionality for the filesystem as long as the above is functional
    def _addNewFile(self, filepath : str, file : bytes) -> bool:
        """Internal method for adding a new file to the filesystem.
        Basic implementation handles folder creation, only override if needed.

        Args:
            filepath (str): Full filepath ending with extension.
            file (bytes): File contents as raw data.

        Returns:
            bool: True if the file was added successfully.
        """
        folderPath, filename = self._sensitiveFsSplit(filepath)
        if not(self.doesFolderExist(folderPath)):
            if not(self.addFolder(folderPath)):
                return False
        return self._requiredAddNewFileToExistentFolder(filepath, file)

    def _renameFile(self, filepathOld : str, filepathNew : str, overwriteIfExists : bool) -> bool:
        """Internal method for renaming an existing file within the filesystem.
        Basic implementation will perform a full copy of the original file. Override if there is a method which can directly modify the name of the source file.

        Args:
            filepathOld (str): Original filepath with extension.
            filepathNew (str): New filepath with extension.
            overwriteIfExists (bool): True to overwrite if data at the new path already exists.

        Returns:
            bool: True if the full renaming operation was completed. False may leave fragments of the operation.
        """
        if not(self.addFile(filepathNew, self.getFile(filepathOld), overwriteIfExists)):
            return False
        return self.removeFile(filepathOld)

    def _replaceExistentFile(self, filepath : str, file : bytes) -> bool:
        """Internal method for replacing existent files within the filesystem.
        Basic implementation will remove the file and re-add it. This may be sufficient but could mess with filesystems that enforce ordering to their structures.
        Override this if you have means to directly interface with the file contents instead.

        Args:
            filepath (str): Full filepath ending with extension.
            file (bytes): File contents as raw data.

        Returns:
            bool: True if the file was replaced successfully. False may leave fragments of the operation.
        """

        if self.removeFile(filepath):
            if self.addFile(filepath, file):
                return True
        return False

    def _moveExistentFile(self, filepathSource : str, filepathDest : str, overwriteIfExists : bool) -> bool:
        """Internal method from moving data at a valid filepath to another filepath.
        Basic implementation already uses internal methods, only override if needed.

        Args:
            filepathSource (str): Full source filepath ending with extension.
            filepathDest (str): Full destination filepath ending with extension.
            overwriteIfExists (bool): True to overwrite data if the destination filepath already exists.

        Returns:
            bool: True if the move operation was successful. False may leave fragments of the operation.
        """

        fileContents = self.getFile(filepathSource)

        if fileContents == None:
            return False

        if self.doesFileExist(filepathDest):
            if not(overwriteIfExists):
                return False
            if not(self.removeFile(filepathDest)):
                return False

        return self.removeFile(filepathSource) and self.addFile(filepathDest, fileContents)

    def _doesFileExist(self, filepath : str) -> bool:
        """Internal method called to check if there exists data for some path.
        Basic implementation requests data to check if it exists. Override this if there is a less demanding strategy.

        Args:
            filepath (str): Full filepath ending with extension.

        Returns:
            bool: True if there is data at the filepath.
        """
        return self.getFile(filepath) != None

    def _renameFolder(self, folderPathOld : str, folderPathNew : str) -> bool:
        """Internal method to rename a folder. This will only be called if both the source and destination folders exist.
        Basic implementation will perform a full copy to a new folder.
        Override this if there's a direct or cheaper way to modify folder names.

        Args:
            folderPathOld (str): Full source folder path.
            folderPathNew (str): Full destination folder path.

        Returns:
            bool: True if rename operation was successful. False may leave fragments of the operation.
        """
        if not(self.moveFolderContents(folderPathOld, folderPathNew)):
            return False
        return self.removeFolder(folderPathOld)

    def _moveFolderContents(self, folderPathSource : str, folderPathDest : str, overwriteIfExists : bool = True) -> bool:
        """Internal method called to move one folder's contents from one destination to another. This will only be called if a folder exists at both the source and destination paths.
        Basic implementation calls upon other external methods to create new folders and move files individually.
        Override this if there is a less demanding strategy, e.g. shifting pointers instead of copying data.

        Args:
            folderPathSource (str): Full source folder path.
            folderPathDest (str): Full destination folder path.
            overwriteIfExists (bool, optional): True to overwrite if the destination already has data. Defaults to True.

        Returns:
            bool: True if movement operation was successful or there was nothing to move. False may leave fragments of the operation.
        """  
        # Source and Destination folders exist
        for filepath in self.getFilepathsInFolder(folderPathSource, sorted=False):

            destFilepath = self._sensitiveFsJoin(folderPathDest, self._sensitiveFsRelpath(filepath, folderPathSource))
            status = self.moveFile(filepath, destFilepath, overwriteIfExists)
            if not(status):
                # Return False if the operation failed for any reason except we weren't allowed to overwrite
                #     an existing file
                if not(not(overwriteIfExists) and self.doesFileExist(destFilepath)):
                    return False

        return self.removeFolder(folderPathSource)

    def _getCountItemsInFolder(self, folderPath : str) -> int:
        """Internal method for checking how many items are inside an existent folder.
        Basic implementation will use available filepaths. Override if there is a more accessible statistic.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            int: Count of how many items are within this folder.
        """
        return len(self.getFilepathsInFolder(folderPath, sorted=False))



    # Not recommended to reimplement - public facing
    def addFile(self, filepath : str, file : bytes, overwriteIfExists : bool = True) -> bool:
        if self.doesFileExist(filepath):
            if overwriteIfExists:
                self._wasModified = True
                return self._replaceExistentFile(filepath, file)
            return False
        self._wasModified = True
        return self._addNewFile(filepath, file)

    def renameFile(self, filepath : str, filenameRename : str, overwriteIfExists = True) -> bool:
        if self.doesFileExist(filepath):
            folderPath, _filename = self._sensitiveFsSplit(filepath)
            filenameRename = self._sensitiveFsJoin(folderPath, filenameRename)
            if filepath == filenameRename:
                return True
            self._wasModified = True
            return self._renameFile(filepath, filenameRename, overwriteIfExists)
        return False

    def replaceFile(self, filepath : str, file : bytes, createIfNotExists : bool = True) -> bool:
        if self.doesFileExist(filepath):
            self._wasModified = True
            return self._replaceExistentFile(filepath, file)
        elif createIfNotExists:
            return self.addFile(filepath, file)
        else:
            return False

    def removeFile(self, filepath : str) -> bool:
        if self.doesFileExist(filepath):
            self._wasModified = True
            return self._requiredRemoveExistentFile(filepath)
        return True

    def moveFile(self, filepathSource : str, filepathDest : str, overwriteIfExists : bool = True) -> bool:
        if filepathSource == filepathDest:
            return True
        if self.doesFileExist(filepathSource):
            self._wasModified = True
            return self._moveExistentFile(filepathSource, filepathDest, overwriteIfExists)
        return False

    def addFolder(self, folderPath : str) -> bool:
        if self.doesFolderExist(folderPath):
            return True
        self._wasModified = True
        return self._requiredAddNewFolderNested(folderPath)
                
    def removeFolder(self, folderPath : str, removeIfFull : bool = True) -> bool:
        if not(self.doesFolderExist(folderPath)):
            return True
        elif self.getCountItemsInFolder(folderPath) > 0 and not(removeIfFull):
            return False
        self._wasModified = True
        return self._requiredRemoveFolderNested(folderPath)
    
    def renameFolder(self, folderPath : str, folderName : str, mergeIfExists : bool = True) -> bool:
        # TODO - Change to overwrite (simplifies moveFolderContents syntax)
        folderPathSub, _folderName = self._sensitiveFsSplit(folderPath)
        folderPathNew = self._sensitiveFsJoin(folderPathSub, folderName)
        if folderPathNew == folderPath:
            return True

        if self.doesFolderExist(folderPathNew):
            if not(mergeIfExists):
                return False
        else:
            if not(self.addFolder(folderPathNew)):
                return False

        self._wasModified = True
        return self._renameFolder(folderPath, folderPathNew)

    def moveFolderContents(self, folderPathSource : str, folderPathDest : str, overwriteIfExists : bool = True) -> bool:
        # TODO - Maybe just modify to normal move, or add a normal move method below
        if self.doesFolderExist(folderPathSource):
            if not(self.doesFolderExist(folderPathDest)):
                if not(self.addFolder(folderPathDest)):
                    return False
            
            self._wasModified = True
            return self._moveFolderContents(folderPathSource, folderPathDest, overwriteIfExists)
        # Return True if there was nothing to move in the first place
        return True

    def doesFileExist(self, filepath : str) -> bool:
        return self._doesFileExist(filepath)

    def doesFolderExist(self, folderPath : str) -> bool:
        return self._requiredDoesFolderExist(folderPath)

    def getFile(self, filepath : str) -> Optional[bytes]:
        return self._requiredGetFile(filepath)
    
    def getFilepathsInFolder(self, folderPath : str, sorted=True) -> List[str]:
        if self.doesFolderExist(folderPath):
            if sorted:
                # TODO - Sort by directory (not so great)
                output = self._requiredGetFilepathsInFolder(folderPath)
                output.sort()
                return output
            else:
                return self._requiredGetFilepathsInFolder(folderPath)
        return []
    
    def getCountItemsInFolder(self, folderPath : str) -> int:
        if self.doesFolderExist(folderPath):
            return self._getCountItemsInFolder(folderPath)
        return 0
    
    def hasFilesystemBeenModified(self) -> bool:
        return self._wasModified
    
    def resetModifiedFlag(self):
        self._wasModified = False