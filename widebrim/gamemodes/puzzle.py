from ..engine.state.layer import ScreenLayerNonBlocking
from ..engine.state.enum_mode import GAMEMODES
from .nazo_popup.intro import IntroLayer
from .nazo_popup.outro import OutroLayer
from .nazo_popup.mode import HandlerTile2, BaseQuestionObject, HandlerFreeButton, HandlerDivide, HandlerTouch, HandlerOnOff2, HandlerTraceButton

ID_TO_NAZO_HANDLER = {2:HandlerFreeButton,

                      3:"OnOff",
                      14:"OnOff",

                      5:HandlerTraceButton,

                      6:"TraceOnly",
                      34:"TraceOnly",

                      9:HandlerDivide,
                      15:HandlerDivide,

                      10:HandlerTouch,
                      11:"Tile",
                      13:"Pancake",

                      16:"DrawInput",
                      20:"DrawInput",
                      21:"DrawInput",
                      22:"DrawInput",
                      28:"DrawInput",
                      32:"DrawInput",
                      35:"DrawInput",

                      18:HandlerTile2,
                      26:HandlerTile2,
                      
                      17:"Knight",
                      23:HandlerOnOff2,
                      24:"Rose",
                      25:"Slide2",
                      27:"Skate",
                      29:"PegSolitaire",
                      30:"Couple",
                      31:"Lamp",
                      33:"Bridge"}

def getPuzzleHandler(laytonState, screenController, callbackOnTerminate):
    if laytonState.getNazoData() != None:
        try:
            handler = ID_TO_NAZO_HANDLER[laytonState.getNazoData().idHandler]
            if type(handler) != str:
                return handler(laytonState, screenController, callbackOnTerminate)
                handler = BaseQuestionObject(laytonState, screenController, callbackOnTerminate)
        except KeyError:
            pass
    return BaseQuestionObject(laytonState, screenController, callbackOnTerminate)

class PuzzlePlayer(ScreenLayerNonBlocking):
    def __init__(self, laytonState, screenController):
        ScreenLayerNonBlocking.__init__(self)
        self.laytonState = laytonState
        self.screenController = screenController
        self._popup = None

        # Use of bypass callbacks eventually causes stack depth error, so delay potential loops to next frame to allow stack to unroll.
        # This is mimicing a very long while loop in game which could potentially go on forever
        self._waitingToUnrollAndRestart = False

        # TODO - Triggers some sound to stop here
        activeNazoEntry = self.laytonState.getCurrentNazoListEntry()
        if activeNazoEntry != None:
            # TODO - This actually checks that the puzzle has nothing attached to it - no flags at all
            if not (self.laytonState.saveSlot.puzzleData.getPuzzleData(activeNazoEntry.idExternal - 1).wasEncountered):
                self.laytonState.saveSlot.puzzleData.getPuzzleData(activeNazoEntry.idExternal - 1).wasEncountered = True

        self.laytonState.wasPuzzleSkipped = False
        if self.laytonState.loadCurrentNazoData():
            # Do intro screen and start loading chain
            print("Puzzle player was spawned, handler", self.laytonState.getNazoData().idHandler)
            self.__callbackSpawnPuzzleIntro()
        else:
            # I think this will cause a softlock. Bypass potentially required (switch to next gamemode?)
            # TODO - Check the nazo data grabbing function for what it does under failure condition
            #        Checked, initial loading never checks for nazo script. Only grabbed in base object.
            self.doOnKill()
    
    def update(self, gameClockDelta):
        if self._waitingToUnrollAndRestart:
            self._waitingToUnrollAndRestart = False
            self.__callbackSpawnPuzzleIntro()
        if self._popup != None:
            self._popup.update(gameClockDelta)
    
    def draw(self, gameDisplay):
        if self._popup != None:
            self._popup.draw(gameDisplay)
    
    def handleTouchEvent(self, event):
        if self._popup != None:
            return self._popup.handleTouchEvent(event)
        return super().handleTouchEvent(event)

    def __callbackSpawnPuzzleIntro(self):
        self._popup = IntroLayer(self.laytonState, self.screenController, self.__callbackSpawnPuzzleObject)

    def __callbackSpawnPuzzleObject(self):
        # This should change the popup to a puzzle popup, but currently bypass to spawn end popup.
        self.laytonState.saveSlot.puzzleData.getPuzzleData(self.laytonState.getCurrentNazoListEntry().idExternal - 1).wasSolved = True     # Hack
        self._popup = getPuzzleHandler(self.laytonState, self.screenController, self.__callbackOnPuzzleEnd)
        # self.__callbackOnPuzzleEnd()

    def __callbackOnPuzzleEnd(self):
        # If user tried to solved puzzle, display outro layer.
        if not(self.laytonState.wasPuzzleSkipped):
            self._popup = OutroLayer(self.laytonState, self.screenController, None)
            # Callbacks can't be called during init, or very bad things happen
            self.__callbackOnTerminateMode()
        else:
            self.__callbackOnTerminateMode()

    def __callbackOnTerminateMode(self):
        self._popup = None
        # TODO - One more unknown condition
        if self.laytonState.wasPuzzleSkipped or True:
            self.laytonState.setGameMode(self.laytonState.getGameModeNext()) # Usually EndPuzzle
            self.laytonState.unloadCurrentNazoData()
            
            if self.laytonState.getGameMode() == GAMEMODES.Nazoba:
                # TODO - Again only checks flag for value of 2... how does nazoba flag work here?
                if self.laytonState.saveSlot.puzzleData.getPuzzleData(self.laytonState.getCurrentNazoListEntry().idExternal - 1).wasSolved:

                    # TODO - Make const, actually play the event. Nazoba mode is already set but this triggers the reward popups if they were required.
                    self.laytonState.setEventId(18000)
                    # TODO - There's one more check about the game being complete so another event can be played

            self.doOnKill()
        else:
            self._waitingToUnrollAndRestart = True