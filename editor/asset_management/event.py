from .chapter import loadStoryFlag
from widebrim.engine.const import EVENT_ID_START_PUZZLE, EVENT_ID_START_TEA, PATH_DB_EV_INF2, PATH_DB_RC_ROOT, PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_PACK_EVENT_DAT, PATH_PACK_EVENT_SCR
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.engine_ext.utils import substituteLanguageString

from typing import Dict, List, Optional, Tuple, Type
from widebrim.engine.state.manager import Layton2GameState
from widebrim.madhatter.common import log, logSevere
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.madhatter.hat_io.asset_dat.event import EventData
from widebrim.madhatter.hat_io.asset_dlz.ev_inf2 import DlzEntryEvInf2, EventInfoList

from widebrim.engine.const import PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C
from widebrim.madhatter.hat_io.asset_dlz.ev_lch import DlzEntryEventDescriptorBank, DlzEntryEventDescriptorBankNds, EventDescriptorBankNds
from widebrim.madhatter.hat_io.asset_script import GdScript

class EventExecutionGroup():
    def __init__(self, group : List[int]):
        self.group = group
    
    def __str__(self):
        return "Unknwn :: " + str(self.group)

# TODO - Puzzle ID is given during execution. Not guarenteed (can be overriden by script, don't know the effects...)
class PuzzleExecutionGroup(EventExecutionGroup):
    def __init__(self, idInternalPuzzle : int, idBase : int, idRetry : int, idReturnAfterSolve : int, idSolve : int, idSkip : int):
        super().__init__([idBase, idRetry, idReturnAfterSolve, idSolve, idSkip])
        self.idInternalPuzzle = idInternalPuzzle
        self.idBase = idBase
        self.idRetry = idRetry
        self.idReturnAfterSolve = idReturnAfterSolve
        self.idSolve = idSolve
        self.idSkip = idSkip
    
    def __str__(self):
        return "Puzzle Group " + str(self.idInternalPuzzle) + "\nBase   :: " + str(self.idBase) + "\nRetry  :: " + str(self.idRetry) + "\nReturn :: " + str(self.idReturnAfterSolve) + "\nSolve  :: " + str(self.idSolve) + "\nSkip   :: " + str(self.idSkip)

class TeaExecutionGroup(EventExecutionGroup):
    def __init__(self, idBase : int, idSolve : int, idFail : int, idSkip : int, idRetry : int):
        super().__init__([idBase, idSolve, idFail, idSkip, idRetry])
        self.idBase = idBase
        self.idSolve = idSolve
        self.idFail = idFail
        self.idSkip = idSkip
        self.idRetry = idRetry
    
    def __str__(self):
        return "Tea Group\nBase   :: " + str(self.idBase) + "\nSolve  :: " + str(self.idSolve) + "\nFail   :: " + str(self.idFail) + "\nSkip   :: " + str(self.idSkip) + "\nRetry  :: " + str(self.idRetry)

class EventConditionAwaitingViewedExecutionGroup(EventExecutionGroup):
    def __init__(self, flagViewed, idBase, idViewed):
        super().__init__([idBase, idViewed])
        self.idBase = idBase
        self.idViewed = idViewed
        self.flagViewed = flagViewed
    
    def __str__(self):
        return "Event Conditional (jump if viewed, flag " + str(self.flagViewed) + ")\nBase   :: " + str(self.idBase) + "\nViewed :: " + str(self.idViewed)

class EventConditionPuzzleExecutionGroup(EventConditionAwaitingViewedExecutionGroup, EventExecutionGroup):
    def __init__(self, limit, flagViewed, idBase, idViewed, idSuccessful):
        EventConditionAwaitingViewedExecutionGroup.__init__(self, flagViewed, idBase, idViewed)
        self.group.append(idSuccessful)
        self.limit = limit
        self.idSuccessful = idSuccessful
    
    def __str__(self):
        return "Event Conditional (jump if " + str(self.limit) + " puzzles solved and jump if viewed, flag " + str(self.flagViewed) + ")\nBase   :: " + str(self.idBase) + "\nViewed :: " + str(self.idViewed) + "\nLimit  :: " + str(self.idSuccessful)

