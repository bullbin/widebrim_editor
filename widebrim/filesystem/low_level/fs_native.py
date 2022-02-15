from typing import List, Optional
from .fs_base import FilesystemBase
from os import getcwd, makedirs, remove, walk
from os.path import exists, isfile
from shutil import rmtree

# TODO - Mixed pathing...
# TODO - Should mark filesystem slashes in method or some return method
# TODO - Maybe convert everything to remove initial slash (more conformant to everything...)

class FilesystemNative(FilesystemBase):
    def __init__(self, pathFsRootFolder : str = getcwd()):
        """Filesystem to work with your native platform.

        NOTE: Filesystem restrictions comply to your platform. It is recommended to use backslashes as convention to prevent mixed-slash issues from appearing.

        Args:
            pathFsRootFolder (str, optional): Filesystem root directory. Should not end in slashes. Defaults to current working directory.
        """
        self.__pathRoot = pathFsRootFolder
    
    def _sensitiveFsJoin(self, x: str, y: str) -> str:
        # TODO - Bugs with empty directory names (not permitted anyways)
        # TODO - Needs better solution...
        if (len(y) > 0 and y[0] != "\\") and (len(x) > 0 and x[-1] != "\\"):
            return x + "\\" + y
        return x + y

    def _requiredAddNewFileToExistentFolder(self, filepath: str, file: bytes) -> bool:
        try:
            with open(self._sensitiveFsJoin(self.__pathRoot, filepath), 'wb') as output:
                output.write(file)
            return True
        except OSError:
            return False
    
    def _requiredAddNewFolderNested(self, folderPath: str) -> bool:
        folderPath = self._sensitiveFsJoin(self.__pathRoot, folderPath)
        try:
            makedirs(folderPath)
        except OSError:
            return False
        return True
    
    def _requiredDoesFolderExist(self, folderPath: str) -> bool:
        folderPath = self._sensitiveFsJoin(self.__pathRoot, folderPath)
        if exists(folderPath) and not(isfile(folderPath)):
            return True
        return False
    
    def _requiredGetFile(self, filepath: str) -> Optional[bytes]:
        filepath = self._sensitiveFsJoin(self.__pathRoot, filepath)
        try:
            with open(filepath, 'rb') as fileInput:
                return fileInput.read()
        except FileNotFoundError:
            return None
        except OSError:
            return False
    
    def _requiredGetFilepathsInFolder(self, folderPath: str) -> List[str]:
        # HACK - Add trailing slash
        folderPath = self._sensitiveFsJoin(self.__pathRoot, folderPath)
        output = []

        for root, dir, files in walk(folderPath):
            for file in files:
                relpath = self._sensitiveFsRelpath(root, folderPath)
                if relpath == ".":
                    relpath = "\\"
                else:
                    relpath = "\\" + relpath
                temp = self._sensitiveFsJoin(relpath, file)
                output.append(temp.replace("\\", "/"))
        return output
    
    def _requiredRemoveExistentFile(self, filepath: str) -> bool:
        filepath = self._sensitiveFsJoin(self.__pathRoot, filepath)
        # TODO - May raise errors, need to check
        remove(filepath)
        return True
    
    def _requiredRemoveFolderNested(self, folderPath: str) -> bool:
        folderPath = self._sensitiveFsJoin(self.__pathRoot, folderPath)
        # TODO - May raise errors, need to check
        rmtree(folderPath)
        return True