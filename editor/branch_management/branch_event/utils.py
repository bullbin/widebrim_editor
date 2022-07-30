
from widebrim.engine.state.manager.state import Layton2GameState

def getNameForPuzzle(state : Layton2GameState, internalPuzzleId : int) -> str:
    if (entry := state.getNazoListEntry(internalPuzzleId)) != None:
        return "%03d - %s" % (entry.idExternal, entry.name)
    return "i%03d" % internalPuzzleId

def getNameForEvent(state : Layton2GameState, eventId : int, tabName : bool = True) -> str:
    """_summary_

    Args:
        state (Layton2GameState): _description_
        eventId (int): _description_

    Returns:
        str: _description_
    """

    # TODO - Merge into branch_event for unified name generation, will produce more consistent results

    eventDescriptor = None

    if eventId < 20000:
        # If the event is not in the event DB, it is automatically non-conditional
        # There are two other conditions:
        # - Event type 2:
        #     - base event, base event + 1
        # - Event type 5:
        #     - base event, base event + 1, base event + 2
        if state.getEventInfoEntry(eventId) == None:
            return str(eventId)
        else:
            if (entry := state.getEventInfoEntry(eventId - 2)) != None:
                if entry.typeEvent == 5:
                    # Limit viewed, successful event
                    return "%i - Limit Met" % (eventId - 2)
            if (entry := state.getEventInfoEntry(eventId - 1)) != None:
                if entry.typeEvent == 2 or entry.typeEvent == 5:
                    # Visited again
                    return "%i - Next Visit" % (eventId - 1)

            entry = state.getEventInfoEntry(eventId)
            if entry.typeEvent == 2 or entry.typeEvent == 5:
                # Conditional branch root
                return str(eventId) + " - Initial"
            elif entry.typeEvent == 1:
                # TODO - type 4?
                # Removable
                return str(eventId) + " (Removable)"
        
        if entry.typeEvent == 0:
            return str(eventId)
        elif entry.typeEvent == 3:
            return str(eventId) + " (No branching)"
        elif entry.typeEvent == 6:
            return str(eventId) + " (AutoEvent specific)"
        else:
            return str(eventId) + " (Unknown " + str(entry.typeEvent) + ")"

    elif eventId <= 30000:
        # Not a great heuristic but who cares
        branchId = eventId % 5
        evInfBase = state.getEventInfoEntry(eventId - branchId)
        isRemovable = False
        if evInfBase != None:
            name = getNameForPuzzle(state, evInfBase.dataPuzzle)
            if evInfBase.typeEvent == 4:
                isRemovable = True
        else:
            name = "UnkPuzzle %i" % eventId
        
        if branchId == 0:
            name += " - Initial"
        elif branchId == 1:
            name += " - Reattempt"
        elif branchId == 2:
            name += " - Revisit"
        elif branchId == 3:
            name += " - Solved"
        else:
            name += " - Skipped"
        
        if isRemovable:
            name += " (Removable)"
        return name
    else:
        return str(eventId) + "(Unimplemented)"