# TODO - Refigure out tea hooks for random events
# Room: No effective limit, can launch any handler. But branching on room loading and event setting?
def getEvents(filesystem : WriteableFilesystemCompatibilityLayer, laytonState : Layton2GameState) -> Tuple[Tuple[List[int], List[int]], List[Type[EventExecutionGroup]]]:
    """Gets a list of every event stored inside ROM and bundles them according to branching rules.
    
    Note that this approach does not take into account engine edits or forced behaviours, eg breaking execution by jumping to leaves in event branches rather than the head itself.
    This is exhaustive but groups may not be accurate to execution.

    Args:
        laytonState (Layton2GameState): Game state used for language pathing.

    Returns:
        Tuple[Tuple[List[int], List[int]], List[Type[EventExecutionGroup]]]: Form of (   ([Events in database], [Events not in database])   , [Event branches])
    """
    eventsUntracked = []
    eventsTracked = []
    eventsMissing = []
    eventGroups = []
    eventsGrouped = []

    # TODO - Hook to vfs, has proper implementation of file finding...
    def getEventArchiveIds() -> List[int]:
        output = []
        for x in range(10, 100):
            if x == 24:
                if filesystem.doesFileExist(PATH_EVENT_SCRIPT_A % x) or filesystem.doesFileExist(PATH_EVENT_SCRIPT_B % x) or filesystem.doesFileExist(PATH_EVENT_SCRIPT_C % x):
                    output.append(x)
            else:
                if filesystem.doesFileExist(PATH_EVENT_SCRIPT % x):
                    output.append(x)
        return output
    
    def addEventsFromIdToUntracked(ids : List[int]):
        def exploreArchive(path : str, id : int, start=0, stop=1000):
            packArchive = filesystem.getPack(path)
            for x in range(start, stop):
                pathScript = PATH_PACK_EVENT_SCR % (id, x)
                if packArchive.getFile(pathScript) != None:
                    eventsUntracked.append((id * 1000) + x)
        
        for id in ids:
            if id == 24:
                exploreArchive(PATH_EVENT_SCRIPT_A % id, id, stop=300)
                exploreArchive(PATH_EVENT_SCRIPT_B % id, id, start=300, stop=600)
                exploreArchive(PATH_EVENT_SCRIPT_C % id, id, start=600)
            else:
                exploreArchive(PATH_EVENT_SCRIPT % id, id)

    def classifyByEventDatabase():
        eventDb = EventInfoList()
        pathEventDb = substituteLanguageString(laytonState, PATH_DB_EV_INF2)
        if (data := filesystem.getData(pathEventDb)) != None:
            eventDb.load(data)
        
        for indexEntry in range(eventDb.getCountEntries()):
            entry = eventDb.getEntry(indexEntry)
            if entry.idEvent in eventsUntracked:
                # Tea Event
                if entry.idEvent >= EVENT_ID_START_TEA:
                    # TODO - Figure out progression on these
                    # 0 - Base tea event
                    # 1 - Tea solved event
                    # 2 - Tea failed event
                    # 3 - Tea quit event
                    # 4 - Tea retry event (event viewed flag)
                    tempGroup = []
                    for testId in [entry.idEvent, entry.idEvent + 1, entry.idEvent + 2, entry.idEvent + 3, entry.idEvent + 4]:
                        if testId in eventsUntracked:
                            eventsUntracked.remove(testId)
                            tempGroup.append(testId)
                            eventsGrouped.append(testId)
                        else:
                            tempGroup.append(None)

                    eventGroups.append(TeaExecutionGroup(tempGroup[0], tempGroup[1], tempGroup[2], tempGroup[3], tempGroup[4]))
                    continue
                
                # Puzzle Event (designated IDs) - TODO Room Event set
                elif entry.idEvent >= EVENT_ID_START_PUZZLE:
                    # Base - 0
                    # Viewed again - 1
                    # Viewed after solved - 2
                    # Solved - 3
                    # Skipped - 4
                    # TODO - Will fail on bad scripting input (eg offset.) But this really shouldn't be offset anyways!
                    tempGroup = []
                    for testId in [entry.idEvent, entry.idEvent + 1, entry.idEvent + 2, entry.idEvent + 3, entry.idEvent + 4]:
                        if testId in eventsUntracked:
                            eventsUntracked.remove(testId)
                            tempGroup.append(testId)
                            eventsGrouped.append(testId)
                        else:
                            # TODO - Proper formatting...
                            tempGroup.append(None)

                    eventGroups.append(PuzzleExecutionGroup(entry.dataPuzzle, tempGroup[0], tempGroup[1], tempGroup[2], tempGroup[3], tempGroup[4]))
                    continue

                else:
                    tempGroup = [entry.idEvent]

                    # Type 6 - Room Do, some strange stateful measure
                    if entry.typeEvent == 5:
                        # Puzzle limit then if already viewed...
                        if entry.idEvent + 2 in eventsUntracked:
                            tempGroup.append(entry.idEvent + 2)
                            eventsGrouped.append(entry.idEvent + 2)
                            eventsUntracked.remove(entry.idEvent + 2)
                        else:
                            tempGroup.append(None)

                    # Type 4 - Puzzle that disappears after solved

                    # Type 3 - Unknown...

                    # If already viewed...
                    if entry.typeEvent == 2 or entry.typeEvent == 5:
                        if entry.idEvent + 1 in eventsUntracked:
                            tempGroup.append(entry.idEvent + 1)
                            eventsGrouped.append(entry.idEvent + 1)
                            eventsUntracked.remove(entry.idEvent + 1)
                        else:
                            tempGroup.append(None)
                        
                        if len(tempGroup) == 3:
                            eventGroups.append(EventConditionPuzzleExecutionGroup(entry.dataPuzzle, entry.indexEventViewedFlag, tempGroup[0], tempGroup[2], tempGroup[1]))
                        else:
                            eventGroups.append(EventConditionAwaitingViewedExecutionGroup(entry.indexEventViewedFlag, tempGroup[0], tempGroup[1]))
                        eventsUntracked.remove(entry.idEvent)
                        continue

                    # Type 1 - Disappears after viewed
                eventsTracked.append(entry.idEvent)
                eventsUntracked.remove(entry.idEvent)

            elif entry.idEvent not in eventsTracked and entry.idEvent not in eventsGrouped:
                eventsMissing.append(entry.idEvent)
        
        for eventId in eventsTracked:
            entry = eventDb.searchForEntry(eventId)
            if entry.typeEvent not in [0,1,4]:
                log("Broken link", entry.idEvent, entry.typeEvent)

    #def cullUntrackedNullScripts():
    #    for eventId in eventsUntracked:

    addEventsFromIdToUntracked(getEventArchiveIds())
    classifyByEventDatabase()

    return ((eventsTracked, eventsUntracked), eventGroups)

