from __future__ import annotations
from math import ceil, sqrt
from typing import List, Optional, TYPE_CHECKING, Union
from widebrim.engine.anim.button import AnimatedButton, NullButton
from pygame.constants import BLEND_RGB_SUB, MOUSEBUTTONDOWN

from pygame.event import Event
from widebrim.madhatter.hat_io.asset_dat.place import Exit, PlaceData, EventEntry, TObjEntry
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.engine.file import FileInterface
from widebrim.engine.const import PATH_PACK_PLACE_NAME, PATH_TEXT_GOAL, PATH_TEXT_PLACE_NAME, RESOLUTION_NINTENDO_DS
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from widebrim.engine.state.enum_mode import GAMEMODES
if TYPE_CHECKING:
    from widebrim.engine.state.state import Layton2GameState
    from widebrim.engine_ext.state_game import ScreenController
    from widebrim.madhatter.hat_io.asset_dat.place import BgAni
    from pygame import Surface

from widebrim.engine.anim.fader import Fader
from widebrim.engine.state.layer import ScreenLayerNonBlocking
from widebrim.engine.exceptions import FileInvalidCritical
from widebrim.engine.anim.font.static import generateImageFromString
from widebrim.engine_ext.utils import getAnimFromPath, getTxt2String
from .const import *
from .animJump import AnimJumpHelper
from .tobjPopup import TObjPopup

