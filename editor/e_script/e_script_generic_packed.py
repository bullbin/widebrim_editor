from editor.e_script.e_script_generic import FrameScriptEditor
from wx import Window
from editor.gui.command_annotator.bank import ScriptVerificationBank
from editor.gui.command_annotator.baselineAnnotationGenerator import BaselineVerificationBank

from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.madhatter.hat_io.asset_script import GdScript

class FrameScriptEditorPackedEvent(FrameScriptEditor):
    def __init__(self, parent: Window, state: Layton2GameState, bankInstructions: ScriptVerificationBank, pathPack : str, nameGds : str):
        self.__pathPack = pathPack
        self.__nameGds = nameGds
        script = GdScript()
        if (data := state.getFileAccessor().getPackedData(pathPack, nameGds)) != None:
            script.load(data)
        super().__init__(parent, state, bankInstructions, script)

class FrameScriptEditorPackedEventNoBank(FrameScriptEditorPackedEvent):
    def __init__(self, parent: Window, state: Layton2GameState, pathPack: str, nameGds: str):
        bankInstructions = BaselineVerificationBank(state.getFileAccessor())
        bankInstructions.applyDefaultInstructionHeuristics()
        bankInstructions.applyExtendedOperandTypingHeuristics()
        super().__init__(parent, state, bankInstructions, pathPack, nameGds)