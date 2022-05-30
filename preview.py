try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(0)
except ImportError:
    pass

from os import getcwd, path
from typing import Any, Dict, Optional, Union

from widebrim.madhatter import common

def noLog(*args, **kwargs):
    pass

common.logVerbose = noLog
common.log = noLog

from wx import App, ID_OK, ID_CANCEL
from editor.embed_mod import EditorWindow
from editor.d_firstrun import DialogFirstRunWarning
from editor.d_startup import DialogStartup

#from editor.d_imp_back import DialogueImportBackground
#from editor.d_pickerBgx import DialogPickerBgx
#from widebrim.engine.const import LANGUAGES
#from widebrim.engine.state.manager.state import Layton2GameState

from widebrim.filesystem.compatibility import FusedFileInterface
from widebrim.engine_ext.utils import cleanTempFolder
import pygame
from json import loads, dumps
from ndspy import rom

def getSettingsPath():
    return path.join(getcwd(), "nopush_settings.json")

def saveSettingsJson(settings : Dict[str, Union[bool, str]]) -> bool:
    try:
        with open(getSettingsPath(), "w+") as jsonOut:
            jsonOut.write(dumps(settings))
        return True
    except:
        return False

def loadSettingsJson() -> Dict[str, Union[bool, str]]:

    def getDefaultSettingsDict() -> Dict[str, Union[bool, str]]:
        return {"acceptEula":False,
                "autoloadLast":False,
                "pathLastRom":"",
                "pathLastPatch":""}

    def getOnDeviceDict() -> Dict[str, Any]:
        try:
            jsonString = ""
            with open(getSettingsPath(), 'r') as jsonDat:
                jsonString = jsonDat.read()
            return loads(jsonString)
        except IOError:
            return {}
        except:
            return {}
    
    settings = getDefaultSettingsDict()
    settingsChanges = getOnDeviceDict()
    for key in settings.keys():
        if key in settingsChanges:
            if type(settings[key]) == type(settingsChanges[key]):
                settings[key] = settingsChanges[key]
    # Does not account for ranges, but not a problem (yet)
    return settings

class App(App):
    def OnInit(self):
        self.__configuration = loadSettingsJson()
        self.__filesystem : Optional[FusedFileInterface] = None

        if not(self.__configuration["acceptEula"]):
            with DialogFirstRunWarning(None) as firstRun:
                if firstRun.ShowModal() == ID_OK:
                    self.__configuration["acceptEula"] = True
                    saveSettingsJson(self.__configuration)
            
        if self.__configuration["acceptEula"]:
            forceStartup = False
            if self.__configuration["autoloadLast"] and self.__configuration["pathLastPatch"] != "" and self.__configuration["pathLastRom"] != None:
                try:
                    romData = rom.NintendoDSRom.fromFile(self.__configuration["pathLastRom"])
                    self.__filesystem = FusedFileInterface(romData, self.__configuration["pathLastPatch"], False)
                except:
                    forceStartup = True

            if not(self.__configuration["autoloadLast"] and self.__configuration["pathLastPatch"] != "" and self.__configuration["pathLastRom"] != None) or forceStartup:
                with DialogStartup(None, self.__configuration, self.__setFilesystem) as startup:
                    if startup.ShowModal() == ID_CANCEL:
                        self.__filesystem = None
        
        if self.__filesystem != None:
            self.frame = EditorWindow(self.__filesystem, self.__triggerReturnOnClose, parent = None)
            self.frame.Show()
            self.SetTopWindow(self.frame)
        return True
    
    def __triggerReturnOnClose(self):
        self.frame.Close()
        with DialogStartup(None, self.__configuration, self.__setFilesystem) as startup:
            if startup.ShowModal() == ID_CANCEL:
                self.__filesystem = None
        
        if self.__filesystem != None:
            self.frame = EditorWindow(self.__filesystem, self.__triggerReturnOnClose, parent = None)
            self.frame.Show()
            self.SetTopWindow(self.frame)

    def __setFilesystem(self, fs : FusedFileInterface):
        self.__filesystem = fs
    
    def OnExit(self):
        saveSettingsJson(self.__configuration)
        return super().OnExit()

debug = App()
debug.MainLoop()

#debugState = Layton2GameState(LANGUAGES.English, FusedFileInterface(rom.NintendoDSRom.fromFile("rom2.nds"), r"patch", False))
#testDialog = DialogPickerBgx(None, debugState, debugState.getFileAccessor(), "/data_lt2/bg")
#testDialog.ShowModal()
#testDialog.Destroy()
#print(testDialog.GetPath())

# TODO - Doctor's home chain?

# TODO - Puzzle 24, wrong number of operations
# TODO - widebrim cleanup

pygame.quit()
cleanTempFolder()

# TODO - failure loading logo (oops) and broken border on title
# TODO - String validation
# TODO - Slashes not recognised
# TODO - Try/except to prevent loading bad data
# TODO - New patch format that combines nazo data and nazo list entry
# TODO - how are slots drawn? by character order or slot order?
# TODO - event descriptions (unused db)
# TODO - cut puzzles are bad lol
# TODO - State not being cleared between puzzles (58, 59)


# FS Plans
# ani
#     exclude system, tobj, sub, subgame, title, menu