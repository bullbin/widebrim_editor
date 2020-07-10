from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.file import FileInterface
from ..engine.state.enum_mode import GAMEMODES, STRING_TO_GAMEMODE_VALUE
from ..engine.const import PATH_EVENT_SCRIPT, PATH_EVENT_SCRIPT_A, PATH_EVENT_SCRIPT_B, PATH_EVENT_SCRIPT_C, PATH_EVENT_TALK, PATH_EVENT_TALK_A, PATH_EVENT_TALK_B, PATH_EVENT_TALK_C, PATH_PACK_EVENT_DAT, PATH_PACK_EVENT_SCR, PATH_PACK_TALK
from ..madhatter.hat_io.asset import LaytonPack
from ..madhatter.hat_io.asset_script import GdScript
from ..madhatter.hat_io.asset_sav import FlagsAsArray
from ..madhatter.typewriter.stringsLt2 import OPCODES_LT2

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

        # print("Tried to add drama layer...")

        ScreenLayerNonBlocking.__init__(self)
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

            except:
                print("Failed to fetch required data for event!")
                self._canBeKilled = True
        
        goalInfoEntry = self.laytonState.getGoalInfEntry()
        # TODO - Goal versus objective?
        if goalInfoEntry != None:
            self.laytonState.saveSlot.chapter = goalInfoEntry.goal
            self.laytonState.saveSlot.goal = goalInfoEntry.goal

        if not(self._canBeKilled):
            if self.laytonState.entryEvInfo.indexEventViewedFlag != None:
                self.laytonState.saveSlot.eventViewed.setSlot(True, self.laytonState.entryEvInfo.indexEventViewedFlag)

        self.screenController.fadeIn()

        print("Loaded event", spawnId)

    def update(self, gameClockDelta):
        if not(self._canBeKilled):
            while self.scriptCurrentCommandIndex < self.script.getInstructionCount():
                
                command = self.script.getInstruction(self.scriptCurrentCommandIndex)
                opcode = int.from_bytes(command.opcode, byteorder = 'little')
                
                if opcode == OPCODES_LT2.SetGameMode.value:
                    try:
                        self.laytonState.setGameMode(GAMEMODES(STRING_TO_GAMEMODE_VALUE[command.operands[0].value[:-1]]))
                        print("Set current context to", self.laytonState.getGameMode().name)
                    except:
                        print("SetGameMode Handler", command.operands[0].value, "unimplemented!")
                
                elif opcode == OPCODES_LT2.SetEndGameMode.value:
                    try:
                        self.laytonState.setGameModeNext(GAMEMODES(STRING_TO_GAMEMODE_VALUE[command.operands[0].value[:-1]]))
                        print("Set next context to", self.laytonState.getGameModeNext().name)
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

                elif opcode == OPCODES_LT2.LoadSubBG.value:
                    self.screenController.setBgSub(command.operands[0].value)

                elif opcode == OPCODES_LT2.SetMovieNum.value:
                    self.laytonState.setMovieNum(command.operands[0].value)

                elif opcode == OPCODES_LT2.ModifyBGPal.value:
                    # TODO - 3 unknowns in this command
                    self.screenController.modifyPaletteMain(command.operands[3].value)

                elif opcode == OPCODES_LT2.ModifySubBGPal.value:
                    self.screenController.modifyPaletteSub(command.operands[3].value)

                else:
                    #print("\tSkipped command!")
                    print("Unimplemented", OPCODES_LT2(opcode).name)

                self.scriptCurrentCommandIndex += 1
            
            # TODO - REENABLE THIS BEFORE PUSH!!
            self._canBeKilled = True