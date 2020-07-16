from ..engine.state.layer import ScreenLayerBlocking, ScreenCollectionBlocking
from ..engine.state.enum_mode import GAMEMODES, STRING_TO_GAMEMODE_VALUE
from ..engine.anim.image_anim import AnimatedImageObject
from ..engine.exceptions import FileInvalidCritical
from ..engine.file import FileInterface

from ..engine.const import PATH_CHAP_ROOT, RESOLUTION_NINTENDO_DS, PATH_FACE_ROOT, PATH_BODY_ROOT, TIME_FRAMECOUNT_TO_MILLISECONDS
from ..engine.const import PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C
from ..engine.const import PATH_PACK_EVENT_DAT, PATH_PACK_EVENT_SCR, PATH_PACK_TALK

from ..madhatter.hat_io.asset import LaytonPack
from ..madhatter.hat_io.asset_script import GdScript
from ..madhatter.hat_io.asset_sav import FlagsAsArray
from ..madhatter.hat_io.asset_image import AnimatedImage
from ..madhatter.typewriter.stringsLt2 import OPCODES_LT2

# TODO - Remove workaround by properly creating library
from ..madhatter.hat_io.binary import BinaryReader

from pygame import Surface
from pygame.transform import flip

class EventPlayer(ScreenCollectionBlocking):
    def __init__(self, laytonState, screenController):
        ScreenCollectionBlocking.__init__(self)
        self.screenController = screenController
        self.addToCollection(EventHandler(laytonState, screenController))
    
    def isUpdateBlocked(self):
        return self.screenController.getFadingStatus()

    def update(self, gameClockDelta):
        if len(self._layers) == 0:
            self._canBeKilled = True
        else:
            super().update(gameClockDelta)

class CharacterController():

    SLOT_OFFSET = {0:0,     1:0,
                   2:0,     3:0,
                   4:52,    5:52,
                   6:0}
    SLOT_LEFT  = [0,3,4]    # Verified against game binary
    # Left side characters need flipping

    SLOT_RIGHT = [2,5,6]

    def __init__(self, characterIndex, characterInitialAnimIndex=0, characterVisible=False, characterSlot=0):

        dataCharacter = FileInterface.getData(PATH_BODY_ROOT % characterIndex)
        if dataCharacter != None:
            madhatterImage = AnimatedImage.fromBytesArc(dataCharacter, functionGetFileByName=self._functionGetAnimationFromName)
            self.imageCharacter = AnimatedImageObject.fromMadhatter(madhatterImage)
            self.imageCharacter.setAnimationFromIndex(characterInitialAnimIndex)
        else:
            self.imageCharacter = None

        self._visibility = characterVisible
        self._drawLocation = (0,0)

        self._characterIsFlipped = False
        self._characterFlippedSurface = Surface(self.imageCharacter.getDimensions()).convert_alpha()
        self._characterFlippedSurfaceNeedsUpdate = False

        self.setCharacterSlot(characterSlot)

    def update(self, gameClockDelta):
        if self.imageCharacter != None:
            if self._characterIsFlipped and (self.imageCharacter.update(gameClockDelta) or self._characterFlippedSurfaceNeedsUpdate):
                self._characterFlippedSurface.fill((0,0,0,0))
                self.imageCharacter.draw(self._characterFlippedSurface)
                self._characterFlippedSurface = flip(self._characterFlippedSurface, True, False)

    def draw(self, gameDisplay):
        if self._visibility and self.imageCharacter != None:
            if self._characterIsFlipped:
                gameDisplay.blit(self._characterFlippedSurface, self._drawLocation)
            else:
                self.imageCharacter.draw(gameDisplay)

    def _functionGetAnimationFromName(self, name):
        name = name.split(".")[0] + ".arc"
        resolvedPath = PATH_FACE_ROOT % name
        return FileInterface.getData(resolvedPath)

    def setVisibility(self, isVisible):
        self._visibility = isVisible
    
    def setCharacterSlot(self, slot):

        def getImageOffset():
            offset = self.imageCharacter.getVariable("drawoff")
            if offset != None:
                return (abs(offset[0]), abs(offset[1]))
            else:
                return (0,0)

        if slot in CharacterController.SLOT_OFFSET:
            self._slot = slot

            if self.imageCharacter != None:
                offset = CharacterController.SLOT_OFFSET[self._slot]
                variableOffset = getImageOffset()

                if slot in CharacterController.SLOT_LEFT:
                    self._characterIsFlipped = True
                    self._characterFlippedSurfaceNeedsUpdate = True
                    self.imageCharacter.setPos((0,0))
                    self._drawLocation = (offset + variableOffset[0], RESOLUTION_NINTENDO_DS[1] * 2 - variableOffset[1] - self.imageCharacter.getDimensions()[1])
                else:
                    self._characterIsFlipped = False
                    self._drawLocation = (RESOLUTION_NINTENDO_DS[0] - self.imageCharacter.getDimensions()[0] - offset - variableOffset[0],
                                          RESOLUTION_NINTENDO_DS[1] * 2 - self.imageCharacter.getDimensions()[1] - variableOffset[1])

                    self.imageCharacter.setPos(self._drawLocation)

    def setCharacterAnimationFromName(self, animName):
        animName = animName.split("\x00")[0]
        if self.imageCharacter != None:
            self.imageCharacter.setAnimationFromName(animName)
    
    def setCharacterAnimationFromIndex(self, animIndex):
        if self.imageCharacter != None:
            self.imageCharacter.setAnimationFromIndex(animIndex)

