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
from editor.embed_mod import EditorWindow
from editor.d_imp_back import DialogueImportBackground
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
# TODO - Doctor's home chain?

# TODO - Puzzle 24, wrong number of operations
# TODO - widebrim cleanup

pygame.quit()

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