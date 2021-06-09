from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from widebrim.engine.anim.font.staticFormatted import StaticTextHelper
from widebrim.madhatter.hat_io.asset_script import GdScript

from widebrim.engine_ext.const import PATH_TEMP
from widebrim.engine.state.enum_mode import GAMEMODES
from widebrim.engine.file import FileInterface
from widebrim.engine.const import PATH_PACK_TXT, RESOLUTION_NINTENDO_DS
from widebrim.engine_ext.utils import decodeArchiveString, ensureTempFolder, getPackedData
from widebrim.gamemodes.core_popup.script import ScriptPlayer

from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2

from subprocess import Popen, PIPE
from pygame import Surface
from pygame.image import frombuffer
from .const import *
from os import remove

if TYPE_CHECKING:
    from widebrim.engine.state.state import Layton2GameState
    from widebrim.engine_ext.state_game import ScreenController

# Thank you FFMPEG team for supporting mobiclip! 4.4 minimum req.

# TODO - Implement skip
# TODO - Implement drawable
class MovieSurface():
    def __init__(self, indexMovie : int, callback : Optional[callable], framerate : float = 23.98):
        # TODO - 256x192 is stored in file too, but what about modifications? SDK lib should handle it fine so we should ffprobe the data out first

        # Calculate size of raw frame
        self.__bufferSize       = RESOLUTION_NINTENDO_DS[0] * RESOLUTION_NINTENDO_DS[1] * 3
        self.__pathMovieFile    = None
        self.__surfVideo    :   Surface  = Surface(RESOLUTION_NINTENDO_DS)
        self.__procConv     :   Optional[Popen] = None
        self.__pos              = (0,RESOLUTION_NINTENDO_DS[1])
        self.__timeElapsed  :   float = 0
        self.__timeFrame        = 1000 / framerate
        self.__callback         = callback

        # Credit to https://stackoverflow.com/a/62870947 for the command used in this process

        if ensureTempFolder():
            if ((movieData := FileInterface.getData(PATH_MOBICLIP_MOVIE % indexMovie)) != None):
                try:
                    with open(PATH_TEMP + "//" + PATH_TEMP_MOVIE_FILE, 'wb') as movieTemp:
                        movieTemp.write(movieData)
                        # TODO - Writes empty even if not found...
                        self.__pathMovieFile = PATH_TEMP + "//" + PATH_TEMP_MOVIE_FILE
                    
                    # TODO - Switch to python ffmpeg for platform agnostic ffmpeg
                    command = [ "ffmpeg",
                                '-loglevel', 'quiet',
                                '-i', self.__pathMovieFile,
                                # Mobiclip decoder doesn't deswizzle correctly...
                                '-filter_complex', 'colorchannelmixer=1:0:0:0:0:0:1:0:0:1:0:0:0:0:0:1', 
                                '-f', 'image2pipe',
                                '-s', '%dx%d' % RESOLUTION_NINTENDO_DS,
                                '-pix_fmt', 'rgb24',
                                '-vcodec', 'rawvideo',
                                '-' ]
                    
                    self.__procConv = Popen(command, stdout=PIPE, bufsize=self.__bufferSize * COUNT_BUFFER_FRAMES)
                        
                except:
                    pass

        if self.__procConv == None:
            self.cleanup()

    def setPos(self, pos):
        # TODO - Validate
        self.__pos = pos
    
    def getPos(self):
        return self.__pos

    def canStart(self) -> bool:
        return self.__procConv != None

    def cleanup(self):
        if self.__procConv != None:
            self.__procConv.stdout.close()
            self.__procConv.terminate()
            self.__procConv.wait()
            self.__procConv = None
            try:
                remove(self.__pathMovieFile)
            except:
                pass

            if callable(self.__callback):
                self.__callback()
                self.__callback = None

    def update(self, gameClockDelta):
        if self.__procConv != None:
            self.__timeElapsed += gameClockDelta
            while self.__timeElapsed >= self.__timeFrame:
                try:
                    self.__surfVideo = frombuffer(self.__procConv.stdout.read(self.__bufferSize), (self.__surfVideo.get_width(), self.__surfVideo.get_height()), 'RGB')
                    self.__timeElapsed -= self.__timeFrame
                except:
                    # Buffer underrun. Can happen for variety of reasons. We want a frame but its not ready yet
                    if self.__procConv.poll() != None:
                        # ffmpeg has finished. Video either errored or has finished playing. Since buffer is empty, we can terminate early
                        self.cleanup()
                        break
                    else:
                        # Flush just in case...
                        self.__procConv.stdout.flush()
    
    def draw(self, gameDisplay):
        gameDisplay.blit(self.__surfVideo, self.__pos)

