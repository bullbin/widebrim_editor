from ....engine.state.enum_mode import GAMEMODES
from ....engine.file import FileInterface
from ....engine.const import PATH_PUZZLE_SCRIPT, PATH_PACK_PUZZLE, PATH_PUZZLE_BG, PATH_PUZZLE_BG_LANGUAGE, PATH_PUZZLE_BG_NAZO_TEXT, RESOLUTION_NINTENDO_DS
from ....engine_ext.utils import getImageFromPath, getAnimFromPath, getAnimFromPathWithAttributes
from ....engine.anim.font.scrolling import ScrollingFontHelper
from ....engine.anim.image_anim import ImageFontRenderer
from ....engine.anim.button import AnimatedButton
from ...core_popup.script import ScriptPlayer
from ....madhatter.hat_io.asset import LaytonPack
from ....madhatter.hat_io.asset_script import GdScript
from .const import PATH_ANI_SUB_TEXT, PATH_ANI_BTN_HINT, PATH_ANI_BTN_MEMO, PATH_ANI_BTN_QUIT, PATH_ANI_BTN_RESTART, PATH_ANI_BTN_SUBMIT

from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP

# TODO - Get positions from game. Currently from shortbrim
# TODO - What happens if the scroller draws too many lines for the top screen? Does it go to the bottom?

# TODO - This is from intro...
def getNumberFontRendererFromImage(anim, varName):
    if anim != None:
        output = ImageFontRenderer(anim)
        if anim.getVariable(varName) != None:
            xRightmost  = anim.getVariable(varName)[0]
            y           = anim.getVariable(varName)[1]
            stride      = anim.getVariable(varName)[2]
            maxNum      = anim.getVariable(varName)[5]

            output.setPos((xRightmost,y))
            output.setStride(stride)
            output.setMaxNum(maxNum)
        
        return output
    return None

