from typing import List, Optional

class Filesystem():
    
    def addFile(self, filepath : str, file : bytes) -> bool:
        """Add a file into this filesystem.

        Args:
            filepath (str): Full filepath ending with extension.
            file (bytes): File contents as raw data.

        Returns:
            bool: True if the file was added successfully.
        """
        # TODO - Only run if doesn't exist? Not sure about abstractions...
        return False
    
    def _replaceExistentFile(self, filepath : str, file : bytes) -> bool:
        return False

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
        return self.addFile(filepath, file)

    def _removeExistentFile(self, filepath) -> bool:
        return False

    def removeFile(self, filepath : str) -> bool:
        """Removes a file from the filesystem.

        Args:
            filepath (str): Full filepath ending with extension.

        Returns:
            bool: True if the filepath is no longer valid in the filesystem.
        """
        if self.doesFileExist(filepath):
            return self._removeExistentFile(filepath)
        return True

    def _moveExistentFile(self, filepathSource, filepathDest, overwriteIfExists) -> bool:

        fileContents = self.getFile(filepathSource)

        if fileContents == None:
            return False

        if self.doesFileExist(filepathDest):
            if not(overwriteIfExists):
                return False
            if not(self.removeFile(filepathDest)):
                return False

        return self.removeFile(filepathSource) and self.addFile(filepathDest, fileContents)

    def moveFile(self, filepathSource : str, filepathDest : str, overwriteIfExists : bool = True) -> bool:
        if self.doesFileExist(filepathSource):
            return self._moveExistentFile(filepathSource, filepathDest, overwriteIfExists)
        return False

    def addFolder(self, folderPath : str) -> bool:
        return False
                
    def removeFolder(self, folderPath : str) -> bool:
        return False
    
    def moveFolder(self, folderPathSource : str, folderPathDest : str, overwriteIfExists : bool = True) -> bool:
        return False

    def doesFileExist(self, filepath) -> bool:
        return False

    def doesFolderExist(self, filepath) -> bool:
        return False

    def getFile(self, filepath) -> Optional[bytes]:
        return None
    
    def getFilepathsInFolder(self, filepath) -> List[str]:
        return []