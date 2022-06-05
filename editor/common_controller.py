from typing import Optional
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer

class GuiCommon():
    def __init__(self):
        self.fileAccessor : Optional[WriteableFilesystemCompatibilityLayer] = None
        self.bankInstructions = None
    
    def getAbstractionLevel(self):
        pass

    def isRunningFromFused(self):
        pass

    def pauseWidebrim(self):
        pass

    def resetWidebrim(self):
        pass

    def triggerSync(self):
        pass

    def stopWidebrim(self):
        pass

    def startWidebrim(self):
        pass