def __createEventFromList(filesystem : WriteableFilesystemCompatibilityLayer, idEvents : List[int]):
    
    def getEventPaths(id) -> Tuple[Tuple[str,str], str]:
        packId = id // 1000
        
        subId = id % 1000
        if packId != 24:
            pathPack = PATH_EVENT_SCRIPT
        else:
            if subId < 300:
                pathPack = PATH_EVENT_SCRIPT_A
            elif subId < 600:
                pathPack = PATH_EVENT_SCRIPT_B
            else:
                pathPack = PATH_EVENT_SCRIPT_C
        
        pathPack = pathPack % packId
        nameId = PATH_PACK_EVENT_SCR % (packId, subId)
        nameDat = PATH_PACK_EVENT_DAT % (packId, subId)
        return ((nameId, nameDat), pathPack)
    
    idEvents = list(idEvents)
    idEvents.sort()

    packOpenPath = None
    packEvent : Optional[LaytonPack] = None
    for id in idEvents:
        filenames, pathPack = getEventPaths(id)
        nameId, nameDat = filenames

        if pathPack != packOpenPath:
            if packOpenPath != None:
                packEvent : LaytonPack
                packEvent.files.sort(key=lambda x: x.name)
                packEvent.save()
                packEvent.compress()
                filesystem.writeableFs.replaceFile(packOpenPath, packEvent.data)
            
            packEvent = filesystem.getPack(pathPack)
            packOpenPath = pathPack
        
        # TODO - madhatter currently zeroes out music section. Not breaking but it should be copied from database (convention)
        # TODO - rewrite laytonPack, too much unabstracted access...
        fileEvent = GdScript()
        fileEventData = EventData()
        fileEvent.save()
        fileEventData.save()
        fileEvent.name = nameId
        fileEventData.name = nameDat
        packEvent.files.append(fileEvent)
        packEvent.files.append(fileEventData)
    
    if packOpenPath != None:
        packEvent : LaytonPack
        packEvent.files.sort(key=lambda x: x.name)
        packEvent.save()
        packEvent.compress()
        filesystem.writeableFs.replaceFile(packOpenPath, packEvent.data)

