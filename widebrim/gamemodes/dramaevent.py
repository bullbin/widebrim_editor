from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES, STRING_TO_GAMEMODE_VALUE
from ..engine.anim.image_anim import AnimatedImageObject
from ..engine.anim.fader import Fader
from ..engine.anim.font.scrolling import ScrollingFontHelper
from ..engine.exceptions import FileInvalidCritical
from ..engine.file import FileInterface

from ..engine.const import PATH_CHAP_ROOT, RESOLUTION_NINTENDO_DS, PATH_FACE_ROOT, PATH_BODY_ROOT, TIME_FRAMECOUNT_TO_MILLISECONDS
from ..engine.const import PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C
from ..engine.const import PATH_PACK_EVENT_DAT, PATH_PACK_EVENT_SCR, PATH_PACK_TALK, PATH_EVENT_BG, PATH_PLACE_BG, PATH_EVENT_ROOT, PATH_ANI, PATH_NAME_ROOT

from ..madhatter.hat_io.asset import LaytonPack
from ..madhatter.hat_io.asset_script import GdScript
from ..madhatter.hat_io.asset_sav import FlagsAsArray
from ..madhatter.hat_io.asset_image import AnimatedImage
from ..madhatter.typewriter.stringsLt2 import OPCODES_LT2

# TODO - Remove workaround by properly creating library
from ..madhatter.hat_io.binary import BinaryReader

from pygame import Surface, MOUSEBUTTONUP
from pygame.transform import flip

def functionGetAnimationFromName(name):
    name = name.split(".")[0] + ".arc"
    resolvedPath = PATH_FACE_ROOT % name
    return FileInterface.getData(resolvedPath)

# TODO - Bugfix, Layton anim b2 normal has an extra space that for some reason is not counted. Present in RAM dumps as well so being loaded with that space.
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

# TODO - Centralise a popup with background and cursor fade in, used in TextWindow and all other event windows (eg reward popup, stock screen)

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
            if scriptTextWindow.getInstruction(0).operands[1].value != "NONE\x00":
                self.characterController.setCharacterAnimationFromName(scriptTextWindow.getInstruction(0).operands[1].value[:-1])
            if scriptTextWindow.getInstruction(0).operands[2].value != "NONE\x00":
                self.animNameOnExit = scriptTextWindow.getInstruction(0).operands[2].value[:-1]
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
        animName = animName.split("\x00")[0]
        if self.imageCharacter != None:
            if self.imageCharacter.setAnimationFromName(animName):
                self._baseAnimName = self.imageCharacter.animActive.name
    
    def setCharacterAnimationFromIndex(self, animIndex):
        if self.imageCharacter != None:
            if self.imageCharacter.setAnimationFromIndex(animIndex):
                self._baseAnimName = self.imageCharacter.animActive.name

class EventPlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):

        def substituteEventPath(inPath, inPathA, inPathB, inPathC):

            def trySubstitute(path, lang, evId):
                try:
                    return path % (lang, evId)
                except TypeError:
                    return path % evId

            if self.eventId != 24:
                return trySubstitute(inPath, self.laytonState.language.value, self.eventId)
            elif self.eventSubId < 300:
                return trySubstitute(inPathA, self.laytonState.language.value, self.eventId)
            elif self.eventSubId < 600:
                return trySubstitute(inPathB, self.laytonState.language.value, self.eventId)
            else:
                return trySubstitute(inPathC, self.laytonState.language.value, self.eventId)

        def getEventTalkPath():
            return substituteEventPath(PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C)

        def getEventScriptPath():
            return substituteEventPath(PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C)

        # TODO - Search for language image as well as non-language image

        ScreenLayerNonBlocking.__init__(self)
        self.screenController = screenController
        self.laytonState = laytonState

        # Looking at binary reveals that it actually sets the current mode to room..
        # TODO - This should be GameMode. Causes a regression however at event 20003
        self.laytonState.setGameModeNext(GAMEMODES.Room)
        self.packEventTalk = LaytonPack()

        self.scriptCurrentCommandIndex = 0
        self.script         = GdScript()
        self.talkScript     = GdScript()
        self.eventData      = None

        spawnId = self.laytonState.getEventId()
        self.eventId = spawnId // 1000
        self.eventSubId = spawnId % 1000

        self.characters = []
        self.nameCharacters = []
        self.characterSpawnIdToCharacterMap = {}

        self.isWaitingForTouch = False
        self.popup = None

        if spawnId == -1:
            self.terminate()
        else:
            print("Loaded event", spawnId)
            # Centralise this so it can be deleted when finished
            try:
                self.packEventTalk.load(FileInterface.getData(getEventTalkPath()))
                packEventScript = LaytonPack()
                packEventScript.load(FileInterface.getData(getEventScriptPath()))

                self.script.load(packEventScript.getFile(PATH_PACK_EVENT_SCR % (self.eventId, self.eventSubId)))
                self.eventData = packEventScript.getFile(PATH_PACK_EVENT_DAT % (self.eventId, self.eventSubId))

                # TODO - Rewrite event info module

                if self.eventData == None:
                    raise FileInvalidCritical()
            
                self.eventData = BinaryReader(data=self.eventData)
                self.screenController.setBgMain(PATH_PLACE_BG % self.eventData.readU16())
                self.screenController.setBgSub(PATH_EVENT_BG % self.eventData.readU16())

                introBehaviour = self.eventData.readUInt(1)
                if introBehaviour == 0 or introBehaviour == 3:
                    self.screenController.modifyPaletteMain(120)
                
                if introBehaviour != 1:
                    self.screenController.fadeIn()

                self.eventData.seek(6)
                for charIndex in range(8):
                    character = self.eventData.readUInt(1)
                    if character != 0:
                        self.characters.append(CharacterController(self.laytonState, character))
                        self.characterSpawnIdToCharacterMap[character] = self.characters[-1]

                for charIndex in range(8):
                    slot = self.eventData.readUInt(1)
                    if charIndex < len(self.characters):
                        self.characters[charIndex].setCharacterSlot(slot)

                for charIndex in range(8):
                    visibility = self.eventData.readUInt(1) == 1
                    if charIndex < len(self.characters):
                        self.characters[charIndex].setVisibility(visibility)
                
                for charIndex in range(8):
                    animIndex = self.eventData.readUInt(1)
                    if charIndex < len(self.characters):
                        self.characters[charIndex].setCharacterAnimationFromIndex(animIndex)

            except TypeError:
                print("Failed to catch script data for event!")
                self.terminate()
            except FileInvalidCritical:
                print("Failed to fetch required data for event!")
                self.terminate()
        
            goalInfoEntry = self.laytonState.getGoalInfEntry()
            # TODO - Goal versus objective?
            # Maybe if unk is 1, also update chapter.

            # TODO - This is incorrect. Photo event sequence proves this
            # After initial photo event which triggers popup, chapter and goal are different.
            # FML

            if goalInfoEntry != None:
                # Does the unk cause the window to pop up?
                if goalInfoEntry.type == 1:
                    print("\tUpdated goal and chapter to", goalInfoEntry.goal)
                    self.laytonState.saveSlot.chapter = goalInfoEntry.goal
                else:
                    print("\tUpdated goal to", goalInfoEntry.goal)
                self.laytonState.saveSlot.goal = goalInfoEntry.goal

            if not(self._canBeKilled):
                if self.laytonState.entryEvInfo != None and self.laytonState.entryEvInfo.indexEventViewedFlag != None:
                    self.laytonState.saveSlot.eventViewed.setSlot(True, self.laytonState.entryEvInfo.indexEventViewedFlag)

    def terminate(self):
        # TODO - Bugfix required. This should be current gamemode but it doesn't work.
        # This unfortunately doesn't spawn correct behaviour anyway under this model but it still needs to be fixed.
        # TODO - Research more into next handler. What happens if the next gamemode is set in chapter event? Or normal gamemode?
        # When reaching a forced save screen, will this force the event to run twice? Perhaps hitting no on the question to save invalidates this event.

        # According to research, this event should run first, destroying the event currently queued to play. But playing the game, the chapter event plays first.
        # Why is this the case?

        if self.laytonState.saveSlot.idImmediateEvent != -1:
            self.laytonState.setEventId(self.laytonState.saveSlot.idImmediateEvent)
            self.laytonState.setGameModeNext(GAMEMODES.DramaEvent)
            self.laytonState.saveSlot.idImmediateEvent = -1
        self._canBeKilled = True

    def draw(self, gameDisplay):
        
        for controller in self.characters:
            controller.draw(gameDisplay)

        if self.popup != None:
            self.popup.draw(gameDisplay)

    def handleTouchEvent(self, event):
        if self.popup != None:
            self.popup.handleTouchEvent(event)
        elif self.isWaitingForTouch and event.type == MOUSEBUTTONUP:
            self.isWaitingForTouch = False
        return super().handleTouchEvent(event)

    def update(self, gameClockDelta):
        # TODO - Maybe also detect if popup active
        if self.screenController.getFadingStatus():
            return self.updateBlocked(gameClockDelta)
        return self.updateNonBlocked(gameClockDelta)

    def updateBlocked(self, gameClockDelta):
        for controller in self.characters:
            controller.update(gameClockDelta)

    def updateNonBlocked(self, gameClockDelta):

        def triggerPopup(popup):
            self.popup = popup
            self.scriptCurrentCommandIndex += 1

        if not(self._canBeKilled):
            if self.popup == None:
                while not(self.isWaitingForTouch) and self.scriptCurrentCommandIndex < self.script.getInstructionCount() and not(self.screenController.getFadingStatus()):
                    
                    command = self.script.getInstruction(self.scriptCurrentCommandIndex)
                    opcode = int.from_bytes(command.opcode, byteorder = 'little')
                    
                    if opcode == OPCODES_LT2.TextWindow.value:

                        self.talkScript = GdScript()
                        self.talkScript.load(self.packEventTalk.getFile(PATH_PACK_TALK % (self.eventId, self.eventSubId, command.operands[0].value)), isTalkscript=True)
                        triggerPopup(TextWindow(self.laytonState, self.characterSpawnIdToCharacterMap, self.talkScript))
                        break

                    elif opcode == OPCODES_LT2.WaitInput.value:
                        self.isWaitingForTouch = True

                    elif opcode == OPCODES_LT2.DoStockScreen.value:
                        triggerPopup(PlaceholderPopup())
                        break

                    elif opcode == OPCODES_LT2.DoSubItemAddScreen.value:
                        # TODO - Only trigger on popups which mean something
                        if self.laytonState.entryNzList != None and self.laytonState.entryNzList.idReward != -1:
                            triggerPopup(PlaceholderPopup())
                            break
                    
                    elif opcode == OPCODES_LT2.DoHukamaruAddScreen.value:
                        # TODO - Not accurate, but required to get fading looking correct
                        self.screenController.obscureViewLayer()

                        # TODO - How best to handle this?
                        for character in self.characters:
                            character.setVisibility(False)
                    
                    elif opcode == OPCODES_LT2.DoSaveScreen.value:
                        # TODO - Not accurate, but required to not softlock. Research required
                        self.screenController.obscureViewLayer()
                        if command.operands[0].value != -1:
                            self.laytonState.saveSlot.idImmediateEvent = command.operands[0].value
                    
                    elif opcode == OPCODES_LT2.DoItemAddScreen.value:
                        self.laytonState.saveSlot.storyItemFlag.setSlot(True, command.operands[0].value)
                        triggerPopup(PlaceholderPopup())
                        break

                    elif opcode == OPCODES_LT2.DoPhotoPieceAddScreen.value:
                        self.laytonState.saveSlot.photoPieceFlag.setSlot(True, command.operands[0].value)

                        photoPieceAddCounter = bytearray(self.laytonState.saveSlot.eventCounter.toBytes(outLength=128))
                        photoPieceAddCounter[0x18] = photoPieceAddCounter[0x18] + 1
                        if photoPieceAddCounter[0x18] == 0:
                            # String in popup is 222
                            pass
                        else:
                            # String in popup is 212
                            pass
                        self.laytonState.saveSlot.eventCounter = FlagsAsArray.fromBytes(photoPieceAddCounter)

                        triggerPopup(PlaceholderPopup())
                        break

                    elif opcode == OPCODES_LT2.SetGameMode.value:
                        try:
                            self.laytonState.setGameMode(STRING_TO_GAMEMODE_VALUE[command.operands[0].value[:-1]])
                        except:
                            print("SetGameMode Handler", command.operands[0].value, "unimplemented!")
                    
                    elif opcode == OPCODES_LT2.SetEndGameMode.value:
                        try:
                            self.laytonState.setGameModeNext(STRING_TO_GAMEMODE_VALUE[command.operands[0].value[:-1]])
                        except:
                            print("SetEndGameMode Handler", command.operands[0].value, "unimplemented!")

                    elif opcode == OPCODES_LT2.SetDramaEventNum.value:
                        self.laytonState.setEventId(command.operands[0].value)

                    elif opcode == OPCODES_LT2.SetPuzzleNum.value:
                        self.laytonState.setPuzzleId(command.operands[0].value)
                    
                    elif opcode == OPCODES_LT2.ReleaseItem.value:
                        self.laytonState.saveSlot.storyItemFlag.setSlot(False, command.operands[0].value)
                    
                    elif opcode == OPCODES_LT2.SetPlace.value:
                        self.laytonState.saveSlot.roomIndex = command.operands[0].value
                    
                    elif opcode == OPCODES_LT2.SetEventCounter.value:
                        indexCounter = command.operands[0].value
                        valueCounter = command.operands[1].value

                        if 0 <= indexCounter < 128:
                            tempEventCounter = bytearray(self.laytonState.saveSlot.eventCounter.toBytes(outLength=128))
                            tempEventCounter[indexCounter] = valueCounter
                            self.laytonState.saveSlot.eventCounter = FlagsAsArray.fromBytes(tempEventCounter)
                    
                    # TODO - Auto event repeat

                    elif opcode == OPCODES_LT2.AddEventCounter.value:
                        indexCounter = command.operands[0].value
                        valueCounter = command.operands[1].value

                        if 0 <= indexCounter < 128:
                            tempEventCounter = bytearray(self.laytonState.saveSlot.eventCounter.toBytes(outLength=128))
                            tempEventCounter[indexCounter] = tempEventCounter[indexCounter] + valueCounter
                            self.laytonState.saveSlot.eventCounter = FlagsAsArray.fromBytes(tempEventCounter)

                    elif opcode == OPCODES_LT2.OrEventCounter.value:
                        indexCounter = command.operands[0].value
                        valueCounter = command.operands[1].value

                        if 0 <= indexCounter < 128:
                            tempEventCounter = bytearray(self.laytonState.saveSlot.eventCounter.toBytes(outLength=128))
                            tempEventCounter[indexCounter] = tempEventCounter[indexCounter] | valueCounter
                            self.laytonState.saveSlot.eventCounter = FlagsAsArray.fromBytes(tempEventCounter)

                    elif opcode == OPCODES_LT2.AddMemo.value:
                        self.laytonState.saveSlot.memoFlag.flagEnabled.setSlot(True, command.operands[0].value)
                        self.laytonState.saveSlot.memoFlag.flagNew.setSlot(True, command.operands[0].value)

                    elif opcode == OPCODES_LT2.LoadBG.value:
                        self.screenController.setBgMain(command.operands[0].value)
            
                    elif opcode == OPCODES_LT2.LoadSubBG.value:
                        self.screenController.setBgSub(command.operands[0].value)

                    elif opcode == OPCODES_LT2.SetMovieNum.value:
                        self.laytonState.setMovieNum(command.operands[0].value)

                    elif opcode == OPCODES_LT2.SetEventTea.value:
                        self.laytonState.setGameModeNext(GAMEMODES.EventTea)
                        # TODO - 2 unks, maybe about the current tea mode?
                        # Additionally, the tea screen uses the current state of the bottom screen, which needs to be captured.
                        # This could be a problem with current pipeline as the fader writes over the screen
                        # Maybe this could be recorded in the fader layer before the obstruction

                    elif opcode == OPCODES_LT2.CheckCounterAutoEvent.value:
                        if 0 <= command.operands[0].value < 128:
                            # Type 0 of CheckEventCounter
                            eventCounterEncoded = self.laytonState.saveSlot.eventCounter.toBytes(outLength=128)
                            if eventCounterEncoded[command.operands[0].value] == command.operands[1].value:
                                self.laytonState.setGameMode(GAMEMODES.DramaEvent)
                                self.laytonState.setGameModeNext(GAMEMODES.DramaEvent)



                    elif opcode == OPCODES_LT2.ModifyBGPal.value:
                        # TODO - 3 unknowns in this command
                        self.screenController.modifyPaletteMain(command.operands[3].value)

                    elif opcode == OPCODES_LT2.ModifySubBGPal.value:
                        self.screenController.modifyPaletteSub(command.operands[3].value)



                    elif opcode == OPCODES_LT2.DrawChapter.value:
                        self.screenController.fadeIn()
                        self.screenController.setBgMain(PATH_CHAP_ROOT % command.operands[0].value)
                        self.isWaitingForTouch = True



                    elif opcode == OPCODES_LT2.FadeIn.value:
                        self.screenController.fadeIn()
                    
                    elif opcode == OPCODES_LT2.FadeOut.value:
                        self.screenController.fadeOut()

                    elif opcode == OPCODES_LT2.FadeInFrame.value:
                        self.screenController.fadeIn(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS)
                    
                    elif opcode == OPCODES_LT2.FadeOutFrame.value:
                        self.screenController.fadeOut(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS)
                    
                    elif opcode == OPCODES_LT2.FadeInOnlyMain.value:
                        self.screenController.fadeInMain()
                    
                    elif opcode == OPCODES_LT2.FadeOutOnlyMain.value:
                        self.screenController.fadeOutMain()

                    elif opcode == OPCODES_LT2.FadeInFrameMain.value:
                        self.screenController.fadeInMain(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS)
                    
                    elif opcode == OPCODES_LT2.FadeOutFrameMain.value:
                        self.screenController.fadeOutMain(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS)
                    
                    elif opcode == OPCODES_LT2.FadeInFrameSub.value:
                        self.screenController.fadeInSub(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS)
                    
                    elif opcode == OPCODES_LT2.FadeOutFrameSub.value:
                        self.screenController.fadeOutSub(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS)

                    elif opcode == OPCODES_LT2.WaitFrame.value:
                        self.screenController.setWaitDuration(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS)

                    elif opcode == OPCODES_LT2.WaitVSyncOrPenTouch.value:
                        self.screenController.setWaitDuration(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS, canBeSkipped=True)



                    elif opcode == OPCODES_LT2.SpriteOn.value:
                        if 0 <= command.operands[0].value < len(self.characters):
                            self.characters[command.operands[0].value].setVisibility(True)

                    elif opcode == OPCODES_LT2.SpriteOff.value:
                        if 0 <= command.operands[0].value < len(self.characters):
                            self.characters[command.operands[0].value].setVisibility(False)

                    elif opcode == OPCODES_LT2.SetSpriteAnimation.value:
                        if command.operands[0].value in self.characterSpawnIdToCharacterMap:
                            self.characterSpawnIdToCharacterMap[command.operands[0].value].setCharacterAnimationFromName(command.operands[1].value)

                    elif opcode == OPCODES_LT2.SetSpritePos.value:
                        if command.operands[0].value < len(self.characters):
                            self.characters[command.operands[0].value].setCharacterSlot(command.operands[1].value)

                    elif opcode == OPCODES_LT2.DoSpriteFade.value:
                        self.characters[command.operands[0].value].setVisibility(command.operands[1].value >= 0)

                    else:
                        #print("\tSkipped command!")
                        print("\nUnimplemented", OPCODES_LT2(opcode).name)
                        print(command)

                    self.scriptCurrentCommandIndex += 1
                
                if not(self.isWaitingForTouch) and not(self.screenController.getFadingStatus()) and self.scriptCurrentCommandIndex >= self.script.getInstructionCount() and self.popup == None:
                    self.terminate()
            else:
                self.popup.update(gameClockDelta)
                if self.popup.canBeTerminated:
                    self.popup = None
        
        for controller in self.characters:
            controller.update(gameClockDelta)