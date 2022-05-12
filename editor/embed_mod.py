# Credits for Pygame embedding - they provided the basic code which helped with this solution
# Original code by David Barker (aka Animatinator), 14/07/2010
#     Patch for cross-platform support by Sean McKean, 16/07/2010
#     Patch to fix redrawing issue by David Barker, 20/07/2010
#     Modernised by Yuxi Luo (Skycocoo), 19/06/2018

# TODO - Understand this, seems to be HighDPI related
# RESIZE_PERCENT = 1.125

# Force SDL to disable video output
from os import environ

from widebrim.filesystem.fused import FusedFilesystem

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

from typing import Callable, Optional
from pygame import Surface
import pygame
from editor.nopush_editor import Editor
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine_ext.state_game import ScreenCollectionGameModeSpawner

from wx import Timer, EVT_TIMER, EVT_PAINT, EVT_CLOSE, Bitmap, ClientDC, PaintDC, Icon, CallAfter, aui
from wx import Image as WxImageNonConflict
from widebrim.engine.state.state import Layton2GameState
from widebrim.engine.file import FileInterface

from editor.e_puzzle import FramePuzzleEditor
from editor.e_script import FrameScriptEditor
from editor.e_overview import FrameOverview
from widebrim.engine_ext.rom.banner import getBannerImageFromRom, getNameStringFromRom
from threading import Thread, Lock
from time import sleep, perf_counter
from traceback import print_exc

