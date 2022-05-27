from widebrim.engine.const import PATH_NAME_ROOT, PATH_ANI
from widebrim.engine.file import FileInterface
from widebrim.gamemodes.dramaevent.const import PATH_BODY_ROOT, PATH_BODY_ROOT_LANG_DEP

from typing import List, Optional
from widebrim.engine.state.manager import Layton2GameState

class CharacterEntry():
    def __init__(self, index : int, pathImage : str, pathName : Optional[str]):
        self._index : int = index
        self._pathImage = pathImage
        self._pathName : Optional[str] = pathName
    
    def __str__(self):
        return str(self._index) + "\n" + str(self._pathImage) + "\n" + str(self._pathName)

def getCharacters(laytonState : Layton2GameState) -> List[CharacterEntry]:
    """Returns a list of all character assets accessible from the ROM.
    Asset order is given by ID ascending. While all characters are accessible from events, not all will be visible from the character bonus screen.

    Args:
        laytonState (Layton2GameState): _description_

    Returns:
        List[CharacterEntry]: _description_
    """
    output = []
    for charIndex in range(1,256):
        if charIndex == 86 or charIndex == 87:
            pathAsset = PATH_BODY_ROOT_LANG_DEP.replace("?", laytonState.language.value)
        else:
            pathAsset =  PATH_BODY_ROOT
        pathAsset = PATH_ANI % pathAsset
        if FileInterface.doesFileExist(pathAsset % charIndex):
            if FileInterface.doesFileExist(PATH_ANI % (PATH_NAME_ROOT % (laytonState.language.value, charIndex))):
                output.append(CharacterEntry(charIndex, pathAsset % charIndex, PATH_ANI % (PATH_NAME_ROOT % (laytonState.language.value, charIndex))))
            else:
                output.append(CharacterEntry(charIndex, pathAsset % charIndex, None))
    return output
