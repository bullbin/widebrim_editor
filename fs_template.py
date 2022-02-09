from typing import List, Optional
from os.path import dirname, relpath, join
from abc import ABC, abstractmethod

class Filesystem(ABC):
    """Class for lowest level abstraction of filesystem access.
    """
    
    # These methods are needed to get the filesystem functional
    @abstractmethod
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

    @abstractmethod
    def _requiredDoesFolderExist(self, folderPath : str) -> bool:
        """Reimplement this in your filesystem. This is expected to run on any path but only return True if the folder path is valid and accessible.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            bool: True if the folder exists and is accessible.
        """
        return False

    @abstractmethod
    def _requiredAddNewFileToExistentFolder(self, folderPath : str, file : bytes) -> bool:
        """Reimplement this in your filesystem. This method may be called on any existent folder path.
        This is expected to perform simple file addition to a known good folder path.

        Args:
            folderPath (str): Folder path without any extension.
            file (bytes): File contents as raw data.

        Returns:
            bool: True if the file addition operation was successful.
        """
        return False
    
    @abstractmethod
    def _requiredRemoveExistentFile(self, filepath : str) -> bool:
        """Reimplement this in your filesystem. This method may be called on any existent filepath.
        This is expected to fully remove a file from the filesystem such that it will not be detectable by any other public methods.

        Args:
            filepath (str): Folder path without any extension.

        Returns:
            bool: True if the file removal operation was successful.
        """
        return False

    @abstractmethod
    def _requiredAddNewFolderNestled(self, folderPath : str) -> bool:
        """Reimplement this in your filesystem. This method may be called on any non-existent folder path.
        This is expected to handle both nestled and simple folder addition.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            bool: True if the folder was added successfully. False may leave fragments of the operation.
        """
        return False

    @abstractmethod
    def _requiredRemoveFolderNestled(self, folderPath : str) -> bool:
        """Reimplement this in your filesystem. This method may be called on any existed folder path.
        This is expected to handle both nestled and simple folder removal, as well as deletion of any contents.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            bool: True if the folder was removed successfully. False may leave fragments of the operation.
        """
        return False
    
    @abstractmethod
    def _requiredGetFilepathsInFolder(self, folderPath : str) -> List[str]:
        """Reimplement this in your filesystem. This method may be called on any existent folder path.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            List[str]: List of absolute (to filesystem) paths for any files inside the folder, including nestled directories. Empty if folder has no contents.
        """
        return []



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
        if not(self.doesFolderExist(dirname(filepath))):
            if not(self.addFolder(dirname(filepath))):
                return False
        return self._requiredAddNewFileToExistentFolder(filepath, file)

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
        for filepath in self.getFilepathsInFolder(folderPathSource):

            destFilepath = join(folderPathDest, relpath(filepath, folderPathSource))
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
        return len(self.getFilepathsInFolder(folderPath))



    # Not recommended to reimplement - public facing
    def addFile(self, filepath : str, file : bytes, overwriteIfExists : bool = True) -> bool:
        """Add a file into this filesystem.

        Args:
            filepath (str): Full filepath ending with extension.
            file (bytes): File contents as raw data.
            overwriteIfExists (bool, optional): Overwrite if the file already exists. Defaults to True.

        Returns:
            bool: True if the file was added successfully.
        """

        if self.doesFileExist(filepath):
            if overwriteIfExists:
                return self._replaceExistentFile(filepath, file)
            return False
        return self._addNewFile(filepath, file)

    def replaceFile(self, filepath : str, file : bytes, createIfNotExists : bool = True) -> bool:
        """Replace the contents of a file in the filesystem.

        Args:
            filepath (str): Full filepath ending with extension.
            file (bytes): File contents as raw data.
            createIfNotExists (bool, optional): Creates a new file if the path was not found. Defaults to True.

        Returns:
            bool: True if the file was replaced successfully.
        """
        if self.doesFileExist(filepath):
            return self._replaceExistentFile(filepath, file)
        elif createIfNotExists:
            return self.addFile(filepath, file)
        else:
            return False

    def removeFile(self, filepath : str) -> bool:
        """Removes a file from the filesystem.

        Args:
            filepath (str): Full filepath ending with extension.

        Returns:
            bool: True if the filepath is no longer valid in the filesystem.
        """
        if self.doesFileExist(filepath):
            return self._requiredRemoveExistentFile(filepath)
        return True

    def moveFile(self, filepathSource : str, filepathDest : str, overwriteIfExists : bool = True) -> bool:
        """Moves file from one path to another.

        Args:
            filepathSource (str): Full source filepath with extension.
            filepathDest (str): Full source destination with extension.
            overwriteIfExists (bool, optional): [description]. Defaults to True.

        Returns:
            bool: [description]
        """
        if self.doesFileExist(filepathSource):
            return self._moveExistentFile(filepathSource, filepathDest, overwriteIfExists)
        return False

    def addFolder(self, folderPath : str) -> bool:
        """Adds folder(s) to the filesystem. May take in a nestled folder path.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            bool: True if the final folder destination now exists. False may leave fragments of the operation.
        """
        if self.doesFolderExist(folderPath):
            return True
        return self._requiredAddNewFolderNestled(folderPath)
                
    def removeFolder(self, folderPath : str, removeIfFull : bool = True) -> bool:
        """Removes a folder from the filesystem.

        Args:
            folderPath (str): Folder path without any extension.
            removeIfFull (bool, optional): Allow deletion of non-empty folders. Defaults to True.

        Returns:
            bool: True if the folder no longer exists. False may mean folder removal was incomplete or was unattempted because removeIfFull was disabled.
        """
        if not(self.doesFolderExist(folderPath)):
            return True
        elif self.getCountItemsInFolder(folderPath) > 0 and not(removeIfFull):
            return False
        return self._requiredRemoveFolderNestled(folderPath)
    
    def moveFolderContents(self, folderPathSource : str, folderPathDest : str, overwriteIfExists : bool = True) -> bool:
        """Moves the contents of one folder from one destination to another, including copying all (nestled) files at the source.

        Args:
            folderPathSource (str): Full source folder path.
            folderPathDest (str): Full destination folder path.
            overwriteIfExists (bool, optional): True to overwrite if the destination already has data. Defaults to True.

        Returns:
            bool: True if movement operation was successful or there was nothing to move. False may leave fragments of the operation.
        """
        if self.doesFolderExist(folderPathSource):
            if not(self.doesFolderExist(folderPathDest)):
                if not(self.addFolder(folderPathDest)):
                    return False
            return self._moveFolderContents(folderPathSource, folderPathDest, overwriteIfExists)
        # Return True if there was nothing to move in the first place
        return True

    def doesFileExist(self, filepath : str) -> bool:
        """Checks if there exists data for some path in the filesystem.

        Args:
            filepath (str): Full filepath with extension.

        Returns:
            bool: True if data exists for this filepath.
        """
        return self._doesFileExist(filepath)

    def doesFolderExist(self, folderPath : str) -> bool:
        """Checks if there exists some folder at some path in the filesystem.

        Args:
            folderPath (str): Folder path without extension.

        Returns:
            bool: True if there exists a folder at this path.
        """
        return self._requiredDoesFolderExist(folderPath)

    def getFile(self, filepath : str) -> Optional[bytes]:
        """Fetch the contents of a file at a path in the filesystem.

        Args:
            filepath (str): Filepath with extension.

        Returns:
            Optional[bytes]: None if the file does not exist or was unreachable, bytes otherwise
        """
        # NOTE: Will grab file twice unless you override the doesFileExist internal method!
        if self.doesFileExist(filepath):
            return self._requiredGetFile(filepath)
        return None
    
    def getFilepathsInFolder(self, folderPath : str) -> List[str]:
        """Returns a list of any paths of files accessible from within this folder.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            List[str]: List of absolute (to filesystem) paths for any files inside the folder. Empty if folder doesn't exist or has no contents.
        """
        if self.doesFolderExist(folderPath):
            return self._requiredGetFilepathsInFolder(folderPath)
        return []
    
    def getCountItemsInFolder(self, folderPath : str) -> int:
        """Returns a count of how many files are accessible from within this folder.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            int: Count of how many items are within this folder.
        """
        if self.doesFolderExist:
            return self._getCountItemsInFolder(folderPath)
        return 0