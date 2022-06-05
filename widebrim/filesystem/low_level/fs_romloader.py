from typing import Dict, List, Optional, Tuple

from .fs_base import FilesystemBase
import ndspy.rom, ndspy.fnt

# TODO - Protect against modifying some files (/ftc is a no-no, contains banners. Don't allow deleting since it probably uses hardcoded file IDs (seems to start at 0))
# TODO - Sensitive methods might fail on zero-length folder names
# TODO - Disallow zero length folders
# TODO - String verification

class FilesystemNds(FilesystemBase):
    def __init__(self, rom : ndspy.rom.NintendoDSRom):
        """Filesystem to work with Nintendo DS ROMs.

        NOTE: The internal pathing does not follow all conventions. The root folder exists at the "/" path. Path splits are handled by "/" rather than the backslash.

        Args:
            rom (ndspy.rom.NintendoDSRom): Nintendo DS ROM to open filesystem of.
        """
        super().__init__()

        self.__folderNameToFolder : Dict[str, ndspy.fnt.Folder] = {} 
        self.__foldersInRom : List[ndspy.fnt.Folder]            = []
        self.__rom : ndspy.rom.NintendoDSRom                    = rom

        def doRecursiveAdd(folder, nameFolder):
            self.__foldersInRom.append(folder)

            # HACK - Why is the DS filesystem like this? Root of FS should be "/", not empty
            if nameFolder == "":
                self.__folderNameToFolder["/"] = folder
            else:
                self.__folderNameToFolder[nameFolder] = folder

            for name, childFolder in folder.folders:
                doRecursiveAdd(childFolder, nameFolder + "/" + name)

        # Build some quick look-up tables
        doRecursiveAdd(rom.filenames, "")
    
    def _sensitiveFsJoin(self, x: str, y: str) -> str:
        return super()._sensitiveFsJoin(x, y).replace("\\", "/")
    
    def _sensitiveFsRelpath(self, filepath: str, folderPath: str) -> str:
        return super()._sensitiveFsRelpath(filepath, folderPath).replace("\\", "/")
    
    def _sensitiveFsSplit(self, filepath: str) -> Tuple[str, str]:
        head, tail = super()._sensitiveFsSplit(filepath)
        head = head.replace("\\", "/")
        tail = tail.replace("\\", "/") # TODO - Needed?
        return (head,tail)

    def _requiredAddNewFileToExistentFolder(self, filepath: str, file: bytes) -> bool:
        folderPath, filename = self._sensitiveFsSplit(filepath)
        folder = self.__folderNameToFolder[folderPath]
        newFileId = folder.firstID + len(folder.files)
        folder.files.append(filename)
        for shiftFolder in self.__foldersInRom:
            if shiftFolder.firstID >= newFileId and shiftFolder != folder:
                shiftFolder.firstID += 1
        self.__rom.files.insert(newFileId, file)
        return True
    
    def _requiredAddNewFolderNested(self, folderPath: str) -> bool:
        # TODO - Use split (?)
        currentPath = ""
        if len(folderPath) > 0 and folderPath[0] == "/":
            currentTarget = self.__folderNameToFolder["/"]
            folderPath = folderPath[1:]
            folderSubPath = folderPath.split("/")
        else:
            # Files not beginning at the FS root can't exist inside the ROM
            return False

        for segment in folderSubPath:
            currentPath += "/" + segment
            if currentPath in self.__folderNameToFolder:
                currentTarget = self.__folderNameToFolder[currentPath]
            else:
                # Create folder
                if currentTarget != None:
                    print("Created folder", currentPath)

                    # Get next ID by looking at folder list
                    nextId = self.__foldersInRom.index(currentTarget)
                    if nextId == len(self.__foldersInRom) - 1:
                        # No next folder, manually calculate ID
                        nextId += len(currentTarget.files)
                    else:
                        # Look at next folder, as it will start where last folder left off
                        nextId = self.__foldersInRom[nextId + 1].firstID
                    
                    nextTarget = ndspy.fnt.Folder(firstID = nextId)

                    # Insert directly after parent (replace next folder)
                    # TODO - Insert last in parent - kind of annoying to figure out though
                    #        Would require searching name, going back to folder index...
                    self.__foldersInRom.insert(self.__foldersInRom.index(currentTarget) + 1, nextTarget)
                    self.__folderNameToFolder[currentPath] = nextTarget
                    currentTarget.folders.insert(0, (segment, nextTarget))
                    currentTarget = nextTarget
                else:
                    print("No target", currentPath)
                    return False
        return True
    
    def _requiredDoesFolderExist(self, folderPath: str) -> bool:
        return folderPath in self.__folderNameToFolder
    
    def _requiredGetFile(self, filepath: str) -> Optional[bytes]:
        # TODO - Files on root path behaviour
        if self.__rom.filenames.idOf(filepath) != None:
            return self.__rom.getFileByName(filepath)
        return None
    
    def _requiredGetFilepathsInFolder(self, folderPath: str) -> List[str]:
        output = []

        def recursiveSearch(folder : ndspy.fnt.Folder, parentPath : str):
            for file in list(folder.files):
                output.append(self._sensitiveFsJoin(parentPath, file))
            for nameFolder, childFolder in list(folder.folders):
                recursiveSearch(childFolder, self._sensitiveFsJoin(parentPath, nameFolder))

        if folderPath in self.__folderNameToFolder:
            folder = self.__folderNameToFolder[folderPath]
            recursiveSearch(folder, folderPath)
        
        return output
    
    def _requiredRemoveExistentFile(self, filepath: str) -> bool:
        fileId = self.__rom.filenames.idOf(filepath)
        if fileId == None:
            # True if filename couldn't be resolved (file doesn't exist)
            return True

        # Remove from parent folder
        folderPath, filename = self._sensitiveFsSplit(filepath)
        folder = self.__folderNameToFolder[folderPath]
        folder.files.remove(filename)
        
        # Shift IDs for above folders to correct for missing file
        indexFolder = self.__foldersInRom.index(folder)
        if indexFolder < len(self.__foldersInRom) - 1:
            for folder in self.__foldersInRom[indexFolder + 1:]:
                folder.firstID -= 1
        
        self.__rom.files.pop(fileId)
        return True
    
    def _requiredRemoveFolderNested(self, folderPath: str) -> bool:
        def recursiveFolderDelete(folderPath : str, parentFolder : ndspy.fnt.Folder = None):

            if folderPath in self.__folderNameToFolder:
                folder = self.__folderNameToFolder[folderPath]

                if parentFolder == None:
                    parentFolderPath = self._sensitiveFsSplit(folderPath)[0]
                    if parentFolderPath in self.__folderNameToFolder:
                        parentFolder = self.__folderNameToFolder[parentFolderPath]

                for nameFolder, dumpFolder in folder.folders:
                    if not(recursiveFolderDelete(self._sensitiveFsJoin(folderPath, nameFolder), parentFolder=parentFolder)):
                        return False
                
                # Weird bug in iteration of folder.files that causes every other filename to be lost
                filenames = list(folder.files)

                for file in filenames:
                    if not(self.removeFile(self._sensitiveFsJoin(folderPath, file))):
                        # print("Failed to remove", folderPath + "/" + file)
                        return False
                
                if parentFolder != None:
                    # Remove folder from parent
                    for indexFolder, folderPair in enumerate(parentFolder.folders):
                        nameFolder, dumpFolder = folderPair
                        if dumpFolder == folder:
                            parentFolder.folders.pop(indexFolder)
                            del self.__folderNameToFolder[folderPath]
                            self.__foldersInRom.pop(self.__foldersInRom.index(folder)) 
                            break
            else:
                # Folder not found, so doesn't exist (could be bad if executed from the above...)
                return True
            return True

        return recursiveFolderDelete(folderPath, None)
    
    def getRom(self):
		# TODO - Abstract to only save. Don't want this accessible
        # TODO - Can mess with modification function, be careful
        return self.__rom