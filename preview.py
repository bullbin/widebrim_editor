try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(0)
except ImportError:
    pass

from widebrim.madhatter import common

def noLog(*args, **kwargs):
    pass

common.log = noLog

from wx import App, CANCEL
from embed_mod import EditorWindow
from d_imp_back import DialogueImportBackground
import pygame

class App(App):
    def OnInit(self):
        self.frame = EditorWindow(parent = None)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

debug = App()
debug.MainLoop()

#testDialog = DialogueImportBackground(None)
#testDialog.ShowModal()
#testDialog.Destroy()


# TODO - Puzzle 24, wrong number of operations

pygame.quit()

# TODO - failure loading logo (oops) and broken border on title
# TODO - String validation
# TODO - Slashes not recognised
# TODO - Try/except to prevent loading bad data
# TODO - New patch format that combines nazo data and nazo list entry