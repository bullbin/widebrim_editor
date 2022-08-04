from typing import Dict, List, Optional
from widebrim.engine.const import PATH_DB_AUTOEVENT, PATH_DB_PLACEFLAG, PATH_PROGRESSION_DB
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.filesystem.compatibility.compatibilityRom import WriteableRomFileInterface
from widebrim.gamemodes.room.const import PATH_PACK_PLACE, PATH_PLACE_A, PATH_PLACE_B
from widebrim.madhatter.hat_io.asset import File, LaytonPack
from widebrim.engine.file import ReadOnlyFileInterface
from re import search, match
from widebrim.madhatter.hat_io.asset_autoevent import AutoEvent, AutoEventSubPlaceEntry

from widebrim.madhatter.hat_io.asset_placeflag import PlaceFlag

def _loadPlaceFlag(state : Layton2GameState) -> PlaceFlag:
    placeFlag = PlaceFlag()
    if (data := state.getFileAccessor().getPackedData(PATH_PROGRESSION_DB, PATH_DB_PLACEFLAG)):
        placeFlag.load(data)
    return placeFlag

def _savePlaceFlag(state : Layton2GameState, placeFlag : PlaceFlag) -> bool:
    packProgression = state.getFileAccessor().getPack(PATH_PROGRESSION_DB)
    fileNotFound = True
    # TODO - GetFile
    for file in packProgression.files:
        if file.name == PATH_DB_PLACEFLAG:
            placeFlag.save()
            file.data = placeFlag.data
            fileNotFound = False
            break

    if fileNotFound:
        placeFlag.name = PATH_DB_PLACEFLAG
        placeFlag.save()
        packProgression.files.append(placeFlag)
    
    packProgression.save()
    packProgression.compress()
    
    accessor : WriteableRomFileInterface = state.getFileAccessor()
    accessor.writeableFs.replaceFile(PATH_PROGRESSION_DB, packProgression.data)
    return True

def _loadAutoEvent(state : Layton2GameState) -> AutoEvent:
    autoEvent = AutoEvent()
    if (data := state.getFileAccessor().getPackedData(PATH_PROGRESSION_DB, PATH_DB_AUTOEVENT)):
        autoEvent.load(data)
    return autoEvent

def _saveAutoEvent(state : Layton2GameState, autoEvent : AutoEvent) -> bool:
    packProgression = state.getFileAccessor().getPack(PATH_PROGRESSION_DB)
    fileNotFound = True
    # TODO - GetFile
    for file in packProgression.files:
        if file.name == PATH_DB_AUTOEVENT:
            autoEvent.save()
            file.data = autoEvent.data
            fileNotFound = False
            break

    if fileNotFound:
        autoEvent.name = PATH_DB_AUTOEVENT
        autoEvent.save()
        packProgression.files.append(autoEvent)
    
    packProgression.save()
    packProgression.compress()
    
    accessor : WriteableRomFileInterface = state.getFileAccessor()
    accessor.writeableFs.replaceFile(PATH_PROGRESSION_DB, packProgression.data)
    return True

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

def getPackPathForPlaceIndex(indexPlace : int) -> str:
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

def _sortRoomPack(pack : LaytonPack) -> LaytonPack:
    # TODO - Fix in-place when storage API is rewritten
    datPlace = PATH_PACK_PLACE.replace("%i", "%s")
    datPlace = datPlace % ("([0-9]*)", "([0-9]*)")

    placeKeys : Dict[int, Dict[int, bytes]] = {}

    output = LaytonPack()
    for file in pack.files:
        if (result := match(datPlace, file.name)) != None:
            idxPlace = int(result.group(1))
            idxSubPlace = int(result.group(2))
            if idxPlace not in placeKeys:
                placeKeys[idxPlace] = {}

            placeKeys[idxPlace][idxSubPlace] = file.data
    
    for idxPlace in sorted(placeKeys.keys()):
        for idxSubPlace in sorted(placeKeys[idxPlace].keys()):
            output.files.append(File(name=(PATH_PACK_PLACE % (idxPlace, idxSubPlace)), data=placeKeys[idxPlace][idxSubPlace]))

    output.name = pack.name
    return output

def deleteRoom(state : Layton2GameState, indexPlace : int) -> bool:
    autoEvent = _loadAutoEvent(state)
    placeFlag = _loadPlaceFlag(state)

    # TODO - Delete submap info entries
    subMapInfo = None
    
    datPlace = PATH_PACK_PLACE.replace("%i", "%s")
    datPlace = datPlace % (str(indexPlace), "[0-9]*")

    collection = autoEvent.getEntry(indexPlace)
    for x in range(8):
        collection.setSubPlaceEntry(x, AutoEventSubPlaceEntry(0,0,0))
    for entry in placeFlag.entries:
        if entry.roomIndex == indexPlace:
            entry.clear()
    
    pathPlace = getPackPathForPlaceIndex(indexPlace)
    packPlace = state.getFileAccessor().getPack(PATH_PLACE_A)

    for file in reversed(packPlace.files):
        if match(datPlace, file.name) != None:
            packPlace.files.remove(file)
    
    _saveAutoEvent(autoEvent)
    _savePlaceFlag(placeFlag)



def _createRoomByIndexForced(state : Layton2GameState, indexPlace : int, forceDelete : bool = False) -> Optional[PlaceGroup]:
    pathPlace = getPackPathForPlaceIndex(indexPlace)
    packPlace = state.getFileAccessor().getPack(PATH_PLACE_A)

    autoEvent = _loadAutoEvent(state)
    # TODO - Can probably borrow loaded placeflag from state
    placeFlag = _loadPlaceFlag(state)

    # TODO - Delete submap info entries
    subMapInfo = None
    
    datPlace = PATH_PACK_PLACE.replace("%i", "%s")
    datPlace = datPlace % (str(indexPlace), "[0-9]*")

    if forceDelete:
        collection = autoEvent.getEntry(indexPlace)
        for x in range(8):
            collection.setSubPlaceEntry(x, None)
        placeFlag.getEntry(indexPlace).clear()
    
    toRemove = []
    for indexFile, file in packPlace.files:
        pass
    
    

def createRoomAsFirstFree(state : Layton2GameState, minIndex : int = 1, excludeFixedPurpose : bool = True) -> Optional[PlaceGroup]:
    # TODO - Riddleton number
    fixedPurpose : List[int] = [0, 46]
    placeGroups = getPlaceGroups(state.getFileAccessor())
    rooms = {}

    for group in placeGroups:
        rooms[group.indexPlace] = group

    for x in range(max(0, minIndex), 128):
        if (x not in rooms):
            if (excludeFixedPurpose and x not in fixedPurpose) or not(excludeFixedPurpose):
                return _createRoomByIndexForced(state, x)
    return None

def createRoomByIndex(state : Layton2GameState, indexPlace : int, overwrite=False) -> Optional[PlaceGroup]:
    if 0 <= indexPlace < 128:
        if not(overwrite):
            placeGroups = getPlaceGroups(state.getFileAccessor())
            for group in placeGroups:
                if group.indexPlace == indexPlace:
                    if not(overwrite):
                        return None
                    break
        return _createRoomByIndexForced(state, indexPlace, forceDelete = True)
    return None

def deleteRoom(state : Layton2GameState, indexPlace : int) -> bool:
    return False