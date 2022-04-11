from widebrim.engine.config import FILE_USE_PATCH, PATH_PATCH
from os import path

# TODO - From FileInterface
# TODO - Whole filesystem needs rewrite
def _getResolvedPatchPath(inPath : str) -> str:
    if len(inPath) > 0 and (inPath[0] == "/" or inPath[0] == "\\"):
        if inPath[0] == "/":
            return inPath.lstrip("/")
        elif inPath[0] == "\\":
            return inPath.lstrip("\\")
    return inPath

def _isPatchFolderArchive(filepath):
    return len(filepath) > 4 and filepath[-4:] == ".plz"

def getFilesInFolder(pathToFolder : str, recurse = False):
    if FILE_USE_PATCH:
        pathPatch = path.join(PATH_PATCH, pathToFolder)
