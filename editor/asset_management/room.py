from typing import Dict, List, Optional
from widebrim.engine.const import PATH_DB_AUTOEVENT, PATH_DB_PLACEFLAG, PATH_DB_RC_ROOT, PATH_DB_SM_INF, PATH_PROGRESSION_DB
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.filesystem.compatibility.compatibilityRom import WriteableRomFileInterface
from widebrim.gamemodes.room.const import PATH_PACK_PLACE, PATH_PLACE_A, PATH_PLACE_B
from widebrim.madhatter.hat_io.asset import File, LaytonPack
from widebrim.engine.file import ReadOnlyFileInterface
from re import search, match

from widebrim.madhatter.hat_io.asset_autoevent import AutoEvent
from widebrim.madhatter.hat_io.asset_dat.place import PlaceDataNds
from widebrim.madhatter.hat_io.asset_dlz.sm_inf import DlzEntrySubmapInfo, SubmapInfoNds

from widebrim.madhatter.hat_io.asset_placeflag import PlaceFlag

def _saveProgressionFile(state : Layton2GameState, newFile : File, path : str) -> bool:
    print("Saving progression file", path)
    packProgression = state.getFileAccessor().getPack(PATH_PROGRESSION_DB)
    fileNotFound = True
    # TODO - GetFile
    for file in packProgression.files:
        if file.name == path:
            newFile.save()
            file.data = newFile.data
            fileNotFound = False
            break

    if fileNotFound:
        print("\tFailed to find progression file!")
        newFile.name = path
        newFile.save()
        packProgression.files.append(newFile)
    
    packProgression.save()
    packProgression.compress()
    
    accessor : WriteableRomFileInterface = state.getFileAccessor()
    accessor.writeableFs.replaceFile(PATH_PROGRESSION_DB, packProgression.data)
    return True

def loadPlaceFlag(state : Layton2GameState) -> PlaceFlag:
    placeFlag = PlaceFlag()
    if (data := state.getFileAccessor().getPackedData(PATH_PROGRESSION_DB, PATH_DB_PLACEFLAG)) != None:
        placeFlag.load(data)
    return placeFlag

def savePlaceFlag(state : Layton2GameState, placeFlag : PlaceFlag) -> bool:
    return _saveProgressionFile(state, placeFlag, PATH_DB_PLACEFLAG)

def loadAutoEvent(state : Layton2GameState) -> AutoEvent:
    autoEvent = AutoEvent()
    if (data := state.getFileAccessor().getPackedData(PATH_PROGRESSION_DB, PATH_DB_AUTOEVENT)) != None:
        autoEvent.load(data)
    return autoEvent

def saveAutoEvent(state : Layton2GameState, autoEvent : AutoEvent) -> bool:
    return _saveProgressionFile(state, autoEvent, PATH_DB_AUTOEVENT)

def _loadSubmapInfo(state : Layton2GameState) -> SubmapInfoNds:
    output = SubmapInfoNds()
    if (submapData := state.getFileAccessor().getData(PATH_DB_RC_ROOT % PATH_DB_SM_INF)) != None:
        output.load(submapData)
    return output

def _saveSubmapInfo(state : Layton2GameState, submapInfo : SubmapInfoNds) -> bool:
    fileAccessor : WriteableRomFileInterface = state.getFileAccessor()
    submapInfo.save()
    submapInfo.compress()
    return fileAccessor.writeableFs.replaceFile(PATH_DB_RC_ROOT % PATH_DB_SM_INF, submapInfo.data)

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
    print("Deleting room", indexPlace)
    if not(0 <= indexPlace < 128):
        return False

    autoEvent = loadAutoEvent(state)
    placeFlag = loadPlaceFlag(state)
    subMapInfo = _loadSubmapInfo(state)
    
    datPlace = PATH_PACK_PLACE.replace("%i", "%s")
    datPlace = datPlace % (str(indexPlace), "[0-9]*")

    collection = autoEvent.getEntry(indexPlace)
    for x in range(8):
        collection.getSubPlaceEntry(x).clear()
    
    placeFlagEntry = placeFlag.getEntry(indexPlace)
    if placeFlagEntry != None:
        placeFlagEntry.clear()

    for indexEntry in range(subMapInfo.getCountEntries()):
        entry : DlzEntrySubmapInfo = subMapInfo.getEntry(indexEntry)
        if entry.indexPlace == indexPlace:
            subMapInfo.removeEntry(indexEntry)

    pathPlace = getPackPathForPlaceIndex(indexPlace)
    packPlace = state.getFileAccessor().getPack(pathPlace)

    for file in reversed(packPlace.files):
        if match(datPlace, file.name) != None:
            packPlace.files.remove(file)
    
    saveAutoEvent(state, autoEvent)
    savePlaceFlag(state, placeFlag)
    _saveSubmapInfo(state, subMapInfo)
    packPlace.save()
    packPlace.compress()
    return state.getFileAccessor().writeableFs.replaceFile(pathPlace, packPlace.data)

def _createRoomByIndexForced(state : Layton2GameState, indexPlace : int, forceDelete : bool = True) -> Optional[PlaceGroup]:
    if forceDelete:
        if not(deleteRoom(state, indexPlace)):
            return None

    pathPlace = getPackPathForPlaceIndex(indexPlace)
    packPlace = state.getFileAccessor().getPack(pathPlace)

    # After deleting, everything should be ready (initial state is ignored, so should be good to just add data...)
    newPlaceData = PlaceDataNds()
    newPlaceData.name = PATH_PACK_PLACE % (indexPlace, 0)
    newPlaceData.save()
    packPlace.files.append(newPlaceData)

    packPlace.save()
    packPlace.compress()
    if state.getFileAccessor().writeableFs.replaceFile(pathPlace, packPlace.data):
        return PlaceGroup(indexPlace, [0])
    return None

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