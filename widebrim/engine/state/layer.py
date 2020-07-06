class ScreenLayer():
    def __init__(self):
        self.canBeKilled        = False
    
    def getContextState(self):
        return self.canBeKilled
    
    def draw(self, gameDisplay):
        pass

    def update(self, gameClockDelta):
        pass
    
    def handleKeyboardEvent(self, event):
        # Return True if the event was absorbed
        return False

    def handleTouchEvent(self, event):
        # Return True if the event was absorbed
        pass

class ScreenCollection():
    def __init__(self):
        self._layers = []

    def addToCollection(self, screenObject):
        self._layers.append(screenObject)
    
    def removeFromCollection(self, index):
        if 0 <= index < len(self._layers):
            self._layers.pop(index)
            return True
        return False
    
    def draw(self, gameDisplay):
        for layer in self._layers:
            layer.draw(gameDisplay)
        
    def update(self, gameClockDelta):
        for indexLayer in range(len(self._layers) - 1, -1, -1):
            layer = self._layers[indexLayer]
            layer.update(gameClockDelta)
            if layer.getContextState():
                self.removeFromCollection(indexLayer)
    
    def handleKeyboardEvent(self, event):
        for indexLayer in range(len(self._layers) - 1, -1, -1):
            if self._layers[indexLayer].handleKeyboardEvent(event):
                break
    
    def handleTouchEvent(self, event):
        for indexLayer in range(len(self._layers) - 1, -1, -1):
            if self._layers[indexLayer].handleTouchEvent(event):
                break