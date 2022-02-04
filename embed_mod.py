# Credits for Pygame embedding - they provided the basic code which helped with this solution
# Original code by David Barker (aka Animatinator), 14/07/2010
#     Patch for cross-platform support by Sean McKean, 16/07/2010
#     Patch to fix redrawing issue by David Barker, 20/07/2010
#     Modernised by Yuxi Luo (Skycocoo), 19/06/2018

# TODO - Understand this, seems to be HighDPI related
# RESIZE_PERCENT = 1.125

# Force SDL to disable video output
from os import environ
environ["SDL_VIDEODRIVER"] = "dummy"

# Disable high DPI behaviour on Windows, which causes blurriness
try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
    # Credit - https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# Override display init to create raw canvas
from pygame.display import init, set_mode
from widebrim.engine import convenience
from widebrim.engine.const import RESOLUTION_NINTENDO_DS

def initDisplayEmbed():
    global _HAS_CAPTION_BEEN_SET
    init()
    _HAS_CAPTION_BEEN_SET = True
    output = set_mode((RESOLUTION_NINTENDO_DS[0], int(RESOLUTION_NINTENDO_DS[1] * 2)))
    return output

convenience.initDisplay = initDisplayEmbed

# After this point, be careful only with conflicts. Patches completed on widebrim

from typing import Optional
from pygame import Surface
import pygame
from nopush_editor import Editor
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine_ext.state_game import ScreenCollectionGameModeSpawner

from wx import Timer, EVT_TIMER, EVT_PAINT, Bitmap, ClientDC, PaintDC, BitmapFromBuffer, Icon
from wx import Image as WxImageNonConflict
from widebrim.engine.state.state import Layton2GameState
from widebrim.engine.file import FileInterface

from e_puzzle import FramePuzzleEditor
from widebrim.engine_ext.rom.banner import getBannerImageFromRom, getNameStringFromRom

