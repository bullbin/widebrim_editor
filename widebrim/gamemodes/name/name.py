from ...engine.state.layer import ScreenLayerNonBlocking
from ...engine.state.enum_mode import GAMEMODES
from ...engine.const import RESOLUTION_NINTENDO_DS
from ...engine.exceptions import FileInvalidCritical
from ...engine.anim.button import StaticButton, NullButton
from ...engine.string import getSubstitutedString
from ...engine.anim.font.static import generateImageFromStringStrided
from ...engine_ext.utils import getAnimFromPath
from .const import PATH_BG_NAME_1, PATH_BG_NAME_2, PATH_BG_NAME_3, PATH_BG_NAME_4, PATH_BG_SUB_HAM, PATH_BG_SUB_NAME, PATH_ANI_BUTTON, PATH_ANI_CURSOR, PATH_ANI_OK, POS_BUTTON_OK
from .const import POS_BUTTON_DOWN, SIZE_BUTTON_DOWN, POS_BUTTON_SHIFT, SIZE_BUTTON_SHIFT, COUNT_KEY, COUNT_KEY_SPECIAL, SIZE_KEY
from .const import PATH_PACK_TEXT, PATH_KIGOU, PATH_KOMOJI, PATH_OOMOJI, PATH_TOKUSHU
from .const import BTN_NORMAL_NAME, BTN_NORMAL_POS, BTN_ACCENT_NAME, BTN_ACCENT_POS, BTN_SPACE_NAME, BTN_SPACE_POS, BTN_BACK_NAME, BTN_BACK_POS, POS_ANI_CURSOR, STRIDE_CHARACTER, POS_ENTRY_TEXT
from .const import NAMES_BLOCKED, PATH_BAD_NAME, POS_BAD_NAME

from ...engine.file import FileInterface
from ...madhatter.hat_io.asset import LaytonPack
from pygame import MOUSEBUTTONUP, BLEND_RGB_SUB, BLEND_RGB_MULT, Surface

# TODO - Used in code entry? Not ready for use yet

class KeyboardButton(NullButton):
    def __init__(self, pos, posEnd, callback=None):
        NullButton.__init__(self, pos, posEnd, callback=callback)
        self.needsHighlightSurface = False

    def doOnMouseTargetting(self):
        self.needsHighlightSurface = True

    def doOnMouseAwayFromTarget(self):
        self.needsHighlightSurface = False

