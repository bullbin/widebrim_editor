from editor.nopush_editor import EditTalkscriptRich
from widebrim.engine.state.manager import Layton2GameState
from widebrim.engine.anim.font.const import BLEND_MAP
from widebrim.engine.anim.font.static import generateImageFromString
from typing import Optional, List, Dict, Tuple
from wx import Window, Image, Bitmap
from wx.richtext import RichTextImage, RichTextBuffer, RichTextParagraph, RichTextPlainText, RichTextRange
from pygame import Surface, BLEND_SUB, BLEND_ADD, Rect
from pygame.image import tostring
from pygame.draw import circle, rect

from editor.asset_management.string.talkscript import ENCODE_MAP, convertTalkStringToSegments, Segment, Command, CommandClear, CommandPause, CommandLineBreak, CommandSetPitch, CommandSwitchAnimation, CommandSwitchColor

def createSquircle(width_visible : int, height : int, color : Tuple[int,int,int]) -> Surface:
    output : Surface = Surface((width_visible + height, height)).convert_alpha()
    output.fill((255,255,255,255))
    circle_midpoint = height // 2
    circle(output, color=color, radius=(height / 2), center=(circle_midpoint, circle_midpoint))
    circle(output, color=color, radius=(height / 2), center=(width_visible + circle_midpoint, circle_midpoint))
    rect(output, color=color, rect=Rect(circle_midpoint, 0, width_visible, height))
    return output

def convertPygameToBitmap(surface : Surface, hasTransparency : bool = False) -> Bitmap:
    if hasTransparency:
        bitmap : Bitmap = Bitmap.FromBufferRGBA(surface.get_width(), surface.get_height(), tostring(surface, "RGBA"))
    else:
        bitmap : Bitmap = Bitmap.FromBuffer(surface.get_width(), surface.get_height(), tostring(surface, "RGB"))
    return bitmap

