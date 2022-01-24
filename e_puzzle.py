# HACK - Please please please run the embed_mod file first! It initiates the widebrim modules in the correct
#        ordering for the embed to work without weird popup windows, etc.

from typing import Callable, Optional
from nopush_editor import editorPuzzle
from widebrim.engine.const import PATH_NAZO_A, PATH_NAZO_B, PATH_NAZO_C, PATH_PACK_NAZO, PATH_PUZZLE_BG, PATH_PUZZLE_BG_LANGUAGE, PATH_PUZZLE_BG_NAZO_TEXT, RESOLUTION_NINTENDO_DS
from widebrim.engine.file import FileInterface
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine.state.state import Layton2GameState
from widebrim.engine_ext.utils import getImageFromPath, substituteLanguageString
from widebrim.gamemodes.nazo_popup.mode.base.base import BaseQuestionObject
from widebrim.gamemodes.nazo_popup.mode.base.const import PATH_BG_JITEN_WAIT_UNLOCK_1, PATH_BG_JITEN_WAIT_UNLOCK_2, PATH_BG_JITEN_WAIT_UNLOCK_3, PATH_BG_UNLOCKED, POS_HINTTEXT
from widebrim.gamemodes.nazo_popup.outro.const import PATH_BG_ANSWER, PATH_BG_ANSWER_LANG, PATH_BG_FAIL, PATH_BG_PASS
from widebrim.madhatter.common import logSevere

from widebrim.madhatter.hat_io.asset_dat import NazoDataNds
from widebrim.madhatter.hat_io.asset_dlz.nz_lst import NazoListNds
from widebrim.engine.string import getSubstitutedString

from pygame import Surface
from pygame.image import tostring
from widebrim.engine.anim.font.staticFormatted import StaticTextHelper

import wx

# TODO - Pass arguments properly :(
# TODO - Permanence in state will make life a lot easier, means we never need to reload the state and can just "destroy" it instead
# TODO - How to preserve state?
#        nz_lst is destructive, since changes are held in widebrim's memory
#        nz_dat is non-destructive, since changes are reloaded outside of engine

class FramePuzzleEditor(editorPuzzle):

    INVALID_FRAME_COLOR = (255,0,0)

    def __init__(self, parent, internalId : int, state : Layton2GameState, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 550), style=wx.TAB_TRAVERSAL, name=wx.EmptyString):
        super().__init__(parent, id, pos, size, style, name)
        self.__state = state
        self.__idInternal = internalId
        self.__nazoData : Optional[NazoDataNds] = None
        self.__nazoListEntry : Optional[NazoListNds] = None

        self.__internalTextSurface  = Surface(RESOLUTION_NINTENDO_DS)
        self.__internalTextSurface.fill(FramePuzzleEditor.INVALID_FRAME_COLOR)
        self.__textRenderer         = StaticTextHelper(state.fontQ, yBias=2)
        self.__backgroundText : Optional[Surface] = None

        # TODO - class member
        self.__invalidSurface = Surface(RESOLUTION_NINTENDO_DS)
        self.__invalidSurface.fill(FramePuzzleEditor.INVALID_FRAME_COLOR)
        self._reload()

    def _reload(self):
        # Loads from nazo data on ROM!
        self.__nazoData = self.__state.getNazoDataAtId(self.__idInternal)
        self.__nazoListEntry = self.__state.getNazoListEntry(self.__idInternal)

        if self.__nazoData == None or self.__nazoListEntry == None:
            logSevere("ERROR LOADING DATA FOR PUZZLE", self.__idInternal)
            return
        
        self.puzzleName.SetValue(self.__nazoData.getTextName())
        self.puzzlePicaratMax.SetValue(str(self.__nazoData.getPicaratStage(0)))
        self.puzzlePicaratMid.SetValue(str(self.__nazoData.getPicaratStage(1)))
        self.puzzlePicaratMin.SetValue(str(self.__nazoData.getPicaratStage(2)))
        self.puzzleInternalId.SetValue(str(self.__idInternal))
        self._reloadActiveText()
        self._reloadBackgroundAnswer()
        self._reloadBackgroundMain()
        self._reloadBackgroundPrompt()
    
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
    
    def _reloadBackgroundPrompt(self):
        if self.__nazoData != None:
            if self.__nazoData.isBgPromptLanguageDependent():
                pathBg = PATH_PUZZLE_BG_LANGUAGE % self.__nazoData.bgMainId
            else:
                pathBg = PATH_PUZZLE_BG % self.__nazoData.bgMainId
            
            background = getImageFromPath(self.__state, pathBg)
            if background == None:
                background = self.__invalidSurface
            self.previewBackgroundMain.SetBitmap(wx.BitmapFromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

    def _reloadBackgroundMain(self):
        if self.__nazoData != None:
            pathBg = PATH_PUZZLE_BG_NAZO_TEXT % self.__nazoData.bgSubId
            background = getImageFromPath(self.__state, pathBg)
            if background == None:
                background = self.__invalidSurface
            self.previewBackgroundSub.SetBitmap(wx.BitmapFromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

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
            self.previewBackgroundAnswer.SetBitmap(wx.BitmapFromBuffer(background.get_width(), background.get_height(), tostring(background, "RGB")))

    def _updateTextDisplay(self):
        if self.__backgroundText != None:
            self.__internalTextSurface.fill((0,0,0))
            self.__internalTextSurface.blit(self.__backgroundText, (0,0))
        else:
            self.__internalTextSurface.fill(FramePuzzleEditor.INVALID_FRAME_COLOR)

        self.__textRenderer.setText(self.textEdit.GetValue(), substitute=False)
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
            
        self.hintPreview.SetBitmap(wx.BitmapFromBuffer(RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1], tostring(self.__internalTextSurface, "RGB")))

    def prepareWidebrimState(self):
        self.__state.setPuzzleId(self.__idInternal)

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
        
        packNazo = FileInterface.getPack(substituteLanguageString(self.__state, pathNazo))
        self.__nazoData.save()
        packNazo.writeData(PATH_PACK_NAZO % self.__idInternal, self.__nazoData.data)

    def textSelectChoiceOnChoice(self, event):
        self._reloadActiveText()
        return super().textSelectChoiceOnChoice(event)
    
    def textEditOnText(self, event):
        self._updateTextDisplay()
        return super().textEditOnText(event)

    def paneEditParamOnCollapsiblePaneChanged(self, event):
        self.editorScroll.Layout()
        return super().paneEditParamOnCollapsiblePaneChanged(event)
    
    def paneEditBackgroundsOnCollapsiblePaneChanged(self, event):
        self.editorScroll.Layout()
        return super().paneEditBackgroundsOnCollapsiblePaneChanged(event)
    
    def paneEditTextOnCollapsiblePaneChanged(self, event):
        self.editorScroll.Layout()
        return super().paneEditTextOnCollapsiblePaneChanged(event)