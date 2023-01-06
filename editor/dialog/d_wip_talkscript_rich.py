from editor.nopush_editor import EditTalkscriptRich
from widebrim.engine.state.manager import Layton2GameState
from widebrim.engine.anim.font.const import BLEND_MAP
from widebrim.engine.anim.font.static import generateImageFromString
from typing import Optional, List, Dict, Tuple
from widebrim.madhatter.common import logSevere

from wx import Window, Image, Bitmap, TEXT_ATTR_TEXT_COLOUR, Colour
from wx.richtext import RichTextImage, RichTextBuffer, RichTextParagraph, RichTextObject, RichTextRange, RichTextPlainText, RichTextAttr
from pygame import Surface, BLEND_SUB, BLEND_ADD, Rect
from pygame.image import tostring
from pygame.draw import rect
from pygame.gfxdraw import aacircle, filled_circle

from editor.asset_management.string.talkscript import ENCODE_MAP, convertTalkStringToSegments, Segment, Command, CommandClear, CommandPause, CommandLineBreak, CommandSetPitch, CommandSwitchAnimation, CommandSwitchColor

COLOR_ENCODE_MAP : Dict[str, str] = {}
for k, v in BLEND_MAP.items():
    if v not in COLOR_ENCODE_MAP:
        COLOR_ENCODE_MAP[v] = k

