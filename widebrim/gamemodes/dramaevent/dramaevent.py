from ...engine.state.enum_mode import GAMEMODES
from ...engine.anim.image_anim import AnimatedImageObject
from ...engine.anim.fader import Fader
from ...engine.anim.font.scrolling import ScrollingFontHelper
from ...engine.exceptions import FileInvalidCritical
from ...engine.file import FileInterface
from ..core_popup.script import ScriptPlayer

from ...engine.const import RESOLUTION_NINTENDO_DS, PATH_FACE_ROOT, PATH_BODY_ROOT, PATH_CHAP_ROOT
from ...engine.const import PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C
from ...engine.const import PATH_PACK_EVENT_DAT, PATH_PACK_EVENT_SCR, PATH_PACK_TALK, PATH_EVENT_BG, PATH_PLACE_BG, PATH_EVENT_ROOT, PATH_ANI, PATH_NAME_ROOT

from ...madhatter.hat_io.asset import LaytonPack
from ...madhatter.hat_io.asset_script import GdScript
from ...madhatter.hat_io.asset_sav import FlagsAsArray
from ...madhatter.hat_io.asset_image import AnimatedImage
from ...madhatter.typewriter.stringsLt2 import OPCODES_LT2

from .storage import EventStorage
from .popup import *
from ..core_popup.save import SaveLoadScreenPopup

from .const import *

# TODO - Remove workaround by properly creating library
from ...madhatter.hat_io.binary import BinaryReader

from pygame import Surface, MOUSEBUTTONUP
from pygame.transform import flip

def functionGetAnimationFromName(name):
    name = name.split(".")[0] + ".arc"
    resolvedPath = PATH_FACE_ROOT % name
    return FileInterface.getData(resolvedPath)

# TODO - During fading, the main screen doesn't actually seem to be updated.

# TODO - Set up preparations for many hardcoded event IDs which are called for various tasks in binary
#        aka nazoba hell, since there's so much back and forth to spawn the extra handler due to memory constraints on NDS

class Popup():

    # Note - Inaccurate, as characters share the same alpha as this layer. Colours should bleed over characters as alpha channel is used for fading, not separate surface.

    DURATION_FADE = 300

    def __init__(self):
        self.fader = Fader(Popup.DURATION_FADE)
        self.canBeTerminated = False
    
    def doWhileActive(self, gameClockDelta):
        self.fader.update(gameClockDelta)

        if self.fader.getStrength() == 0:
            self.canBeTerminated = True

    def doOnExit(self):
        pass

    def update(self, gameClockDelta):
        if not(self.canBeTerminated):
            self.doWhileActive(gameClockDelta)

    def draw(self, gameDisplay):
        pass

    def getContextState(self):
        return self.canBeTerminated

    def isPopupDone(self):
        return True
    
    def handleTouchEventForPopup(self, event):
        pass

    def handleTouchEvent(self, event):
        # If the popup is currently fading, skip it.
        if event.type == MOUSEBUTTONUP:
            if self.isPopupDone():
                if not(self.fader.getActiveState()) and self.fader.getStrength() == 1:
                    self.fader.setInvertedState(True)
                    self.fader.reset()
                    self.doOnExit()
            else:
                self.handleTouchEventForPopup(event)

class PlaceholderPopup(Popup):

    def __init__(self):
        Popup.__init__(self)
        self.surface = Surface((40,40))
        self.surface.fill((255,0,0))
        self.surface.set_alpha(0)
    
    def doWhileActive(self, gameClockDelta):
        self.fader.update(gameClockDelta)
        self.surface.set_alpha(round(self.fader.getStrength() * 255))

        if self.fader.getStrength() == 0:
            self.canBeTerminated = True

    def draw(self, gameDisplay):
        gameDisplay.blit(self.surface, (0,0))

