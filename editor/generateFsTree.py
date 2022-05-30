from typing import Dict, List, Tuple
from widebrim.filesystem.fused import FusedFilesystem
from widebrim.filesystem.low_level.fs_base import FilesystemBase
from wx import TreeCtrl

class FolderTreeNode():
    def __init__(self, path : str):
        self.folders : List[FolderTreeNode] = []
        self.files : List[str] = []
        self.path = path
        self.treeRef = None
    
    def clearTreeReferencesForGc(self):
        for folder in self.folders:
            folder.clearTreeReferencesForGc()
        self.treeRef = None

    def toString(self, indent=0):
        output = ""
        for file in self.files:
            output += "\n" + ("\t" * indent) + file
        for folder in self.folders:
            output += folder.toString(indent=indent + 1)
        return output

    def __str__(self):
        return self.toString()

def generateFolderStructureFromRelativeRoot(fs : FilesystemBase, pathRoot : str) -> Tuple[FolderTreeNode, Dict[str, FolderTreeNode]]:
    """Generates a folder tree for all filepaths spanning from a root path.

    Args:
        fs (FilesystemBase): Filesystem for file access
        pathRoot (str): Absolute root path to folder inside filesystem. Should not contain extra slashes.

    Returns:
        Tuple[FolderTreeNode, Dict[str, FolderTreeNode]]: (Root folder, Absolute path to FolderTreeNode lookup dictionary)
    """

    # TODO - Will not be compatible with native, should use FS-native join and split methods

    rootFolder = FolderTreeNode(pathRoot)
    folderLookup = {pathRoot : rootFolder}
    
    filepaths = fs.getFilepathsInFolder(pathRoot)
    filepaths.sort(key=len, reverse=False)
    for path in filepaths:
        trueFolderPath = "/".join(path.split("/")[:-1])
        folderPath = trueFolderPath

        while folderPath not in folderLookup:
            folderPath = "/".join(folderPath.split("/")[:-1])
        
        targetFolder = folderLookup[folderPath]
        while folderPath != trueFolderPath:
            remainder = trueFolderPath[len(folderPath) + 1:]
            if remainder.count("/") == 0:
                folderPath = folderPath + "/" + remainder
            else:
                folderPath = folderPath + "/" + ("/".join(remainder.split("/")[:-1]))

            newFolder = FolderTreeNode(folderPath)
            targetFolder.folders.append(newFolder)
            folderLookup[folderPath] = newFolder
            targetFolder = newFolder

        targetFolder.files.append(path)
    
    return (rootFolder, folderLookup)

def populateTreeCtrlFromFolderTree(treeCtrl : TreeCtrl, rootFolder : FolderTreeNode):
    """Populates a wx.TreeCtrl with directory information.

    Args:
        treeCtrl (TreeCtrl): wx.TreeCtrl. Can be populated; contents will be emptied.
        rootFolder (FolderTreeNode): Valid folder tree. Will fail if modified.
    """
    
    def generateBranchForFolder(parentFolder : FolderTreeNode, childFolder : FolderTreeNode):
        if parentFolder.treeRef != None:
            childFolder.treeRef = treeCtrl.AppendItem(parentFolder.treeRef, childFolder.path[len(parentFolder.path) + 1:], data=childFolder.path)
            for folder in childFolder.folders:
                generateBranchForFolder(childFolder, folder)
            for file in childFolder.files:
                treeCtrl.AppendItem(childFolder.treeRef, file[len(childFolder.path) + 1:], data=file)

    rootFolder.clearTreeReferencesForGc()
    treeCtrl.DeleteAllItems()
    rootFolder.treeRef = treeCtrl.AddRoot("/", data=rootFolder.path)
    
    for folder in rootFolder.folders:
        generateBranchForFolder(rootFolder, folder)
    for file in rootFolder.files:
        treeCtrl.AppendItem(rootFolder.treeRef, file[len(rootFolder.path) + 1:], data=file)