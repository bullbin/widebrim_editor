from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES
from ..engine.file import FileInterface
from ..engine.anim.image_anim import AnimatedImageObject
from ..engine.exceptions import FileInvalidCritical
from ..engine.const import PATH_PLACE_A, PATH_PLACE_B, PATH_PACK_PLACE, PATH_PLACE_BG, PATH_PLACE_MAP, PATH_ANI, PATH_EXT_BGANI, RESOLUTION_NINTENDO_DS, PATH_EXT_EXIT, PATH_EXT_EVENT
from ..engine.const import PATH_PACK_PLACE_NAME, PATH_TEXT_PLACE_NAME, PATH_PACK_TXT2, PATH_TEXT_GOAL

from pygame import MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEMOTION, BLEND_RGB_SUB

from ..madhatter.hat_io.asset import LaytonPack
from ..madhatter.hat_io.asset_image import AnimatedImage
from ..madhatter.hat_io.asset_dat.place import PlaceData

from ..engine.anim.font.static import generateImageFromString

from time import time

def wasBoundingCollided(bounding, pos):
    if bounding.x <= pos[0] and bounding.y <= pos[1]:
        if (bounding.x + bounding.width) >= pos[0] and (bounding.y + bounding.height) >= pos[1]:
            return True
    return False