class RoomPlayer(ScreenLayerNonBlocking):
    
    LAYTON_TRANSITION_PIXELS_PER_SECOND = 256
    POS_CENTER_TEXT_ROOM_TITLE  = (170,7)
    POS_CENTER_TEXT_OBJECTIVE   = (128,172)
    
    def __init__(self, laytonState : Layton2GameState, screenController : ScreenController):
        super().__init__()
        
        self.laytonState = laytonState
        self.screenController = screenController

        self.__isInteractable : bool = False

        self.__animMemberParty : List[Optional[AnimatedImageObject]] = []
        for indexParty in range(4):
            if len(NAME_ANIM_PARTY) > indexParty and len(POS_X_ANIM_PARTY) > indexParty:
                if indexParty < 2 or self.laytonState.saveSlot.partyFlag.getSlot(indexParty - 2):
                    self.__animMemberParty.append(getAnimFromPath(PATH_ANIM_PARTY, spawnAnimName=NAME_ANIM_PARTY[indexParty], pos=(POS_X_ANIM_PARTY[indexParty], POS_Y_ANIM_PARTY)))

        self.__animFirstTouch : Optional[AnimatedImageObject] = None
        if self.laytonState.isFirstTouchEnabled:
            self.__animFirstTouch = getAnimFromPath(PATH_ANIM_FIRSTTOUCH, spawnAnimName="gfx")
            if self.__animFirstTouch != None:
                width, height = self.__animFirstTouch.getDimensions()
                self.__animFirstTouch.setPos(((RESOLUTION_NINTENDO_DS[0] - width) // 2, ((RESOLUTION_NINTENDO_DS[1] - height) // 2) + RESOLUTION_NINTENDO_DS[1]))
        
        self.__hasPhotoPieceInArea : bool = False
        self.__hasPhotoPieceInAreaBeenTaken : bool = False

        self.__enablePhotoPieceOverlay : bool = False
        self.__photoPieceMessage : Optional[AnimatedImageObject] = None
        self.__photoPieceNumbers : Optional[AnimatedImageObject] = None

        self.__animBackground   : List[Optional[AnimatedImageObject]]   = []
        self.__animEvent        : List[Optional[AnimatedImageObject]]   = []
        self.__animMapArrow     : Optional[AnimatedImageObject]         = None
        self.__enableMapArrow   : bool                                  = False
        self.__animMapIcon      : Optional[AnimatedImageObject]         = getAnimFromPath(PATH_ANIM_MAPICON)
        if self.__animMapIcon != None:
            self.__animMapIcon.setAnimationFromIndex(1)

        self.__animNumberIcon : Optional[AnimatedImageObject]       = getAnimFromPath(PATH_ANIM_SOLVED_TEXT % self.laytonState.language.value)
        if self.__animNumberIcon != None and self.__animNumberIcon.setAnimationFromIndex(1):
            self.__animNumberIcon.setPos(POS_SOLVED_TEXT)

        self.__animEventStart : Optional[AnimatedImageObject] = getAnimFromPath(PATH_ANIM_ICON_BUTTONS)
        self.__animTouchIcon : Optional[AnimatedImageObject] = getAnimFromPath(PATH_ANIM_TOUCH_ICON, pos=POS_TOUCH_ICON)
        if self.__animTouchIcon != None and self.__animTouchIcon.setAnimationFromIndex(1):
            self.__animTouchIcon.setCurrentAnimationLoopStatus(False)

        self.__placeData : Optional[PlaceData] = None

        self.__inMoveMode : bool = False
        self.__btnMoveMode : Optional[AnimatedButton] = None
        if (moveModeButton := getAnimFromPath(PATH_BTN_MOVEMODE, pos=(230,350))) != None:
            self.__btnMoveMode = AnimatedButton(moveModeButton, "on", "off", callback=self.__startMoveMode)
        
        self.__tObjWindow           : Optional[TObjPopup]       = None

        # Not accurate parts
        self.__targetEvent          : Optional[Union[EventEntry, Exit]] = None
        self.__faderEventAnim       : Fader                     = Fader(500, initialActiveState=False)
        self.__positionEventAnim    : Optional[AnimJumpHelper]  = None
        self.__targetExit           : Optional[Exit]            = None
        
        self.__faderTiming          : Fader                     = Fader(500, initialActiveState=False)
        self.__hasTransitionedCompleted : bool                  = False

        self.__highlightedIndexExit : Optional[int]             = None
        self.__buttonsExit          : List[NullButton]          = []

        self.__textObjective        : Optional[Surface]         = None
        self.__textRoomTitle        : Optional[Surface]         = None
        self.__posObjective     = (0,0)
        self.__posRoomTitle     = (0,0)

        # Disgustingly inaccurate
        self.__imageExitOff : List[Optional[Surface]] = []
        self.__imageExitOn  : List[Optional[Surface]] = []
        for indexExitImage in range(8):
            if (exitImage := getAnimFromPath(PATH_EXT_EXIT % indexExitImage)) != None:
                exitImage.setAnimationFromName("gfx")
                self.__imageExitOff.append(exitImage.getActiveFrame())
                exitImage.setAnimationFromName("gfx2")
                self.__imageExitOn.append(exitImage.getActiveFrame())
            else:
                self.__imageExitOff.append(None)
                self.__imageExitOn.append(None)

        if self.__hasAutoEvent():
            # TODO - This is part of init more than separate function imo
            self.laytonState.setGameMode(GAMEMODES.DramaEvent)
            self.__disableInteractivity()
            self.doOnKill()

        elif self.__loadRoom():
            self.__loadPhotoPieceText()
            # TODO - Generate objective (goal) string text here
            self.screenController.fadeIn(callback=self.__enableInteractivity)

    def draw(self, gameDisplay):
        if self.__textRoomTitle != None:
            gameDisplay.blit(self.__textRoomTitle, self.__posRoomTitle, special_flags=BLEND_RGB_SUB)
        if self.__textObjective != None:
            gameDisplay.blit(self.__textObjective, self.__posObjective, special_flags=BLEND_RGB_SUB)

        if self.__enableMapArrow and self.__animMapArrow != None:
            self.__animMapArrow.draw(gameDisplay)
        
        for anim in self.__animMemberParty + self.__animBackground + self.__animEvent:
            if anim != None:
                anim.draw(gameDisplay)

        if self.__animNumberIcon != None:
            self.__animNumberIcon.draw(gameDisplay)

        # TODO - Check first touch, draw over everything if needed
        # Once touched, clear flag, play SFX and free anim object

        # Stops being accurate here
        if self.__targetEvent != None and self.__animEventStart != None:
            self.__animEventStart.setPos(self.__positionEventAnim.getPosition(self.__faderEventAnim.getStrength()))
            self.__animEventStart.draw(gameDisplay)
        
        if self.__animMapIcon != None:
            if self.__targetExit != None and not(self.__hasTransitionedCompleted):
                x = ((1 - self.__faderTiming.getStrength()) * self.__placeData.posMap[0]) + (self.__faderTiming.getStrength() * self.__targetExit.posTransition[0])
                y = ((1 - self.__faderTiming.getStrength()) * self.__placeData.posMap[1]) + (self.__faderTiming.getStrength() * self.__targetExit.posTransition[1])

                if self.__faderTiming.getStrength() == 1.0:
                    self.__hasTransitionedCompleted = True

                    self.__animMapIcon.setPos(self.__targetExit.posTransition)
                    self.__animMapIcon.draw(gameDisplay)

                    # Trying to minimise jump at end of transition
                    self.__doRoomTransition()
                else:
                    self.__animMapIcon.setPos((ceil(x), ceil(y)))
                    self.__animMapIcon.draw(gameDisplay)
            else:
                self.__animMapIcon.draw(gameDisplay)
        
        if self.__inMoveMode:
            if self.__placeData != None and self.__targetExit == None and self.__targetEvent == None:
                if self.__highlightedIndexExit == None:
                    for indexExit in range(self.__placeData.getCountExits()):
                        exit = self.__placeData.getExit(indexExit)
                        buttonExit = self.__buttonsExit[indexExit]
                        if 0 <= exit.idImage < 8:
                            image = self.__imageExitOff[exit.idImage]
                            if image != None:
                                gameDisplay.blit(image, buttonExit.getPos())
                else:
                    exit = self.__placeData.getExit(self.__highlightedIndexExit)
                    buttonExit = self.__buttonsExit[self.__highlightedIndexExit]
                    if 0 <= exit.idImage < 8:
                        if buttonExit.getTargettedState():
                            image = self.__imageExitOn[exit.idImage]
                        else:
                            image = self.__imageExitOff[exit.idImage]

                        if image != None:
                            gameDisplay.blit(image, buttonExit.getPos())
        else:
            if self.__btnMoveMode != None:
                self.__btnMoveMode.draw(gameDisplay)

        if self.__animTouchIcon != None:
            self.__animTouchIcon.draw(gameDisplay)
        
        if self.__tObjWindow != None:
            self.__tObjWindow.draw(gameDisplay)

        return super().draw(gameDisplay)

    def update(self, gameClockDelta):
        for anim in self.__animMemberParty + self.__animBackground + self.__animEvent:
            if anim != None:
                anim.update(gameClockDelta)
        
        if self.__targetEvent != None:
            self.__faderEventAnim.update(gameClockDelta)
            if self.__animEventStart != None:
                self.__animEventStart.update(gameClockDelta)

        self.__faderTiming.update(gameClockDelta)

        if not(self.__inMoveMode) and self.__btnMoveMode != None:
            self.__btnMoveMode.update(gameClockDelta)
        
        if self.__animTouchIcon != None:
            self.__animTouchIcon.update(gameClockDelta)

        if self.__tObjWindow != None:
            self.__tObjWindow.update(gameClockDelta)

        return super().update(gameClockDelta)
    
    def handleTouchEvent(self, event):

        def wasBoundingCollided(bounding, pos):
            if bounding.x <= pos[0] and bounding.y <= pos[1]:
                if (bounding.x + bounding.width) >= pos[0] and (bounding.y + bounding.height) >= pos[1]:
                    return True
            return False
        
        def getPressedEvent(pos) -> Optional[EventEntry]:
            if self.__placeData != None:
                for indexObjEvent in range(self.__placeData.getCountObjEvents()):
                    objEvent : EventEntry = self.__placeData.getObjEvent(indexObjEvent)
                    if wasBoundingCollided(objEvent.bounding, pos):
                        return objEvent
            return None
        
        def getPressedExit(pos, immediateOnly = False) -> Optional[Exit]:
            for indexExit in range(self.__placeData.getCountExits()):
                exitEntry = self.__placeData.getExit(indexExit)
                if (immediateOnly and exitEntry.canBePressedImmediately()) or not(immediateOnly):
                    if wasBoundingCollided(exitEntry.bounding, boundaryTestPos):
                        return exitEntry
            return None

        if self.__tObjWindow != None:
            self.__tObjWindow.handleTouchEvent(event)
            return True

        if self.__isInteractable:

            boundaryTestPos = (event.pos[0], event.pos[1] - RESOLUTION_NINTENDO_DS[1])

            # TODO - Hide touch cursor on MOUSEBUTTONDOWN
            if self.__animTouchIcon != None and event.type == MOUSEBUTTONDOWN:
                self.__animTouchIcon.setPos(POS_TOUCH_ICON)

            if self.__inMoveMode:
                for indexButton, button in enumerate(self.__buttonsExit):
                    self.__highlightedIndexExit = indexButton
                    if button.handleTouchEvent(event):
                        return True
                self.__highlightedIndexExit = None

            if self.__inMoveMode and event.type == MOUSEBUTTONDOWN:
                if (objExit := getPressedExit(boundaryTestPos)) != None:
                    self.__startExit(objExit)
                    return True
                self.__inMoveMode = False

            else:
                # TODO - Event handling is not very accurate; just reuses code from previous room handler
                if event.type == MOUSEBUTTONDOWN and (objEvent := getPressedEvent(boundaryTestPos)) != None:
                    self.__startEventSpawn(objEvent)
                    return True
                
                # TODO - Hint coins checked here

                # TODO - TObj checked here
                if event.type == MOUSEBUTTONDOWN and self.__placeData != None:
                    for indexTObj in range(self.__placeData.getCountObjText()):
                        if (tObj := self.__placeData.getObjText(indexTObj)) != None:
                            tObj : TObjEntry
                            if wasBoundingCollided(tObj.bounding, boundaryTestPos):
                                self.__startTObj(tObj.idChar, tObj.idTObj, False)
                                return True
                
                if self.__btnMoveMode.handleTouchEvent(event):
                    return True

                # TODO - Bag checked here
                
                if event.type == MOUSEBUTTONDOWN and (objExit := getPressedExit(boundaryTestPos, immediateOnly=True)) != None:
                    self.__startExit(objExit)
                    return True
                
                # TODO - Draw touch cursor
                if self.__animTouchIcon != None and event.type == MOUSEBUTTONDOWN and event.pos[1] >= RESOLUTION_NINTENDO_DS[1]:
                    if self.__animTouchIcon.setAnimationFromIndex(1) and self.__animTouchIcon.getActiveFrame != None:
                        width, height = self.__animTouchIcon.getDimensions()
                        self.__animTouchIcon.setPos((event.pos[0] - width // 2, event.pos[1] - height // 2))

        return super().handleTouchEvent(event)

    def __disableInteractivity(self):
        self.__isInteractable = False

    def __enableInteractivity(self):
        self.__isInteractable = True
    
    def __startMoveMode(self):
        self.__inMoveMode = not(self.__inMoveMode)

    def __callbackExitFromButton(self):
        self.__startExit(self.__placeData.getExit(self.__highlightedIndexExit))

    def __startTObj(self, idChar, idText, isFirstHintCoin):
        self.__disableInteractivity()
        self.__tObjWindow = TObjPopup(self.laytonState, self.screenController, idText, idChar, callback=self.__callbackEndTObj)

    def __callbackEndTObj(self):
        self.__tObjWindow = None
        self.__enableInteractivity()

    def __callbackEndTObjFirstHint(self):
        self.__callbackEndTObj()
        self.laytonState.setGameMode(GAMEMODES.DramaEvent)
        self.laytonState.setEventId(10080)
        self.screenController.fadeOut(callback=self.doOnKill)

    def __startEventSpawn(self, objEvent : Union[EventEntry, Exit]):
        self.__targetEvent = objEvent
        self.__disableInteractivity()
        
        isExclamation = True
        if type(objEvent) == EventEntry:
            idEvent = objEvent.idEvent
        else:
            idEvent = objEvent.spawnData

        if 20000 > idEvent or 30000 <= idEvent:
            isExclamation = False
            
        else:
            # TODO - This doesn't work
            if (evInf := self.laytonState.getEventInfoEntry(idEvent)) != None:
                if evInf.typeEvent != 0:
                    if (puzzleEntry := self.laytonState.saveSlot.puzzleData.getPuzzleData(evInf.dataPuzzle - 1)) != None:
                        if puzzleEntry.wasSolved:
                            isExclamation = False
        
        # TODO - can boundings be backwards?
        boundingCenterX = objEvent.bounding.x + (objEvent.bounding.width // 2)
        boundingCenterY = objEvent.bounding.y + (objEvent.bounding.height // 2)

        initialPos = (boundingCenterX, boundingCenterY)
        if self.__animEventStart != None:
            if isExclamation:
                if self.__animEventStart.setAnimationFromName("1") and (surf := self.__animEventStart.getActiveFrame()) != None:
                    initialPos = (boundingCenterX - (surf.get_width() // 2), boundingCenterY - (surf.get_height() // 2))
            else:
                if self.__animEventStart.setAnimationFromName("2") and (surf := self.__animEventStart.getActiveFrame()) != None:
                    initialPos = (boundingCenterX - (surf.get_width() // 2), (objEvent.bounding.y - surf.get_height()) + 4)

        initialPos = (initialPos[0], RESOLUTION_NINTENDO_DS[1] + initialPos[1])
        self.__positionEventAnim = AnimJumpHelper(initialPos, isExclamation)
        self.__faderEventAnim.setDuration(500)
        self.__faderEventAnim.setCallback(self.__killActiveRoomPlayerEvent)

        # Warning: VERY high level
        self.laytonState.setEventId(idEvent)
        self.laytonState.setGameMode(GAMEMODES.DramaEvent)

    def __startExit(self, objExit : Exit):
        self.__disableInteractivity()

        if objExit.canSpawnEvent():
            if objExit.canTriggerExclamationPopup():
                self.__startEventSpawn(objExit)
            else:
                self.laytonState.setEventId(objExit.spawnData)
                self.laytonState.setGameMode(GAMEMODES.DramaEvent)
                self.screenController.fadeOut(callback=self.doOnKill)
            return

        if objExit.spawnData == 0x3f:
            self.laytonState.setGameMode(GAMEMODES.Nazoba)
            self.screenController.fadeOut(callback=self.doOnKill)
            return
        
        print("Attempting seamless transition...")
        self.__targetExit = objExit
        self.screenController.fadeOutMain(duration=100, callback=self.__moveLaytonIcon)

    def __moveLaytonIcon(self):
        self.__hasTransitionedCompleted = False
        distanceX = self.__targetExit.posTransition[0] - self.__placeData.posMap[0]
        distanceY = self.__targetExit.posTransition[1] - self.__placeData.posMap[1]
        distance = sqrt(distanceX ** 2 + distanceY ** 2)
        duration = (distance / RoomPlayer.LAYTON_TRANSITION_PIXELS_PER_SECOND) * 1000

        self.__faderTiming.setDuration(duration)
        self.__faderTiming.setActiveState(True)

    def __doRoomTransition(self):
        currentTsMapIndex = self.__placeData.bgMapId
        self.laytonState.setPlaceNum(self.__targetExit.spawnData)
        if self.__hasAutoEvent():
            self.screenController.fadeOutSub(callback=self.doOnKill)
            self.laytonState.setGameMode(GAMEMODES.DramaEvent)
        else:
            print("Loading room data...")
            if self.__loadRoomData():
                if self.__placeData.bgMapId != currentTsMapIndex:
                    print("Room data was different, killing gamemode...")
                    self.laytonState.setGameMode(GAMEMODES.Room)
                    # TODO - Bugfix, fadeOut causes infinite loop?
                    self.screenController.fadeOutSub(callback=self.doOnKill)
                else:
                    print("Room data needs refreshing, starting...")
                    self.__loadRoom()
                    self.screenController.fadeInMain(callback=self.__enableInteractivity)

    def __loadPhotoPieceText(self):
        photoPieceByte = self.laytonState.saveSlot.eventCounter.toBytes(outLength=128)[24]
        if 0 < photoPieceByte < 16:
            self.__enablePhotoPieceOverlay = True
            self.__photoPieceMessage = getAnimFromPath(PATH_ANIM_PIECE_MESSAGE % self.laytonState.language, spawnAnimName="gfx", pos=POS_PIECE_MESSAGE)
            self.__photoPieceNumbers = getAnimFromPath(PATH_ANIM_NUM_PIECE_NUM)

    def __killActiveRoomPlayerEvent(self):
        self.screenController.fadeOut(duration=250, callback=self.doOnKill)

    def __loadRoomData(self) -> bool:

        def getPlaceData():
            if self.laytonState.getPlaceNum() < 40:
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

            namePlace = PATH_PACK_PLACE % (self.laytonState.getPlaceNum(), self.laytonState.saveSlot.roomSubIndex)
            return packPlace.getFile(namePlace)

        self.__calculateRoom()
        if (tempPlaceData := getPlaceData()) != None:
            placeData = PlaceData()
            placeData.load(tempPlaceData)
            self.__placeData = placeData

            # TODO - Get place string from jiten.plz, decode
            # TODO - Check if any entries for photo database here

            # TODO - Check if photo piece taken, set bools, unk camera check

            return True
        return False

    def __loadRoom(self):
        if self.__loadRoomData():

            self.__animBackground   = []
            self.__animEvent        = []
            self.__buttonsExit      = []

            # Remove trace of last state
            self.__targetEvent = None
            self.__targetExit = None
            self.__inMoveMode = False
            self.__highlightedIndexExit = None

            self.__textObjective = generateImageFromString(self.laytonState.fontEvent, getTxt2String(self.laytonState, PATH_TEXT_GOAL % self.laytonState.saveSlot.goal))
            self.__posObjective = (RoomPlayer.POS_CENTER_TEXT_OBJECTIVE[0] - self.__textObjective.get_width() // 2, RoomPlayer.POS_CENTER_TEXT_OBJECTIVE[1])
            
            if (jitenPackData := FileInterface.getData(PATH_PACK_PLACE_NAME % self.laytonState.language.value)) != None:
                jitenPack = LaytonPack()
                jitenPack.load(jitenPackData)
                # TODO - String substituter
                self.__textRoomTitle = generateImageFromString(self.laytonState.fontEvent, jitenPack.getFile(PATH_TEXT_PLACE_NAME % self.laytonState.getPlaceNum()).decode('ascii'))
                self.__posRoomTitle = (RoomPlayer.POS_CENTER_TEXT_ROOM_TITLE[0] - self.__textRoomTitle.get_width() // 2, RoomPlayer.POS_CENTER_TEXT_ROOM_TITLE[1])

            self.screenController.setBgMain(PATH_PLACE_BG % self.__placeData.bgMainId)
            self.screenController.setBgSub(PATH_PLACE_MAP % self.__placeData.bgMapId)

            if self.__animMapIcon != None and (surf := self.__animMapIcon.getActiveFrame()) != None:
                self.__animMapIcon.setPos(self.__placeData.posMap)

            for indexBackgroundAnim in range(self.__placeData.getCountObjBgEvent()):
                if (bgAni := self.__placeData.getObjBgEvent(indexBackgroundAnim)) != None:
                    bgAni : BgAni
                    # TODO - Everything just spawns with anim index 1 where "gfx" is
                    if (anim := getAnimFromPath(PATH_ANIM_BGANI % bgAni.name, spawnAnimName="gfx", pos=bgAni.pos)) != None:
                        anim.setPos((anim.getPos()[0], anim.getPos()[1] + RESOLUTION_NINTENDO_DS[1]))
                        self.__animBackground.append(anim)
                        
            # TODO - Seems to have tea stuff heree
            for indexObjEvent in range(self.__placeData.getCountObjEvents()):
                objEvent = self.__placeData.getObjEvent(indexObjEvent)

                # TODO - What is the second byte of spawnData used for?
                if objEvent.idImage != 0:
                    if (eventAsset := getAnimFromPath(PATH_EXT_EVENT % (objEvent.idImage & 0xff), spawnAnimName="gfx")) != None:
                        eventAsset.setPos((objEvent.bounding.x, objEvent.bounding.y + RESOLUTION_NINTENDO_DS[1]))
                    self.__animEvent.append(eventAsset)   
                else:
                    self.__animEvent.append(None)
            
            # TODO - Exits, and first strange function
            for indexExit in range(self.__placeData.getCountExits()):
                exit : Exit = self.__placeData.getExit(indexExit)
                pos = (exit.bounding.x, exit.bounding.y + RESOLUTION_NINTENDO_DS[1])
                posEnd = (pos[0] + exit.bounding.width, pos[1] + exit.bounding.height)
                self.__buttonsExit.append(NullButton(pos, posEnd, callback=self.__callbackExitFromButton))

            self.__setupGuideArrows()
            return True
        return False

    def __setupGuideArrows(self):
        if self.__animMapArrow == None:
            self.__animMapArrow = getAnimFromPath(PATH_ANIM_MAP_ARROW.replace("?", self.laytonState.language.value))
        
        x = 0
        y = 0
        targetImage = None
        self.__enableMapArrow = False
        self.laytonState.loadSubmapInfo()
        for indexEventViewed in EVENT_VIEWED_MAP_ARROW:
            if (submapEntry := self.laytonState.getSubmapInfoEntry(indexEventViewed)) != None:
                self.__enableMapArrow = True
                x,y = submapEntry.pos
                targetImage = submapEntry.indexImage
                if submapEntry.indexImage == 0:
                    y += 14
                elif submapEntry.indexImage == 5:
                    y -= 14

        self.laytonState.unloadSubmapInfo()
                
        if self.__enableMapArrow and self.__animMapArrow != None:
            if self.__animMapArrow.setAnimationFromName(str(targetImage)):
                if (imageMapArrow := self.__animMapArrow.getActiveFrame()) != None:
                    self.__animMapArrow.setPos((x - imageMapArrow.get_width() // 2,y - imageMapArrow.get_height() // 2))
            else:
                self.__enableMapArrow = False

    def __calculateChapter(self):

        storyFlag = self.laytonState.dbStoryFlag
        saveSlot = self.laytonState.saveSlot

        indexStoryFlag = storyFlag.getIndexFromChapter(saveSlot.chapter)
        if indexStoryFlag == -1:
            # The game apparently does this too
            # Setting chapter and goal to 510 after passing event 15250 causes the chapter to reset to 390, like the game.
            indexStoryFlag = 0

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

    def __calculateRoom(self):

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
        indexRoom = self.laytonState.getPlaceNum()

        self.__calculateChapter()

        indexSubRoom = 0
        for proposedSubRoom in range(1,16):
            placeFlagEntry = placeFlag.entries[indexRoom].getEntry(proposedSubRoom)
            placeFlagCounterEntry = placeFlag.entries[indexRoom].getCounterEntry(proposedSubRoom)
            if placeFlagEntry.chapterStart == 0 or placeFlagEntry.chapterEnd == 0:
                break

            chapter = self.laytonState.saveSlot.chapter
            workingSubRoom = indexSubRoom
            if placeFlagEntry.chapterStart <= chapter and placeFlagEntry.chapterEnd >= chapter:
                workingSubRoom = proposedSubRoom

                if placeFlagCounterEntry.indexEventCounter != 0:
                    workingSubRoom = indexSubRoom
                    if checkEventCounter(placeFlagCounterEntry):
                        workingSubRoom = proposedSubRoom
            
            indexSubRoom = workingSubRoom
        
        self.laytonState.saveSlot.roomSubIndex = indexSubRoom

    def __hasAutoEvent(self) -> bool:

        def getEventInfoEventViewedIdFlag(eventId):
            eventInfo = self.laytonState.getEventInfoEntry(eventId)
            if eventInfo == None:
                return eventInfo
            return eventInfo.indexEventViewedFlag

        def hasAutoEventBeenExecuted(eventId):
            eventViewedFlag = getEventInfoEventViewedIdFlag(eventId)
            if eventViewedFlag != None:
                return self.laytonState.saveSlot.eventViewed.getSlot(eventViewedFlag)
            return False

        autoEvent = self.laytonState.dbAutoEvent

        autoEventId = None
        for entryId in range(8):
            entry = autoEvent.entries[self.laytonState.getPlaceNum()].getSubPlaceEntry(entryId)
            if entry != None and entry.chapterStart <= self.laytonState.saveSlot.chapter <= entry.chapterEnd:
                autoEventId = entry.idEvent
        
        if autoEventId != None:
            # TODO - Can there be multiple autoevents that pass the above check?
            if hasAutoEventBeenExecuted(autoEventId):
                return False
            
            repeatId = getEventInfoEventViewedIdFlag(autoEventId)
            if repeatId == self.laytonState.saveSlot.idHeldAutoEvent:
                # TODO - Figure out exactly how game does this check. Hack implemented in setter for place which works around loops caused by
                # repeating autoevents. Current implementation assumes room set will be executed, which could do weird stuff in longer event chains
                return False

            self.laytonState.setEventId(autoEventId)
            return True
        return False