class NamePlayer(ScreenLayerNonBlocking):

    LENGTH_ENTRY = 10

    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)
        self.screenController = screenController
        self.laytonState = laytonState
        self.entry = ""
        self.activeMap = ""

        try:
            tempPack = LaytonPack()
            tempPack.load(FileInterface.getData(PATH_PACK_TEXT))
            # TODO - Pad to correct size
            self.mapKigou = getSubstitutedString(tempPack.getFile(PATH_KIGOU).decode('shift-jis'))
            self.mapKomoji = getSubstitutedString(tempPack.getFile(PATH_KOMOJI).decode('shift-jis'))
            self.mapOomoji = getSubstitutedString(tempPack.getFile(PATH_OOMOJI).decode('shift-jis'))
            self.mapTokushu = getSubstitutedString(tempPack.getFile(PATH_TOKUSHU).decode('shift-jis'))
            del tempPack

        except:
            raise FileInvalidCritical

        if self.laytonState.getGameMode() == GAMEMODES.Name:
            self.screenController.setBgSub(PATH_BG_SUB_NAME)
        else:
            self.screenController.setBgSub(PATH_BG_SUB_HAM)

        self.indexBg = 0
        self.keys = []
        self.countKeys = COUNT_KEY_SPECIAL
        self.activeKey = 0
        self.drawNamesBlockedScreen = False

        def callbackOnOk():
            if len(self.entry) != 0:
                if self.entry in NAMES_BLOCKED:
                    self.drawNamesBlockedScreen = True
                else:
                    if self.laytonState.getGameMode() == GAMEMODES.Name:
                        # Player is entering the name on their save file!
                        self.laytonState.saveSlot.name = self.entry
                        self.laytonState.setGameMode(GAMEMODES.Room)
                    else:
                        # Player is entering the hamster name
                        self.laytonState.saveSlot.minigameHamsterState.name = self.entry
                        self.laytonState.setGameMode(GAMEMODES.DramaEvent)
                        self.laytonState.setEventId(11101)

                    self._canBeKilled = True

        def callbackOnDownShift():
            if self.indexBg == 1:
                self._setIndexBg(0)
            else:
                self._setIndexBg(1)
            self._updateKeyPositionDefault()
        
        def callbackOnShift():
            self._setIndexBg(2)
            self._updateKeyPositionDefault()
        
        def callbackOnSub():
            self._setIndexBg(0)
            self._updateKeyPositionDefault()
        
        def callbackOnAccent():
            self._setIndexBg(3)
            self._updateKeyPositionSpecial()

        def callbackOnSpace():
            self._addCharToEntry(" ")

        def callbackOnErase():
            if len(self.entry) > 0:
                self.entry = self.entry[:-1]
                self._updateEntry()

        def callbackOnKeyPress():
            self._addCharToEntry(self.activeMap[self.activeKey])
            if self.indexBg == 2:
                self._setIndexBg(0)

        for indexKey in range(self.countKeys):
            self.keys.append(KeyboardButton((0,0), SIZE_KEY, callback=callbackOnKeyPress))

        self.keyDownShift = NullButton((POS_BUTTON_DOWN[0],
                                        POS_BUTTON_DOWN[1] + RESOLUTION_NINTENDO_DS[1]),
                                       (POS_BUTTON_DOWN[0] + SIZE_BUTTON_DOWN[0],
                                        POS_BUTTON_DOWN[1] + RESOLUTION_NINTENDO_DS[1] + SIZE_BUTTON_DOWN[1]),
                                       callback = callbackOnDownShift)
        self.keyShift = NullButton((POS_BUTTON_SHIFT[0],
                                    POS_BUTTON_SHIFT[1] + RESOLUTION_NINTENDO_DS[1]),
                                   (POS_BUTTON_SHIFT[0] + SIZE_BUTTON_SHIFT[0],
                                    POS_BUTTON_SHIFT[1] + RESOLUTION_NINTENDO_DS[1] + SIZE_BUTTON_SHIFT[1]),
                                   callback = callbackOnShift)

        tempBankButtons = getAnimFromPath(PATH_ANI_BUTTON)

        def getButtonFromBank(bank, name, pos, callback):
            bank.setAnimationFromName(name)
            return StaticButton((pos[0], pos[1] + RESOLUTION_NINTENDO_DS[1]), bank.getActiveFrame(), callback=callback, targettedOffset=(1,1))

        self.buttonSub = getButtonFromBank(tempBankButtons, BTN_NORMAL_NAME, BTN_NORMAL_POS, callbackOnSub)
        self.buttonAccent = getButtonFromBank(tempBankButtons, BTN_ACCENT_NAME, BTN_ACCENT_POS, callbackOnAccent)
        self.buttonSpace = getButtonFromBank(tempBankButtons, BTN_SPACE_NAME, BTN_SPACE_POS, callbackOnSpace)
        self.buttonErase = getButtonFromBank(tempBankButtons, BTN_BACK_NAME, BTN_BACK_POS, callbackOnErase)

        self.buttonOk = getAnimFromPath(PATH_ANI_OK.replace("?", self.laytonState.language.value))
        self.buttonOk.setAnimationFromName("gfx")
        self.buttonOk = StaticButton((POS_BUTTON_OK[0], POS_BUTTON_OK[1] + RESOLUTION_NINTENDO_DS[1]), self.buttonOk.getActiveFrame(), callback=callbackOnOk, targettedOffset=(1,1))

        self.surfaceBadName = getAnimFromPath(PATH_BAD_NAME.replace("?", self.laytonState.language.value))
        self.surfaceBadName.setAnimationFromName("gfx")
        self.surfaceBadName.setPos(((RESOLUTION_NINTENDO_DS[0] - self.surfaceBadName.getDimensions()[0]) // 2, POS_BAD_NAME[1] + RESOLUTION_NINTENDO_DS[1]))

        self.animCursor = getAnimFromPath(PATH_ANI_CURSOR)
        self.animCursor.setAnimationFromIndex(1)
        self.animCursor.setPos((POS_ANI_CURSOR[0], POS_ANI_CURSOR[1] + RESOLUTION_NINTENDO_DS[1]))

        self.surfaceEntry = None
        self.surfaceHighlight = Surface(SIZE_KEY)
        # Produces similar colour, but sticking with Pygame's blend modes
        self.surfaceHighlight.fill((255,128,128))

        callbackOnSub()
        self.screenController.fadeIn()

    def update(self, gameClockDelta):
        self.animCursor.update(gameClockDelta)

        if self.drawNamesBlockedScreen:
            self.surfaceBadName.update(gameClockDelta)

    def draw(self, gameDisplay):
        self.animCursor.draw(gameDisplay)
        
        if self.surfaceEntry != None:
            gameDisplay.blit(self.surfaceEntry, (POS_ENTRY_TEXT[0] + 1, POS_ENTRY_TEXT[1] + RESOLUTION_NINTENDO_DS[1]), special_flags=BLEND_RGB_SUB)

        for key in self.keys:
            if key.needsHighlightSurface:
                gameDisplay.blit(self.surfaceHighlight, key.getPos(), special_flags=BLEND_RGB_MULT)
                break

        self.buttonSub.draw(gameDisplay)
        self.buttonAccent.draw(gameDisplay)
        self.buttonSpace.draw(gameDisplay)
        self.buttonErase.draw(gameDisplay)
        self.buttonOk.draw(gameDisplay)

        if self.drawNamesBlockedScreen:
            self.surfaceBadName.draw(gameDisplay)

    def handleTouchEvent(self, event):
        if self.drawNamesBlockedScreen:
            if event.type == MOUSEBUTTONUP:
                self.drawNamesBlockedScreen = False
                self._clearEntry()
        else:
            self.buttonSub.handleTouchEvent(event)
            self.buttonAccent.handleTouchEvent(event)
            self.buttonSpace.handleTouchEvent(event)
            self.buttonErase.handleTouchEvent(event)
            self.buttonOk.handleTouchEvent(event)

            if self.indexBg != 3:
                self.keyDownShift.handleTouchEvent(event)
                self.keyShift.handleTouchEvent(event)
            
            for indexKey in range(self.countKeys):
                self.activeKey = indexKey
                if self.keys[indexKey].handleTouchEvent(event):
                    break

    # Update key position functions reversed from game, so constants have not been pulled to module as modifying
    # these in the ROM would have no effect on key position.
    def _updateKeyPositionDefault(self):
        x = 0xf
        y = 0x31
        for indexKey, key in enumerate(self.keys):
            key.setPos((x,y + RESOLUTION_NINTENDO_DS[1]))
            x += 0x13   # Key stride
            if indexKey == 0xb:
                x = 0x18
                y = 0x44
            elif indexKey == 0x17:
                x = 0x22
                y = 0x57
            elif indexKey == 0x22:
                x = 0x2b
                y = 0x6a
            
        self.countKeys = COUNT_KEY

    def _updateKeyPositionSpecial(self):
        y = 0x31
        indexKey = 0
        for indexRow in range(4):
            x = 5
            for indexColumn in range(0xd):
                self.keys[indexKey].setPos((x,y + RESOLUTION_NINTENDO_DS[1]))
                x += 0x13
                indexKey += 1
            y += 0x13
        
        self.countKeys = COUNT_KEY_SPECIAL

    def _updateEntry(self):
        if len(self.entry) == NamePlayer.LENGTH_ENTRY:
            self.animCursor.setPos((POS_ANI_CURSOR[0] + (STRIDE_CHARACTER * (NamePlayer.LENGTH_ENTRY - 1)), POS_ANI_CURSOR[1] + RESOLUTION_NINTENDO_DS[1]))
        else:
            self.animCursor.setPos((POS_ANI_CURSOR[0] + (STRIDE_CHARACTER * len(self.entry)), POS_ANI_CURSOR[1] + RESOLUTION_NINTENDO_DS[1]))
            
        self.surfaceEntry = generateImageFromStringStrided(self.laytonState.fontEvent, self.entry, STRIDE_CHARACTER)

    def _clearEntry(self):
        self.entry = ""
        self._updateEntry()

    def _addCharToEntry(self, char):
        if len(self.entry) >= NamePlayer.LENGTH_ENTRY:
            self.entry = self.entry[0:NamePlayer.LENGTH_ENTRY - 1] + char
            self._updateEntry()
        elif len(self.entry) < NamePlayer.LENGTH_ENTRY:
            self.entry += char
            self._updateEntry()

    def _setIndexBg(self, newId):
        self.indexBg = newId
        if newId == 0:
            self.activeMap = self.mapKomoji
            self.screenController.setBgMain(PATH_BG_NAME_1)
        elif newId == 1:
            self.activeMap = self.mapOomoji
            self.screenController.setBgMain(PATH_BG_NAME_2)
        elif newId == 2:
            self.activeMap = self.mapKigou
            self.screenController.setBgMain(PATH_BG_NAME_3)
        else:
            self.activeMap = self.mapTokushu
            self.screenController.setBgMain(PATH_BG_NAME_4)