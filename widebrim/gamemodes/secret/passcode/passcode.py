from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from widebrim.engine.state.layer import ScreenLayerNonBlocking
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine_ext.utils import getAnimFromPath, getButtonFromPath, getStaticButtonFromAnim

from .const import *

if TYPE_CHECKING:
    from widebrim.engine.state.state import Layton2GameState
    from widebrim.engine_ext.state_game import ScreenController
    from widebrim.engine.anim.button import StaticButton

class PasscodePlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState : Layton2GameState, screenController : ScreenController):
        ScreenLayerNonBlocking.__init__(self)

        self.__laytonState = laytonState
        self.__screenController = screenController
        self.__buttons = []

        def addButtonIfNotNone(button : Optional[StaticButton]):
            if button != None:
                self.__buttons.append(button)

        self.__animBtn = getAnimFromPath(PATH_ANIM_BUTTONS % laytonState.language.value)

        # TODO - Code overlay on these events
        # TODO - Code overlay on this gamemode
        if self.__laytonState.saveSlot.codeInputFlags.getSlot(0) == True:
            addButtonIfNotNone(getStaticButtonFromAnim(self.__animBtn, NAME_ANIM_CURIOUS_ENABLED, self.__callbackOnCuriousEnabled, POS_BTN_CURIOUS, clickOffset=BTN_CLICK_OFFSET))
        else:
            addButtonIfNotNone(getStaticButtonFromAnim(self.__animBtn, NAME_ANIM_CURIOUS_DISABLED, self.__callbackOnCuriousDisabled, POS_BTN_CURIOUS, clickOffset=BTN_CLICK_OFFSET))

        if self.__laytonState.saveSlot.codeInputFlags.getSlot(8) == True:
            addButtonIfNotNone(getStaticButtonFromAnim(self.__animBtn, NAME_ANIM_FUTURE_ENABLED, self.__callbackOnFutureEnabled, POS_BTN_FUTURE, clickOffset=BTN_CLICK_OFFSET))
        else:
            addButtonIfNotNone(getStaticButtonFromAnim(self.__animBtn, NAME_ANIM_FUTURE_DISABLED, self.__callbackOnFutureDisabled, POS_BTN_FUTURE, clickOffset=BTN_CLICK_OFFSET))

        self.__btnCancel = getButtonFromPath(laytonState, PATH_ANIM_BTN_CANCEL, callback=self.__callbackOnCancel)
        addButtonIfNotNone(self.__btnCancel)

        screenController.setBgMain(PATH_BG_MAIN % self.__laytonState.language.value)
        screenController.setBgSub(PATH_BG_SUB % self.__laytonState.language.value)

        # TODO - Sound index here (haha)

        screenController.fadeIn()

    def __callbackOnCuriousEnabled(self):
        self.__laytonState.setGameMode(GAMEMODES.DramaEvent)
        self.__laytonState.setGameModeNext(GAMEMODES.Passcode)
        self.__laytonState.setEventId(ID_EVENT_SECRET)
        self.__screenController.fadeOut(callback=self.doOnKill)

    def __callbackOnCuriousDisabled(self):
        self.__laytonState.setGameMode(GAMEMODES.CodeInputCurious)
        self.__screenController.fadeOut(callback=self.doOnKill)

    def __callbackOnFutureEnabled(self):
        self.__laytonState.setGameMode(GAMEMODES.DramaEvent)
        self.__laytonState.setGameModeNext(GAMEMODES.Passcode)
        self.__laytonState.setEventId(ID_EVENT_CONCEPT_ART)
        self.__screenController.fadeOut(callback=self.doOnKill)

    def __callbackOnFutureDisabled(self):
        self.__laytonState.setGameMode(GAMEMODES.CodeInputFuture)
        self.__screenController.fadeOut(callback=self.doOnKill)

    def __callbackOnCancel(self):
        # TODO - for some reason game stores an extra variable about whether in secret mode or not
        self.__laytonState.setGameMode(GAMEMODES.TopSecretMenu)
        self.__screenController.fadeOut(callback=self.doOnKill)

    def draw(self, gameDisplay):
        for button in self.__buttons:
            button.draw(gameDisplay)
    
    def update(self, gameClockDelta):
        if self.__btnCancel != None:
            self.__btnCancel.update(gameClockDelta)
    
    def handleTouchEvent(self, event):
        if not(self.__screenController.getFadingStatus()):
            for button in self.__buttons:
                if button.handleTouchEvent(event):
                    return True
        return super().handleTouchEvent(event)