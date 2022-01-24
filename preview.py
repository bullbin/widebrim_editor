from widebrim.madhatter import common

def noLog(*args, **kwargs):
    pass

common.log = noLog

from wx import App
from embed_mod import EditorWindow

class App(App):
    def OnInit(self):
        self.frame = EditorWindow(parent = None)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

debug = App()
debug.MainLoop()

# TODO - failure loading logo (oops) and broken border on title
# TODO - String validation
# TODO - Slashes not recognised
# TODO - Try/except to prevent loading bad data