def __createEventDatabaseEntries(filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, idEvents : List[int], names : List[str] = [], addOptional : bool = False):
    evLch = EventDescriptorBankNds()
    evInf = EventInfoList()

    if (data := filesystem.getData(substituteLanguageString(state, PATH_DB_RC_ROOT % ("%s/ev_lch.dlz")))) != None:
        evLch.load(data)
    if (data := filesystem.getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)
    
    # TODO - Sort
    for indexEvent, id in enumerate(idEvents):
        entry = evInf.searchForEntry(id)
        if entry == None:
            newEntry = DlzEntryEvInf2(id, 0, id, None, None, None)
            evInf.addEntry(newEntry)
        else:
            entry.dataPuzzle = None
            entry.indexEventViewedFlag = None
            entry.indexStoryFlag = None
            entry.idEvent = id
            entry.dataSoundSet = id
            entry.typeEvent = 0
        
        entry = evLch.searchForEntry(id)
        if indexEvent < len(names):
            nameString = names[indexEvent]
        else:
            nameString = "New widebrim Event"

        if entry == None:
            newEntry = DlzEntryEventDescriptorBankNds(id, nameString)
            evLch.addEntry(newEntry)
        else:
            entry.description = nameString

    evInf.save()
    evInf.compress()
    filesystem.writeableFs.replaceFile(substituteLanguageString(state, PATH_DB_EV_INF2), evInf.data)

    evLch.save()
    evLch.compress()
    filesystem.writeableFs.replaceFile(substituteLanguageString(state, PATH_DB_RC_ROOT % ("%s/ev_lch.dlz")), evLch.data)

    # TODO - this is not good, avoid using files from widebrim's state outside of the preview engine!
    state.unloadEventInfoDb()

def createBlankEvent(filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, idEvent : int) -> int:
    """Creates a template event alongside data. This adds entries for the string and event databases, alongside empty event data and an empty event script.
    
    Note: This will overwrite any event existing with that ID.

    Args:
        filesystem (WriteableFilesystemCompatibilityLayer): _description_
        state (Layton2GameState): _description_
        idEvent (int): _description_

    Returns:
        int: _description_
    """

    __createEventFromList(filesystem, [idEvent])
    __createEventDatabaseEntries(filesystem, state, [idEvent])
    return idEvent

# TODO - Maybe just use puzzle entry
def createBlankPuzzleEventChain(filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, baseIdEvent : int, internalPuzzleId : int, externalPuzzleId : int) -> PuzzleExecutionGroup:
    idEvents = [baseIdEvent, baseIdEvent + 1, baseIdEvent + 2, baseIdEvent + 3, baseIdEvent + 4]
    nameEvents = ["(S)No.%03i" % externalPuzzleId, "(R)No.%03i" % externalPuzzleId, "(A)No.%03i" % externalPuzzleId, "(C)No.%03i" % externalPuzzleId, "(F)No.%03i" % externalPuzzleId]
    
    __createEventFromList(filesystem, idEvents)
    __createEventDatabaseEntries(filesystem, state, idEvents, nameEvents)

    # TODO - Hold these open
    evInf = EventInfoList()
    if (data := filesystem.getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)

    for id in idEvents:
        entryInf = evInf.searchForEntry(id)
        if (id - baseIdEvent) < 2:
            entryInf.dataPuzzle = internalPuzzleId
    
    evInf.save()
    evInf.compress()
    filesystem.writeableFs.replaceFile(substituteLanguageString(state, PATH_DB_EV_INF2), evInf.data)
    
    # TODO - Entry events need to do switch gamemode and launch puzzle commands
    return PuzzleExecutionGroup(internalPuzzleId, idEvents[0], idEvents[1], idEvents[2], idEvents[3], idEvents[4])

