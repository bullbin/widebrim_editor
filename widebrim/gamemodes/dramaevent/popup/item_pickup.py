from .utils import FadingPopup

class ItemPopup(FadingPopup):
    def __init__(self, laytonState, screenController, itemIndex):
        # prizewindow2
        # item_icon (anim is itemIndex + 1)
        # cursorWait

        # It might be time to invest in sharing these assets, like the game does.
        screenController.fadeInMain()

