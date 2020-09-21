from ...engine.anim.font.static import generateImageFromString
from ...engine.anim.button import AnimatedButton, NullButton
from ...engine.config import PATH_SAVE
from ...engine.const import PATH_PACK_TXT2, PATH_TEXT_GENERIC, PATH_PACK_PLACE_NAME, PATH_TEXT_PLACE_NAME, RESOLUTION_NINTENDO_DS
from ...engine.file import FileInterface
from ...madhatter.hat_io.asset import LaytonPack
from ...madhatter.hat_io.asset_sav import Layton2SaveFile

from ..title.utils import getAnimFromPath

from .const import PATH_BG_FILELOAD, PATH_BG_FILESAVE, PATH_ANI_BTN_BACK, ID_SAVE_EMPTY
from .utils import MainScreenPopup

from pygame import Surface, BLEND_RGB_SUB

class SaveLoadScreenPopup(MainScreenPopup):

    MODE_SAVE = 0
    MODE_LOAD = 1

    # All values from ROM
    OFFSET_BOTTOM_TEXT  = 0x39
    OFFSET_MIDDLE_TEXT  = 0x2f
    OFFSET_TOP_TEXT     = 0x25

    OFFSET_X_EMPTY_TEXT = 0x8a
    OFFSET_X_BOX_TEXT   = 0x5b
    
    OFFSET_X_SLOT_START = 0x03
    OFFSET_X_SLOT_END   = 0xfa

    OFFSET_Y_SLOT_START = 0x1f

    STRIDE_BOX          = 0x2e
    HEIGHT_SLOT         = 0x2b

    def __init__(self, laytonState, screenController, mode, bgIndex, callbackOnTerminate, callbackOnSlot):
        MainScreenPopup.__init__(self, callbackOnTerminate)

        self.saveData = Layton2SaveFile()
        try:
            with open(PATH_SAVE, 'rb') as saveIn:
                if not(self.saveData.load(saveIn.read())):
                    self.saveData = Layton2SaveFile()
        except FileNotFoundError:
            pass

        self.surfaceName    = [None, None, None]
        self.surfacePlace   = [None, None, None]
        self.surfaceNameX   = [0,0,0]
        self.surfacePlaceX   = [0,0,0]

        self.slotButtons = []
        self.slotIndexSlot = []
        self.slotActive = None

        # TODO - Support saving, which has a popup with the overwrite screen

        def callbackOnSlotAccessed():
            if mode == SaveLoadScreenPopup.MODE_LOAD:
                laytonState.timeStartTimer()
                laytonState.saveSlot = self.saveData.getSlotData(self.slotActive)
            else:
                laytonState.timeUpdateStoredTime()
                print("Saving unsupported!")

            callbackOnSlot()

        try:
            textPack = LaytonPack()
            textPack.load(FileInterface.getData(PATH_PACK_TXT2 % laytonState.language.value))
            self.surfaceEmpty = generateImageFromString(laytonState.fontEvent, surfaceEmpty.getFile(PATH_TEXT_GENERIC % ID_SAVE_EMPTY).decode('shift-jis'))
        except:
            self.surfaceEmpty = Surface((0,0))
        
        self.surfaceEmptyX = (SaveLoadScreenPopup.OFFSET_X_EMPTY_TEXT - self.surfaceEmpty.get_width() // 2)
        
        try:
            textPack = LaytonPack()
            textPack.load(FileInterface.getData(PATH_PACK_PLACE_NAME % laytonState.language.value))

            for indexSlot in range(3):
                saveSlot = self.saveData.getSlotData(indexSlot)
                if saveSlot.isActive:
                    indexPlace = saveSlot.roomIndex
                    if indexPlace == 0x5c:
                        indexPlace = 0x26
                    tempTextFile = textPack.getFile(PATH_TEXT_PLACE_NAME % indexPlace)
                    if tempTextFile != None:
                        try:
                            self.surfacePlace[indexSlot] = generateImageFromString(laytonState.fontQ, tempTextFile.decode('shift-jis'))
                            self.surfacePlaceX[indexSlot] = SaveLoadScreenPopup.OFFSET_X_BOX_TEXT - self.surfacePlace[indexSlot].get_width() // 2
                        except UnicodeDecodeError:
                            pass
                    
                    self.surfaceName[indexSlot] = generateImageFromString(laytonState.fontEvent, saveSlot.name)
                    self.surfaceNameX[indexSlot] = SaveLoadScreenPopup.OFFSET_X_BOX_TEXT - self.surfaceName[indexSlot].get_width() // 2

                    self.slotButtons.append(NullButton((SaveLoadScreenPopup.OFFSET_X_SLOT_START, SaveLoadScreenPopup.OFFSET_Y_SLOT_START + RESOLUTION_NINTENDO_DS[1] + (SaveLoadScreenPopup.STRIDE_BOX * indexSlot)),
                                                        (SaveLoadScreenPopup.OFFSET_X_SLOT_END,
                                                        SaveLoadScreenPopup.OFFSET_Y_SLOT_START + RESOLUTION_NINTENDO_DS[1] + SaveLoadScreenPopup.HEIGHT_SLOT + (SaveLoadScreenPopup.STRIDE_BOX * indexSlot)),
                                                        callback=callbackOnSlotAccessed))
                    self.slotIndexSlot.append(indexSlot)

                elif mode == SaveLoadScreenPopup.MODE_SAVE:
                    # Always add a button if in save menu, since empty slots can be overwritten
                    self.slotButtons.append(NullButton((SaveLoadScreenPopup.OFFSET_X_SLOT_START, SaveLoadScreenPopup.OFFSET_Y_SLOT_START + RESOLUTION_NINTENDO_DS[1] + (SaveLoadScreenPopup.STRIDE_BOX * indexSlot)),
                                    (SaveLoadScreenPopup.OFFSET_X_SLOT_END,
                                    SaveLoadScreenPopup.OFFSET_Y_SLOT_START + RESOLUTION_NINTENDO_DS[1] + SaveLoadScreenPopup.HEIGHT_SLOT + (SaveLoadScreenPopup.STRIDE_BOX * indexSlot)),
                                    callback=callbackOnSlotAccessed))
        except:
            textPack = None
                
        # TODO - Make class variable
        self.buttonBack = AnimatedButton(getAnimFromPath(PATH_ANI_BTN_BACK % laytonState.language.value), "on", "off", callback=callbackOnTerminate)

        if mode == SaveLoadScreenPopup.MODE_LOAD:
            screenController.setBgMain(PATH_BG_FILELOAD % (laytonState.language.value, bgIndex + 1))
        else:
            screenController.setBgMain(PATH_BG_FILESAVE % (laytonState.language.value))

        screenController.fadeInMain()
    
    def draw(self, gameDisplay):
        self.buttonBack.draw(gameDisplay)

        offsetBottom    = SaveLoadScreenPopup.OFFSET_BOTTOM_TEXT + RESOLUTION_NINTENDO_DS[1]
        offsetMiddle    = SaveLoadScreenPopup.OFFSET_MIDDLE_TEXT + RESOLUTION_NINTENDO_DS[1]
        offsetTop       = SaveLoadScreenPopup.OFFSET_TOP_TEXT + RESOLUTION_NINTENDO_DS[1]

        for indexSlot in range(3):
            if self.saveData.getSlotData(indexSlot).isActive:
                gameDisplay.blit(self.surfaceName[indexSlot], (self.surfaceNameX[indexSlot], offsetTop), special_flags=BLEND_RGB_SUB)
                if self.surfacePlace[indexSlot] != None:
                    gameDisplay.blit(self.surfacePlace[indexSlot], (self.surfacePlaceX[indexSlot], offsetBottom), special_flags=BLEND_RGB_SUB)
            else:
                gameDisplay.blit(self.surfaceEmpty, (self.surfaceEmptyX, offsetMiddle), special_flags=BLEND_RGB_SUB)
            
            offsetBottom += SaveLoadScreenPopup.STRIDE_BOX
            offsetMiddle += SaveLoadScreenPopup.STRIDE_BOX
            offsetTop += SaveLoadScreenPopup.STRIDE_BOX
    
    def update(self, gameClockDelta):
        self.buttonBack.update(gameClockDelta)
    
    def handleTouchEvent(self, event):
        self.buttonBack.handleTouchEvent(event)
        for indexButton, slot in enumerate(self.slotButtons):
            self.slotActive = self.slotIndexSlot[indexButton]
            slot.handleTouchEvent(event)