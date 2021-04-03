from __future__ import annotations
from typing import Callable, Optional, TYPE_CHECKING
from widebrim.engine.const import RESOLUTION_NINTENDO_DS
if TYPE_CHECKING:
    from widebrim.engine.state.state import Layton2GameState
    from widebrim.engine_ext.state_game import ScreenController
    
from widebrim.gamemodes.dramaevent.popup.utils import FadingPopupAnimBackground
from widebrim.engine_ext.utils import getAnimFromPathWithAttributes, getAnimFromPath, getPackedString
from widebrim.engine.anim.font.staticFormatted import StaticTextHelper
from .const import NAME_ANIM_CURSOR_WAIT, PATH_ANIM_CURSOR_WAIT, PATH_ANIM_TOBJ_WINDOW, PATH_ANIM_TOBJ_ICON, PATH_FILE_HINTCOIN, PATH_FILE_TOBJ, PATH_PACK_TOBJ, POS_CURSOR_WAIT, POS_TOBJ_ICON, POS_TOBJ_TEXT_CENTRAL_LINE

class TObjPopup(FadingPopupAnimBackground):
    def __init__(self, laytonState : Layton2GameState, screenController : ScreenController, indexTObj : int, idIcon : int, callback : Optional[Callable]):

        self.__animIcon = getAnimFromPath(PATH_ANIM_TOBJ_ICON)
        if self.__animIcon != None:
            self.__animIcon.setPos((POS_TOBJ_ICON[0], POS_TOBJ_ICON[1] + RESOLUTION_NINTENDO_DS[1]))
            if indexTObj == -1:
                # Hint coin
                self.__animIcon.setAnimationFromName("3")
            else:
                self.__animIcon.setAnimationFromName(str(idIcon + 1))

        self.__animCursorWait = getAnimFromPath(PATH_ANIM_CURSOR_WAIT, spawnAnimName=NAME_ANIM_CURSOR_WAIT, pos=(POS_CURSOR_WAIT[0], POS_CURSOR_WAIT[1] + RESOLUTION_NINTENDO_DS[1]))

        if (bgAnim := getAnimFromPathWithAttributes(PATH_ANIM_TOBJ_WINDOW)) != None:
            bgAnim.setAnimationFromIndex(1)
            FadingPopupAnimBackground.__init__(self, laytonState, screenController, callback, bgAnim)
        else:
            FadingPopupAnimBackground.__init__(self, laytonState, screenController, callback, None)
        
        self.laytonState = laytonState
        self.__textRenderer = StaticTextHelper(self.laytonState.fontEvent)
        if len(tObjText := self.__getTObjText(indexTObj)) > 0:
            self.__textRenderer.setText(tObjText)
            # Probably okay?
            countLines = len(tObjText.split("\n"))
            linesAbove = countLines // 2
            useHalfOffset = (countLines % 2 == 0)
            
            # 4 is the yBias here
            yOffset = -linesAbove * (self.laytonState.fontEvent.dimensions[1] + 4)
            if useHalfOffset:
                yOffset += self.laytonState.fontEvent.dimensions[1] // 2
            
            self.__textRenderer.setPos((POS_TOBJ_TEXT_CENTRAL_LINE[0], POS_TOBJ_TEXT_CENTRAL_LINE[1] + yOffset + RESOLUTION_NINTENDO_DS[1]))
    
    def __getTObjText(self, indexTObj : int) -> str:
        # TODO - usage of getPackedString in room
        if indexTObj != -1:
            return getPackedString(PATH_PACK_TOBJ % self.laytonState.language.value, PATH_FILE_TOBJ % indexTObj)
        return getPackedString(PATH_PACK_TOBJ % self.laytonState.language.value, PATH_FILE_HINTCOIN)

    def drawForegroundElements(self, gameDisplay):
        self.__animIcon.draw(gameDisplay)
        self.__textRenderer.draw(gameDisplay)
        return super().drawForegroundElements(gameDisplay)