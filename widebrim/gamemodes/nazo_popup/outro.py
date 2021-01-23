from ..core_popup.utils import FullScreenPopup

# Bypass outro since its not important yet
class OutroLayer(FullScreenPopup):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        FullScreenPopup.__init__(self, callbackOnTerminate)
        print("Spawned outro!")
