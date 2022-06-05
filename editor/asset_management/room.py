from typing import List
from widebrim.gamemodes.room.const import PATH_PACK_PLACE, PATH_PLACE_A, PATH_PLACE_B
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.engine.file import ReadOnlyFileInterface
from re import search

class PlaceGroup():
    def __init__(self, idxPlace : int, indicesStates : List[int]):
        self.indexPlace     : int       = idxPlace
        self.indicesStates  : List[int] = indicesStates

    def __str__(self):
        output = ""
        for state in self.indicesStates:
            output += PATH_PACK_PLACE % (self.indexPlace, state) + "\n"
        if len(output) > 0:
            output = output[:-1]
        return output

def getPackPathForPlaceIndex(indexPlace : str) -> str:
    """Returns the filepath for the pack containing data for a given place index.

    Args:
        indexPlace (str): Place index.

    Returns:
        str: Absolute path pack.
    """
    if indexPlace < 40:
        return PATH_PLACE_A
    return PATH_PLACE_B

def getPlaceGroups(fileInterface : ReadOnlyFileInterface) -> List[PlaceGroup]:
    """Returns a sorted list of place groups containing information about all place substates.

    Args:
        fileInterface (ReadOnlyFileInterface): File interface for getting place packs.

    Returns:
        List[PlaceGroup]: Sorted list of place groups.
    """

    def getPlaceDataForIndex(packPlace : LaytonPack, idxPlace : int) -> List[int]:
        datPlace = PATH_PACK_PLACE.replace("%i", "%s")
        datPlace = datPlace % (str(idxPlace), "([0-9]*)")

        namePlaces = []
        for file in packPlace.files:
            if (result := search(datPlace, file.name)) != None:
                namePlaces.append(int(result.group(1)))
        
        namePlaces.sort()
        return namePlaces

    datPlace = PATH_PACK_PLACE.replace("%i", "%s")
    datPlace = datPlace % ("([0-9]*)", "[0-9]*")

    output = []
    countedIndices = []
    for indexPack, pack in enumerate([fileInterface.getPack(PATH_PLACE_A), fileInterface.getPack(PATH_PLACE_B)]):
        for file in pack.files:
            if (result := search(datPlace, file.name)) != None:
                idxPlace = int(result.group(1))
                if idxPlace < 40 and indexPack == 0:
                    if idxPlace not in countedIndices:
                        output.append(PlaceGroup(idxPlace, getPlaceDataForIndex(pack, idxPlace)))
                        countedIndices.append(idxPlace)
                elif idxPlace >= 40 and indexPack == 1:
                    if idxPlace not in countedIndices:
                        output.append(PlaceGroup(idxPlace, getPlaceDataForIndex(pack, idxPlace)))
                        countedIndices.append(idxPlace)

    output.sort(key=lambda x: x.indexPlace)
    return output