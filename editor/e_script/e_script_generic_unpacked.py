from editor.e_script.e_script_generic import FrameScriptEditor
from wx import Window
from editor.bank.command_annotator.bank import ScriptVerificationBank

from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.common import logSevere
from widebrim.madhatter.hat_io.asset_script import GdScript

class FrameScriptEditorUnpackedEvent(FrameScriptEditor):
    def __init__(self, parent: Window, state: Layton2GameState, bankInstructions: ScriptVerificationBank, pathGds : str):
        self.__pathGds = pathGds
        script = GdScript()
        if state.getFileAccessor().doesFileExist(pathGds):
            script.load(state.getFileAccessor().getData(pathGds))
        super().__init__(parent, state, bankInstructions, script)
    
    def syncChanges(self):
        self._eventScript.save()
        fs : WriteableFilesystemCompatibilityLayer = self._state.getFileAccessor()
        if not(fs.writeableFs.addFile(self.__pathGds, self._eventScript.data)):
            logSevere("Failed to save event script!", name="ScriptEditUC")