class TextWindow(Popup):

    # TODO - Improve redundancy, although these are all critical assets
    dataWindow = FileInterface.getData(PATH_ANI % (PATH_EVENT_ROOT % "twindow.arc"))
    madhatterImage = AnimatedImage.fromBytesArc(dataWindow, functionGetFileByName=functionGetAnimationFromName)
    SPRITE_WINDOW = AnimatedImageObject.fromMadhatter(madhatterImage)
    SPRITE_WINDOW.setPos((0, SPRITE_WINDOW.getVariable("pos")[1] + RESOLUTION_NINTENDO_DS[1]))

    DICT_SLOTS = {0:"LEFT",
                  2:"RIGHT",
                  3:"LEFT_L",
                  4:"LEFT_R",
                  5:"RIGHT_L",
                  6:"RIGHT_R"}

    def __init__(self, laytonState, characterSpawnIdToCharacterMap, scriptTextWindow):
        Popup.__init__(self)
        self.animNameOnExit = None
        if scriptTextWindow.getInstruction(0).operands[0].value in characterSpawnIdToCharacterMap:
            self.characterController = characterSpawnIdToCharacterMap[scriptTextWindow.getInstruction(0).operands[0].value]

            # TODO - Make const
            if scriptTextWindow.getInstruction(0).operands[1].value != "NONE":
                self.characterController.setCharacterAnimationFromName(scriptTextWindow.getInstruction(0).operands[1].value)
            if scriptTextWindow.getInstruction(0).operands[2].value != "NONE":
                self.animNameOnExit = scriptTextWindow.getInstruction(0).operands[2].value
        else:
            self.characterController = None

        self.isNameActive = False
        if self.characterController != None and self.characterController.getVisibility() and self.characterController.slot in TextWindow.DICT_SLOTS:
            self.isArrowActive = True
            TextWindow.SPRITE_WINDOW.setAnimationFromName(TextWindow.DICT_SLOTS[self.characterController.slot])
            TextWindow.SPRITE_WINDOW.subAnimation.getActiveFrame().set_alpha(0)
            if self.characterController.imageName != None and self.characterController.imageName.getActiveFrame() != None:
                self.characterController.imageName.getActiveFrame().set_alpha(0)
                self.isNameActive = True
        else:
            # TODO - This is more a workaround, initial train event and 14180 demonstrate that this does not hold true
            self.isArrowActive = False
            TextWindow.SPRITE_WINDOW.setAnimationFromName("gfx")

        TextWindow.SPRITE_WINDOW.getActiveFrame().set_alpha(0)

        self.textScroller = ScrollingFontHelper(laytonState.fontEvent)
        self.textScroller.setText(scriptTextWindow.getInstruction(0).operands[4].value)
        self.textScroller.setPos((8, RESOLUTION_NINTENDO_DS[1] + 141))
    
    def doWhileActive(self, gameClockDelta):
        self.fader.update(gameClockDelta)
        TextWindow.SPRITE_WINDOW.getActiveFrame().set_alpha(round(self.fader.getStrength() * 255))
        if self.isArrowActive:
            TextWindow.SPRITE_WINDOW.subAnimation.getActiveFrame().set_alpha(round(self.fader.getStrength() * 255))

        if self.isNameActive:
            self.characterController.imageName.getActiveFrame().set_alpha(round(self.fader.getStrength() * 255))

        if self.characterController != None:
            if self.textScroller.isWaiting() or not(self.textScroller.getActiveState()):
                self.characterController.setCharacterTalkingState(False)
            else:
                self.characterController.setCharacterTalkingState(True)

        if self.fader.getStrength() == 0:
            self.canBeTerminated = True
        elif self.fader.getStrength() == 1:
            self.textScroller.update(gameClockDelta)
    
    def doOnExit(self):
        if self.characterController != None:
            self.characterController.setCharacterTalkingState(False)
            if self.animNameOnExit != None:
                self.characterController.setCharacterAnimationFromName(self.animNameOnExit)

    def isPopupDone(self):
        return not(self.textScroller.getActiveState())

    def handleTouchEventForPopup(self, event):
        if not(self.fader.getActiveState()):
            if self.textScroller.getActiveState():
                if not(self.textScroller.isWaiting()):
                    self.textScroller.skip()
                else:
                    self.textScroller.setTap()

    def draw(self, gameDisplay):
        TextWindow.SPRITE_WINDOW.draw(gameDisplay)

        if self.isNameActive:
            self.characterController.imageName.draw(gameDisplay)
        
        if self.fader.getStrength() == 1:
            self.textScroller.draw(gameDisplay)