class EditorWindow(Editor):
    def __init__(self, callbackReturnOnExit : Callable, parent):
        super().__init__(parent)
        self.__callbackAfterExit = callbackReturnOnExit
        self.__widebrimTimer = Timer(self)
        self.__widebrimAnchor = self.panelWidebrimInjection
        self.__widebrimRenderSurface = Surface((RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1] * 2), 0 , 32)
        self._widebrimState = Layton2GameState()
        self.__widebrimRenderLayers : Optional[ScreenCollectionGameModeSpawner] = None
        self.__widebrimSpeedMultipler = 1

        # TODO - Handle termination better, do not access state outside of here (thread safety...)
        self.__widebrimIsBusy = False
        self.__widebrimLastUpdateTime = 0
        self.__widebrimDrawLock = Lock()            # Lock to prevent widebrim screen being modified while update is running
        self.__widebrimStateLock = Lock()           # Lock to prevent widebrim state being modified while update is running

        # Bind drawing and timing events to pygame routines
        self.Bind(EVT_PAINT, self.__repaintWidebrim)
        self.Bind(EVT_TIMER, self.__updateWidebrim, self.__widebrimTimer)
        self.Bind(EVT_CLOSE, self.__doOnClose)
        self.spawnHandler(GAMEMODES.Reset)

        self.auiTabs.AddPage(FrameOverview(self.auiTabs, self._widebrimState), "Overview", select=False)
        self.framesExtended.Check()
        self._setWidebrimFramerate(1000)
        self.__refreshRomProperties()

    def __refreshRomProperties(self):
        self.romTextCode.SetValue(FileInterface.getRom().idCode.decode('ascii'))
        self.romTextName.SetValue(getNameStringFromRom(FileInterface.getRom(), FileInterface.getLanguage()))
        bannerImage = getBannerImageFromRom(FileInterface.getRom())
        bitmapBanner = Bitmap.FromBuffer(bannerImage.size[0], bannerImage.size[1], bannerImage.convert("RGB").tobytes("raw", "RGB"))
        self.previewIcon.SetBitmap(bitmapBanner)
        self.SetIcon(Icon(bitmapBanner))

    def spawnHandler(self, gamemode):
        # Acquire all resources to make sure that widebrim is not operating at all on anything when we tell it to change states
        # Prevents breaking everything
        self.__widebrimStateLock.acquire()
        self.__widebrimDrawLock.acquire()
        self._widebrimState.setGameMode(gamemode)
        self.__widebrimRenderLayers = ScreenCollectionGameModeSpawner(self._widebrimState)
        self.__widebrimDrawLock.release()
        self.__widebrimStateLock.release()
    
    def forceSyncOnButtonClick(self, event):
        page = self.auiTabs.GetCurrentPage()
        print("CALLED SYNC")
        try:
            page.syncChanges()
        except AttributeError as e:
            print("WARNING: Page probably doesn't have syncChange method...")
            print_exc()
        
        return super().forceSyncOnButtonClick(event)

    def __ensureProgressSaved(self):
        pass

    def __doOnClose(self, event):
        # Stop the timer to prevent widebrim being updated
        self.__widebrimTimer.Stop()
        # Allow thread to terminate on its own
        while self.__widebrimIsBusy:
            sleep(0.5)
        event.Skip()

    def _setWidebrimFramerate(self, fps):
        if 0 < fps <= 1000:
            self.__widebrimTimer.Stop()
            self.__widebrimLastUpdateTime = perf_counter()
            self.__widebrimTimer.Start(1000//fps, False)
            return True
        return False

    def _setWidebrimSpeedMultipler(self, multiplier):
        if multiplier > 0:
            self.__widebrimSpeedMultipler = multiplier
            return True
        return False

    def __drawWidebrim(self, dc):
        pos = self.__widebrimAnchor.GetPosition()
        self.__widebrimDrawLock.acquire()
        s = pygame.image.tostring(self.__widebrimRenderSurface, 'RGB')                             # Convert surface to raw image
        self.__widebrimDrawLock.release()
        img = WxImageNonConflict(self.__widebrimRenderSurface.get_width(), self.__widebrimRenderSurface.get_height(), s)  # Load image into wx
        bmp = Bitmap(img)                                                           # Convert image to bitmap
        dc.DrawBitmap(bmp, pos.x, pos.y, False)                                                # Draw bitmap over embedded zone
        del dc

    def __repaintWidebrim(self, event):
        self.__drawWidebrim(PaintDC(self))
        event.Skip()

    def __updateWidebrim(self, event):

        def redraw():
            self.__drawWidebrim(ClientDC(self))

        def updateWidebrimState():
            if self.__widebrimRenderLayers != None:
                self.__widebrimStateLock.acquire()
                elapsed = perf_counter() - self.__widebrimLastUpdateTime
                try:
                    self.__widebrimRenderLayers.update(elapsed * 1000 * self.__widebrimSpeedMultipler)
                except Exception as e:
                    print("Error occured during widebrim update!")
                    print("\tThis is usually recoverable; to prevent the GUI from crashing, we will continue.")
                    print_exc()
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN:
                        self.__widebrimRenderLayers.handleTouchEvent(event)

                self.__widebrimLastUpdateTime = perf_counter()
                self.__widebrimStateLock.release()
            
            if self.__widebrimRenderLayers != None:
                self.__widebrimDrawLock.acquire()
                self.__widebrimRenderLayers.draw(self.__widebrimRenderSurface)
                self.__widebrimDrawLock.release()
            
            CallAfter(redraw)
            self.__widebrimIsBusy = False
        
        # Don't spawn multiple update threads
        if self.__widebrimIsBusy == False:
            self.__widebrimIsBusy = True
            widebrimUpdateThread = Thread(target=updateWidebrimState)
            widebrimUpdateThread.start()

        event.Skip()
    
    def widebrimButtonRestartStateOnButtonClick(self, event):
        page = self.auiTabs.GetCurrentPage()
        if type(page) == FramePuzzleEditor or type(page) == FrameScriptEditor:
            self.spawnHandler(page.prepareWidebrimState())
        return super().widebrimButtonRestartStateOnButtonClick(event)

    def auiTabsOnAuiNotebookPageClose(self, event):
        indexPage = event.GetSelection()
        page = self.auiTabs.GetPage(indexPage)
        if type(page) == FrameOverview:
            event.Veto()
        else:
            event.Skip()
        return super().auiTabsOnAuiNotebookPageClose(event)

    def auiTabsOnAuiNotebookPageChanged(self, event):
        # TODO - don't know what wx is doing but its causing state to be refreshed multiple times which slows everything down
        # TODO - Change this, multiple pages can cause bugs (close one, previous may not update)
        page = self.auiTabs.GetCurrentPage()
        page.ensureLoaded()

        # Disable close on overview
        if type(page) == FrameOverview:
            self.auiTabs.SetWindowStyle(self.auiTabs.GetWindowStyle() & ~aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
        else:
            self.auiTabs.SetWindowStyle(self.auiTabs.GetWindowStyle() | aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)

        if type(page) == FramePuzzleEditor or type(page) == FrameScriptEditor:
            # TODO - Not thread safe
            self.spawnHandler(page.prepareWidebrimState())
        event.Skip()
    
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
    
    def framesExtendedOnMenuSelection(self, event):
        # This seems crazy but the timer seems to be VSync restricted anyway
        self._setWidebrimFramerate(1000)
        return super().framesExtendedOnMenuSelection(event)
    
    def menuPrefOverviewEnableEvtInfOnMenuSelection(self, event):
        self.auiTabs.GetPage(0).setCommentStatus(self.menuPrefOverviewEnableEvtInf.IsChecked())
        return super().menuPrefOverviewEnableEvtInfOnMenuSelection(event)

    def submenuFileReturnToStartupOnMenuSelection(self, event):
        CallAfter(self.__callbackAfterExit)
        return super().submenuFileReturnToStartupOnMenuSelection(event)

    # TODO - Pause, play, return to startup
    def submenuEnginePauseOnMenuSelection(self, event):
        return super().submenuEnginePauseOnMenuSelection(event)

    def widebrimButtonPausePlayOnButtonClick(self, event):
        return super().widebrimButtonPausePlayOnButtonClick(event)