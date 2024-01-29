from typing import Any, Optional, List
from editor.asset_management.string.talkscript import convertTalkStringToSegments, Segment
from widebrim.engine.anim.font.scrolling import ScrollingFontHelper
from widebrim.engine.anim.font.static import generateImageFromString
from widebrim.engine.const import RESOLUTION_NINTENDO_DS
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.madhatter.common import logSevere
from ..nopush_editor import EditTalkscript
from wx import Window, Bitmap, Timer, EVT_TIMER, EVT_CLOSE, ID_OK, ID_CANCEL

from pygame import Surface
from pygame.image import tostring

# TODO - This is a stopgap for functionality while something that can properly use the talkscript library is being crafted

class DialogTalkScriptTextEditor(EditTalkscript):
    def __init__(self, parent : Window, state : Layton2GameState, stringTalkscript : str = ""):
        super().__init__(parent)
        self._state : Layton2GameState = state
        self.__renderedValue : Optional[str] = None
        self.textRenderer = ScrollingFontHelper(state.fontEvent)
        self.surfPreview = Surface(RESOLUTION_NINTENDO_DS)
        self.surfPreview.fill((255,255,255))

        self.segments = convertTalkStringToSegments(stringTalkscript)
        self.tidyString = ""
        for segment in self.segments:
            self.tidyString += segment.getEncodedString()
        self.tidyString = "\n".join(self.tidyString.split("@B"))
        self.tidyString = "\n@p@c".join(self.tidyString.split("@p@c"))
        self.textCtrlTalkscript.SetValue(self.tidyString)
        
        self.__redrawPreview(None)
        
        self.__timerUpdate = Timer(self)
        self.Bind(EVT_TIMER, self.__redrawPreview, self.__timerUpdate)
        self.Bind(EVT_CLOSE, self.__onClose)

        self.__timerUpdate.Start(1000//60, False)

    def __onClose(self, event):
        self.__timerUpdate.Stop()
        event.Skip()
    
    def btnCancelOnButtonClick(self, event):
        self.__timerUpdate.Stop()
        self.EndModal(ID_CANCEL)
        return super().btnCancelOnButtonClick(event)
    
    def btnConfirmOnButtonClick(self, event):
        self.__timerUpdate.Stop()
        self.EndModal(ID_OK)
        return super().btnConfirmOnButtonClick(event)

    def GetValue(self) -> str:
        encoded : str = self.textCtrlTalkscript.GetValue()
        encoded = encoded.replace("\n@p@c", "@p@c")
        encoded = encoded.replace("\n", "@B")
        segments = convertTalkStringToSegments(encoded)
        output = ""
        for segment in segments:
            output += segment.getEncodedString()
        return output

    def __redrawPreview(self, event : Any):
        encoded = self.textCtrlTalkscript.GetValue()
        start = self.textCtrlTalkscript.GetInsertionPoint()
        if start >= len(encoded):
            start = len(encoded) - 1

        while start >= 0:
            if encoded[start] == "@":
                if (start + 1) < len(encoded):
                    if encoded[start + 1] == "c":
                        start = start + 2
                        break 
            start -= 1
        start = max(start, 0)
        
        end = self.textCtrlTalkscript.GetInsertionPoint()
        while end < len(encoded):
            if encoded[end] == "@":
                if (end + 1) < len(encoded):
                    if encoded[end + 1] == "c":
                        end = end
                        break
            end += 1
        
        end = min(len(encoded), end)
        selection = encoded[start:end].replace("\n@p@c", "@p@c")
        selection = selection.replace("\n", "@B")

        if self.__renderedValue != selection:
            self.__renderedValue = selection
            self.textRenderer.setText(selection)
            try:
                while self.textRenderer.getActiveState():
                    self.textRenderer.skip()
                    if self.textRenderer.isWaiting():
                        self.textRenderer.setTap()
            except IndexError:
                logSevere("TextScroller hit bad dialogue! Check for unclosed commands.", name="TalkScriptDlg")

            self.surfPreview.fill((255,255,255))
            self.textRenderer.draw(self.surfPreview)
            self.bitmapPreview.SetBitmap(Bitmap.FromBuffer(RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1], tostring(self.surfPreview, "RGB")))  
    
    def __getWrappedEquivalent(self, encoded : str) -> str:
        # Remove control characters from input

        MAX_LINE_WIDTH = 240

        segments = convertTalkStringToSegments(encoded)

        lineText : str = ""
        outputSegments : List[Segment] = []

        for segment in segments:
            outputSegments.append(Segment([]))
            outputSegments[-1].commandsAfterFinish = segment.commandsAfterFinish

            for line in segment.lines:
                lineText = ""

                # TODO - May not consider other languages!
                for token in line:
                    if type(token) == str:
                        newToken : Optional[str] = ""

                        for word in token.split(" "):
                            if len(lineText) == 0:
                                testLine : str = word
                            else:
                                testLine : str = lineText + " " + word

                            testSurface : Surface = generateImageFromString(self._state.fontEvent, testLine)
                            if testSurface.get_width() > MAX_LINE_WIDTH:
                                # Token cannot be added to this line, break here
                                if testLine == word:
                                    # If the word itself doesn't fit on the line
                                    newToken = word
                                
                                if len(outputSegments[-1].lines[-1]) == 0:
                                    outputSegments[-1].lines[-1].append(newToken)
                                else:
                                    outputSegments[-1].lines.append([newToken])

                                if testLine == word:
                                    newToken = ""
                                    lineText = ""
                                else:
                                    newToken = word
                                    lineText = word
                            else:
                                # Continue line (token)
                                if len(newToken) == 0:
                                    newToken = word
                                else:
                                    newToken += " " + word

                                lineText = testLine
                        
                        if newToken != "":
                            if len(outputSegments[-1].lines[-1]) == 0:
                                outputSegments[-1].lines[-1].append(newToken)
                            else:
                                outputSegments[-1].lines.append([newToken])
                    else:
                        outputSegments[-1].lines[-1].append(token)

        return outputSegments

    def btnApplyWrapOnButtonClick(self, event):
        encoded = self.textCtrlTalkscript.GetValue()
        encoded = encoded.replace("\n@p@c", "@p@c")
        encoded = encoded.replace("\n", "@B")

        wrapped : List[Segment] = self.__getWrappedEquivalent(encoded)
        self.tidyString = ""
        for segment in wrapped:
            self.tidyString += segment.getEncodedString()

        self.tidyString = "\n".join(self.tidyString.split("@B"))
        self.tidyString = "\n@p@c".join(self.tidyString.split("@p@c"))
        self.textCtrlTalkscript.SetValue(self.tidyString)

        self.__renderedValue = None
        self.__redrawPreview(None)

        return super().btnApplyWrapOnButtonClick(event)

    def textCtrlTalkscriptOnText(self, event):
        # TODO - Support continuous wrapping, need to add button to strip all line breaks
        self.__redrawPreview(None)
        return super().textCtrlTalkscriptOnText(event)