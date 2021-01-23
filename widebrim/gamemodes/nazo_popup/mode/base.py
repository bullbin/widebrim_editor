from ....engine.state.enum_mode import GAMEMODES
from ....engine.file import FileInterface
from ....engine.const import PATH_PUZZLE_SCRIPT, PATH_PACK_PUZZLE, PATH_PUZZLE_BG, PATH_PUZZLE_BG_LANGUAGE, PATH_PUZZLE_BG_NAZO_TEXT
from ....engine_ext.utils import getImageFromPath
from ....engine.anim.font.scrolling import ScrollingFontHelper
from ...core_popup.script import ScriptPlayer
from ....madhatter.hat_io.asset_dat.nazo import NazoData
from ....madhatter.hat_io.asset import LaytonPack
from ....madhatter.hat_io.asset_script import GdScript

# TODO - Get positions from game. Currently from shortbrim
# TODO - What happens if the scroller draws too many lines for the top screen? Does it go to the bottom?

class BaseQuestionObject(ScriptPlayer):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, GdScript())

        nzLstEntry = laytonState.getCurrentNazoListEntry()
        nazoData = laytonState.getNazoData()

        self.__isPuzzleElementsActive = False
        self.__scrollerPrompt = ScrollingFontHelper(self.laytonState.fontQ, yBias=2)
        self.__scrollerPrompt.setPos((11,22))

        # Set backgrounds
        if nazoData != None and nzLstEntry != None:
            if nazoData.flagUseLanguageBackground:
                screenController.setBgMain(PATH_PUZZLE_BG_LANGUAGE % nazoData.bgMainId)
            else:
                screenController.setBgMain(PATH_PUZZLE_BG % nazoData.bgMainId)

            screenController.setBgSub(PATH_PUZZLE_BG_NAZO_TEXT % nazoData.bgSubId)

            self.__scrollerPrompt.setText(nazoData.getTextPrompt())

        # Some wifi check here
        
        # Initialise script
        packPuzzleScript = LaytonPack()
        packPuzzleScriptData = FileInterface.getData(PATH_PUZZLE_SCRIPT)
        if packPuzzleScriptData != None:
            packPuzzleScript.load(packPuzzleScriptData)

        if nzLstEntry != None:
            scriptData = packPuzzleScript.getFile(PATH_PACK_PUZZLE % nzLstEntry.idInternal)
            if scriptData != None:
                self._script.load(scriptData)

        # Set end gamemode on finish
        # TODO - Gamemode 11 used?
        if laytonState.getGameModeNext() not in [GAMEMODES.UnkNazo, GAMEMODES.Room,
                                                 GAMEMODES.Jiten0, GAMEMODES.Jiten1,
                                                 GAMEMODES.SecretJiten, GAMEMODES.Challenge,
                                                 GAMEMODES.Nazoba]:
            laytonState.setGameModeNext(GAMEMODES.EndPuzzle)

        # TODO - Create hint mode popup and buttons to grab
        # TODO - Then call mode to create game environment
    
    def __enablePuzzleElements(self):
        self.__isPuzzleElementsActive = True
    
    def __disablePuzzleElements(self):
        self.__isPuzzleElementsActive = False
    
    def __getPuzzleElementsEnabledState(self):
        return self.__isPuzzleElementsActive

    def _doUnpackedCommand(self, opcode, operands):
        # Puzzles stub out all other commands, so always return False
        return False

    def update(self, gameClockDelta):
        super().update(gameClockDelta)
        if self.__getPuzzleElementsEnabledState():
            self.__scrollerPrompt.update(gameClockDelta)
            self.updatePuzzleElements(gameClockDelta)
    
    def draw(self, gameDisplay):
        super().draw(gameDisplay)
        self.__scrollerPrompt.draw(gameDisplay)
        self.drawPuzzleElements(gameDisplay)
    
    def handleTouchEvent(self, event):
        self.handleTouchEventPuzzleElements(event)
        return super().handleTouchEvent(event)

    def updatePuzzleElements(self, gameClockDelta):
        pass

    def drawPuzzleElements(self, gameDisplay):
        pass

    def handleTouchEventPuzzleElements(self, event):
        return False

    def doOnComplete(self):
        # Start puzzle, so fade in...
        # Override kill behaviour, since this indicates puzzle script has finished loading
        self.screenController.fadeIn(callback=self.__enablePuzzleElements)
        pass