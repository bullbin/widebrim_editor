# HACK - Please please please run the embed_mod file first! It initiates the widebrim modules in the correct
#        ordering for the embed to work without weird popup windows, etc.

from typing import List, Optional
from editor.e_script.e_script_generic_packed import FrameScriptEditorPackedEvent, FrameScriptEditorPackedEventNoBank

from editor.puzzle.drawInput import DrawInputEditor
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.hat_io.asset_script import GdScript
from .gen_editor import editorPuzzle
from widebrim.engine.anim.font.scrolling import ScrollingFontHelper
from widebrim.engine.const import PATH_NAZO_A, PATH_NAZO_B, PATH_NAZO_C, PATH_PACK_NAZO, PATH_PACK_PLACE_NAME, PATH_PACK_PUZZLE, PATH_PUZZLE_BG, PATH_PUZZLE_BG_LANGUAGE, PATH_PUZZLE_BG_NAZO_TEXT, PATH_PUZZLE_SCRIPT, PATH_TEXT_PLACE_NAME, RESOLUTION_NINTENDO_DS
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine.state.manager import Layton2GameState
from widebrim.engine_ext.utils import decodeStringFromPack, getImageFromPath, substituteLanguageString
from widebrim.gamemodes.nazo_popup.mode.base.base import BaseQuestionObject
from widebrim.gamemodes.nazo_popup.mode.base.const import PATH_BG_UNLOCKED, POS_HINTTEXT
from widebrim.gamemodes.nazo_popup.outro.const import PATH_BG_ANSWER, PATH_BG_ANSWER_LANG, PATH_BG_FAIL, PATH_BG_PASS
from widebrim.madhatter.common import log, logSevere

from widebrim.madhatter.hat_io.asset_dat import NazoDataNds
from widebrim.madhatter.hat_io.asset_dlz.nz_lst import NazoListNds
from widebrim.engine.string import getSubstitutedString

from pygame import Surface
from pygame.image import tostring

# TODO - Remove wx dependency
import wx
from wx import Bitmap

# TODO - Pass arguments properly :(
# TODO - Permanence in state will make life a lot easier, means we never need to reload the state and can just "destroy" it instead
# TODO - How to preserve state?
#        nz_lst is destructive, since changes are held in widebrim's memory
#        nz_dat is non-destructive, since changes are reloaded outside of engine

