from typing import List, Tuple
from widebrim.engine.const import LANGUAGES
from filesystem.low_level.fs_romloader import FilesystemNds

def purgeFilepaths(romFs : FilesystemNds, language : LANGUAGES, rootFolder : str, extensionConversion : List[Tuple[str, str]], paths : List[str]) -> List[List[str]]:
    """Function to remove a filtered set of files from ROM.

    Args:
        romFs (FilesystemNds): ROM filesystem
        language (LANGUAGES): ROM language
        rootFolder (str): Folder to restrict operations to
        extensionConversion (List[Tuple[str, str]]): Tuples to convert extensions from internal to real
        paths (List[str]): List of filepaths to purge

    Returns:
        List[List[str]]: List[Removed, Ambiguous, Missing]
    """
    exclude = []
    allPaths = romFs.getFilepathsInFolder(rootFolder)
    output = [[],[],[]]

    for path in paths:
        for extensionPair in extensionConversion:
            before, after = extensionPair
            path = path.replace("." + before, "." + after)

        path = path.replace("?", language.value)
        if "%" in path:
            if "/%s/" in path:
                path = path.replace("/%s/", "/" + language.value + "/")
        
        if "%" in path:
            # Ambiguous matches shouldn't be removed, but they should be considered...
            output[1].append(path)
        elif path not in exclude:
            exclude.append(path)

    for indexPath, path in enumerate(allPaths):
        allPaths[indexPath] = path[len(rootFolder) + 1:]

    for path in exclude:
        if path in allPaths:
            allPaths.remove(path)
        else:
            output[2].append(path)
    
    for path in allPaths:
        output[0].append(path)
        romFs.removeFile(rootFolder + "/" + path)
    
    return output