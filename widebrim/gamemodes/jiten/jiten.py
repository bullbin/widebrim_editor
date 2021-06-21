from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from widebrim.engine.anim.font.staticFormatted import StaticTextHelper
from widebrim.engine.const import RESOLUTION_NINTENDO_DS
from widebrim.madhatter.hat_io.asset_image.image import AnimatedImage
from widebrim.gamemodes.mystery.const import PATH_ANIM_BUTTON_CANCEL
from widebrim.engine.anim.button import AnimatedButton, NullButton
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from widebrim.engine.state.enum_mode import GAMEMODES

from widebrim.engine.state.layer import ScreenLayerNonBlocking
from widebrim.engine_ext.utils import getAnimFromPathWithAttributes, getButtonFromPath, getPackedString, getStaticButtonFromAnim, getAnimFromPath
from .const import *

if TYPE_CHECKING:
    from widebrim.engine.state.state import Layton2GameState
    from widebrim.engine_ext.state_game import ScreenController

class JitenPlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState : Layton2GameState, screenController : ScreenController, callbackOnTerminate : Optional[callable] = None):
        super().__init__()

        self.__inFavouriteMode              : bool  = False
        self.__lastSelectedFavouriteIndex   : int   = 0
        self.__lastSelectedNormalIndex      : int   = 0
        self.__textRendererLocation : StaticTextHelper  = StaticTextHelper(laytonState.font18)
        self.__textRendererType     : StaticTextHelper  = StaticTextHelper(laytonState.font18)
        self.__textRendererName     : StaticTextHelper  = StaticTextHelper(laytonState.font18)
        self.__animPreview          : Optional[AnimatedImageObject] = None # TODO - jiten_q1
        self.__isInteractive        : bool = False

        if laytonState.getGameModeNext() == GAMEMODES.JitenWiFi:
            # TODO - Save game to source slot, display message if save failed
            pass

        self.__laytonState = laytonState
        self.__screenController = screenController
        self.__sourceGameMode = self.__laytonState.getGameMode()

        self.__buttons : List[AnimatedButton] = []
        self.__buttonsHitbox : List[NullButton] = []

        def addButtonIfNotNone(button : Optional[AnimatedButton]):
            if button != None:
                self.__buttons.append(button)
        
        def getHitbox(pos, dimensions, callback=None) -> NullButton:
            pos = (pos[0], pos[1] + RESOLUTION_NINTENDO_DS[1])
            posEnd = (pos[0] + dimensions[0], pos[1] + dimensions[1])
            return NullButton(pos, posEnd, callback=callback)

        self.__animJitenNum : Optional[AnimatedImageObject] = getAnimFromPath(PATH_ANIM_NUM % laytonState.language.value)
        
        if self.__sourceGameMode == GAMEMODES.JitenWiFi:
            addButtonIfNotNone(getButtonFromPath(laytonState, PATH_ANIM_BTN_ALL, None, NAME_ANIM_JITEN_BTN_SOLVE_OFF_WIFI, NAME_ANIM_JITEN_BTN_SOLVE_ON_WIFI, pos=POS_BTN_SOLVE, customDimensions=DIM_BTN_SOLVE))
        else:
            addButtonIfNotNone(getButtonFromPath(laytonState, PATH_ANIM_BTN_ALL, None, NAME_ANIM_JITEN_BTN_SOLVE_OFF, NAME_ANIM_JITEN_BTN_SOLVE_ON, pos=POS_BTN_SOLVE, customDimensions=DIM_BTN_SOLVE))
        # TODO - Set button dimensions, settable in engine

        addButtonIfNotNone(getButtonFromPath(laytonState, PATH_ANIM_BTN_ALL, None, NAME_ANIM_JITEN_BTN_UP_OFF, NAME_ANIM_JITEN_BTN_UP_ON, pos=POS_BTN_UP, customDimensions=DIM_BTN_MOVE))
        addButtonIfNotNone(getButtonFromPath(laytonState, PATH_ANIM_BTN_ALL, None, NAME_ANIM_JITEN_BTN_UP_MANY_OFF, NAME_ANIM_JITEN_BTN_UP_MANY_ON, pos=POS_BTN_UP_MANY, customDimensions=DIM_BTN_MOVE))
        addButtonIfNotNone(getButtonFromPath(laytonState, PATH_ANIM_BTN_ALL, None, NAME_ANIM_JITEN_BTN_DOWN_OFF, NAME_ANIM_JITEN_BTN_DOWN_ON, pos=POS_BTN_DOWN, customDimensions=DIM_BTN_MOVE))
        addButtonIfNotNone(getButtonFromPath(laytonState, PATH_ANIM_BTN_ALL, None, NAME_ANIM_JITEN_BTN_DOWN_MANY_OFF, NAME_ANIM_JITEN_BTN_DOWN_MANY_ON, pos=POS_BTN_DOWN_MANY, customDimensions=DIM_BTN_MOVE))

        self.__animCover1 : Optional[AnimatedImageObject] = None
        self.__animCover2 : Optional[AnimatedImageObject] = None
        self.__animTitle  : Optional[AnimatedImageObject] = None
        self.__animModeSelect : Optional[AnimatedImageObject] = None
        self.__animPrize : Optional[AnimatedImageObject] = None
        self.__animUpperNum : Optional[AnimatedImageObject] = None
        self.__animHintbox : Optional[AnimatedImageObject] = None

        # TODO - Scroll, hitboxes (non-favourite)
        x = POS_CORNER_HITBOX_SELECT[0]
        y = POS_CORNER_HITBOX_SELECT[1] + RESOLUTION_NINTENDO_DS[1]
        for _indexHitbox in range(5):
            self.__buttonsHitbox.append(getHitbox((x,y), SIZE_HITBOX_SELECT))
            y += BIAS_HITBOX_SELECT_Y

        if self.__sourceGameMode == GAMEMODES.JitenWiFi:
            # TODO - Merge these
            self.__screenController.setBgMain(PATH_BG_MAIN_WIFI)
            self.__animCover1 = getAnimFromPathWithAttributes(PATH_ANIM_COVER_WIFI_1, posVariable=ANIM_VAR_POS_TAG_JITEN_GUARD)
            self.__animCover2 = getAnimFromPathWithAttributes(PATH_ANIM_COVER_WIFI_2, posVariable=ANIM_VAR_POS_TAG_JITEN_GUARD)
            addButtonIfNotNone(getButtonFromPath(laytonState, PATH_ANIM_BUTTON_CANCEL, self.__callbackOnExit))
        else:
            self.__screenController.setBgMain(PATH_BG_MAIN)
            self.__screenController.setBgSub(PATH_BG_SUB % laytonState.language.value)
            self.__animTitle = getAnimFromPath(PATH_ANIM_INTRO_TEXT % laytonState.language.value)
            self.__animModeSelect = getAnimFromPathWithAttributes(PATH_ANIM_TABS, posVariable=ANIM_VAR_POS_TAG_JITEN_GUARD)
            
            # TODO - store in favourite mode in the main object, not save container. Set animation based on state.
            if self.__animModeSelect != None:
                if self.__inFavouriteMode:
                    self.__animModeSelect.setAnimationFromName(NAME_ANIM_TAG_TAB_PICKS)
                else:
                    self.__animModeSelect.setAnimationFromName(NAME_ANIM_TAG_TAB_ALL)
            
            # TODO - Unk button 5
            self.__animCover1 = getAnimFromPathWithAttributes(PATH_ANIM_COVER, posVariable=ANIM_VAR_POS_TAG_JITEN_GUARD)
            self.__animPrize = getAnimFromPath(PATH_ANIM_PRIZE, pos=POS_ANIM_PRIZE)
            self.__animHintbox = getAnimFromPath(PATH_ANIM_HINT)
            self.__buttonsHitbox.append(getHitbox(POS_BTN_FROM_FAV, DIM_BTN_FROM_FAVOURITES))
            self.__buttonsHitbox.append(getHitbox(POS_BTN_TO_FAV, DIM_BTN_TO_FAVOURITES))

            x = POS_CORNER_FAVOURITE[0]
            y = POS_CORNER_FAVOURITE[1] + RESOLUTION_NINTENDO_DS[1]
            for _indexHitbox in range(5):
                self.__buttonsHitbox.append(getHitbox((x,y), SIZE_HITBOX_FAVOURITE))
                y += BIAS_HITBOX_SELECT_Y
            
            addButtonIfNotNone(getButtonFromPath(laytonState, PATH_ANIM_BTN_ALL, self.__callbackOnExit, animOff=NAME_ANIM_JITEN_BTN_ALT_CLOSE_OFF, animOn=NAME_ANIM_JITEN_BTN_ALT_CLOSE_CLICK, customDimensions=DIM_BTN_CLOSE, pos=POS_BTN_CLOSE))

            # TODO - Question logo is fetched here and writes some save flags
        
            if self.__sourceGameMode == GAMEMODES.JitenSecret:
                self.__laytonState.setGameModeNext(GAMEMODES.SecretMenu)
        
        # TODO - Populate internal structure (names, etc...)

        self.__screenController.fadeIn(callback=self.__enableInteractivity)

    def __enableInteractivity(self):
        self.__isInteractive = True

    def __disableInteractivity(self):
        self.__isInteractive = False

    def __updateSelectedPuzzle(self):
        if self.__sourceGameMode != GAMEMODES.JitenWiFi:
            if self.__inFavouriteMode:
                puzzleId = self.__lastSelectedFavouriteIndex
            else:
                puzzleId = self.__lastSelectedNormalIndex

            # TODO - Text renderers and preview will be voided before check, since game does it in awkward way (and can't decide when to use stack)

            if puzzleId != 0:
                nzLstEntry = self.__laytonState.getNazoListEntryByExternal(puzzleId)
                if nzLstEntry != None:
                    nazoData = self.__laytonState.getNazoDataAtId(nzLstEntry.idInternal)
                    if nazoData != None:
                        nazoType = nazoData.idHandler
                        if nazoType == 0x23:
                            nazoType = 0x16
                        
                        textType = getPackedString(PATH_PACK_JITEN.replace("?", self.__laytonState.language.value), PATH_TEXT_NAZO_TYPE % nazoType)
                        self.__textRendererType.setText(textType[0:min(len(textType), 64)])

                        # TODO - Unk validation check (2_Nazo_ValidateAndGetUnkData)
                        puzzleData = self.__laytonState.saveSlot.puzzleData.getPuzzleData(puzzleId - 1)
                        if puzzleData.enableNazoba:
                            textLocation = getPackedString(PATH_PACK_JITEN.replace("?", self.__laytonState.language.value), PATH_TEXT_JITEN_MISSING)
                        else:
                            textLocation = getPackedString(PATH_PACK_JITEN.replace("?", self.__laytonState.language.value), PATH_TEXT_JITEN_PLACE % nazoData.indexPlace)

                        self.__textRendererLocation.setText(textLocation[0:min(len(textLocation), 64)])
                        self.__textRendererName.setText(nazoData.name[0:min(len(nazoData.name, 64))])
            
                    self.__animPreview = getAnimFromPath(PATH_ANIM_PREVIEW % nzLstEntry.idInternal, pos=POS_ANIM_PREVIEW)

    def __callbackOnExit(self):
        # TODO - Reverse this
        self.__disableInteractivity()
        if self.__sourceGameMode == GAMEMODES.JitenBag:
            self.__laytonState.setGameMode(GAMEMODES.Bag)
        elif self.__sourceGameMode == GAMEMODES.JitenSecret:
            self.__laytonState.setGameMode(GAMEMODES.SecretMenu)
        else:
            # TODO - Overlay for WiFi is annoying
            pass
            #self.__laytonState.setGameMode(GAMEMODES.)
        self.__screenController.fadeOut(callback=self.doOnKill)

    def draw(self, gameDisplay):
        for drawable in self.__buttons:
            drawable.draw(gameDisplay)
        
        return super().draw(gameDisplay)
    
    def handleTouchEvent(self, event):
        if self.__isInteractive:
            for interactable in self.__buttons:
                if interactable.handleTouchEvent(event):
                    return True
        return super().handleTouchEvent(event)