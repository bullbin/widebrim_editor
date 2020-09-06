from ..core_popup.utils import FullScreenPopup

# Bypass intro since its not important yet
class IntroLayer(FullScreenPopup):
    def __init__(self, laytonState, screenController, callbackOnTerminate):
        FullScreenPopup.__init__(self, callbackOnTerminate)
        print("Spawned intro!")

        if callable(callbackOnTerminate):
            callbackOnTerminate()