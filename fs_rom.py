from typing import List, Optional
import ndspy.rom, ndspy.fnt

# TODO - Rename file, rename folder, move file, move folder

# Only functional for ROMs which use filenames, not file IDs
class FilesystemRom():

    def __init__(self, rom : ndspy.rom.NintendoDSRom):
        # Don't interface directly to the ROM - file and folder references are order-sensitive here
        #      Instead only use offered methods to access or change data

        self.__folderNameToFolder = {}
        self.__foldersInRom = []
        self.__rom = rom

        def doRecursiveAdd(folder, nameFolder):
            self.__foldersInRom.append(folder)
            self.__folderNameToFolder[nameFolder] = folder
            for name, childFolder in folder.folders:
                doRecursiveAdd(childFolder, nameFolder + "/" + name)

        doRecursiveAdd(rom.filenames, "")

    def addFile(self, filename : str, file : bytes) -> bool:
        # TODO - Create folder if does not exist
        # TODO - Use path module!
        # TODO - Check if file exists (could be terrible...)
        folderPath = "/".join(filename.split("/")[:-1])
        filename = filename.split("/")[-1]

        if folderPath in self.__folderNameToFolder:
            folder = self.__folderNameToFolder[folderPath]
            folder : ndspy.fnt.Folder
        else:
            return False

        newFileId = folder.firstID + len(folder.files)
        folder.files.append(filename)
        
        for shiftFolder in self.__foldersInRom:
            if shiftFolder.firstID >= newFileId and shiftFolder != folder:
                shiftFolder.firstID += 1
        
        self.__rom.files.insert(newFileId, file)
        return True

    def removeFile(self, filename : str) -> bool:
        fileId = self.__rom.filenames.idOf(filename)
        if fileId == None:
            return False

        folderName = "/".join(filename.split("/")[:-1])
        filename = filename.split("/")[-1]

        if folderName in self.__folderNameToFolder:
            folder = self.__folderNameToFolder[folderName]
            folder : ndspy.fnt.Folder

            if filename in folder.files:
                folder.files.remove(filename)
            else:
                return False
            
            indexFolder = self.__foldersInRom.index(folder)
            if indexFolder < len(self.__foldersInRom) - 1:
                for folder in self.__foldersInRom[indexFolder + 1:]:
                    folder.firstID -= 1
            
            self.__rom.files.pop(fileId)
            return True

        return False

    def addFolder(self, folderPath) -> bool:

        folderSubPath = folderPath[1:].split("/")
        currentPath = ""
        currentTarget = None
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
                
    def removeFolder(self, folderPath, parentFolder=None) -> bool:
        if folderPath in self.__folderNameToFolder:
            print("Deleted folder", folderPath)
            folder = self.__folderNameToFolder[folderPath]
            folder : ndspy.fnt.Folder

            if parentFolder == None:
                parentFolderPath = "/".join(folderPath.split("/")[:-1])
                if parentFolderPath in self.__folderNameToFolder:
                    parentFolder = self.__folderNameToFolder[parentFolderPath]

            # TODO - Do not allow the user to recurse this...
            for nameFolder, dumpFolder in folder.folders:
                self.removeFolder(folderPath + "/" + nameFolder, parentFolder=parentFolder)
            
            # Weird bug in iteration of folder.files that causes every other filename to be lost
            filenames = list(folder.files)

            for file in filenames:
                if not(self.removeFile(folderPath + "/" + file)):
                    print("Failed to remove", folderPath + "/" + file)
            
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
            print("Did not find", folderPath)
            return False
        return True

    def getFile(self, filepath) -> Optional[bytes]:
        if self.__rom.filenames.idOf(filepath) != None:
            return self.__rom.getFileByName(filepath)
        return None
    
    def getFilepathsInFolder(self, filepath) -> List[str]:

        output = []

        def recursiveSearch(folder : ndspy.fnt.Folder, parentPath):
            for file in list(folder.files):
                output.append(parentPath + "/" + file)
            for nameFolder, childFolder in list(folder.folders):
                recursiveSearch(childFolder, parentPath + "/" + nameFolder)

        if filepath in self.__folderNameToFolder:
            folder = self.__folderNameToFolder[filepath]
            recursiveSearch(folder, filepath)
        
        return output

    def save(self, filepath):
        self.__rom.saveToFile(filepath)