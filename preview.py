from os import getcwd, path
import sys

# Credit - https://stackoverflow.com/questions/50843845/git-submodule-import-statements-failing/73885828#73885828
# This is disgusting and bad! I love the idea of submodules but this is not it
# To fix linting, you will need to add the widebrim submodule folder - sorry
submodule_name = 'widebrim'
(parent_folder_path, current_dir) = path.split(path.dirname(__file__))
sys.path.append(path.join(parent_folder_path, submodule_name))

try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(0)
except ImportError:
    pass

from typing import Any, Dict, Optional, Union
from widebrim.madhatter.common import NamedLogger

NamedLogger.SHOW_UNIMPORTANT = False
NamedLogger.SHOW_IMPORTANT = True

from wx import App, ID_OK, ID_CANCEL
from editor.embed_mod import EditorWindow
from editor.d_firstrun import DialogFirstRunWarning
from editor.d_startup import DialogStartup

from filesystem.compatibility import WriteableFusedFileInterface
from filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from filesystem.compatibility.compatibilityRom import WriteableRomFileInterface
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
                "useVfs":False,
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

class WidebrimEditor(App):
    def OnInit(self):
        self.__configuration = loadSettingsJson()
        self.__filesystem : Optional[WriteableFilesystemCompatibilityLayer] = None

        if not(self.__configuration["acceptEula"]):
            with DialogFirstRunWarning(None) as firstRun:
                if firstRun.ShowModal() == ID_OK:
                    self.__configuration["acceptEula"] = True
                    saveSettingsJson(self.__configuration)
            
        if self.__configuration["acceptEula"]:
            if self.__configuration["autoloadLast"] and self.__configuration["pathLastRom"] != "":
                try:
                    romData = rom.NintendoDSRom.fromFile(self.__configuration["pathLastRom"])
                    if not(self.__configuration["useVfs"]):
                        self.__setFilesystem(WriteableRomFileInterface(romData))
                    elif self.__configuration["pathLastPatch"] != "":
                        self.__setFilesystem(WriteableFusedFileInterface(romData, self.__configuration["pathLastPatch"], False))
                except:
                    pass
            
            if self.__filesystem == None:
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

    def __setFilesystem(self, fs : WriteableFilesystemCompatibilityLayer):
        self.__filesystem = fs
    
    def OnExit(self):
        saveSettingsJson(self.__configuration)
        return super().OnExit()

debug = WidebrimEditor()
debug.MainLoop()

pygame.quit()
cleanTempFolder()