class RoomPlayer(ScreenLayerNonBlocking):

    # TODO - Speed up loading. Stutter exceeds 500ms which causes faders to look very strange

    ANIM_MOVE_MODE = AnimatedImageObject.fromMadhatter(AnimatedImage.fromBytesArc(FileInterface.getData(PATH_ANI % "map/movemode.arc")))
    ANIM_MOVE_MODE.setPos((230,350))

    IMAGE_EXIT_OFF = []
    IMAGE_EXIT_ON  = []

    IMAGE_EXCLAMATION = None

    POS_CENTER_TEXT_ROOM_TITLE  = (170,7)
    POS_CENTER_TEXT_OBJECTIVE   = (128,172)

    # TODO - Button anim type

    # Shh, pylint
    indexExitImage  = 0
    exitAssetData   = None
    exitAsset       = None
    for indexExitImage in range(8):
        exitAssetData = FileInterface.getData(PATH_ANI % (PATH_EXT_EXIT % indexExitImage))
        if exitAssetData != None:
            exitAsset = AnimatedImageObject.fromMadhatter(AnimatedImage.fromBytesArc(exitAssetData))
            exitAsset.setAnimationFromName("gfx")
            IMAGE_EXIT_OFF.append(exitAsset.getActiveFrame())
            exitAsset.setAnimationFromName("gfx2")
            IMAGE_EXIT_ON.append(exitAsset.getActiveFrame())
        else:
            IMAGE_EXIT_OFF.append(None)
            IMAGE_EXIT_ON.append(None)

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

        self.isInMoveMode = False
        self.indexMoveModePressed = None
        self.isTerminating = False

        self.bgAni = []
        self.objEvent = []

        self.textObjective = None
        self.textRoomTitle = None
        self.posObjective = (0,0)
        self.posRoomTitle = (0,0)

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
            print("Loaded room", self.laytonState.saveSlot.roomIndex, self.laytonState.saveSlot.roomSubIndex)
            placeDataBytes = getPlaceData()
            if placeDataBytes == None:
                raise FileInvalidCritical()

            self.placeData = PlaceData()
            self.placeData.load(placeDataBytes)

            self.screenController.setBgMain(PATH_PLACE_BG % self.placeData.bgMainId)
            self.screenController.setBgSub(PATH_PLACE_MAP % self.placeData.bgMapId)
            
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

                # TODO - What is the second byte of spawnData used for?
                # Strange behaviour at end of carriage, tiny sprite clipped at bottom

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
                        print("Failed to load", PATH_ANI % (PATH_EXT_EVENT % tempMaskedId))
                else:
                    self.objEvent.append(None)

            RoomPlayer.ANIM_MOVE_MODE.setAnimationFromName("off")

            self._updateUpperScreenText()
            self.screenController.fadeIn()

            print("Total load time", round((time() - fullLoadTime) * 1000, 2))

    def update(self, gameClockDelta):
        if self.isTerminating:
            if self.screenController.getFaderIsViewObscured():
                self._canBeKilled = True

        for anim in self.bgAni:
            anim.update(gameClockDelta)
        
        for anim in self.objEvent:
            if anim != None:
                anim.update(gameClockDelta)
        
        RoomPlayer.ANIM_MOVE_MODE.update(gameClockDelta)

        return super().update(gameClockDelta)
    
    def draw(self, gameDisplay):

        def drawAllExits():

            def drawFromEntry(entry, imageSource):
                tempOffsetPos = (entry.bounding.x, entry.bounding.y + RESOLUTION_NINTENDO_DS[1])
                if imageSource[entry.idImage] != None:
                    gameDisplay.blit(imageSource[entry.idImage], tempOffsetPos)

            if self.indexMoveModePressed != None:
                if self.isTerminating:
                    drawFromEntry(self.placeData.getExit(self.indexMoveModePressed), RoomPlayer.IMAGE_EXIT_OFF)
                else:
                    drawFromEntry(self.placeData.getExit(self.indexMoveModePressed), RoomPlayer.IMAGE_EXIT_ON)
            else:
                for indexExit in range(self.placeData.getCountExits()):
                    drawFromEntry(self.placeData.getExit(indexExit), RoomPlayer.IMAGE_EXIT_OFF)

        for anim in self.bgAni:
            anim.draw(gameDisplay)
        
        for anim in self.objEvent:
            if anim != None:
                anim.draw(gameDisplay)
        
        if self.textObjective != None:
            gameDisplay.blit(self.textObjective, self.posObjective, special_flags=BLEND_RGB_SUB)
        if self.textRoomTitle != None:
            gameDisplay.blit(self.textRoomTitle, self.posRoomTitle, special_flags=BLEND_RGB_SUB)

        if self.isInMoveMode:
            drawAllExits()
        else:
            RoomPlayer.ANIM_MOVE_MODE.draw(gameDisplay)

    def startTermination(self):
        self.screenController.obscureViewLayer()
        self.isTerminating = True

    def handleTouchEvent(self, event):
        
        def doExit(exitEntry):
            if exitEntry.canSpawnEvent():
                self.laytonState.setGameModeNext(GAMEMODES.DramaEvent)
                self.laytonState.setEventId(exitEntry.spawnData)
            else:
                # TODO - Replicate in-game behaviour. Currently just terminating
                self.laytonState.setGameModeNext(GAMEMODES.Room)
                self.laytonState.saveSlot.roomIndex = exitEntry.spawnData
            self.startTermination()

        # TODO - Stop interaction on blocking event
        if not(self.isTerminating):

            boundaryTestPos = (event.pos[0], event.pos[1] - RESOLUTION_NINTENDO_DS[1])
            if self.isInMoveMode:
                # If an exit was pressed, set the highlight variable to its index
                if event.type == MOUSEBUTTONDOWN:
                    self.indexMoveModePressed = None
                    for indexExit in range(self.placeData.getCountExits()):
                        if wasBoundingCollided(self.placeData.getExit(indexExit).bounding, boundaryTestPos):
                            self.indexMoveModePressed = indexExit
                            break
                
                # If an exit is being held down but the cursor moves off it, reset the highlight variable
                elif event.type == MOUSEMOTION and self.indexMoveModePressed != None:
                    if not(wasBoundingCollided(self.placeData.getExit(self.indexMoveModePressed).bounding, boundaryTestPos)):
                        self.indexMoveModePressed = None
                        # TODO - Reset animation fader here, as this would mean that the mouse has moved off the initial clicked target
                
                # If the exit has made it through the above and the user lifts their cursor on it, execute the exit
                elif event.type == MOUSEBUTTONUP:
                    if self.indexMoveModePressed != None and wasBoundingCollided(self.placeData.getExit(self.indexMoveModePressed).bounding, boundaryTestPos):
                        doExit(self.placeData.getExit(self.indexMoveModePressed))
                    else:
                        self.isInMoveMode = False
                        self.indexMoveModePressed = None
            
            else:
                if event.type == MOUSEBUTTONUP:
                    # TODO - Change to button, as this must have also been pressed initially for it to do anything
                    if RoomPlayer.ANIM_MOVE_MODE.wasPressed(event.pos):
                        self.isInMoveMode = not(self.isInMoveMode)
                        return super().handleTouchEvent(event)

                    for indexExit in range(self.placeData.getCountExits()):
                        exitEntry = self.placeData.getExit(indexExit)
                        if exitEntry.canBePressedImmediately() and wasBoundingCollided(exitEntry.bounding, boundaryTestPos):
                            doExit(self.placeData.getExit(indexExit))
                            return super().handleTouchEvent(event)

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

    def _updateUpperScreenText(self):
        # What happens if control characters are used in this text?
        try:
            tempPack = LaytonPack()
            tempPack.load(FileInterface.getData(PATH_PACK_TXT2 % self.laytonState.language.value))
            self.textObjective = generateImageFromString(self.laytonState.fontEvent, tempPack.getFile(PATH_TEXT_GOAL % self.laytonState.saveSlot.goal).decode('ascii'))
            tempPack = LaytonPack()
            tempPack.load(FileInterface.getData(PATH_PACK_PLACE_NAME % self.laytonState.language.value))
            self.textRoomTitle = generateImageFromString(self.laytonState.fontEvent, tempPack.getFile(PATH_TEXT_PLACE_NAME % self.laytonState.saveSlot.roomIndex).decode('ascii'))

            self.posObjective = (RoomPlayer.POS_CENTER_TEXT_OBJECTIVE[0] - self.textObjective.get_width() // 2, RoomPlayer.POS_CENTER_TEXT_OBJECTIVE[1])
            self.posRoomTitle = (RoomPlayer.POS_CENTER_TEXT_ROOM_TITLE[0] - self.textRoomTitle.get_width() // 2, RoomPlayer.POS_CENTER_TEXT_ROOM_TITLE[1])
        except:
            self.textObjective = None
            self.textRoomTitle = None
            print("Failed to load room text!")

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

                    nzLstEntry = self.laytonState.getNazoListEntry(subFlag.param)
                    if nzLstEntry != None and not(saveSlot.puzzleData.getPuzzleData(nzLstEntry.idExternal - 1).wasSolved):
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