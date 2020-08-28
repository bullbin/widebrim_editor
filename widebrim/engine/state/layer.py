# TODO : Switch this around...
# Layers will need a blocking system to ensure certain events do not happen during a fading operation.
# For example, a script needs to stop execution during fading to prevent things from happening too soon
# This means also exposing a method to reveal if fading is occuring.
# Additionally at some point it would be good to support dirty rendering

class ScreenLayer():
    def __init__(self):
        self._canBeKilled = False
    
    def getContextState(self):
        return self._canBeKilled
    
    def doOnKill(self):
        self._canBeKilled = True

    def draw(self, gameDisplay):
        pass
    
    def handleKeyboardEvent(self, event):
        # Return True if the event was absorbed
        return False

    def handleTouchEvent(self, event):
        # Return True if the event was absorbed
        return False

class ScreenLayerBlocking(ScreenLayer):
    def __init__(self):
        ScreenLayer.__init__(self)
    
    def updateBlocked(self, gameClockDelta):
        pass

    def updateNonBlocked(self, gameClockDelta):
        pass

class ScreenLayerNonBlocking(ScreenLayer):
    def __init__(self):
        ScreenLayer.__init__(self)
    
    def update(self, gameClockDelta):
        pass

class ScreenCollection(ScreenLayer):
    def __init__(self):
        ScreenLayer.__init__(self)
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
                return True
        return False
    
    def handleTouchEvent(self, event):
        for indexLayer in range(len(self._layers) - 1, -1, -1):
            if self._layers[indexLayer].handleTouchEvent(event):
                return True
        return False

class ScreenCollectionBlocking(ScreenCollection):
    def __init__(self):
        ScreenCollection.__init__(self)
    
    def isUpdateBlocked(self):
        return False
    
    def update(self, gameClockDelta):

        if self.isUpdateBlocked():
            def updateLayer(inLayer):
                inLayer.updateBlocked(gameClockDelta)
        else:
            def updateLayer(inLayer):
                inLayer.updateNonBlocked(gameClockDelta)

        for indexLayer in range(len(self._layers) - 1, -1, -1):
            layer = self._layers[indexLayer]
            updateLayer(layer)
            if layer.getContextState():
                self.removeFromCollection(indexLayer)