class BaseQuestionObject(ScriptPlayer):

    POS_QUESTION_TEXT = (13,22)

    def __init__(self, laytonState, screenController, callbackOnTerminate):
        super().__init__(laytonState, screenController, GdScript())

        self._callbackOnTerminate = callbackOnTerminate

        nzLstEntry = laytonState.getCurrentNazoListEntry()
        nazoData = laytonState.getNazoData()

        self.__isPuzzleElementsActive = False
        self.__scrollerPrompt = ScrollingFontHelper(self.laytonState.fontQ, yBias=2)
        self.__scrollerPrompt.setPos(BaseQuestionObject.POS_QUESTION_TEXT) # Verified, 27_Question_MaybeDrawTopText

        # TODO - Unify language replacement, like bg
        self.__animSubText = getAnimFromPath(PATH_ANI_SUB_TEXT.replace("?", laytonState.language.value))

        self._loadPuzzleBg()
        if nazoData != None:
            self.screenController.setBgSub(PATH_PUZZLE_BG_NAZO_TEXT % nazoData.bgSubId)
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
        self.__buttons = []
        self.__getButtons()

        self._isTerminating = False
        self.__isInteractingWithPuzzle = False
    
    def __enablePuzzleElements(self):
        self.__isPuzzleElementsActive = True
    
    def __disablePuzzleElements(self):
        self.__isPuzzleElementsActive = False
    
    def __getPuzzleElementsEnabledState(self):
        return self.__isPuzzleElementsActive

    def _doUnpackedCommand(self, opcode, operands):
        # Puzzles stub out all other commands, so always return False
        return False
    
    def _doReset(self):
        pass

    def _setButtonEnabled(self):
        pass

    def update(self, gameClockDelta):
        if not(self._isTerminating):
            super().update(gameClockDelta)
            if self.__getPuzzleElementsEnabledState():
                self.__scrollerPrompt.update(gameClockDelta)
                for button in self.__buttons:
                    button.update(gameClockDelta)
                self.updatePuzzleElements(gameClockDelta)
    
    def draw(self, gameDisplay):
        super().draw(gameDisplay)
        self.__drawSubScreenOverlay(gameDisplay)
        self.__scrollerPrompt.draw(gameDisplay)
        for button in self.__buttons:
            button.draw(gameDisplay)
        self.drawPuzzleElements(gameDisplay)
    
    def handleTouchEvent(self, event):
        # TODO - TOUCH! animation
        if not(self._isTerminating):
            # TODO - Get mouse region, it's somewhere in binary
            if event.type == MOUSEBUTTONDOWN:
                x,y = event.pos
                if 0 <= x < 190:
                    self.__isInteractingWithPuzzle = True
                else:
                    self.__isInteractingWithPuzzle = False
            
            if self.__isInteractingWithPuzzle:
                x, y = event.pos
                if x > 190:
                    x = 190
                if y < RESOLUTION_NINTENDO_DS[1]:
                    y = RESOLUTION_NINTENDO_DS[1]
                event.pos = x,y
                self.handleTouchEventPuzzleElements(event)
            
                if event.type == MOUSEBUTTONUP:
                    self.__isInteractingWithPuzzle = False
            else:
                for button in self.__buttons:
                    button.handleTouchEvent(event)
            
        return super().handleTouchEvent(event)

    def updatePuzzleElements(self, gameClockDelta):
        pass

    def drawPuzzleElements(self, gameDisplay):
        pass

    def handleTouchEventPuzzleElements(self, event):
        return False

    def _wasAnswerSolution(self):
        return False

    def _startJudgement(self):
        self.laytonState.wasPuzzleSolved = self._wasAnswerSolution()
        self._isTerminating = True
        self.screenController.fadeOut(callback=self._callbackOnTerminate)

    def _doOnJudgementPress(self):
        self._startJudgement()

    def doOnComplete(self):
        # Start puzzle, so fade in...
        # Override kill behaviour, since this indicates puzzle script has finished loading
        self.screenController.fadeIn(callback=self.__enablePuzzleElements)
        pass

    def hasQuitButton(self):
        return True
    
    def hasMemoButton(self):
        return True
    
    def hasSubmitButton(self):
        return True
    
    def hasRestartButton(self):
        return True
    
    def __getButtons(self):
        def getButtonObject(pathAnim, callback=None):
            if "?" in pathAnim:
                pathAnim = pathAnim.replace("?", self.laytonState.language.value)
            elif "%s" in pathAnim:
                pathAnim = pathAnim % self.laytonState.language.value

            image = getAnimFromPathWithAttributes(pathAnim)
            if image != None:
                return AnimatedButton(image, "on", "off", callback=callback)
            return None
        
        def addIfNotNone(button):
            if button != None:
                self.__buttons.append(button)

        if self.hasQuitButton():
            addIfNotNone(getButtonObject(PATH_ANI_BTN_QUIT, self.__doQuit))
        if self.hasMemoButton():
            addIfNotNone(getButtonObject(PATH_ANI_BTN_MEMO))
        if self.hasRestartButton():
            addIfNotNone(getButtonObject(PATH_ANI_BTN_RESTART, callback=self._doReset))
        if self.hasSubmitButton():
            addIfNotNone(getButtonObject(PATH_ANI_BTN_SUBMIT, callback=self._doOnJudgementPress))

    def __doQuit(self):
        self.laytonState.wasPuzzleSkipped = True
        self.screenController.fadeOut(callback=self._callbackOnTerminate)

    def _loadPuzzleBg(self):
        nzLstEntry = self.laytonState.getCurrentNazoListEntry()
        nazoData = self.laytonState.getNazoData()

        # Set backgrounds
        if nazoData != None and nzLstEntry != None:
            if nazoData.flagUseLanguageBackground:
                self.screenController.setBgMain(PATH_PUZZLE_BG_LANGUAGE % nazoData.bgMainId)
            else:
                self.screenController.setBgMain(PATH_PUZZLE_BG % nazoData.bgMainId)

    def __drawSubScreenOverlay(self, gameDisplay):
        # TODO - 27_Question_MaybeDrawTopText
        # TODO - Probably more efficient to create a surface and cache this, since it only changes with hint coin usage
        nzLstEntry = self.laytonState.getCurrentNazoListEntry()
        if nzLstEntry != None and self.__animSubText != None:

            def drawFromVariable(nameVar, nameAnim):
                posVars = self.__animSubText.getVariable(nameVar)
                if posVars != None:
                    self.__animSubText.setAnimationFromName(nameAnim)
                    self.__animSubText.setPos((posVars[0], posVars[1]))
                    self.__animSubText.draw(gameDisplay)
            
            def drawFontRenderer(nameVar, text, usePadding=False):
                fontRenderer = getNumberFontRendererFromImage(self.__animSubText, nameVar)
                fontRenderer.setUsePadding(usePadding)
                fontRenderer.setText(text)
                fontRenderer.drawBiased(gameDisplay)
                
            drawFromVariable("nazo_p", "nazo")
            
            if nzLstEntry.idInternal == 206:
                # Unk?
                pass
            elif nzLstEntry.idExternal < 154:
                # Standard
                drawFromVariable("pk_p", "pk")
                drawFromVariable("hint_p", "hint")

                picaratSlot = self.laytonState.saveSlot.puzzleData.getPuzzleData((self.laytonState.getNazoData().idExternal - 1))
                if picaratSlot != None:
                    picaratSlot = picaratSlot.levelDecay
                else:
                    picaratSlot = 0

                drawFontRenderer("pos", nzLstEntry.idExternal, usePadding=True)
                drawFontRenderer("pos2", self.laytonState.getNazoData().getPicaratStage(picaratSlot))
                drawFontRenderer("pos3", self.laytonState.getNazoData().getPicaratStage(0))
                drawFontRenderer("pos4", self.laytonState.saveSlot.hintCoinAvailable)
            else:
                # WiFi
                drawFromVariable("w_p", "w")