class FramePuzzleEditor(editorPuzzle):

    INVALID_FRAME_COLOR = (255,0,0)

    def __init__(self, parent, filesystem : WriteableFilesystemCompatibilityLayer, internalId : int, state : Layton2GameState, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(640, 640), style=wx.TAB_TRAVERSAL, name=wx.EmptyString):
        super().__init__(parent, id, pos, size, style, name)
        self._filesystem = filesystem
        self.__state = state
        self.__idInternal = internalId
        self.__nazoData : Optional[NazoDataNds] = None
        self.__nazoListEntry : Optional[NazoListNds] = None
        self.__nazoScript = GdScript()

        self.__internalTextSurface  = Surface(RESOLUTION_NINTENDO_DS)
        self.__internalTextSurface.fill(FramePuzzleEditor.INVALID_FRAME_COLOR)
        self.__textRenderer         = ScrollingFontHelper(state.fontQ, yBias=2)
        self.__backgroundText : Optional[Surface] = None

        self.__lastAcceptedPicaratValues : List[int] = [0,0,0]

        # TODO - class member
        self.__invalidSurface = Surface(RESOLUTION_NINTENDO_DS)
        self.__invalidSurface.fill(FramePuzzleEditor.INVALID_FRAME_COLOR)

        self.__rewardChoices = []
        self.__choiceToIdMap = []

        self._editor = None # TODO - Generic type with syncChanges method...
        self._loaded = False

    def ensureLoaded(self):
        if not(self._loaded):
            self.__generateRewardChoices()
            self.__generatePlaceStrings()
            self._reload()
            self._loaded = True

    def __changeExternalIdSelection(self):
        if self.__nazoData != None:
            self.puzzlePickExternalId.Clear()
            self.puzzlePickExternalId.AppendItems([str(self.__nazoData.idExternal), "Next free...", "Manual ID..."])
            self.puzzlePickExternalId.SetSelection(0)

    def __generateRewardChoices(self):
        self.__rewardChoices = []
        self.__rewardChoices.append("None")
        for x in range(10):
            self.__rewardChoices.append("Camera Part " + str(x + 1))
        for x in range(10):
            self.__rewardChoices.append("Camera Part (INVALID) " + str(x + 1))
        for x in range(8):
            self.__rewardChoices.append("Tea Ingredient " + str(x + 1))
        for x in range(12):
            self.__rewardChoices.append("Tea Ingredient (INVALID) " + str(x + 1))
        for x in range(10):
            self.__rewardChoices.append("Hamster Toy " + str(x + 1))
        for x in range(10):
            self.__rewardChoices.append("Hamster Toy (INVALID) " + str(x + 1))
        for x in range(12):
            self.__rewardChoices.append("Diary Entry " + str(x + 1))
        for x in range(55):
            self.__rewardChoices.append("Diary Entry (INVALID) " + str(x + 1))
        self.choiceReward.AppendItems(self.__rewardChoices)
    
    def __generatePlaceStrings(self):
        # TODO - If editing, do not enable changing 63 (needs to be Riddleton's Shack)
        packPlace = self._filesystem.getPack(substituteLanguageString(self.__state, PATH_PACK_PLACE_NAME))
        choicesPlace = []
        for indexPlace in range(256):
            stringName = PATH_TEXT_PLACE_NAME % indexPlace
            if packPlace.getFile(stringName) != None:
                self.__choiceToIdMap.append(indexPlace)
                choicesPlace.append(decodeStringFromPack(packPlace, stringName))
        self.choicePlace.AppendItems(choicesPlace)

    def _reload(self):
        # Loads from nazo data on ROM!
        self.__nazoData = self.__state.getNazoDataAtId(self.__idInternal)
        self.__nazoListEntry = self.__state.getNazoListEntry(self.__idInternal)

        if self.__nazoData == None or self.__nazoListEntry == None:
            logSevere("ERROR LOADING DATA FOR PUZZLE", self.__idInternal)
            return

        if (data := self._filesystem.getPackedData(PATH_PUZZLE_SCRIPT, PATH_PACK_PUZZLE % self.__idInternal)) != None:
            self.__nazoScript = GdScript()
            self.__nazoScript.load(data)
        
        self.puzzleName.SetValue(self.__nazoData.getTextName())
        self.puzzlePicaratMax.ChangeValue(str(self.__nazoData.getPicaratStage(0)))
        self.puzzlePicaratMid.ChangeValue(str(self.__nazoData.getPicaratStage(1)))
        self.puzzlePicaratMin.ChangeValue(str(self.__nazoData.getPicaratStage(2)))
        self.puzzleInternalId.SetValue(str(self.__idInternal))

        self.useAltCharacter.SetValue(self.__nazoData.isLukeSolver())
        self.useAltVoice.SetValue(self.__nazoData.isLukeVoicelines())

        self.__lastAcceptedPicaratValues[0] = self.__nazoData.getPicaratStage(0)
        self.__lastAcceptedPicaratValues[1] = self.__nazoData.getPicaratStage(1)
        self.__lastAcceptedPicaratValues[2] = self.__nazoData.getPicaratStage(2)

        reward = self.__nazoData.getReward()
        if reward == None:
            self.choiceReward.SetSelection(0)
        else:
            category, index = reward
            self.choiceReward.SetSelection(1 + int(category * 20) + index)
        
        if len(self.__choiceToIdMap) > 0:
            val = self.__nazoData.getPlaceIndex()
            for indexChoice, choice in enumerate(self.__choiceToIdMap):
                if choice == val:
                    self.choicePlace.SetSelection(indexChoice)
                    break
        
        if self.__nazoData.idHandler in [16, 20, 21, 22, 28, 32, 35]:
            self._editor = DrawInputEditor(self.paneGameplayEditor.GetPane(), self.__state, self.__nazoData, self.__nazoScript)
            sizer = self.paneGameplayEditor.GetPane().GetSizer()
            sizer.Add(self._editor, 0, wx.EXPAND)
        else:
            self._editor = FrameScriptEditorPackedEventNoBank(self.paneGameplayEditor.GetPane(), self.__state, "/data_lt2/script/puzzle.plz", "q%i_param.gds" % self.__idInternal)
            self._editor.ensureLoaded()
            sizer = self.paneGameplayEditor.GetPane().GetSizer()
            sizer.Add(self._editor, 0, wx.EXPAND)

        self._reloadActiveText()
        self._reloadBackgroundAnswer()
        self._reloadBackgroundMain()
        self._reloadBackgroundPrompt()
        self.__changeExternalIdSelection()
    
    def _reloadActiveText(self):
        if self.__nazoData != None:
            select = self.textSelectChoice.GetCurrentSelection()
            if select == 0:
                self.textEdit.SetValue(getSubstitutedString(self.__nazoData.getTextHints()[0]))
                self.__backgroundText = getImageFromPath(self.__state, PATH_BG_UNLOCKED % (self.__state.language.value, select + 1))
                self.__textRenderer.setPos(POS_HINTTEXT)
            elif select == 1:
                self.textEdit.SetValue(getSubstitutedString(self.__nazoData.getTextHints()[1]))
                self.__backgroundText = getImageFromPath(self.__state, PATH_BG_UNLOCKED % (self.__state.language.value, select + 1))
                self.__textRenderer.setPos(POS_HINTTEXT)
            elif select == 2:
                self.textEdit.SetValue(getSubstitutedString(self.__nazoData.getTextHints()[2]))
                self.__backgroundText = getImageFromPath(self.__state, PATH_BG_UNLOCKED % (self.__state.language.value, select + 1))
                self.__textRenderer.setPos(POS_HINTTEXT)
            elif select == 3:
                self.textEdit.SetValue(getSubstitutedString(self.__nazoData.getTextPrompt()))
                self.__backgroundText = getImageFromPath(self.__state, PATH_PUZZLE_BG_NAZO_TEXT % self.__nazoData.bgSubId)
                self.__textRenderer.setPos(BaseQuestionObject.POS_QUESTION_TEXT)
            elif select == 4:
                self.textEdit.SetValue(getSubstitutedString(self.__nazoData.getTextIncorrect()))
                self.__backgroundText = getImageFromPath(self.__state, PATH_BG_FAIL % self.__nazoData.bgSubId)
                self.__textRenderer.setPos(BaseQuestionObject.POS_QUESTION_TEXT)
            elif select == 5:
                # TODO - Not strictly correct!!
                self.textEdit.SetValue(getSubstitutedString(self.__nazoData.getTextCorrect()))
                self.__backgroundText = getImageFromPath(self.__state, PATH_BG_PASS % self.__nazoData.bgSubId)
                self.__textRenderer.setPos(BaseQuestionObject.POS_QUESTION_TEXT)
            else:
                print(select)
                self.textEdit.SetValue("Unintended value!!!")
            
            self._updateTextDisplay()
    
    def puzzlePickExternalIdOnChoice(self, event):
        index = self.puzzlePickExternalId.GetSelection()
        if index == 1:
            # Next free ID
            if self.__nazoData.idExternal > 153:
                # Wi-Fi puzzle, need to scroll through (don't remember limits)
                self.puzzlePickExternalId.SetSelection(0)
                pass
            else:
                idBefore = self.__nazoData.idExternal
                for x in range(153):
                    if self.__state.getNazoListEntryByExternal(x + 1) == None:
                        self.__nazoData.idExternal = x + 1
                        self.__changeExternalIdSelection()
                        break
                if self.__nazoData.idExternal == idBefore:
                    print("No free IDs!")
                    self.puzzlePickExternalId.SetSelection(0)
        else:
            # Manual ID entry
            pass
        self.puzzlePickExternalId.SetSelection(0)

        return super().puzzlePickExternalIdOnChoice(event)

    def choiceRewardOnChoice(self, event):
        if self.__nazoData != None:
            index = self.choiceReward.GetSelection()
            if index == 0:
                self.__nazoData.disableReward()
            else:
                index -= 1
                category = index // 20
                if category > 3:
                    category = 3
                    index = index - 60
                else:
                    index = index % 20
                self.__nazoData.setReward(category, index)

        return super().choiceRewardOnChoice(event)

    def choicePlaceOnChoice(self, event):
        index = self.choiceReward.GetSelection()
        self.__nazoData.indexPlace = self.__choiceToIdMap[index]
        return super().choicePlaceOnChoice(event)

    def _reloadBackgroundPrompt(self):
        if self.__nazoData != None:
            if self.__nazoData.isBgPromptLanguageDependent():
                pathBg = PATH_PUZZLE_BG_LANGUAGE % self.__nazoData.bgMainId
            else:
                pathBg = PATH_PUZZLE_BG % self.__nazoData.bgMainId
            
            background = getImageFromPath(self.__state, pathBg)
            if background == None:
                background = self.__invalidSurface
            self.previewBackgroundMain.SetBitmap(Bitmap.FromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

    def _reloadBackgroundMain(self):
        if self.__nazoData != None:
            pathBg = PATH_PUZZLE_BG_NAZO_TEXT % self.__nazoData.bgSubId
            background = getImageFromPath(self.__state, pathBg)
            if background == None:
                background = self.__invalidSurface
            self.previewBackgroundSub.SetBitmap(Bitmap.FromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

    def _reloadBackgroundAnswer(self):
        if self.__nazoData != None:
            if self.__nazoData.hasAnswerBg():
                if self.__nazoData.isBgAnswerLanguageDependent():
                    pathBg = PATH_BG_ANSWER_LANG % self.__nazoData.getBgMainIndex()
                else:
                    pathBg = PATH_BG_ANSWER % self.__nazoData.getBgMainIndex()
            else:
                pathBg = PATH_BG_PASS % self.__nazoData.getBgSubIndex()

            background = getImageFromPath(self.__state, pathBg)
            if background == None:
                background = self.__invalidSurface
            self.previewBackgroundAnswer.SetBitmap(Bitmap.FromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

    def _updateTextDisplay(self):
        if self.__backgroundText != None:
            self.__internalTextSurface.fill((0,0,0))
            self.__internalTextSurface.blit(self.__backgroundText, (0,0))
        else:
            self.__internalTextSurface.fill(FramePuzzleEditor.INVALID_FRAME_COLOR)

        self.__textRenderer.setColor((0,0,0))
        self.__textRenderer.setText(self.textEdit.GetValue(), substitute=False)
        # TODO - Reuse different renders (static for hint)
        self.__textRenderer.skip()
        self.__textRenderer.draw(self.__internalTextSurface)
        if self.__nazoData != None:
            select = self.textSelectChoice.GetCurrentSelection()
            # TODO - Validate string
            if select < 3:
                self.__nazoData.setHintAtIndex(select, self.textEdit.GetValue())
            elif select == 3:
                self.__nazoData.setPrompt(self.textEdit.GetValue())
            elif select == 4:
                self.__nazoData.setIncorrectPrompt(self.textEdit.GetValue())
            elif select == 5:
                self.__nazoData.setCorrectPrompt(self.textEdit.GetValue())
            else:
                print(select)
                print("CANNOT COMMIT UNKNOWN TO NAZO DATA!!!")
            
        self.hintPreview.SetBitmap(Bitmap.FromBuffer(RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1], tostring(self.__internalTextSurface, "RGB")))

    def prepareWidebrimState(self) -> GAMEMODES:
        self.__state.setPuzzleId(self.__idInternal)
        return GAMEMODES.Puzzle

    def puzzleNameOnText(self, event):
        if self.__nazoListEntry != None and self.__nazoData != None:
            # TODO - String validation
            self.__nazoListEntry.name = self.puzzleName.GetValue()
            self.__nazoData.setName(self.puzzleName.GetValue())
        return super().puzzleNameOnText(event)

    def syncChanges(self):
        """Changes are fragmented within widebrim's filesystem. When sync is called, changes to non-persistent virtual assets are committed to ROM.
        This needs to be called when switching between pages to prevent state desync.
        """
        # TODO - Really need a virtual filesystem implementation. Current filesystem messes with ROM but fetches from patch, not suitable.
        if self.__idInternal < 60:
            pathNazo = PATH_NAZO_A
        elif self.__idInternal < 120:
            pathNazo = PATH_NAZO_B
        else:
            pathNazo = PATH_NAZO_C
        
        packNazo = self._filesystem.getPack(substituteLanguageString(self.__state, pathNazo))
        self.__nazoData.save()

        if self._editor != None:
            log("Writing editor changes...", name="PuzzSpecEdit")
            self._editor.syncChanges()

        # TODO - Bugfix - this is old code
        packNazo.writeData(PATH_PACK_NAZO % self.__idInternal, self.__nazoData.data)

    def __updatePicaratValues(self, clampIndex : int):
        print("HELLO")
        for index, value in enumerate(self.__lastAcceptedPicaratValues):
            if value > 255:
                self.__lastAcceptedPicaratValues[index] = 255

        self.__lastAcceptedPicaratValues.sort(reverse=True)
        print(self.__lastAcceptedPicaratValues)
        self.puzzlePicaratMax.ChangeValue(str(self.__lastAcceptedPicaratValues[0]))
        self.puzzlePicaratMid.ChangeValue(str(self.__lastAcceptedPicaratValues[1]))
        self.puzzlePicaratMin.ChangeValue(str(self.__lastAcceptedPicaratValues[2]))
        if self.__nazoData != None:
            for index, value in enumerate(self.__lastAcceptedPicaratValues):
                self.__nazoData.setPicaratStage(value, index)

    def useAltCharacterOnCheckBox(self, event):
        if self.__nazoData != None:
            self.__nazoData.setLukeSolver(self.useAltCharacter.IsChecked())
        return super().useAltCharacterOnCheckBox(event)

    def useAltVoiceOnCheckBox(self, event):
        if self.__nazoData != None:
            self.__nazoData.setLukeVoicelines(self.useAltVoice.IsChecked())
        return super().useAltVoiceOnCheckBox(event)

    def puzzlePicaratMaxOnText(self, event):
        if self.puzzlePicaratMax.GetValue().isdigit():
            # TODO - May not hold if invalid dat is passed
            self.__lastAcceptedPicaratValues[0] = int(self.puzzlePicaratMax.GetValue())
        
        self.__updatePicaratValues(0)
        return super().puzzlePicaratMaxOnText(event)
    
    def puzzlePicaratMidOnText(self, event):
        if self.puzzlePicaratMid.GetValue().isdigit():
            # TODO - May not hold if invalid dat is passed
            self.__lastAcceptedPicaratValues[1] = int(self.puzzlePicaratMid.GetValue())
        
        self.__updatePicaratValues(1)
        return super().puzzlePicaratMidOnText(event)

    def puzzlePicaratMinOnText(self, event):
        if self.puzzlePicaratMin.GetValue().isdigit():
            # TODO - May not hold if invalid dat is passed
            self.__lastAcceptedPicaratValues[2] = int(self.puzzlePicaratMin.GetValue())

        self.__updatePicaratValues(2)
        return super().puzzlePicaratMinOnText(event)

    def textSelectChoiceOnChoice(self, event):
        self._reloadActiveText()
        return super().textSelectChoiceOnChoice(event)
    
    def textEditOnText(self, event):
        self._updateTextDisplay()
        return super().textEditOnText(event)

    def paneEditParamOnCollapsiblePaneChanged(self, event):
        self.__onScrollSizeChange()
        return super().paneEditParamOnCollapsiblePaneChanged(event)
    
    def paneEditBackgroundsOnCollapsiblePaneChanged(self, event):
        self.__onScrollSizeChange()
        return super().paneEditBackgroundsOnCollapsiblePaneChanged(event)
    
    def paneEditTextOnCollapsiblePaneChanged(self, event):
        self.__onScrollSizeChange()
        return super().paneEditTextOnCollapsiblePaneChanged(event)
    
    def paneGameplayEditorOnCollapsiblePaneChanged(self, event):
        self.__onScrollSizeChange()
        return super().paneGameplayEditorOnCollapsiblePaneChanged(event)

    def __onScrollSizeChange(self):
        self.Freeze()
        minSize = self.editorScroll.GetSizer().GetMinSize()
        self.editorScroll.SetVirtualSize(minSize)
        self.editorScroll.Layout()
        self.Refresh()
        self.Thaw()
    
    def editorScrollOnSize(self, event):
        # idk why this works but it does. any call to setvirtualsize with anything remotely client-shaped works
        # you can do -1,-1 as the size and it layouts properly. i don't understand but i don't need to understand :')
        self.__onScrollSizeChange()
        return super().editorScrollOnSize(event)
    
    # TODO - wrap works for params? why is that?