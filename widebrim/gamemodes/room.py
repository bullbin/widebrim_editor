from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES

class RoomPlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)

        self.laytonState = laytonState
        self._calculateChapter()
        self._calculateRoom()
        if self._executeAutoEvent():
            self.laytonState.setGameModeNext(GAMEMODES.DramaEvent)
            self._canBeKilled = True
            
        print("Attempted to load room", self.laytonState.saveSlot.roomIndex, self.laytonState.saveSlot.roomSubIndex)

        # self._canBeKilled = True

    def _executeAutoEvent(self):

        def hasAutoEventBeenExecuted(eventId):
            eventInfo = self.laytonState.getEventInfoEntry(eventId)
            if eventInfo.indexEventViewedFlag != None:
                return self.laytonState.saveSlot.eventViewed.getSlot(eventInfo.indexEventViewedFlag)
            return False

        autoEvent = self.laytonState.dbAutoEvent

        autoEventId = None
        for entryId in range(8):
            # Chapter definitely used here
            entry = autoEvent.entries[self.laytonState.saveSlot.roomIndex].getSubPlaceEntry(entryId)
            if entry != None and entry.chapterStart <= self.laytonState.saveSlot.chapter < entry.chapterEnd:
                autoEventId = entry.idEvent
        
        if autoEventId != None:
            # TODO - Can there be multiple autoevents that pass the above check?
            if hasAutoEventBeenExecuted(autoEventId):
                return False
            self.laytonState.setEventId(autoEventId)
            return True
        return False

    def _calculateChapter(self):

        storyFlag = self.laytonState.dbStoryFlag
        saveSlot = self.laytonState.saveSlot

        indexStoryFlag = storyFlag.getIndexFromChapter(saveSlot.chapter)

        while indexStoryFlag < 256:

            storyFlagEntry = storyFlag.getGroupAtIndex(indexStoryFlag)

            for indexSubFlag in range(8):
                subFlag = storyFlagEntry.getFlag(indexSubFlag)
                if subFlag.type == 2:
                    if not(saveSlot.puzzleData.getPuzzleData(subFlag.param).wasSolved):
                        saveSlot.chapter = storyFlag.getGroupAtIndex(indexStoryFlag).getChapter()
                        return

                elif subFlag.type == 1:
                    if not(saveSlot.storyFlag.getSlot(subFlag.param)):
                        saveSlot.chapter = storyFlag.getGroupAtIndex(indexStoryFlag).getChapter()
                        return

            indexStoryFlag += 1

    def _calculateRoom(self):

        def checkEventCounter(placeFlagEntry):
            if placeFlagEntry.indexEventCounter > 127:
                return False

            eventCounterEncoded = self.laytonState.saveSlot.eventCounter.toBytes(outLength=128)
            
            output = False
            if placeFlagEntry.decodeMode == 2:
                if placeFlagEntry.unk1 <= eventCounterEncoded[placeFlagEntry.indexEventCounter]:
                    output = True
            elif placeFlagEntry.decodeMode == 1:
                if eventCounterEncoded[placeFlagEntry.indexEventCounter] - placeFlagEntry.unk1 != 0:
                    output = True
            elif placeFlagEntry.decodeMode == 0:
                if eventCounterEncoded[placeFlagEntry.indexEventCounter] - placeFlagEntry.unk1 == 0:
                    output = True
            return output

        placeFlag = self.laytonState.dbPlaceFlag
        indexRoom = self.laytonState.saveSlot.roomIndex

        self._calculateChapter()

        indexSubRoom = 0
        for proposedSubRoom in range(1,16):
            placeFlagEntry = placeFlag.entries[indexRoom].getEntry(proposedSubRoom)
            placeFlagCounterEntry = placeFlag.entries[indexRoom].getCounterEntry(proposedSubRoom)
            if placeFlagEntry.chapterStart == 0 or placeFlagEntry.chapterEnd == 0:
                #print("\tBroken on proposed", proposedSubRoom)
                break

            chapter = self.laytonState.saveSlot.chapter
            workingSubRoom = indexSubRoom
            if placeFlagEntry.chapterStart <= chapter and placeFlagEntry.chapterEnd >= chapter:
                workingSubRoom = proposedSubRoom

                if placeFlagCounterEntry.indexEventCounter != 0:
                    workingSubRoom = indexSubRoom
                    if checkEventCounter(placeFlagCounterEntry):
                        workingSubRoom = proposedSubRoom
            #else:
            #    print("\tFailed chapter check for", proposedSubRoom, "wanted", placeFlagEntry.chapterStart)
            
            indexSubRoom = workingSubRoom
        
        self.laytonState.saveSlot.roomSubIndex = indexSubRoom