class EditorWindow(Editor):
    def __init__(self, parent):
        super().__init__(parent)
        # self.MinSize = Size(round(self.MinSize.width * RESIZE_PERCENT), round(self.MinSize.height * RESIZE_PERCENT))
        self.__widebrimTimer = Timer(self)
        self.__widebrimAnchor = self.panelWidebrimInjection
        self.__widebrimRenderSurface = Surface((RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1] * 2), 0 , 32)
        self._widebrimState = Layton2GameState()
        self.__widebrimRenderLayers : Optional[ScreenCollectionGameModeSpawner] = None
        self.__widebrimSpeedMultipler = 1

        # Bind drawing and timing events to pygame routines
        self.Bind(EVT_PAINT, self.__repaintWidebrim)
        self.Bind(EVT_TIMER, self.__updateWidebrim, self.__widebrimTimer)
        self.spawnHandler(GAMEMODES.Reset)

        self._setWidebrimFramerate(30)
        self._addPage(FramePuzzleEditor, "TEST")
        self.__refreshRomProperties()

    def __refreshRomProperties(self):
        self.romTextCode.SetValue(FileInterface.getRom().idCode.decode('ascii'))
        self.romTextName.SetValue(getNameStringFromRom(FileInterface.getRom(), FileInterface.getLanguage()))
        bannerImage = getBannerImageFromRom(FileInterface.getRom())
        bitmapBanner = BitmapFromBuffer(bannerImage.size[0], bannerImage.size[1], bannerImage.convert("RGB").tobytes("raw", "RGB"))
        self.previewIcon.SetBitmap(bitmapBanner)
        self.SetIcon(Icon(bitmapBanner))

    def spawnHandler(self, gamemode):
        self._widebrimState.setGameMode(gamemode)
        self.__widebrimRenderLayers = ScreenCollectionGameModeSpawner(self._widebrimState)
        self.__widebrimRenderLayers.update(0)
        self.__widebrimRenderLayers.update(0)
    
    def _addPage(self, initForPage, caption):
        size = self.GetSize()
        print(size)
        self.auiTabs.AddPage(initForPage(self.auiTabs, 24, self._widebrimState), caption, select = True)
        print(size)
        self.SetSize(size)
        #self.auiTabs.
    
    def forceSyncOnButtonClick(self, event):
        page = self.auiTabs.GetCurrentPage()
        if type(page) == FramePuzzleEditor:
            page.syncChanges()
            print("CALLED SYNC")
        return super().forceSyncOnButtonClick(event)


    #def _restartWidebrimPreview(self):
    #    """Restart the widebrim preview engine.
    #    Required in certain cases where hotpatching fails - for example,
    #    databases loaded in the global game state are never reloaded.
    #    """

    #    # TODO - Remove all class instances, will lead to strange bugs in future!
    #    # TODO - Remove all caching of instances. Will break something in future!
    #    self._widebrimState = Layton2GameState()
    #    self.__widebrimRenderLayers = None
    #    self.__widebrimRenderSurface = Surface((RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1] * 2), 0 , 32)
    
    def _setWidebrimFramerate(self, fps):
        if 0 < fps <= 1000:
            self.__widebrimTimer.Stop()
            self.__widebrimTimer.Start(1000//fps, False)
            return True
        return False

    def _setWidebrimSpeedMultipler(self, multiplier):
        if multiplier > 0:
            self.__widebrimSpeedMultipler = multiplier
            return True
        return False

    def __drawWidebrim(self, dc):
        if self.__widebrimRenderLayers != None:
            self.__widebrimRenderLayers.draw(self.__widebrimRenderSurface)
        
        pos = self.__widebrimAnchor.GetPosition()
        s = pygame.image.tostring(self.__widebrimRenderSurface, 'RGB')                             # Convert surface to raw image
        img = WxImageNonConflict(self.__widebrimRenderSurface.get_width(), self.__widebrimRenderSurface.get_height(), s)  # Load image into wx
        bmp = Bitmap(img)                                                           # Convert image to bitmap
        dc.DrawBitmap(bmp, pos.x, pos.y, False)                                                # Draw bitmap over embedded zone
        del dc

    def __repaintWidebrim(self, event):
        self.__drawWidebrim(PaintDC(self))
        event.Skip()

    def __updateWidebrim(self, event):
        if self.__widebrimRenderLayers != None:
            self.__widebrimRenderLayers.update(self.__widebrimTimer.GetInterval() * self.__widebrimSpeedMultipler)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN:
                    self.__widebrimRenderLayers.handleTouchEvent(event)

        self.__drawWidebrim(ClientDC(self))
    
    def widebrimButtonRestartStateOnButtonClick(self, event):
        page = self.auiTabs.GetCurrentPage()
        if type(page) == FramePuzzleEditor:
            page.prepareWidebrimState()
            self.spawnHandler(GAMEMODES.Puzzle)
        return super().widebrimButtonRestartStateOnButtonClick(event)

    def auiTabsOnAuiNotebookPageChanged(self, event):
        page = self.auiTabs.GetCurrentPage()
        if type(page) == FramePuzzleEditor:
            page.prepareWidebrimState()
            self.spawnHandler(GAMEMODES.Puzzle)
        return super().auiTabsOnAuiNotebookPageChanged(event)
    
    def speedRealtimeOnMenuSelection(self, event):
        self._setWidebrimSpeedMultipler(1)
        return super().speedRealtimeOnMenuSelection(event)
    
    def speedDoubleOnMenuSelection(self, event):
        self._setWidebrimSpeedMultipler(2)
        return super().speedDoubleOnMenuSelection(event)

    def speedQuadrupleOnMenuSelection(self, event):
        self._setWidebrimSpeedMultipler(4)
        return super().speedQuadrupleOnMenuSelection(event)
    
    def framesFullOnMenuSelection(self, event):
        self._setWidebrimFramerate(60)
        return super().framesFullOnMenuSelection(event)
    
    def framesHalfOnMenuSelection(self, event):
        self._setWidebrimFramerate(30)
        return super().framesHalfOnMenuSelection(event)
    
    # TODO - Pause, play
    def submenuEnginePauseOnMenuSelection(self, event):
        return super().submenuEnginePauseOnMenuSelection(event)

    def widebrimButtonPausePlayOnButtonClick(self, event):
        return super().widebrimButtonPausePlayOnButtonClick(event)