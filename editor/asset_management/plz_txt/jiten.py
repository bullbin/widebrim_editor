from typing import Dict, List, Optional
from widebrim.engine.const import PATH_PACK_PLACE_NAME, PATH_TEXT_PLACE_NAME
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.engine_ext.utils import substituteLanguageString
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.hat_io.asset import File
from widebrim.madhatter.hat_io.const import ENCODING_DEFAULT_STRING

def getUsedRoomNameTags(state : Layton2GameState) -> Dict[int, str]:
    """Returns a dictionary of available room titles with their corresponding ID.

    Args:
        state (Layton2GameState): State used for filesystem access.

    Returns:
        Dict[int, str]: Dictionary mapping from place ID to name.
    """
    output = {}
    packNames = state.getFileAccessor().getPack(substituteLanguageString(state, PATH_PACK_PLACE_NAME))
    for idPlace in range(256):
        filePlaceName = PATH_TEXT_PLACE_NAME % idPlace
        if (data := packNames.getFile(filePlaceName)) != None:
            try:
                data : bytes
                data = data.decode(ENCODING_DEFAULT_STRING)
            except UnicodeDecodeError:
                data = ""
            output[idPlace] = data
    return output

def getFreeRoomJitenNameTagId(state : Layton2GameState, usedTags : Optional[Dict[int, str]] = None) -> List[int]:
    """Returns a sorted list of free room name IDs.

    Args:
        state (Layton2GameState): State used for filesystem access.
        usedTags (Optional[Dict[int, str]], optional): Cached output from getUsedRoomNameTags to reduce wasted work. Only use if previously called. Defaults to None.

    Returns:
        List[int]: List of unused place name IDs.
    """
    if usedTags == None:
        usedTags = getUsedRoomNameTags(state)

    unused = []
    for idPlace in range(1, 256):
        if idPlace not in usedTags:
            unused.append(idPlace)
    return unused

def swapRoomId(state : Layton2GameState, oldId : int, newId : int) -> bool:
    return False

def deleteRoomId(state : Layton2GameState, id : int, forceIfInUse : bool = False, remapTarget : Optional[int] = None):
    pass

def createRoomId(state : Layton2GameState, id : int, title : str, overwriteIfFound : bool) -> bool:
    """Creates a new room name with its corresponding ID.

    Args:
        state (Layton2GameState): State used for filesystem access. Writeable support is needed.
        id (int): Destination ID for writing room name to.
        title (str): Room title. Will be encoded as shift-jis.
        overwriteIfFound (bool): True will allow for overwriting the stored title at the given ID if it exists.

    Returns:
        bool: True if name ID was created. False will be due to ID out of range, overwriting not being permitted or failure to encode title.
    """
    if not(0 < id < 256):
        return False

    if not(overwriteIfFound):
        freeTags = getFreeRoomJitenNameTagId(state)
        if id in freeTags:
            return False
    
    # TODO - Shorten or fail on title being too long (what is limit?)

    try:
        title = title.encode(ENCODING_DEFAULT_STRING)
    except UnicodeEncodeError:
        return False
    
    filename = PATH_TEXT_PLACE_NAME % id
    packNames = state.getFileAccessor().getPack(substituteLanguageString(state, PATH_PACK_PLACE_NAME))

    foundFile = False
    for file in packNames.files:
        if file.name == filename:
            foundFile = True
            file.data = title
            break

    if not(foundFile):
        fileOutput = File(name=filename, data=title)
        packNames.files.append(fileOutput)
    
    packNames.save()
    packNames.compress()
    fileAccessor : WriteableFilesystemCompatibilityLayer = state.getFileAccessor()
    fileAccessor.writeableFs.replaceFile(substituteLanguageString(state, PATH_PACK_PLACE_NAME), packNames.data)
    return True

def createNextNewRoomTitleId(state : Layton2GameState, title : str) -> Optional[int]:
    """Convenience function. Applies given title to first available ID.

    Args:
        state (Layton2GameState): State used for filesystem access. Writeable support is needed.
        title (str): Room title. Will be encoded as shift-jis.

    Returns:
        Optional[int]: ID will be returned if operation was successful. On failure, None is returned. No traces will be left on the filesystem.
    """
    freeTags = getFreeRoomJitenNameTagId(state)
    if len(freeTags) > 0:
        if createRoomId(state, freeTags[0], title, True):
            return freeTags[0]
    return None