def createTagFromText(surface : Surface, fontHeight : int = 9, paddingXSym : int = 4, squircleHeight : int = 16, color : Tuple[int,int,int] = (255,0,0)) -> Image:
    font_true_height = fontHeight * 2
    
    squircle_height : int = min(squircleHeight, font_true_height)
    paddingY = (font_true_height - squircle_height) + 1 # TODO - Validate this...
    
    squircle = createSquircle(surface.get_width(), squircle_height, color)

    # Credit : https://en.wikipedia.org/wiki/Relative_luminance
    luminance = 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]
    if luminance > 0.5:
        squircle.blit(surface, (squircle_height // 2, (squircle_height - surface.get_height()) // 2), special_flags=BLEND_SUB)
    else:
        squircle.blit(surface, (squircle_height // 2, (squircle_height - surface.get_height()) // 2), special_flags=BLEND_ADD)
    
    padded : Surface = Surface((squircle.get_width() + (paddingXSym * 2), squircle.get_height() + paddingY)).convert_alpha()
    padded.fill((255,255,255,255))
    padded.blit(squircle, (paddingXSym, paddingY))

    return convertPygameToBitmap(padded, True).ConvertToImage()

class DialogTalkScriptTextEditorRich(EditTalkscriptRich):
    def __init__(self, parent : Optional[Window], state : Layton2GameState, stringTalkscript : str = "", characters : List[str] = []):
        super().__init__(parent)
        self.__fontPointSize : int = self.rich_ts.GetBasicStyle().GetFont().GetPointSize()
        self._state : Layton2GameState = state
        self.__segments : List[Segment] = self.__preprocessSegments(convertTalkStringToSegments(stringTalkscript)) # Segments handle the pause/clear combo.
        
        # TODO - Ensure these are NOT the same size! This would be a BIG problem...
        self.__imageCommandAnimTrigger = createTagFromText(generateImageFromString(state.fontEvent, "Animation Switch"),    fontHeight = self.__fontPointSize, color=(255,255,0))
        self.__imageCommandPitch       = createTagFromText(generateImageFromString(state.fontEvent, "Change Pitch"),        fontHeight = self.__fontPointSize, color=(0,255,0))
        self.__imageCommandLineBreak   = createTagFromText(generateImageFromString(state.fontEvent, "Line Break"),          fontHeight = self.__fontPointSize, color=(0,0,0))
        self.__imageCommandClear       = createTagFromText(generateImageFromString(state.fontEvent, "Clear Textbox"),       fontHeight = self.__fontPointSize, color=(255,0,0))
        self.__imageCommandPause       = createTagFromText(generateImageFromString(state.fontEvent, "Wait for Tap"),        fontHeight = self.__fontPointSize, color=(255,0,255) )

        tempBtnSurface = Surface((16,16))
        self.__bitmapBtnBlack = convertPygameToBitmap(tempBtnSurface)
        tempBtnSurface.fill((255,0,0))
        self.__bitmapBtnRed = convertPygameToBitmap(tempBtnSurface)
        tempBtnSurface.fill((0,255,0))
        self.__bitmapBtnGreen = convertPygameToBitmap(tempBtnSurface)
        tempBtnSurface.fill((255,255,255))
        self.__bitmapBtnWhite = convertPygameToBitmap(tempBtnSurface)

        self.btnColorBlack.SetBitmap(self.__bitmapBtnBlack)
        self.btnColorWhite.SetBitmap(self.__bitmapBtnWhite)
        self.btnColorRed.SetBitmap(self.__bitmapBtnRed)
        self.btnColorGreen.SetBitmap(self.__bitmapBtnGreen)

        self.__mapImageToAttributes : Dict[RichTextImage, Command] = {}
        self.btnCullLineBreaks.Disable()

        self.Layout()
        self.__formRichTextFromSegments()

    def btnColorBlackOnButtonClick(self, event):
        return super().btnColorBlackOnButtonClick(event)
    
    def btnColorRedOnButtonClick(self, event):
        return super().btnColorRedOnButtonClick(event)
    
    def btnColorWhiteOnButtonClick(self, event):
        return super().btnColorWhiteOnButtonClick(event)
    
    def btnColorGreenOnButtonClick(self, event):
        return super().btnColorGreenOnButtonClick(event)

    def __insertItemAndStoreReference(self, image : Image, command : Command) -> Optional[RichTextImage]:
        insertion_point = self.rich_ts.GetInsertionPoint()
        self.rich_ts.WriteImage(image)
        buffer : RichTextBuffer = self.rich_ts.GetBuffer()
        image_pointer = None
        for child in buffer.GetChildren():
            image_pointer = child.FindObjectAtPosition(insertion_point)
            if image_pointer != None:
                self.__mapImageToAttributes[image_pointer] = command
                break
        
        return image_pointer

    def __doesRichTextStillExistInTree(self, node : RichTextImage) -> bool:
        # TODO - On user modification, check to see if our items are still valid!
        for child in self.rich_ts.GetBuffer().GetChildren():
            for another in child.GetChildren():
                if another == node:
                    return True
        return False

    def __preprocessSegments(self, segments_raw : List[Segment]) -> List[Segment]:

        # We're going to lean completely into our segment implementation which means permission to be DESTRUCTIVE
        output : List[Segment] = []

        if len(segments_raw) == 0:
            return output

        append_command : List[List[Command]] = []
        for _count_segment in range(len(segments_raw) + 1):
            append_command.append([])

        for idx_segment, segment in enumerate(segments_raw):
            processed_segment : Segment = Segment([])
            
            for command in segment.commandsAfterFinish:
                # Segmentation handles our pause/clear separation, but if we want clean display, handoff commands for next segment.
                # TODO - Ensure we only keep commands BEFORE pause in raw text.
                if type(command) == CommandPause or type(command) == CommandClear:
                    continue
                append_command[idx_segment + 1].append(command)
            
            for idx_line, line in enumerate(segment.lines):
                for token in line:
                    processed_segment.lines[0].append(token)
                
                if idx_line < len(segment.lines) - 1:
                    processed_segment.lines[0].append(CommandLineBreak()) # Collapse everything to a single line, but preserve line breaks in case
                                                                        #     we care about the formatting.
            
            output.append(processed_segment)

        # If we have some commands left, add another segment
        if append_command[-1] != []:
            output.append(Segment([]))

        for list_command, segment in zip(append_command[:len(output)], output):
            for command in list_command:    # TODO - Think I need to reverse this...
                segment.lines[0].insert(0, command)

        # Now everything is a single line and we have no commands to run after finishing each segment.
        return output

    def __formRichTextFromSegments(self):
        # Remove line wrapping, rely on autowrap to form segments!
        self.rich_ts.Clear()
        self.__mapImageToAttributes = {}

        self.rich_ts.BeginTextColour((0, 0, 0))
        for idx_segment, segment in enumerate(self.__segments):
            for idx_line, line in enumerate(segment.lines):
                for token in line:
                    if type(token) == str:
                        self.rich_ts.AppendText(token)
                    elif type(token) == CommandSwitchAnimation:
                        self.__insertItemAndStoreReference(self.__imageCommandAnimTrigger, token)
                    elif type(token) == CommandSetPitch:
                        self.__insertItemAndStoreReference(self.__imageCommandPitch, token)
                    elif type(token) == CommandLineBreak:
                        self.__insertItemAndStoreReference(self.__imageCommandLineBreak, token)
                    elif type(token) == CommandPause:
                        self.__insertItemAndStoreReference(self.__imageCommandPause, token)
                    elif type(token) == CommandClear:
                        self.__insertItemAndStoreReference(self.__imageCommandClear, token)
                    elif type(token) == CommandSwitchColor:
                        if token.isValid():
                            self.rich_ts.EndTextColour()
                            self.rich_ts.BeginTextColour(BLEND_MAP[token.code])

                # TODO - We need to fix this, not every single new line will need a space!
                if idx_line != len(segment.lines) - 1:
                    self.rich_ts.AppendText(" ")
            
            if idx_segment != len(self.__segments)  - 1:
                self.rich_ts.Newline()
            
            for command in segment.commandsAfterFinish:
                # TODO - Logging!
                print("Bad - command found in segment after section:", command)
        
        self.__setupButtons()

    def __setupButtons(self):
        anyLineBreaks : bool = False
        for key in self.__mapImageToAttributes:
            if type(self.__mapImageToAttributes[key]) == CommandLineBreak:
                anyLineBreaks = True
                break
        
        if anyLineBreaks:
            self.btnCullLineBreaks.Enable()
        else:
            self.btnCullLineBreaks.Disable()

    def btnCullLineBreaksOnButtonClick(self, event):
        keysToDelete = []

        if self.checkRestrictOperation.IsChecked():
            location_current = self.rich_ts.GetInsertionPoint()
            self.rich_ts.MoveToParagraphStart()
            location_para_start = self.rich_ts.GetInsertionPoint()
            self.rich_ts.MoveToParagraphEnd()
            location_para_end = self.rich_ts.GetInsertionPoint()
            #print("Start %d, Current %d, End %d" % (location_current, location_para_start, location_para_end))
            for image in self.__mapImageToAttributes.keys():
                if type(self.__mapImageToAttributes[image]) == CommandLineBreak:
                    internalRange : RichTextRange = image.GetRange().FromInternal()
                    if internalRange.Start >= location_para_start and internalRange.End <= location_para_end:
                        self.rich_ts.Replace(internalRange.Start, internalRange.End, " ")
                        keysToDelete.append(image)
                    #print("\tLocation", image.GetRange().FromInternal())
            
            self.rich_ts.SetCaretPosition(location_current)
        else:
            for image in self.__mapImageToAttributes.keys():
                if type(self.__mapImageToAttributes[image]) == CommandLineBreak:
                    # TODO - Space replacement isn't foolproof, probably will lead to some duplications in future...
                    self.rich_ts.Replace(image.GetRange().FromInternal().Start, image.GetRange().FromInternal().End, " ")
                    keysToDelete.append(image)
        
        for key in keysToDelete:
            del self.__mapImageToAttributes[key]
        
        self.__setupButtons()
        return super().btnCullLineBreaksOnButtonClick(event)

    def btnWrapToBreaksOnButtonClick(self, event):
        self.__doWrapping()
        return super().btnWrapToBreaksOnButtonClick(event)

    def __doWrapping(self):
        self.__segments = self.__preprocessSegments(self.__toWrapped())
        self.__formRichTextFromSegments()
        
    def __toWrapped(self) -> List[Segment]:
        # Remove control characters from input

        MAX_LINE_WIDTH = 240

        segments = convertTalkStringToSegments(self.__toEncoded())

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
                                
                                hasCurrentLineGotText = False
                                for token in outputSegments[-1].lines[-1]:
                                    if type(token) == str:
                                        hasCurrentLineGotText = True
                                        break
                                
                                if hasCurrentLineGotText:
                                    outputSegments[-1].lines.append([newToken])
                                else:
                                    outputSegments[-1].lines[-1].append(newToken)

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
                            hasCurrentLineGotText = False
                            for token in outputSegments[-1].lines[-1]:
                                if type(token) == str:
                                    hasCurrentLineGotText = True
                                    break
                            
                            if hasCurrentLineGotText:
                                outputSegments[-1].lines.append([newToken])
                            else:
                                outputSegments[-1].lines[-1].append(newToken)
                    else:
                        outputSegments[-1].lines[-1].append(token)

        return outputSegments

    def __toEncoded(self) -> str:

        def removeBadCharacters(token : str) -> str:
            output : str = ""
            for char in token:
                if char in ENCODE_MAP:
                    output += ENCODE_MAP[char]

                # Don't allow any unfiltered commands to escape.
                elif char in ["#", "&"]:
                    continue
                elif char == "<":
                    output += "‹"
                elif char == ">":
                    output += "›"
                
                else:
                    output += char
            return output

        # WHY IS THE API SO BAD?
        output = ""
        buffer : RichTextBuffer = self.rich_ts.GetBuffer()
        objects = buffer.GetChildren()
        for paragraph in objects:
            if type(paragraph) != RichTextParagraph:
                print("Unknown RichTextCtrl item :", paragraph)
                continue

            paragraph : RichTextParagraph
            # Under what we have so far, hopefully it should just be RichTextPlainText and RichTextImage...
            for item in paragraph.GetChildren():
                if type(item) != RichTextImage and type(item) != RichTextPlainText:
                    print("Unknown RichTextCtrl paragraph item :", item)
                    continue
                    
                if type(item) == RichTextPlainText:
                    item : RichTextPlainText
                    output += removeBadCharacters(item.GetText())
                else:
                    item : RichTextImage
                    if item in self.__mapImageToAttributes:
                        output += self.__mapImageToAttributes[item].getEncoded()
                    else:
                        print("Missing", item)
            
            # At the end of every paragraph, pause and clear
            output += "@p@c"
        
        # TODO - Properly cull remaining sections
        if len(output) >= 4:
            output = output[:-4]

        return output

    def GetValue(self) -> str:
        return self.__toEncoded()

    def btnColorBlackOnButtonClick(self, event):
        self.__toEncoded()
        return super().btnColorBlackOnButtonClick(event)