def createBlankTeaEventChain(filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, baseIdEvent : int):
    pass

def ensureEventInDatabase(state : Layton2GameState, idEvent : int):
    evLch = EventDescriptorBankNds()
    evInf = EventInfoList()

    if (data := state.getFileAccessor().getData(substituteLanguageString(state, PATH_DB_RC_ROOT % ("%s/ev_lch.dlz")))) != None:
        evLch.load(data)
    if (data := state.getFileAccessor().getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)
    
    # TODO - Sort
    entryInf = evInf.searchForEntry(idEvent)
    entryLch = evLch.searchForEntry(idEvent)

    if entryInf == None:
        logSevere("Recovered event database for", idEvent)
        newEntry = DlzEntryEvInf2(id, 0, id, None, None, None)
        evInf.addEntry(newEntry)
    if entryLch == None:
        logSevere("Adding placeholder comment for", idEvent)
        newEntry = DlzEntryEventDescriptorBank(idEvent, "Recovered event database for " + str(idEvent))
        entryLch.addEntry(newEntry)
    
    evInf.save()
    evInf.compress()
    state.getFileAccessor().writeableFs.replaceFile(substituteLanguageString(state, PATH_DB_EV_INF2), evInf.data)

    evLch.save()
    evLch.compress()
    state.getFileAccessor().writeableFs.replaceFile(substituteLanguageString(state, PATH_DB_RC_ROOT % ("%s/ev_lch.dlz")), evLch.data)

    # TODO - this is not good, avoid using files from widebrim's state outside of the preview engine!
    state.unloadEventInfoDb()

# TODO - Removable..?
def createConditionalRevisit(filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, baseIdEvent : int, flagRevisit : int) -> EventConditionAwaitingViewedExecutionGroup:
    idEvents = [baseIdEvent, baseIdEvent + 1]
    nameEvents = ["widebrim Conditional", "widebrim Conditional 2"]
    __createEventFromList(filesystem, idEvents)
    __createEventDatabaseEntries(filesystem, state, idEvents, names=nameEvents)

    evInf = EventInfoList()
    if (data := filesystem.getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)

    # TODO - i hope i didn't use any widebrim state accessors here...
    baseEvInf = evInf.searchForEntry(baseIdEvent)
    baseEvInf.typeEvent = 2
    baseEvInf.indexEventViewedFlag = flagRevisit

    evInf.save()
    evInf.compress()
    filesystem.writeableFs.replaceFile(substituteLanguageString(state, PATH_DB_EV_INF2), evInf.data)

    return EventConditionAwaitingViewedExecutionGroup(flagRevisit, baseIdEvent, baseIdEvent + 1)

def createConditionalRevisitAndPuzzleLimit(filesystem : WriteableFilesystemCompatibilityLayer, state : Layton2GameState, baseIdEvent : int, flagRevisit : int, limit : int) -> EventConditionPuzzleExecutionGroup:
    idEvents = [baseIdEvent, baseIdEvent + 1, baseIdEvent + 2]
    nameEvents = ["widebrim Conditional", "widebrim Conditional Retry", "widebrim Conditional Achieved"]
    __createEventFromList(filesystem, idEvents)
    __createEventDatabaseEntries(filesystem, state, idEvents, names=nameEvents)

    evInf = EventInfoList()
    if (data := filesystem.getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)

    # TODO - i hope i didn't use any widebrim state accessors here...
    baseEvInf = evInf.searchForEntry(baseIdEvent)
    baseEvInf.typeEvent = 5
    baseEvInf.indexEventViewedFlag = flagRevisit
    baseEvInf.dataPuzzle = limit

    evInf.save()
    evInf.compress()
    filesystem.writeableFs.replaceFile(substituteLanguageString(state, PATH_DB_EV_INF2), evInf.data)

    return EventConditionPuzzleExecutionGroup(limit, flagRevisit, idEvents[0], idEvents[1], idEvents[2])

def getUsedEventViewedFlags(state : Layton2GameState) -> Dict[int, int]:
    evInf = EventInfoList()
    if (data := state.getFileAccessor().getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)
    
    output = {}

    for indexEntry in range(evInf.getCountEntries()):
        entry = evInf.getEntry(indexEntry)
        if entry.indexEventViewedFlag != None:
            output[entry.idEvent] = entry.indexEventViewedFlag
    
    return output

