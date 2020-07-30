from ..engine.state.layer import ScreenCollection, ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES
from ..engine.const import RESOLUTION_NINTENDO_DS, PATH_BG_ROOT
from ..engine.file import FileInterface
from ..engine.anim.fader import Fader

from ..gamemodes import EventPlayer, RoomPlayer, NarrationPlayer, PuzzlePlayer, UnkTeaPlayer

from ..madhatter.hat_io.asset_image import StaticImage
from ..engine.custom_events import ENGINE_SKIP_CLOCK

from pygame.event import post, Event
from pygame import Surface, image, QUIT, MOUSEBUTTONUP

class BgLayer(ScreenLayerNonBlocking):

    # Holds background layers used in game
    # Only Layer 3 backgrounds should be applied to this layer

    def __init__(self, laytonState):
        ScreenLayerNonBlocking.__init__(self)
        self._laytonState = laytonState

        self._bgMain    = Surface(RESOLUTION_NINTENDO_DS)
        self._bgSub     = Surface(RESOLUTION_NINTENDO_DS)
        self._bgMainPal = Surface(RESOLUTION_NINTENDO_DS)
        self._bgSubPal  = Surface(RESOLUTION_NINTENDO_DS)

        self._palMain   = 0
        self._palSub    = 0
    
    def _getImageFromPath(self, pathBg):

        def fetchBgxImage(path):
            # TODO - Fix unwanted behaviour with reading null-terminated strings, where a null character is left at the end
            if "bgx" in path:
                tempPath = path.split(".")
                path = ".".join(tempPath[:-1]) + ".arc"

            imageFile = FileInterface.getData(PATH_BG_ROOT % path)
            if imageFile != None:
                try:
                    imageFile = StaticImage.fromBytesArc(imageFile)
                    return imageFile.getImage(0)
                except:
                    return None
            return imageFile

        if "?" not in pathBg:
            langPath = pathBg.split("/")
            langPath.insert(-1, self._laytonState.language.value)
            langPath = '/'.join(langPath)
        else:
            langPath = pathBg.replace("?", self._laytonState.language.value)

        bg = fetchBgxImage(langPath)
        if bg == None:
            bg = fetchBgxImage(pathBg)
        return bg
    
    def _setBg(self, pathBg):
        bg = self._getImageFromPath(pathBg)
        if bg != None:
            output = image.fromstring(bg.convert("RGB").tobytes("raw", "RGB"), bg.size, "RGB").convert()
        else:
            output = Surface(RESOLUTION_NINTENDO_DS)
        return output
    
    def _updatePal(self, inImage, darkness):
        tempImage = inImage.copy()
        darkener = Surface((inImage.get_width(), inImage.get_height()))
        darkener.set_alpha(darkness)
        tempImage.blit(darkener, (0,0))
        return tempImage

    def setBgMain(self, pathBg):
        # Should this be blitted instead?
        self._bgMain = self._setBg(pathBg)
        self._bgMainPal = self._updatePal(self._bgMain, self._palMain)

    def setBgSub(self, pathBg):
        self._bgSub = self._setBg(pathBg)
        self._bgSubPal = self._updatePal(self._bgSub, self._palSub)
    
    def modifyPaletteMain(self, darkness):
        self._palMain = darkness
        self._bgMainPal = self._updatePal(self._bgMain, self._palMain)
    
    def modifyPaletteSub(self, darkness):
        self._palSub = darkness
        self._bgSubPal = self._updatePal(self._bgSub, self._palSub)

    def draw(self, gameDisplay):
        gameDisplay.blit(self._bgSubPal, (0,0))
        gameDisplay.blit(self._bgMainPal, (0, RESOLUTION_NINTENDO_DS[1]))