class SubtitleCommand():
    def __init__(self, packSubtitle : LaytonPack, indexMovie : int, indexSubtitle : int, timeStart : float, timeEnd : float):
        self.text = decodeArchiveString(packSubtitle, PATH_TXT_SUBTITLE % (indexMovie, indexSubtitle))
        if self.text == None:
            self.text = ""
        self.timeStart = timeStart
        self.timeEnd = timeEnd

class MoviePlayer(ScriptPlayer):
    def __init__(self, laytonState : Layton2GameState, screenController : ScreenController):
        ScriptPlayer.__init__(self, laytonState, screenController, GdScript())

        if (scriptData := getPackedData(PATH_ARCHIVE_MOVIE_SUBTITLES.replace("?", laytonState.language.value), PATH_NAME_SUBTITLE_SCRIPT % laytonState.getMovieNum())) != None:
            self._script.load(scriptData)
        else:
            self.doOnComplete()

        self.__packTxt : LaytonPack = LaytonPack()
        if (packData := FileInterface.getData(PATH_PACK_TXT % laytonState.language.value)) != None:
            self.__packTxt.load(packData)

        self.__surfaceMovie = MovieSurface(laytonState.getMovieNum(), self.__fadeOutAndTerminate)
        self.__indexActiveSubtitle = -1
        self.__waitingForNextSubtitle = False
        self.__textRendererSubtitle = StaticTextHelper(laytonState.fontEvent, yBias=2)
        self.__textRendererSubtitle.setColor((255,255,255))
        self.__textRendererSubtitle.setPos((RESOLUTION_NINTENDO_DS[0] // 2, RESOLUTION_NINTENDO_DS[1] + 177))
        self.__timeElapsedSeconds = 0
        self.__subtitles : List[SubtitleCommand] = []
    
    def __updateRenderedSubtitle(self):

        def getNextSubtitle():
            # TODO - While loop to eliminate without rendering text if decoding is SEVERELY behind (this maxes at 1 subtitle per frame)
            nextSubIndex = self.__indexActiveSubtitle + 1
            if nextSubIndex < len(self.__subtitles) and self.__subtitles[nextSubIndex].timeStart <= self.__timeElapsedSeconds and self.__subtitles[nextSubIndex].timeEnd > self.__timeElapsedSeconds:
                self.__textRendererSubtitle.setText(self.__subtitles[nextSubIndex].text)
                self.__waitingForNextSubtitle = False
                self.__indexActiveSubtitle = nextSubIndex

        if self.__indexActiveSubtitle != -1:
            # If a subtitle is valid and loaded
            if self.__waitingForNextSubtitle:
                getNextSubtitle()
            else:
                if self.__subtitles[self.__indexActiveSubtitle].timeEnd < self.__timeElapsedSeconds:
                    self.__textRendererSubtitle.setText("")
                    self.__waitingForNextSubtitle = True

        if self.__indexActiveSubtitle == -1 and len(self.__subtitles) != 0:
            getNextSubtitle()

    # TODO - Draw and update returns
    def __drawOnScriptComplete(self, gameDisplay):
        self.__surfaceMovie.draw(gameDisplay)
        self.__textRendererSubtitle.drawXYCenterPointNoBias(gameDisplay)
    
    def __updateOnScriptComplete(self, gameClockDelta):
        self.__timeElapsedSeconds += gameClockDelta / 1000
        self.__updateRenderedSubtitle()
        self.__surfaceMovie.update(gameClockDelta)
    
    def doOnKill(self):
        if self.laytonState.isInMovieMode:
            self.laytonState.setGameMode(GAMEMODES.MovieViewMode)
        else:
            self.laytonState.setGameMode(self.laytonState.getGameModeNext())
        return super().doOnKill()

    def __fadeOutAndTerminate(self):
        self.screenController.fadeOutMain(callback=self.doOnKill)

    def _doUnpackedCommand(self, opcode, operands):
        if opcode == OPCODES_LT2.SetSubTitle.value and len(operands) == 3:
            if len(self.__subtitles) < COUNT_MAX_SUBTITLES:
                self.__subtitles.append(SubtitleCommand(self.__packTxt, self.laytonState.getMovieNum(), operands[0].value, operands[1].value, operands[2].value))
            else:
                print("MOVIE: Bad: Prevented overflow from excessive subtitles.")
            return True
        return super()._doUnpackedCommand(opcode, operands)

    def doOnComplete(self):
        self.update = self.__updateOnScriptComplete
        self.draw = self.__drawOnScriptComplete

        if self.__surfaceMovie.canStart():
            self.screenController.fadeInMain()
        else:
            self.__fadeOutAndTerminate()

    def doOnPygameQuit(self):
        self.__surfaceMovie.cleanup()
        return super().doOnPygameQuit()