def getFreeEventViewedFlags(state : Layton2GameState) -> List[int]:
    """Returns a list of available flags for the EventViewed store in the save. These results are generated using event decoding heuristics so are susceptible to 'unexpected' behaviour.

    Args:
        filesystem (WriteableFilesystemCompatibilityLayer): Filesystem for event information decoding.
        state (Layton2GameState): State used for language fetching.

    Returns:
        List[int]: List of available EventViewed flags.
    """
    usedFlags = getUsedEventViewedFlags(state)

    flags = []
    for x in range(1024):
        flags.append(x)
    
    for usedIndex in usedFlags.values():
        try:
            flags.remove(usedIndex)
        except ValueError:
            logSevere("Event shares EventViewed", usedIndex)

    return flags

def getUsedStoryFlags(state : Layton2GameState) -> Dict[int, int]:
    evInf = EventInfoList()
    if (data := state.getFileAccessor().getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)
    
    output = {}

    for indexEntry in range(evInf.getCountEntries()):
        entry = evInf.getEntry(indexEntry)
        if entry.indexStoryFlag != None:
            if entry.idEvent in output:
                logSevere("UsedStoryFlags: Duplicate detected on", entry.idEvent)
            output[entry.idEvent] = entry.indexStoryFlag
    
    return output

def getFreeStoryFlags(state : Layton2GameState) -> List[int]:
    # TODO - Research whether any are forced (e.g. event variables)
    usedFlags = getUsedStoryFlags(state)

    flags = []
    for x in range(128):
        flags.append(x)
    
    for usedIndex in usedFlags.values():
        try:
            flags.remove(usedIndex)
        except ValueError:
            logSevere("Event shares StoryFlag", usedIndex)

    return flags

def giveEventStoryFlag(state : Layton2GameState, idEvent : int) -> Optional[int]:
    ensureEventInDatabase(state, idEvent)

    evInf = EventInfoList()
    if (data := state.getFileAccessor().getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)

    entry = evInf.searchForEntry(idEvent)

    # Verified: Any event type is permitted storyflag, it will be applied during event sequence regardless
    if entry.indexStoryFlag == None:
        logSevere("EventStoryFlag: Called to add new story flag to", idEvent)
        freeStoryFlags = getFreeStoryFlags(state)
        if len(freeStoryFlags) == 0:
            logSevere("EventStoryFlag: Out of flags!")
            return None

        entry.indexStoryFlag = freeStoryFlags.pop(0)
        logSevere("EventStoryFlag: Added", entry.indexStoryFlag)
        evInf.save()
        evInf.compress()
        state.getFileAccessor().writeableFs.replaceFile(substituteLanguageString(state, PATH_DB_EV_INF2), evInf.data)

        # TODO - this is not good, avoid using files from widebrim's state outside of the preview engine!
        state.unloadEventInfoDb()
    else:
        logSevere("EventStoryFlag:", idEvent, "has flag", entry.indexStoryFlag)

    return entry.indexStoryFlag

def giveEventViewedFlag(state : Layton2GameState, idEvent : int) -> Optional[int]:
    freeFlags = getFreeEventViewedFlags(state)
    if len(freeFlags) == 0:
        logSevere("EventViewedFlags: Out of event viewed flags!")
        return None

    ensureEventInDatabase(state, idEvent)
    evInf = EventInfoList()
    if (data := state.getFileAccessor().getData(substituteLanguageString(state, PATH_DB_EV_INF2))) != None:
        evInf.load(data)

    entry = evInf.searchForEntry(idEvent)

    if entry.indexEventViewedFlag == None:
        if entry.typeEvent == 0:
            logSevere("EventViewedFlags: Upgraded event to type 3!")
            entry.typeEvent = 3
        entry.indexEventViewedFlag = freeFlags.pop(0)
        evInf.save()
        evInf.compress()
        state.getFileAccessor().writeableFs.replaceFile(substituteLanguageString(state, PATH_DB_EV_INF2), evInf.data)

        # TODO - this is not good, avoid using files from widebrim's state outside of the preview engine!
        state.unloadEventInfoDb()

    return entry.indexEventViewedFlag