class CharacterController():

    SLOT_OFFSET = {0:48,     1:128,
                   2:208,     3:31,
                   4:90,    5:128,
                   6:0}
    SLOT_LEFT  = [0,3,4]    # Verified against game binary
    # Left side characters need flipping

    SLOT_RIGHT = [2,5,6]

    def __init__(self, laytonState, characterIndex, characterInitialAnimIndex=0, characterVisible=False, characterSlot=0):

        self._baseAnimName = "Create an Animation"
        self._isCharacterTalking = False

        dataCharacter = FileInterface.getData(PATH_BODY_ROOT % characterIndex)
        if dataCharacter != None:
            madhatterImage = AnimatedImage.fromBytesArc(dataCharacter, functionGetFileByName=functionGetAnimationFromName)
            self.imageCharacter = AnimatedImageObject.fromMadhatter(madhatterImage)
            self.setCharacterAnimationFromIndex(characterInitialAnimIndex)
        else:
            self.imageCharacter = None
        
        dataName = FileInterface.getData(PATH_ANI % (PATH_NAME_ROOT % (laytonState.language.value, characterIndex)))
        if dataName != None:
            dataName = AnimatedImage.fromBytesArc(dataName, functionGetFileByName=functionGetAnimationFromName)
            self.imageName = AnimatedImageObject.fromMadhatter(dataName)
            self.imageName.setAnimationFromName("gfx")
            self.imageName.setPos((self.imageName.getVariable("pos")[0], RESOLUTION_NINTENDO_DS[1] + self.imageName.getVariable("pos")[1]))
        else:
            self.imageName = None

        self._visibility = characterVisible
        self._drawLocation = (0,0)

        self._characterIsFlipped = False
        if self.imageCharacter != None:
            self._characterFlippedSurface = Surface(self.imageCharacter.getDimensions()).convert_alpha()
        else:
            self._characterFlippedSurface = Surface((0,0))
        self._characterFlippedSurfaceNeedsUpdate = True
        
        self.slot = 0
        self.setCharacterSlot(characterSlot)

    def update(self, gameClockDelta):
        if self.imageCharacter != None:
            
            if self.imageCharacter.update(gameClockDelta) or self._characterFlippedSurfaceNeedsUpdate:
                self._characterFlippedSurface.fill((0,0,0,0))
                self.imageCharacter.draw(self._characterFlippedSurface)
                if self._characterIsFlipped:
                    self._characterFlippedSurface = flip(self._characterFlippedSurface, True, False)

    def draw(self, gameDisplay):
        if self._visibility and self.imageCharacter != None:
            gameDisplay.blit(self._characterFlippedSurface, self._drawLocation)

    def setVisibility(self, isVisible):
        self._visibility = isVisible
    
    def getVisibility(self):
        return self._visibility
    
    def setCharacterTalkingState(self, isTalking):
        if isTalking != self._isCharacterTalking:
            if self.imageCharacter != None:
                if isTalking:
                    if not(self.imageCharacter.setAnimationFromName("*" + self._baseAnimName)):
                        # TODO - Does the game even set the animation if its not found? Is the fallback just continuing past animation?
                        self.imageCharacter.setAnimationFromName(self._baseAnimName)
                else:
                    self.imageCharacter.setAnimationFromName(self._baseAnimName)

            self._isCharacterTalking = isTalking

    def setCharacterSlot(self, slot):

        def getImageOffset():
            offset = self.imageCharacter.getVariable("drawoff")
            if offset != None:
                return (offset[0], abs(offset[1]))
            else:
                return (0,0)

        if slot in CharacterController.SLOT_OFFSET:
            self.slot = slot

            if self.imageCharacter != None:
                offset = CharacterController.SLOT_OFFSET[self.slot]
                variableOffset = getImageOffset()

                if slot in CharacterController.SLOT_LEFT:
                    self._characterIsFlipped = True
                    self._drawLocation = (offset - (self.imageCharacter.getDimensions()[0] // 2) - variableOffset[0],
                                      RESOLUTION_NINTENDO_DS[1] * 2 - variableOffset[1] - self.imageCharacter.getDimensions()[1])
                else:
                    self._characterIsFlipped = False
                    self._drawLocation = (offset - (self.imageCharacter.getDimensions()[0] // 2) + variableOffset[0],
                                      RESOLUTION_NINTENDO_DS[1] * 2 - variableOffset[1] - self.imageCharacter.getDimensions()[1])
                
                self._characterFlippedSurfaceNeedsUpdate = True

    def setCharacterAnimationFromName(self, animName):
        if self.imageCharacter != None:
            if self.imageCharacter.setAnimationFromName(animName):
                self._baseAnimName = self.imageCharacter.animActive.name
    
    def setCharacterAnimationFromIndex(self, animIndex):
        if self.imageCharacter != None:
            if self.imageCharacter.setAnimationFromIndex(animIndex):
                self._baseAnimName = self.imageCharacter.animActive.name

class EventPlayer(ScriptPlayer):
    def __init__(self, laytonState, screenController):

        def substituteEventPath(inPath, inPathA, inPathB, inPathC):

            def trySubstitute(path, lang, evId):
                try:
                    return path % (lang, evId)
                except TypeError:
                    return path % evId

            if self._idMain != 24:
                return trySubstitute(inPath, self.laytonState.language.value, self._idMain)
            elif self._idSub < 300:
                return trySubstitute(inPathA, self.laytonState.language.value, self._idMain)
            elif self._idSub < 600:
                return trySubstitute(inPathB, self.laytonState.language.value, self._idMain)
            else:
                return trySubstitute(inPathC, self.laytonState.language.value, self._idMain)

        def getEventTalkPath():
            return substituteEventPath(PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C)

        def getEventScriptPath():
            return substituteEventPath(PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C)

        # TODO - Search for language image as well as non-language image

        ScriptPlayer.__init__(self, laytonState, screenController, GdScript())

        self.laytonState.setGameMode(GAMEMODES.Room)
        self._packEventTalk = LaytonPack()

        spawnId = self.laytonState.getEventId()

        self._idMain = spawnId // 1000
        self._idSub = spawnId % 1000

        self.talkScript     = GdScript()

        self.characters = []
        self.nameCharacters = []
        self.characterSpawnIdToCharacterMap = {}

        self._sharedImageHandler = EventStorage()

        if spawnId == -1:
            self.doOnKill()
        else:
            print("Loaded event", spawnId)
            # Centralise this so it can be deleted when finished
            try:
                packEventScript = LaytonPack()
                packEventScript.load(FileInterface.getData(getEventScriptPath()))
                self._packEventTalk.load(FileInterface.getData(getEventTalkPath()))

                self._script.load(packEventScript.getFile(PATH_PACK_EVENT_SCR % (self._idMain, self._idSub)))
                eventData = packEventScript.getFile(PATH_PACK_EVENT_DAT % (self._idMain, self._idSub))

                # TODO - Rewrite event info module

                if eventData == None:
                    raise FileInvalidCritical()
            
                eventData = BinaryReader(data=eventData)

                # Event_MaybeLoadEvent
                # Wants to set gamemode to puzzle, but this is overriden by setting to room. Done in different functions in game but both run during event
                if ID_EVENT_PUZZLE <= spawnId < ID_EVENT_TEA and self.laytonState.entryEvInfo != None and self.laytonState.entryEvInfo.dataPuzzle != None:
                    self.laytonState.setPuzzleId(self.laytonState.entryEvInfo.dataPuzzle)
                    self.laytonState.setGameModeNext(GAMEMODES.EndPuzzle)
                
                if self.laytonState.entryEvInfo != None and self.laytonState.entryEvInfo.indexEventViewedFlag != None:
                    self.laytonState.saveSlot.eventViewed.setSlot(True, self.laytonState.entryEvInfo.indexEventViewedFlag)

                self.screenController.setBgMain(PATH_PLACE_BG % eventData.readU16())
                # TODO - Game isolates certain range of images which it wants language-specific backgrounds for
                self.screenController.setBgSub(PATH_EVENT_BG % eventData.readU16())

                introBehaviour = eventData.readUInt(1)
                if introBehaviour == 0 or introBehaviour == 3:
                    self.screenController.modifyPaletteMain(120)
                
                if introBehaviour != 1:
                    self.screenController.fadeIn()

                eventData.seek(6)
                for charIndex in range(8):
                    character = eventData.readUInt(1)
                    if character != 0:
                        self.characters.append(CharacterController(self.laytonState, character))
                        self.characterSpawnIdToCharacterMap[character] = self.characters[-1]

                for charIndex in range(8):
                    slot = eventData.readUInt(1)
                    if charIndex < len(self.characters):
                        self.characters[charIndex].setCharacterSlot(slot)

                for charIndex in range(8):
                    visibility = eventData.readUInt(1) == 1
                    if charIndex < len(self.characters):
                        self.characters[charIndex].setVisibility(visibility)
                
                for charIndex in range(8):
                    animIndex = eventData.readUInt(1)
                    if charIndex < len(self.characters):
                        self.characters[charIndex].setCharacterAnimationFromIndex(animIndex)

            except TypeError:
                print("Failed to catch script data for event!")
                self.doOnKill()
            except FileInvalidCritical:
                print("Failed to fetch required data for event!")
                self.doOnKill()
        
            goalInfoEntry = self.laytonState.getGoalInfEntry()
            # TODO - Popup if unk is 1

            if goalInfoEntry != None:
                print("\tUpdated goal to", goalInfoEntry.goal)
                self.laytonState.saveSlot.goal = goalInfoEntry.goal

    def doOnKill(self):
        # TODO - Research more into next handler. What happens if the next gamemode is set in chapter event? Or normal gamemode?
        # When reaching a forced save screen, will this force the event to run twice? Perhaps hitting no on the question to save invalidates this event.

        # According to research, this event should run first, destroying the event currently queued to play. But playing the game, the chapter event plays first.
        # Why is this the case?
        if self.laytonState.saveSlot.idImmediateEvent != -1:
            self.laytonState.setEventId(self.laytonState.saveSlot.idImmediateEvent)
            self.laytonState.setGameMode(GAMEMODES.DramaEvent)
            self.laytonState.saveSlot.idImmediateEvent = -1
        super().doOnKill()

    def draw(self, gameDisplay):
        for controller in self.characters:
            controller.draw(gameDisplay)
        super().draw(gameDisplay)

    def update(self, gameClockDelta):
        for controller in self.characters:
            controller.update(gameClockDelta)

        super().update(gameClockDelta)

    def _spriteOffAllCharacters(self):
        # TODO - Not a good hack! If a fader doesn't need to activate, this can be called immediately, breaking the order of execution!
        for character in self.characters:
            character.setVisibility(False)
        self._makeActive()

    def _doUnpackedCommand(self, opcode, operands):

        def isCharacterSlotValid(indexSlot):
            if type(indexSlot) == int and 0 <= indexSlot <= 7:
                if indexSlot < len(self.characters):
                    return True
            return False

        if opcode == OPCODES_LT2.TextWindow.value:
            tempTalkScript = self._packEventTalk.getFile(PATH_PACK_TALK % (self._idMain, self._idSub, operands[0].value))
            if tempTalkScript != None:
                self.talkScript = GdScript()
                self.talkScript.load(tempTalkScript, isTalkscript=True)
                self._popup = TextWindow(self.laytonState, self.characterSpawnIdToCharacterMap, self.talkScript)
            else:
                # TODO - In reality, if talkscript fails the popup will still appear with whatever text was left in the string buffer
                print("\tTalk script missing!", PATH_PACK_TALK % (self._idMain, self._idSub, operands[0].value))

        elif opcode == OPCODES_LT2.SpriteOn.value:
            if isCharacterSlotValid(operands[0].value):
                self.characters[operands[0].value].setVisibility(True)

        elif opcode == OPCODES_LT2.SpriteOff.value:
            if isCharacterSlotValid(operands[0].value):
                self.characters[operands[0].value].setVisibility(False)

        elif opcode == OPCODES_LT2.DoSpriteFade.value:
            if isCharacterSlotValid(operands[0].value):
                self.characters[operands[0].value].setVisibility(operands[1].value >= 0)

        elif opcode == OPCODES_LT2.DrawChapter.value:
            
            def callbackDrawChapter():
                self._spriteOffAllCharacters()
                self.screenController.setBgMain(PATH_CHAP_ROOT % operands[0].value)
                self.screenController.fadeInMain()
                self._isWaitingForTouch = True
                self._makeInactive()

            self._makeInactive()
            self.screenController.fadeOutMain(duration=0, callback=callbackDrawChapter)
        
        elif opcode == OPCODES_LT2.SetSpritePos.value:
            if isCharacterSlotValid(operands[0].value):
                self.characters[operands[0].value].setCharacterSlot(operands[1].value)
        
        elif opcode == OPCODES_LT2.SetSpriteAnimation.value:
            if operands[0].value in self.characterSpawnIdToCharacterMap:
                self.characterSpawnIdToCharacterMap[operands[0].value].setCharacterAnimationFromName(operands[1].value)

        elif opcode == OPCODES_LT2.GameOver.value:
            # TODO - Remove const. Understand behaviour first. Plays some sound effects and stops BGM.
            def switchToReset():
                self.laytonState.setGameMode(GAMEMODES.Reset)
                self._makeActive()

            def switchToFadeOut():
                self._makeInactive()
                self.screenController.fadeOut(callback=switchToReset)
            
            self._makeInactive()
            timeEntry = self.laytonState.getTimeDefinitionEntry(0x3f1)
            if timeEntry != None:
                self._faderWait.setCallback(switchToFadeOut)
                self._faderWait.setDurationInFrames(timeEntry.countFrames)
            else:
                switchToFadeOut()

        elif opcode == OPCODES_LT2.DoHukamaruAddScreen.value:
            # TODO - Not accurate, but required to get fading looking correct
            self._makeInactive()
            self.screenController.fadeOut(callback=self._spriteOffAllCharacters)

        elif opcode == OPCODES_LT2.DoSubItemAddScreen.value:
            self._popup = PlaceholderPopup()

        elif opcode == OPCODES_LT2.DoStockScreen.value:
            # TODO - This will still execute even if entryNzLst was empty, right. Come up as ID 0
            if self.laytonState.entryNzList != None:
                if self.laytonState.entryNzList.idInternal != 0x87 and self.laytonState.entryNzList.idInternal != 0xcb:
                    self._popup = StockPopup(self.laytonState, self.screenController, self._sharedImageHandler)
        
        elif opcode == OPCODES_LT2.DoNazobaListScreen.value:

            def switchToNazobaList():
                for character in self.characters:
                    character.setVisibility(False)
                self._popup = NazobaListPopup(self.laytonState, self.screenController, self._makeActive, operands[0].value)
            
            self._makeInactive()
            self.screenController.fadeOut(callback=switchToNazobaList)

        elif opcode == OPCODES_LT2.DoItemAddScreen.value:
            self.laytonState.saveSlot.storyItemFlag.setSlot(True, operands[0].value)
            if operands[0].value != 2:
                self._popup = ItemAddPopup(self.laytonState, self.screenController, self._sharedImageHandler, operands[0].value)
        
        elif opcode == OPCODES_LT2.SetSubItem.value:
            self._popup = PlaceholderPopup()
        
        elif opcode == OPCODES_LT2.DoSubGameAddScreen.value:
            self._popup = SubGameAddPopup(self.laytonState, self.screenController, self._sharedImageHandler, operands[0].value)
        
        elif opcode == OPCODES_LT2.DoSaveScreen.value:

            def clearPopup():
                self._popup = None
                self._spriteOffAllCharacters()

            def callbackKillPopup():
                self.screenController.fadeOut(callback=clearPopup)

            def spawnSaveScreenAndTerminateCharacters():
                self._popup = SaveLoadScreenPopup(self.laytonState, self.screenController, SaveLoadScreenPopup.MODE_SAVE, None, callbackKillPopup, callbackKillPopup)

            def switchPopupToSaveScreen():
                self.screenController.fadeOut(callback=spawnSaveScreenAndTerminateCharacters)

            self._makeInactive()
            self._popup = SaveButtonPopup(self.laytonState, self.screenController, self._sharedImageHandler, switchPopupToSaveScreen, callbackKillPopup)
            # TODO - Not accurate. Research required
            if operands[0].value != -1:
                self.laytonState.saveSlot.idImmediateEvent = operands[0].value
        
        elif opcode == OPCODES_LT2.DoPhotoPieceAddScreen.value:
            self.laytonState.saveSlot.photoPieceFlag.setSlot(True, operands[0].value)
            photoPieceAddCounter = bytearray(self.laytonState.saveSlot.eventCounter.toBytes(outLength=128))
            photoPieceAddCounter[0x18] = photoPieceAddCounter[0x18] + 1
            self.laytonState.saveSlot.eventCounter = FlagsAsArray.fromBytes(photoPieceAddCounter)
            self._popup = PhotoPieceAddPopup(self.laytonState, self.screenController, self._sharedImageHandler)
        
        elif opcode == OPCODES_LT2.MokutekiScreen.value:
            self._popup = PlaceholderPopup()
        
        elif opcode == OPCODES_LT2.DoNamingHamScreen.value:
            self._popup = NamingHamPopup(self.laytonState, self.screenController, self._sharedImageHandler)

        elif opcode == OPCODES_LT2.DoLostPieceScreen.value:
            self._popup = PlaceholderPopup()
        
        elif opcode == OPCODES_LT2.DoInPartyScreen.value:
            self._popup = PlaceholderPopup()
        
        elif opcode == OPCODES_LT2.DoOutPartyScreen.value:
            self._popup = PlaceholderPopup()

        elif opcode == OPCODES_LT2.DoDiaryAddScreen.value:
            # Stubbed, but don't want an error
            pass

        else:
            return super()._doUnpackedCommand(opcode, operands)

        return True