class FaderLayer(ScreenLayerNonBlocking):

    DEFAULT_FADE_TIME = 250

    def __init__(self):
        ScreenLayerNonBlocking.__init__(self)
        self._faderSurfMain  = Surface(RESOLUTION_NINTENDO_DS)
        self._faderSurfSub   = Surface(RESOLUTION_NINTENDO_DS)

        self._faderMain     = Fader(0, initialActiveState=False)
        self._faderSub      = Fader(0, initialActiveState=False)
        self._faderWait         = Fader(0, initialActiveState=False)
        self._waitCanBeSkipped  = False
        self.isViewObscured = False

    def update(self, gameClockDelta):
        self._faderMain.update(gameClockDelta)
        self._faderSub.update(gameClockDelta)
        self._faderWait.update(gameClockDelta)

        if self._faderMain.getStrength() == 1 and self._faderSub.getStrength() == 1:
            self.isViewObscured = True
        else:
            self.isViewObscured = False

        self._faderSurfMain.set_alpha(round(self._faderMain.getStrength() * 255))
        self._faderSurfSub.set_alpha(round(self._faderSub.getStrength() * 255))

    def fadeInMain(self, duration=DEFAULT_FADE_TIME):
        post(Event(ENGINE_SKIP_CLOCK))
        self._faderMain.setDuration(duration)
        self._faderMain.setInvertedState(True)
    
    def fadeOutMain(self, duration=DEFAULT_FADE_TIME):
        post(Event(ENGINE_SKIP_CLOCK))
        self._faderMain.setDuration(duration)
        self._faderMain.setInvertedState(False)
    
    def fadeInSub(self, duration=DEFAULT_FADE_TIME):
        post(Event(ENGINE_SKIP_CLOCK))
        self._faderSub.setDuration(duration)
        self._faderSub.setInvertedState(True)
    
    def fadeOutSub(self, duration=DEFAULT_FADE_TIME):
        post(Event(ENGINE_SKIP_CLOCK))
        self._faderSub.setDuration(duration)
        self._faderSub.setInvertedState(False)
    
    def fadeIn(self, duration=DEFAULT_FADE_TIME):
        post(Event(ENGINE_SKIP_CLOCK))
        self.fadeInMain(duration=duration)
        self.fadeInSub(duration=duration)
        
    def fadeOut(self, duration=DEFAULT_FADE_TIME):
        post(Event(ENGINE_SKIP_CLOCK))
        self.fadeOutMain(duration=duration)
        self.fadeOutSub(duration=duration)

    def setWaitDuration(self, duration, canBeSkipped=False):
        self._faderWait.setDuration(duration)
        self._waitCanBeSkipped = canBeSkipped

    def getFaderStatus(self):
        return self._faderSub.getActiveState() or self._faderMain.getActiveState() or self._faderWait.getActiveState()

    def debugGetFaderStatus(self):
        return (self._faderSub.getActiveState(), self._faderMain.getActiveState())
    
    def obscureViewLayer(self):
        if self._faderMain.getStrength() != 1:
            self.fadeOutMain()
        if self._faderSub.getStrength() != 1:
            self.fadeOutSub()

    def draw(self, gameDisplay):
        gameDisplay.blit(self._faderSurfSub, (0,0))
        gameDisplay.blit(self._faderSurfMain, (0,RESOLUTION_NINTENDO_DS[1]))

    def handleTouchEvent(self, event):
        if self._waitCanBeSkipped and event.type == MOUSEBUTTONUP:
            self._faderWait.setActiveState(False)
            self._waitCanBeSkipped = False
        return super().handleTouchEvent(event)

class ScreenController():
    def __init__(self, faderLayer, bgLayer):
        self._faderLayer = faderLayer
        self._bgLayer = bgLayer
        self._waitFader = Fader(0, initialActiveState=False)
        self._waitingForTap = False

    def getFadingStatus(self):
        return self._faderLayer.getFaderStatus()

    def getFaderIsViewObscured(self):
        return self._faderLayer.isViewObscured

    def obscureViewLayer(self):
        if not(self.getFaderIsViewObscured()):
            self._faderLayer.obscureViewLayer()
    
    def debugGetFaderStatus(self):
        return self._faderLayer.debugGetFaderStatus()

    def fadeInMain(self, duration=FaderLayer.DEFAULT_FADE_TIME):
        self._faderLayer.fadeInMain(duration=duration)
    
    def fadeOutMain(self, duration=FaderLayer.DEFAULT_FADE_TIME):
        self._faderLayer.fadeOutMain(duration=duration)
    
    def fadeInSub(self, duration=FaderLayer.DEFAULT_FADE_TIME):
        self._faderLayer.fadeInSub(duration=duration)
    
    def fadeOutSub(self, duration=FaderLayer.DEFAULT_FADE_TIME):
        self._faderLayer.fadeOutSub(duration=duration)
    
    def fadeIn(self, duration=FaderLayer.DEFAULT_FADE_TIME):
        self._faderLayer.fadeIn(duration=duration)
        
    def fadeOut(self, duration=FaderLayer.DEFAULT_FADE_TIME):
        self._faderLayer.fadeOut(duration=duration)

    def setWaitDuration(self, duration, canBeSkipped=False):
        self._faderLayer.setWaitDuration(duration, canBeSkipped=canBeSkipped)

    def setBgMain(self, path):
        self._bgLayer.setBgMain(path)
        self.modifyPaletteMain(0)

    def setBgSub(self, path):
        self._bgLayer.setBgSub(path)
        self.modifyPaletteSub(0)

    def modifyPaletteMain(self, darkness):
        self._bgLayer.modifyPaletteMain(darkness)

    def modifyPaletteSub(self, darkness):
        self._bgLayer.modifyPaletteSub(darkness)

