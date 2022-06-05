from abc import ABC, abstractmethod
from typing import List, Optional

class Filesystem(ABC):

    @abstractmethod
    def addFile(self, filepath : str, file : bytes, overwriteIfExists : bool = True) -> bool:
        """Add a file into this filesystem.

        Args:
            filepath (str): Full filepath ending with extension.
            file (bytes): File contents as raw data.
            overwriteIfExists (bool, optional): Overwrite if the file already exists. Defaults to True.

        Returns:
            bool: True if the file was added successfully.
        """
        return None

    @abstractmethod
    def renameFile(self, filepath : str, filenameRename : str, overwriteIfExists = True) -> bool:
        """Rename the file at a path to a new filename.

        Args:
            filepath (str): Full filepath with extension.
            filenameRename (str): New filename (no path) with extension.
            overwriteIfExists (bool, optional): [description]. Overwrites any file already at the new location. Defaults to True.

        Returns:
            bool: True if the file was renamed successfully.
        """
        return False

    @abstractmethod
    def replaceFile(self, filepath : str, file : bytes, createIfNotExists : bool = True) -> bool:
        """Replace the contents of a file in the filesystem.

        Args:
            filepath (str): Full filepath ending with extension.
            file (bytes): File contents as raw data.
            createIfNotExists (bool, optional): Creates a new file if the path was not found. Defaults to True.

        Returns:
            bool: True if the file was replaced successfully.
        """
        return False

    @abstractmethod
    def removeFile(self, filepath : str) -> bool:
        """Removes a file from the filesystem.

        Args:
            filepath (str): Full filepath ending with extension.

        Returns:
            bool: True if the filepath is no longer valid in the filesystem.
        """
        return False

    @abstractmethod
    def moveFile(self, filepathSource : str, filepathDest : str, overwriteIfExists : bool = True) -> bool:
        """Moves file from one path to another.

        Args:
            filepathSource (str): Full source filepath with extension.
            filepathDest (str): Full source destination with extension.
            overwriteIfExists (bool, optional): True to overwrite the file if it already exists in the filesystem. Defaults to True.

        Returns:
            bool: True if the file was moved successfully. False may leave fragments of the operation.
        """
        return False

    @abstractmethod
    def addFolder(self, folderPath : str) -> bool:
        """Adds folder(s) to the filesystem. May take in a nested folder path.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            bool: True if the final folder destination now exists. False may leave fragments of the operation.
        """
        return False

    @abstractmethod  
    def removeFolder(self, folderPath : str, removeIfFull : bool = True) -> bool:
        """Removes a folder from the filesystem.

        Args:
            folderPath (str): Folder path without any extension.
            removeIfFull (bool, optional): Allow deletion of non-empty folders. Defaults to True.

        Returns:
            bool: True if the folder no longer exists. False may mean folder removal was incomplete or was unattempted because removeIfFull was disabled.
        """
        return False
    
    @abstractmethod
    def renameFolder(self, folderPath : str, folderName : str, mergeIfExists : bool = True) -> bool:
        """Renames a folder within the filesystem.

        Args:
            folderPath (str): Folder path without any extension.
            folderName (str): New folder name (not path) without any extension.
            mergeIfExists (bool, optional): True to merge if the folder already exists. Defaults to True.

        Returns:
            bool: True if the folder name was changed successfully.
        """
        return False

    @abstractmethod
    def moveFolderContents(self, folderPathSource : str, folderPathDest : str, overwriteIfExists : bool = True) -> bool:
        # TODO - Maybe just modify to normal move, or add a normal move method below
        """Moves the contents of one folder from one destination to another, including copying all (nested) files at the source.

        Args:
            folderPathSource (str): Full source folder path.
            folderPathDest (str): Full destination folder path.
            overwriteIfExists (bool, optional): True to overwrite if the destination already has data. Defaults to True.

        Returns:
            bool: True if movement operation was successful or there was nothing to move. False may leave fragments of the operation.
        """
        return False

    @abstractmethod
    def doesFileExist(self, filepath : str) -> bool:
        """Checks if there exists data for some path in the filesystem.

        Args:
            filepath (str): Full filepath with extension.

        Returns:
            bool: True if data exists for this filepath.
        """
        return False

    @abstractmethod
    def doesFolderExist(self, folderPath : str) -> bool:
        """Checks if there exists some folder at some path in the filesystem.

        Args:
            folderPath (str): Folder path without extension.

        Returns:
            bool: True if there exists a folder at this path.
        """
        return False

    @abstractmethod
    def getFile(self, filepath : str) -> Optional[bytes]:
        """Fetch the contents of a file at a path in the filesystem.

        Args:
            filepath (str): Filepath with extension.

        Returns:
            Optional[bytes]: None if the file does not exist or was unreachable, bytes otherwise
        """
        return None
    
    @abstractmethod
    def getFilepathsInFolder(self, folderPath : str, sorted=True) -> List[str]:
        """Returns a list of any paths of files accessible from within this folder.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            List[str]: List of absolute (to filesystem) paths for any files inside the folder. Empty if folder doesn't exist or has no contents.
        """
        return []
    
    @abstractmethod
    def getCountItemsInFolder(self, folderPath : str) -> int:
        """Returns a count of how many files are accessible from within this folder.

        Args:
            folderPath (str): Folder path without any extension.

        Returns:
            int: Count of how many items are within this folder.
        """
        return 0
    
    @abstractmethod
    def hasFilesystemBeenModified(self) -> bool:
        """Returns True if the filesystem has been modified. Changes may not be important (e.g., renaming a file to itself)

        Returns:
            bool: True if the filesystem was modified.
        """
        return False
    
    @abstractmethod
    def resetModifiedFlag(self):
        """Resets the modifie flag for this filesystem. Required, for example, when triggering a save operation.
        """
        pass
