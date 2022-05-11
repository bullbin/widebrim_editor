from widebrim.engine.const import EVENT_ID_START_PUZZLE, EVENT_ID_START_TEA, PATH_DB_EV_INF2, PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_PACK_EVENT_SCR
from widebrim.engine.file import FileInterface
from widebrim.engine_ext.utils import substituteLanguageString

from typing import List, Tuple, Type
from widebrim.engine.state.state import Layton2GameState
from widebrim.madhatter.common import log
from widebrim.madhatter.hat_io.asset_dlz.ev_inf2 import EventInfoList

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
def getEvents(laytonState : Layton2GameState) -> Tuple[Tuple[List[int], List[int]], List[Type[EventExecutionGroup]]]:
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
                if FileInterface.doesFileExist(PATH_EVENT_SCRIPT_A % x) or FileInterface.doesFileExist(PATH_EVENT_SCRIPT_B % x) or FileInterface.doesFileExist(PATH_EVENT_SCRIPT_C % x):
                    output.append(x)
            else:
                if FileInterface.doesFileExist(PATH_EVENT_SCRIPT % x):
                    output.append(x)
        return output
    
    def addEventsFromIdToUntracked(ids : List[int]):
        def exploreArchive(path : str, id : int, start=0, stop=1000):
            packArchive = FileInterface.getPack(path)
            for x in range(start, stop):
                pathScript = PATH_PACK_EVENT_SCR % (id, x)
                if packArchive.getData(pathScript) != None:
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
        if (data := FileInterface.getData(pathEventDb)) != None:
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