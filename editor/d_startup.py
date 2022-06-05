from typing import Dict, Optional, Union

from widebrim.filesystem.compatibility import WriteableFusedFileInterface
from widebrim.filesystem.compatibility.compatibilityRom import WriteableRomFileInterface
from .nopush_editor import StartupConfiguration
from wx import FileDialog, FD_OPEN, FD_FILE_MUST_EXIST, DirDialog, ID_CANCEL, ID_OK, MessageDialog, ICON_ERROR, OK
from ndspy import rom
from widebrim.engine_ext.rom.banner import getNameStringFromRom
from widebrim.engine.const import LANGUAGES
from os import listdir

# TODO - rewrite this!!

class DialogStartup(StartupConfiguration):
    def __init__(self, parent, configuration : Dict[str, Union[str, bool]], callbackReturnFs):
        super().__init__(parent)

        self.__stringCreateLoadedVfs = self.btnCreateNew.GetLabel()
        self.__stringCreateLoaded = "Edit loaded ROM"

        self.__configuration = configuration
        self.__controlsDisabled = False
        self.__rom = None
        self.__romPath = self.__configuration["pathLastRom"]
        self.__pathPatch = self.__configuration["pathLastPatch"]
        self.__callbackReturnFs = callbackReturnFs
        self.useVfs.SetValue(self.__configuration["useVfs"])

        def getLastLoadedRom():
            if self.__configuration["pathLastRom"] != "":
                self.__verifyAndLoadRom(self.__configuration["pathLastRom"])
            else:
                self.__verifyAndLoadRom(None)
        
        self.reopenOnBoot.SetValue(self.__configuration["autoloadLast"])
        getLastLoadedRom()
        self.__updateVfsTooltip()
 
    def __updateVfsTooltip(self):
        if self.useVfs.IsChecked():
            self.btnCreateNew.SetLabel(self.__stringCreateLoadedVfs)
        else:
            self.btnCreateNew.SetLabel(self.__stringCreateLoaded)

    def __disableRomControls(self):
        self.__controlsDisabled = True
        self.textRomName.Disable()
        self.btnCreateEmpty.Disable()
        self.btnReopenLast.Disable()
        self.btnOpenFolder.Disable()
        self.btnCreateNew.Disable()
    
    def __enableRomControls(self):
        self.__controlsDisabled = False
        self.textRomName.Enable()
        self.btnCreateEmpty.Enable()

        # TODO - Handle last properly (tampered FS?)
        if self.__configuration["pathLastPatch"] != "" and self.__configuration["useVfs"]:
            self.btnReopenLast.Enable()
        if self.__configuration["useVfs"]:
            self.btnOpenFolder.Enable()

        self.btnCreateNew.Enable()
    
    def __updateConfigurationState(self):
        self.__configuration["useVfs"] = self.useVfs.IsChecked()
        self.__configuration["autoloadLast"] = self.reopenOnBoot.IsChecked()
        self.__configuration["pathLastRom"] = self.__romPath
        self.__configuration["pathLastPatch"] = self.__pathPatch

    def __verifyAndLoadRom(self, pathRom : Optional[str]):
        # TODO - Create widebrim system to do this
        self.__disableRomControls()
        updateRom = False
        if pathRom != None:
            try:
                ndsRom = rom.NintendoDSRom.fromFile(pathRom)
                if ndsRom.name == b'LAYTON2':
                    self.__rom = ndsRom
                    updateRom = True
                else:
                    MessageDialog(self, "Loading failed - ROM did not have required LAYTON2 ID.", "ROM Loading Error", OK | ICON_ERROR).ShowModal()

            except:
                MessageDialog(self, "Loading failed - ROM could not be loaded.", "ROM Loading Error", OK | ICON_ERROR).ShowModal()
        else:
            updateRom = True
            
        # TODO - Extract icon, language
        if self.__rom == None:
            # TODO - Remove icon?
            self.textRomName.SetLabel("No ROM loaded...")
        else:
            self.__romPath = pathRom
            self.__configuration["pathLastRom"] = self.__romPath
            self.__enableRomControls()
            if updateRom:
                self.textRomName.SetLabel(" ".join(getNameStringFromRom(self.__rom, LANGUAGES.English).split("\n")))

    def useVfsOnCheckBox(self, event):
        self.__configuration["useVfs"] = self.useVfs.IsChecked()
        self.__updateVfsTooltip()
        if not(self.__controlsDisabled):
            self.__disableRomControls()
            self.__enableRomControls()
        return super().useVfsOnCheckBox(event)

    def btnCreateEmptyOnButtonClick(self, event):
        return super().btnCreateEmptyOnButtonClick(event)
    
    def reopenOnBootOnCheckBox(self, event):
        self.__configuration["autoloadLast"] = self.reopenOnBoot.IsChecked()
        return super().reopenOnBootOnCheckBox(event)

    def btnCreateNewOnButtonClick(self, event):
        if self.__configuration["useVfs"]:
            outPath = None
            with DirDialog(self, "Open Empty Patch Folder") as emptyFolder:
                if emptyFolder.ShowModal() != ID_CANCEL:
                    outPath = emptyFolder.GetPath()

            if outPath == None or self.__rom == None:
                return super().btnCreateNewOnButtonClick(event)

            if len(listdir(outPath)) > 0:
                # TODO - yes no
                # Folder isn't empty, might be bad
                pass

            if self.IsModal():
                self.__pathPatch = outPath
                self.__updateConfigurationState()
                self.__callbackReturnFs(WriteableFusedFileInterface(self.__rom, outPath, True))
                self.EndModal(ID_OK)
            else:
                self.Close()
        else:
            if self.IsModal():
                self.__updateConfigurationState()
                self.__callbackReturnFs(WriteableRomFileInterface(self.__rom))
                self.EndModal(ID_OK)
            else:
                self.Close()
        return super().btnCreateNewOnButtonClick(event)
    
    def btnOpenFolderOnButtonClick(self, event):
        outPath = None
        with DirDialog(self, "Open Patch Root Folder") as emptyFolder:
            if emptyFolder.ShowModal() != ID_CANCEL:
                outPath = emptyFolder.GetPath()

        if outPath == None or self.__rom == None:
            return super().btnOpenFolderOnButtonClick(event)

        if len(listdir(outPath)) == 0:
            MessageDialog(self, "Loading failed - Folder did not have any contents.", "Patch Loading Error", OK | ICON_ERROR).ShowModal()
            # TODO - generate new
            # TODO - can we validate the FS?
            # TODO - method to fill missing files...?
            return super().btnOpenFolderOnButtonClick(event)

        if self.IsModal():
            self.__pathPatch = outPath
            self.__updateConfigurationState()
            self.__callbackReturnFs(WriteableFusedFileInterface(self.__rom, outPath, False))
            self.EndModal(ID_OK)
        else:
            self.Close()
        return super().btnOpenFolderOnButtonClick(event)
    
    def btnReopenLastOnButtonClick(self, event):
        # TODO - assumes this will be ok
        self.__pathPatch = self.__configuration["pathLastPatch"]
        if self.IsModal():
            self.__updateConfigurationState()
            self.__callbackReturnFs(WriteableFusedFileInterface(self.__rom, self.__pathPatch, False))
            self.EndModal(ID_OK)
        else:
            self.Close()
        return super().btnReopenLastOnButtonClick(event)
    
    def btnSetupRomOnButtonClick(self, event):
        with FileDialog(self, "Open NDS ROM...", wildcard="Nintendo DS ROM Files (.nds)|*.nds",
                        style=FD_OPEN | FD_FILE_MUST_EXIST) as romDialog:
            if romDialog.ShowModal() != ID_CANCEL:
                self.__verifyAndLoadRom(romDialog.GetPath())
        return super().btnSetupRomOnButtonClick(event)