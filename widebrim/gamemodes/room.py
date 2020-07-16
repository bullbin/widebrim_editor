from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES
from ..engine.file import FileInterface
from ..engine.anim.image_anim import AnimatedImageObject
from ..engine.exceptions import FileInvalidCritical
from ..engine.const import PATH_PLACE_A, PATH_PLACE_B, PATH_PACK_PLACE, PATH_PLACE_BG, PATH_PLACE_MAP, PATH_ANI, PATH_EXT_BGANI, RESOLUTION_NINTENDO_DS, PATH_EXT_EXIT, PATH_EXT_EVENT

from pygame import MOUSEBUTTONUP

from ..madhatter.hat_io.asset import LaytonPack
from ..madhatter.hat_io.asset_image import AnimatedImage
from ..madhatter.hat_io.asset_dat.place import PlaceData

from time import time

def wasBoundingCollided(bounding, pos):
    if bounding.x <= pos[0] and bounding.y <= pos[1]:
        if (bounding.x + bounding.width) >= pos[0] and (bounding.y + bounding.height) >= pos[1]:
            return True
    return False

class RoomPlayer(ScreenLayerNonBlocking):

    # TODO - Speed up loading. Stutter exceeds 500ms which causes faders to look very strange

    EXIT_IMAGES_OFF = []
    EXIT_IMAGES_ON  = []

    for indexExitImage in range(8):
        tempExitAsset = FileInterface.getData(PATH_ANI % (PATH_EXT_EXIT % indexExitImage))

        # TODO - Button anim type

        if tempExitAsset != None:
            exitAsset = AnimatedImageObject.fromMadhatter(AnimatedImage.fromBytesArc(tempExitAsset))
            exitAsset.setAnimationFromName("gfx")
            EXIT_IMAGES_OFF.append(exitAsset.getActiveFrame())
            exitAsset.setAnimationFromName("gfx2")
            EXIT_IMAGES_ON.append(exitAsset.getActiveFrame())
        else:
            EXIT_IMAGES_OFF.append(None)
            EXIT_IMAGES_ON.append(None)

    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)

        def getPlaceData():
            if laytonState.saveSlot.roomIndex < 40:
                packPlaceData = FileInterface.getData(PATH_PLACE_A)
            else:
                packPlaceData = FileInterface.getData(PATH_PLACE_B)
            
            if packPlaceData == None:
                raise FileInvalidCritical()
            else:
                try:
                    packPlace = LaytonPack()
                    packPlace.load(packPlaceData)
                except:
                    raise FileInvalidCritical()

            namePlace = PATH_PACK_PLACE % (laytonState.saveSlot.roomIndex, laytonState.saveSlot.roomSubIndex)
            return packPlace.getFile(namePlace)

        self.laytonState = laytonState
        self.screenController = screenController
        self._calculateChapter()
        self._calculateRoom()

        self.animMoveMode = AnimatedImageObject()
        self.isInMoveMode = False
        self.isTerminating = False

        self.screenController.modifyPaletteMain(0)
        self.screenController.modifyPaletteSub(0)

        self.bgAni = []
        self.objEvent = []

        # Note:
        # If movement co-ordinates are given, the screen is not faded out
        # Instead, a transition occurs and the game then loads the next room and renders it
        # If the top screen changes, the top screen is faded out after the transition
        #    and joins when the bottom screen fades back in
        # If not, only the bottom screen fades in.

        if self._executeAutoEvent():
            self.laytonState.setGameModeNext(GAMEMODES.DramaEvent)
            self._canBeKilled = True
        else:
            print("Attempted to load room", self.laytonState.saveSlot.roomIndex, self.laytonState.saveSlot.roomSubIndex)
            placeDataBytes = getPlaceData()

            if placeDataBytes == None:
                raise FileInvalidCritical()

            self.placeData = PlaceData()
            self.placeData.load(placeDataBytes)

            self.screenController.setBgMain(PATH_PLACE_BG % self.placeData.bgMainId)
            self.screenController.setBgSub(PATH_PLACE_MAP % self.placeData.bgMapId)
            self.indexExitHighlighted = None

            fullLoadTime = time()


            for indexBgAni in range(self.placeData.getCountObjBgEvent()):
                bgAni = self.placeData.getObjBgEvent(indexBgAni)

                # Workaround to remove spr type, probably resolved somewhere
                bgAniAssetName = ".".join(bgAni.name.split(".")[:-1]) + ".arc"
                tempBgAsset = FileInterface.getData(PATH_ANI % (PATH_EXT_BGANI % bgAniAssetName))

                if tempBgAsset != None:
                    bgAsset = AnimatedImage.fromBytesArc(tempBgAsset)
                    self.bgAni.append(AnimatedImageObject.fromMadhatter(bgAsset))
                    self.bgAni[-1].setAnimationFromName("gfx")
                    self.bgAni[-1].setPos((bgAni.pos[0],
                                           bgAni.pos[1] + RESOLUTION_NINTENDO_DS[1]))
                else:
                    print("Failed to load", PATH_ANI % (PATH_EXT_BGANI % bgAniAssetName))

            for indexObjEvent in range(self.placeData.getCountObjEvents()):
                objEvent = self.placeData.getObjEvent(indexObjEvent)

                # masking to everything below 256

                if objEvent.idImage != 0:
                    tempMaskedId = objEvent.idImage % 0xff
                    tempEventAsset = FileInterface.getData(PATH_ANI % (PATH_EXT_EVENT % tempMaskedId))

                    if tempEventAsset != None:
                        eventAsset = AnimatedImageObject.fromMadhatter(AnimatedImage.fromBytesArc(tempEventAsset))
                        eventAsset.setAnimationFromName("gfx")
                        eventAsset.setPos((objEvent.bounding.x, objEvent.bounding.y + RESOLUTION_NINTENDO_DS[1]))
                        self.objEvent.append(eventAsset)
                    else:
                        self.objEvent.append(None)
                        print("FAILED TO GET OBJ EVENT!!", PATH_ANI % (PATH_EXT_EVENT % tempMaskedId))
                else:
                    self.objEvent.append(None)

            # TODO - This is all bad lmao
            self.animMoveMode = AnimatedImageObject.fromMadhatter(AnimatedImage.fromBytesArc(FileInterface.getData(PATH_ANI % "map/movemode.arc")))
            self.animMoveMode.setAnimationFromName("off")
            self.animMoveMode.setPos((230,350))

            self.screenController.fadeIn()



            print("Total load time", time() - fullLoadTime)

    def update(self, gameClockDelta):
        if self.isTerminating:
            if self.screenController.getFaderIsViewObscured():
                self._canBeKilled = True

        for anim in self.bgAni:
            anim.update(gameClockDelta)
        
        for anim in self.objEvent:
            if anim != None:
                anim.update(gameClockDelta)
        
        self.animMoveMode.update(gameClockDelta)

        return super().update(gameClockDelta)
    
    def draw(self, gameDisplay):
        for anim in self.bgAni:
            anim.draw(gameDisplay)
        
        for anim in self.objEvent:
            if anim != None:
                anim.draw(gameDisplay)
        
        if self.isInMoveMode:
            for indexExit in range(self.placeData.getCountExits()):
                exitEntry = self.placeData.getExit(indexExit)
                
                tempOffsetPos = (exitEntry.bounding.x, exitEntry.bounding.y + RESOLUTION_NINTENDO_DS[1])
                if RoomPlayer.EXIT_IMAGES_OFF[exitEntry.idImage] != None:
                    gameDisplay.blit(RoomPlayer.EXIT_IMAGES_OFF[exitEntry.idImage], tempOffsetPos)
        else:
            self.animMoveMode.draw(gameDisplay)

    def startTermination(self):
        self.screenController.obscureViewLayer()
        self.isTerminating = True

    def handleTouchEvent(self, event):

        def evaluateExit(exitEntry):
            boundaryTestPos = (event.pos[0], event.pos[1] - RESOLUTION_NINTENDO_DS[1])
            if wasBoundingCollided(exitEntry.bounding, boundaryTestPos):
                if exitEntry.canSpawnEvent():
                    self.laytonState.setGameModeNext(GAMEMODES.DramaEvent)
                    self.laytonState.setEventId(exitEntry.spawnData)
                else:
                    # TODO - Replicate in-game behaviour. Currently just terminating
                    self.laytonState.setGameModeNext(GAMEMODES.Room)
                    self.laytonState.saveSlot.roomIndex = exitEntry.spawnData
                self.startTermination()
                return True
            return False

        # TODO - Stop interaction on blocking event
        if not(self.isTerminating):
            if event.type == MOUSEBUTTONUP:
                if self.animMoveMode.wasPressed(event.pos):
                    self.isInMoveMode = not(self.isInMoveMode)
                    return super().handleTouchEvent(event)

                if self.isInMoveMode:
                    for indexExit in range(self.placeData.getCountExits()):
                        exitEntry = self.placeData.getExit(indexExit)
                        if evaluateExit(exitEntry):
                            return super().handleTouchEvent(event)
                    self.isInMoveMode = False
                            
                else:
                    for indexExit in range(self.placeData.getCountExits()):
                        exitEntry = self.placeData.getExit(indexExit)
                        if exitEntry.canBePressedImmediately():
                            if evaluateExit(exitEntry):
                                return super().handleTouchEvent(event)

                    boundaryTestPos = (event.pos[0], event.pos[1] - RESOLUTION_NINTENDO_DS[1])
                    for indexEvent in range(self.placeData.getCountObjEvents()):
                        objEvent = self.placeData.getObjEvent(indexEvent)
                        if wasBoundingCollided(objEvent.bounding, boundaryTestPos):
                            self.laytonState.setGameModeNext(GAMEMODES.DramaEvent)
                            self.laytonState.setEventId(objEvent.idEvent)
                            self.startTermination()
                            return super().handleTouchEvent(event)
                    
                    for indexHint in range(self.placeData.getCountHintCoin()):
                        objHint = self.placeData.getObjHintCoin(indexHint)
                        if wasBoundingCollided(objHint.bounding, boundaryTestPos):
                            if not(self.laytonState.saveSlot.roomHintData.getRoomHintData(self.laytonState.saveSlot.roomIndex).hintsFound[indexHint]):
                                self.laytonState.saveSlot.roomHintData.getRoomHintData(self.laytonState.saveSlot.roomIndex).hintsFound[indexHint] = True
                                self.laytonState.saveSlot.hintCoinEncountered += 1
                                self.laytonState.saveSlot.hintCoinAvailable += 1
                                print("Found a hint coin!")

                                if indexHint == 0 and self.laytonState.saveSlot.roomIndex == 3:
                                    # Hardcoded behaviour to force the event after encountering first hint coin to play out
                                    self.laytonState.setGameModeNext(GAMEMODES.DramaEvent)
                                    self.laytonState.setEventId(10080)
                                    self.startTermination()
                                    return super().handleTouchEvent(event)
        
        return super().handleTouchEvent(event)

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
            if entry != None and entry.chapterStart <= self.laytonState.saveSlot.chapter <= entry.chapterEnd:
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

        print("\tPrior to calculation", self.laytonState.saveSlot.chapter)
        self._calculateChapter()
        print("\tAfter calculation", self.laytonState.saveSlot.chapter)

        indexSubRoom = 0
        for proposedSubRoom in range(1,16):
            placeFlagEntry = placeFlag.entries[indexRoom].getEntry(proposedSubRoom)
            placeFlagCounterEntry = placeFlag.entries[indexRoom].getCounterEntry(proposedSubRoom)
            if placeFlagEntry.chapterStart == 0 or placeFlagEntry.chapterEnd == 0:
                print("\tBroken on proposed", proposedSubRoom)
                break

            chapter = self.laytonState.saveSlot.chapter
            workingSubRoom = indexSubRoom
            if placeFlagEntry.chapterStart <= chapter and placeFlagEntry.chapterEnd >= chapter:
                workingSubRoom = proposedSubRoom

                if placeFlagCounterEntry.indexEventCounter != 0:
                    workingSubRoom = indexSubRoom
                    if checkEventCounter(placeFlagCounterEntry):
                        workingSubRoom = proposedSubRoom
            else:
                print("\tFailed chapter check for", proposedSubRoom, "wanted", placeFlagEntry.chapterStart)
            
            indexSubRoom = workingSubRoom
        
        self.laytonState.saveSlot.roomSubIndex = indexSubRoom