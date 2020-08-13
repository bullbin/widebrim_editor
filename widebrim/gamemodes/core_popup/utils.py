from ...engine.state.layer import ScreenLayerNonBlocking

class MainScreenPopup(ScreenLayerNonBlocking):
    def __init__(self, callbackOnTerminate):
        ScreenLayerNonBlocking.__init__(self)