class EventHandler(ScreenLayerBlocking):
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

        # print("Tried to add drama layer...")

        # TODO - Search for language image as well as non-language image

        ScreenLayerBlocking.__init__(self)
        self.screenController = screenController
        self.laytonState = laytonState
        self.laytonState.setGameModeNext(GAMEMODES.Room)
        self.packEventTalk = LaytonPack()

        self.scriptCurrentCommandIndex = 0
        self.script = GdScript()
        self.eventData = None

        spawnId = self.laytonState.getEventId()
        self.eventId = spawnId // 1000
        self.eventSubId = spawnId % 1000

        self.characters = []
        self.characterSpawnIdToCharacterMap = {}

        if spawnId == -1:
            self._canBeKilled = True
        else:
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
                # TODO - Set BG
                self.eventData.seek(6)
                for charIndex in range(8):
                    character = self.eventData.readUInt(1)
                    if character != 0:
                        self.characters.append(CharacterController(character))
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

            except FileInvalidCritical:
                print("Failed to fetch required data for event!")
                self._canBeKilled = True
        
        goalInfoEntry = self.laytonState.getGoalInfEntry()
        # TODO - Goal versus objective?
        # Maybe if unk is 1, also update chapter.
        if goalInfoEntry != None:
            
            if goalInfoEntry.type == 1:
                print("\tUpdated goal and chapter to", goalInfoEntry.goal)
                self.laytonState.saveSlot.chapter = goalInfoEntry.goal
            else:
                print("\tUpdated goal to", goalInfoEntry.goal)
            self.laytonState.saveSlot.goal = goalInfoEntry.goal
        else:
            print("\tNothing to update objective to!")

        if not(self._canBeKilled):
            if self.laytonState.entryEvInfo.indexEventViewedFlag != None:
                self.laytonState.saveSlot.eventViewed.setSlot(True, self.laytonState.entryEvInfo.indexEventViewedFlag)

        self.hasFadedOut = False

        print("Loaded event", spawnId)

    def draw(self, gameDisplay):
        for controller in self.characters:
            controller.draw(gameDisplay)

    def updateNonBlocked(self, gameClockDelta):
        if not(self._canBeKilled):
            while self.scriptCurrentCommandIndex < self.script.getInstructionCount() and not(self.screenController.getFadingStatus()):
                
                command = self.script.getInstruction(self.scriptCurrentCommandIndex)
                opcode = int.from_bytes(command.opcode, byteorder = 'little')
                
                if opcode == OPCODES_LT2.SetGameMode.value:
                    try:
                        self.laytonState.setGameMode(GAMEMODES(STRING_TO_GAMEMODE_VALUE[command.operands[0].value[:-1]]))
                    except:
                        print("SetGameMode Handler", command.operands[0].value, "unimplemented!")
                
                elif opcode == OPCODES_LT2.SetEndGameMode.value:
                    try:
                        self.laytonState.setGameModeNext(GAMEMODES(STRING_TO_GAMEMODE_VALUE[command.operands[0].value[:-1]]))
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
                    self.screenController.modifyPaletteMain(0)
        
                elif opcode == OPCODES_LT2.LoadSubBG.value:
                    self.screenController.setBgSub(command.operands[0].value)
                    self.screenController.modifyPaletteSub(0)

                elif opcode == OPCODES_LT2.SetMovieNum.value:
                    self.laytonState.setMovieNum(command.operands[0].value)



                elif opcode == OPCODES_LT2.ModifyBGPal.value:
                    # TODO - 3 unknowns in this command
                    self.screenController.modifyPaletteMain(command.operands[3].value)

                elif opcode == OPCODES_LT2.ModifySubBGPal.value:
                    self.screenController.modifyPaletteSub(command.operands[3].value)



                elif opcode == OPCODES_LT2.DrawChapter.value:
                    self.screenController.fadeIn()
                    self.screenController.setBgMain(PATH_CHAP_ROOT % command.operands[0].value)
                    # TODO - Global way for waiting until touch



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

                elif opcode == OPCODES_LT2.DoHukamaruAddScreen.value:
                    # TODO - Not accurate, but required to get fading looking correct
                    self.screenController.fadeOut()

                    # TODO - How best to handle this?
                    for character in self.characters:
                        character.setVisibility(False)



                elif opcode == OPCODES_LT2.WaitFrame.value:
                    self.screenController.setWaitDuration(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS)

                elif opcode == OPCODES_LT2.WaitVSyncOrPenTouch.value:
                    self.screenController.setWaitDuration(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS, canBeSkipped=True)

                elif opcode == OPCODES_LT2.WaitFrame2.value:
                    # TODO - What is this?
                    self.screenController.setWaitDuration(duration=command.operands[0].value * TIME_FRAMECOUNT_TO_MILLISECONDS)



                elif opcode == OPCODES_LT2.SpriteOn.value:
                    if 0 <= command.operands[0].value < len(self.characters):
                        self.characters[command.operands[0].value].setVisibility(True)

                elif opcode == OPCODES_LT2.SpriteOff.value:
                    if 0 <= command.operands[0].value < len(self.characters):
                        self.characters[command.operands[0].value].setVisibility(False)

                elif opcode == OPCODES_LT2.SetSpriteAnimation.value:
                    if command.operands[0].value in self.characterSpawnIdToCharacterMap:
                        self.characterSpawnIdToCharacterMap[command.operands[0].value].setCharacterAnimationFromName(command.operands[1].value)

                else:
                    #print("\tSkipped command!")
                    print("Unimplemented", OPCODES_LT2(opcode).name)

                self.scriptCurrentCommandIndex += 1
            
            if not(self.screenController.getFadingStatus()) and self.scriptCurrentCommandIndex >= self.script.getInstructionCount():
                if self.hasFadedOut:
                    if self.screenController.getFaderIsViewObscured():
                        self._canBeKilled = True
                else:
                    self.screenController.obscureViewLayer()
                    self.hasFadedOut = True
        
        for controller in self.characters:
            controller.update(gameClockDelta)