class ScreenCollectionGameModeSpawner(ScreenCollection):
    def __init__(self, laytonState):
        ScreenCollection.__init__(self)

        self.laytonState = laytonState

        layerFader = FaderLayer()
        layerBg    = BgLayer(laytonState)

        self.screenControllerObject = ScreenController(layerFader, layerBg)
        self.addToCollection(layerBg)
        self.addToCollection(layerFader)

        self._currentActiveGameMode = 0
        self._currentActiveGameModeObject = None

        self.waitingForFadeOut = False

    def _loadGameMode(self, indexGameMode):

        layerFader = self._layers.pop()

        if indexGameMode == GAMEMODES.DramaEvent.value:
            self.addToCollection(EventPlayer(self.laytonState, self.screenControllerObject))
        elif indexGameMode == GAMEMODES.Room.value:
            self.addToCollection(RoomPlayer(self.laytonState, self.screenControllerObject))
        elif indexGameMode == GAMEMODES.Narration.value:
            self.addToCollection(NarrationPlayer(self.laytonState, self.screenControllerObject))
        elif indexGameMode == GAMEMODES.Puzzle.value:
            self.addToCollection(PuzzlePlayer(self.laytonState, self.screenControllerObject))
        elif indexGameMode == GAMEMODES.UnkTeaMode.value:
            self.addToCollection(UnkTeaPlayer(self.laytonState, self.screenControllerObject))
            
        else:
            if indexGameMode == GAMEMODES.INVALID.value:
                self._voidGameMode()
            else:
                print("Missing connection for type", indexGameMode)
                self._currentActiveGameMode = indexGameMode
                self._currentActiveGameModeObject = None

            self.addToCollection(layerFader)
            return False
        
        self._currentActiveGameMode = indexGameMode
        self._currentActiveGameModeObject = self._layers[-1]

        self.addToCollection(layerFader)
        return True
    
    def _voidGameMode(self):
        self._currentActiveGameMode = GAMEMODES.INVALID.value
        self._currentActiveGameModeObject = None

    def _triggerQuit(self):
        post(Event(QUIT))
    
    def _switchToNextGameMode(self):
        self.laytonState.setGameMode(self.laytonState.getGameModeNext())
        self.laytonState.setGameModeNext(GAMEMODES.INVALID)

    def update(self, gameClockDelta):

        def startObscuration():
            self.screenControllerObject.obscureViewLayer()
            self.waitingForFadeOut = True

        if not(self.waitingForFadeOut):
            if self._currentActiveGameMode != self.laytonState.getGameMode().value or self.laytonState.gameModeRestartRequired:
                # Active gamemode is outdated, so kill the current instance and load the new one.
                # TODO - Only allow spawning when fader has faded all the way out
                if self.screenControllerObject.getFaderIsViewObscured():
                    if self._currentActiveGameModeObject != None:
                        self.removeFromCollection(self._layers.index(self._currentActiveGameModeObject))
                    
                    self._loadGameMode(self.laytonState.getGameMode().value)
                    self.laytonState.gameModeRestartRequired = False
                else:
                    startObscuration()

            elif self._currentActiveGameMode == GAMEMODES.INVALID.value:
                # Execution hit the invalid state, meaning that it's time to end
                self._triggerQuit()

            elif self._currentActiveGameModeObject == None or self._currentActiveGameModeObject.getContextState():
                # The current layer is finished, so the next one can now be loaded

                # If there was a layer running (not virtual), remove it from the collection
                # TODO - Force fade out on kill before next spawn
                if self.screenControllerObject.getFaderIsViewObscured():
                    if self._currentActiveGameModeObject != None:
                        self.removeFromCollection(self._layers.index(self._currentActiveGameModeObject))

                    # As there is nothing associated with the running handler anymore, void the current instance
                    self._voidGameMode()

                    # Load next game mode for for next update to grab
                    self._switchToNextGameMode()
                else:
                    startObscuration()

        elif self.screenControllerObject.getFaderIsViewObscured():
            self.waitingForFadeOut = False

        # Override original update to ensure game mode object cannot be deleted, as logic above does that properly
        for indexLayer in range(len(self._layers) - 1, -1, -1):
            layer = self._layers[indexLayer]
            layer.update(gameClockDelta)
            if layer.getContextState() and layer != self._currentActiveGameModeObject:
                self.removeFromCollection(indexLayer)
    
    def draw(self, gameDisplay):
        if not(self.screenControllerObject.getFaderIsViewObscured()):
            # Saves CPU, although this leaves a faint trail
            return super().draw(gameDisplay)
        return super().draw(gameDisplay)
        return None