def createSquircle(width_visible : int, height : int, color : Tuple[int,int,int], outline_px : int = 2, outline_color : Tuple[int,int,int] = (0,0,0)) -> Surface:
    
    def squircle_main(width_visible : int, height : int, color : Tuple[int,int,int]) -> Surface:

        def draw_aa_circle(dest : Surface, radius : int, center_x : int, center_y : int):
            # TODO - With even radiuses, the center isn't on the grid so this breaks
            # The fix below isn't amazing but it improves the result
            if radius % 2 == 0:
                aacircle(dest,      center_x, center_y - 1, radius - 1, color)
                filled_circle(dest, center_x, center_y - 1, radius - 1, color)
                aacircle(dest,      center_x, center_y,     radius - 1, color)
                filled_circle(dest, center_x, center_y,     radius - 1, color)
            else:
                aacircle(dest, center_x, center_y, radius, color)
                filled_circle(dest, center_x, center_y, radius, color)

        output : Surface = Surface((width_visible + height, height)).convert_alpha()
        output.fill((255,255,255,0))
        circle_midpoint = (height // 2)
        radius = circle_midpoint
        draw_aa_circle(output, radius, circle_midpoint, circle_midpoint)
        draw_aa_circle(output, radius, circle_midpoint + width_visible, circle_midpoint)
        rect(output, color=color, rect=Rect(circle_midpoint, 0, width_visible, height))
        return output

    outline_px = min(height // 2, outline_px)
    outline_px = max(outline_px, 0)

    if outline_px == 0:
        return squircle_main(width_visible, height, color)
    
    outline_backing = squircle_main(width_visible, height, outline_color)

    height -= (2 * outline_px)
    main_backing = squircle_main(width_visible, height, color)
    outline_backing.blit(main_backing, (outline_px,outline_px))
    return outline_backing

def convertPygameToBitmap(surface : Surface, hasTransparency : bool = False) -> Bitmap:
    if hasTransparency:
        bitmap : Bitmap = Bitmap.FromBufferRGBA(surface.get_width(), surface.get_height(), tostring(surface, "RGBA"))
    else:
        bitmap : Bitmap = Bitmap.FromBuffer(surface.get_width(), surface.get_height(), tostring(surface, "RGB"))
    return bitmap

def createTagFromText(surface : Surface, fontHeight : int = 9, paddingXSym : int = 4, squircleHeight : int = 16, color : Tuple[int,int,int] = (255,0,0)) -> Image:
    # TODO - Figure out line spacing - this really isn't obvious enough...
    line_height = 19
    
    squircle_height : int = min(squircleHeight, fontHeight * 2)
    paddingY = (line_height - squircle_height) // 2

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

    LOG_MODULE_NAME = "TalkScriptEditorRich"

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

    def __remapStoredCommands(self):

        newImages : List[RichTextImage] = []
        remapBuffer : Dict[RichTextImage, Command] = {}

        buffer : RichTextBuffer = self.rich_ts.GetBuffer()
        objects : List[RichTextObject] = buffer.GetChildren()
        for paragraph in objects:
            if type(paragraph) != RichTextParagraph:
                logSevere("Misformatted RichTextCtrl item", paragraph, name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
                continue

            paragraph : RichTextParagraph
            # Under what we have so far, hopefully it should just be RichTextPlainText and RichTextImage...
            for item in paragraph.GetChildren():
                if type(item) == RichTextImage:
                    newImages.append(item)

        if len(newImages) == len(self.__mapImageToAttributes):
            for image, key in zip(newImages, self.__mapImageToAttributes):
                if image.GetRange() == key.GetRange():
                    remapBuffer[image] = self.__mapImageToAttributes[key]
                else:
                    logSevere("Tracking for element", image, "has been lost. This dialog must be reopened.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
        else:
            logSevere("Image tracking has been corrupted. This dialog must be reopened.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
        
        self.__mapImageToAttributes = remapBuffer

    def __applyColorToSelectedText(self, color : Tuple[int,int,int]):
        if self.rich_ts.HasSelection():
            attr = RichTextAttr()
            attr.SetFlags(TEXT_ATTR_TEXT_COLOUR)
            attr.SetTextColour(Colour(color[0], color[1], color[2]))   
            selection = self.rich_ts.GetSelection()
            for sel_range in selection.GetRanges():
                sel_range : RichTextRange
                self.rich_ts.SetStyle(sel_range, attr)
            self.__remapStoredCommands()

    def btnColorBlackOnButtonClick(self, event):
        self.__applyColorToSelectedText(BLEND_MAP["x"])
        return super().btnColorBlackOnButtonClick(event)
    
    def btnColorRedOnButtonClick(self, event):
        self.__applyColorToSelectedText(BLEND_MAP["r"])
        return super().btnColorRedOnButtonClick(event)
    
    def btnColorWhiteOnButtonClick(self, event):
        self.__applyColorToSelectedText(BLEND_MAP["w"])
        return super().btnColorWhiteOnButtonClick(event)
    
    def btnColorGreenOnButtonClick(self, event):
        self.__applyColorToSelectedText(BLEND_MAP["g"])
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
                        self.rich_ts.WriteText(token)
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
                            self.rich_ts.BeginTextColour(Colour(BLEND_MAP[token.code][0], BLEND_MAP[token.code][1], BLEND_MAP[token.code][2]))

                # TODO - We need to fix this, not every single new line will need a space!
                if idx_line != len(segment.lines) - 1:
                    self.rich_ts.AppendText(" ")
            
            if idx_segment != len(self.__segments)  - 1:
                self.rich_ts.Newline()
            
            for command in segment.commandsAfterFinish:
                logSevere("Command untracked in finishing queue:", command, name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
        
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
            for image in self.__mapImageToAttributes.keys():
                if type(self.__mapImageToAttributes[image]) == CommandLineBreak:
                    internalRange : RichTextRange = image.GetRange().FromInternal()
                    if internalRange.Start >= location_para_start and internalRange.End <= location_para_end:
                        self.rich_ts.Replace(internalRange.Start, internalRange.End, " ")
                        keysToDelete.append(image)
            
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
        print(self.__toEncoded())
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
            print("Wrapping", segment)
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

        def removeBadCharacter(char : str) -> str:
            if char in ENCODE_MAP:
                return "<" + ENCODE_MAP[char] + ">"

            # Don't allow any unfiltered commands to escape.
            elif char in ["#", "&"]:
                return ""
            elif char == "<":
                return "<‹>"
            elif char == ">":
                return "<›>"
            
            return char

        # WHY IS THE API SO BAD?
        output = ""
        buffer : RichTextBuffer = self.rich_ts.GetBuffer()
        objects : List[RichTextObject] = buffer.GetChildren()
        lastColorRgba : Tuple[int,int,int,int] = (0,0,0,255)
        for paragraph in objects:
            if type(paragraph) != RichTextParagraph:
                logSevere("Misformatted RichTextCtrl item", paragraph, name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
                continue

            paragraph : RichTextParagraph
            # Under what we have so far, hopefully it should just be RichTextPlainText and RichTextImage...
            for item in paragraph.GetChildren():
                if type(item) != RichTextImage and type(item) != RichTextPlainText:
                    logSevere("Misformatted RichTextParagraph item", item, name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
                    continue
                    
                if type(item) == RichTextPlainText:
                    item : RichTextPlainText
                    rangeParagraph : RichTextRange = item.GetRange().FromInternal()

                    for char_code, start in zip(item.GetText(), range(rangeParagraph.Start, rangeParagraph.End)):
                        attr = RichTextAttr()
                        self.rich_ts.GetStyle(start, attr)
                        if attr.TextColour != lastColorRgba:
                            lastColorRgba = (attr.TextColour[0], attr.TextColour[1], attr.TextColour[2], attr.TextColour[3])
                            colorRgb = (lastColorRgba[0], lastColorRgba[1], lastColorRgba[2])
                            if colorRgb in COLOR_ENCODE_MAP:
                                output += "#" + COLOR_ENCODE_MAP[colorRgb]
                            else:
                                logSevere("Unencodable color detected", colorRgb, "will be removed on output.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
                        output += removeBadCharacter(char_code)
                else:
                    item : RichTextImage
                    if item in self.__mapImageToAttributes:
                        output += self.__mapImageToAttributes[item].getEncoded()
                    else:
                        logSevere("Untracked image", item, "may be destroyed during editing.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
            
            # At the end of every paragraph, pause and clear
            output += "@p@c"
        
        # TODO - Properly cull remaining sections
        if len(output) >= 4:
            output = output[:-4]

        print("Encoded: ", output)
        return output

    def GetValue(self) -> str:
        return self.__toEncoded()

    def __doOnTagPressed(self, tag : RichTextImage):
        if tag not in self.__mapImageToAttributes:
            return
        print("Pressed", self.__mapImageToAttributes[tag]) 

    def rich_tsOnLeftDown(self, event):
        hit_test, hit_char_idx = self.rich_ts.HitTest(event.GetPosition())
        if hit_test == 0:
            for image in self.__mapImageToAttributes:
                if image.GetRange()[0] == hit_char_idx:
                    self.__doOnTagPressed(image)
                    break
        return super().rich_tsOnLeftDown(event)