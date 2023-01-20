from editor.nopush_editor import EditTalkscriptRich
from editor.asset_management.character import CharacterEntry
from widebrim.engine.state.manager import Layton2GameState
from widebrim.engine.anim.font.const import BLEND_MAP
from widebrim.engine.anim.font.static import generateImageFromString
from typing import Optional, List, Dict, Tuple, Union
from widebrim.madhatter.common import logSevere, logVerbose
from widebrim.engine.anim.image_anim.image import AnimatedImageObject

from wx import Window, Image, Bitmap, TEXT_ATTR_TEXT_COLOUR, Colour
from wx.richtext import RichTextImage, RichTextBuffer, RichTextParagraph, RichTextObject, RichTextRange, RichTextPlainText, RichTextAttr
from pygame import Surface, BLEND_SUB, BLEND_ADD, Rect
from pygame.image import tostring
from pygame.transform import scale as scaleSurface
from pygame.draw import rect
from pygame.gfxdraw import aacircle, filled_circle
from math import floor

from editor.asset_management.string.talkscript import ENCODE_MAP, convertTalkStringToSegments, Segment, Command, CommandClear, CommandPause, CommandLineBreak, CommandDelayPlayback, CommandSwitchAnimation, CommandSwitchColor

COLOR_ENCODE_MAP : Dict[str, str] = {}
for k, v in BLEND_MAP.items():
    if v not in COLOR_ENCODE_MAP:
        COLOR_ENCODE_MAP[v] = k

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

    def __init__(self, parent : Optional[Window], state : Layton2GameState, stringTalkscript : str = "", characters : List[Tuple[CharacterEntry, Optional[str], Optional[AnimatedImageObject]]] = []):

        def loadButtonImages(sizeImage : Tuple[int,int] = (16,16)):
            # Prepare images for our colors
            tempBtnSurface = Surface(sizeImage)
            bitmapBtnBlack = convertPygameToBitmap(tempBtnSurface)
            tempBtnSurface.fill((255,0,0))
            bitmapBtnRed = convertPygameToBitmap(tempBtnSurface)
            tempBtnSurface.fill((0,255,0))
            bitmapBtnGreen = convertPygameToBitmap(tempBtnSurface)
            tempBtnSurface.fill((255,255,255))
            bitmapBtnWhite = convertPygameToBitmap(tempBtnSurface)

            self.btnColorBlack.SetBitmap(bitmapBtnBlack)
            self.btnColorWhite.SetBitmap(bitmapBtnWhite)
            self.btnColorRed.SetBitmap(bitmapBtnRed)
            self.btnColorGreen.SetBitmap(bitmapBtnGreen)

            # Prepare images for our icons
            def getCharBitmap(char : str, size : Tuple[int,int] = sizeImage) -> Optional[Bitmap]:
                surf : Surface = generateImageFromString(state.font18, char)
                if surf.get_width() != size[0] and surf.get_height() != size[1]:
                    scale : float = min(size[0] / surf.get_width(), size[1] / surf.get_height())
                    newSize : Tuple[int,int] = (floor(surf.get_width() * scale), floor(surf.get_height() * scale))                
                    scaled = scaleSurface(surf, newSize)

                    # Finally, we need to pad to new size
                    padded = Surface(size)
                    offset = ((size[0] - newSize[0]) // 2, (size[1] - newSize[1]) // 2)
                    padded.blit(scaled, offset)
                    return convertPygameToBitmap(padded, False)
                return convertPygameToBitmap(surf, False)

            self.btnCmdAnim.SetBitmap(getCharBitmap("s"))
            self.btnCmdClear.SetBitmap(getCharBitmap("c"))
            self.btnCmdPause.SetBitmap(getCharBitmap("p"))
            self.btnCmdDelay.SetBitmap(getCharBitmap("v"))
            self.btnCmdLineBreak.SetBitmap(getCharBitmap("n"))

        super().__init__(parent)
        self.__fontPointSize : int = self.rich_ts.GetBasicStyle().GetFont().GetPointSize()
        self._state : Layton2GameState = state
        self.__segments : List[Segment] = self.__preprocessSegments(convertTalkStringToSegments(stringTalkscript)) # Segments handle the pause/clear combo.
        
        # TODO - Ensure these are NOT the same size! This would be a BIG problem...
        self.__imageCommandAnimTrigger = createTagFromText(generateImageFromString(state.fontEvent, "Animation Switch"),    fontHeight = self.__fontPointSize, color=(255,255,0))
        self.__imageCommandDelay       = createTagFromText(generateImageFromString(state.fontEvent, "Delay"),               fontHeight = self.__fontPointSize, color=(0,255,0))
        self.__imageCommandLineBreak   = createTagFromText(generateImageFromString(state.fontEvent, "Line Break"),          fontHeight = self.__fontPointSize, color=(0,0,0))
        self.__imageCommandClear       = createTagFromText(generateImageFromString(state.fontEvent, "Clear Textbox"),       fontHeight = self.__fontPointSize, color=(255,0,0))
        self.__imageCommandPause       = createTagFromText(generateImageFromString(state.fontEvent, "Wait for Tap"),        fontHeight = self.__fontPointSize, color=(255,0,255) )

        self.__attributeImages  : List[RichTextImage]   = []
        self.__attributeList    : List[Command]         = []

        # Disable weird XML handling bug and remove cull line break button (done programmatically)
        self.rich_ts.DropTarget = None
        self.btnCullLineBreaks.Disable()
        loadButtonImages()

        self._isSafeToRead : bool = True

        # Cleanup the state from wxFormBuilder - hide and disable all collapsible elements, hide spacing line, add padding
        self.paneStartingParameters.Hide()
        self.panelSwitchAnimOptions.Disable()
        self.panelSwitchDelayOptions.Disable()
        self.panelSwitchAnimOptions.Hide()
        self.panelSwitchDelayOptions.Hide()
        self.staticlinePaneDivider.Hide()
        self.paneCommandParameters.Hide()
        self.panelSpacing.Show()
        self.Layout()

        self.__formRichTextFromSegments()

    def __getAllImages(self) -> List[RichTextImage]:
        newImages : List[RichTextImage] = []
        buffer : RichTextBuffer = self.rich_ts.GetBuffer()
        objects : List[RichTextObject] = buffer.GetChildren()
        for paragraph in objects:
            if type(paragraph) == RichTextImage:
                newImages.append(paragraph)
                continue
            elif type(paragraph) != RichTextParagraph:
                logSevere("Misformatted RichTextCtrl item", paragraph, name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
                continue

            paragraph : RichTextParagraph
            # Under what we have so far, hopefully it should just be RichTextPlainText and RichTextImage...
            for item in paragraph.GetChildren():
                if type(item) == RichTextImage:
                    newImages.append(item)
        return newImages

    def __remapStoredCommands(self):

        newImages : List[RichTextImage] = self.__getAllImages()

        if len(newImages) == len(self.__attributeImages):
            # This might be dangerous, but it works better...
            self.__attributeImages = newImages
        else:
            logSevere("Image tracking has been corrupted. This dialog must be reopened.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
            for image in newImages:
                logSevere(image, image.GetRange(), name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
        
    def __applyColorToSelectedText(self, color : Tuple[int,int,int]):

        def getImageLocations(images : List[RichTextImage]) -> List[int]:
            output = []
            for image in images:
                output.append(image.GetRange()[0])
            output.sort()
            return output

        if self.rich_ts.HasSelection():
            self._isSafeToRead = False
            attr = RichTextAttr()
            attr.SetFlags(TEXT_ATTR_TEXT_COLOUR)
            attr.SetTextColour(Colour(color[0], color[1], color[2]))   
            selection = self.rich_ts.GetSelection()

            imagesSorted = getImageLocations(self.__getAllImages())
            for sel_range in selection.GetRanges():
                sel_range : RichTextRange
                self.rich_ts.SetStyle(sel_range, attr)
            
            # There seems to be a VERY annoying bug in wx where changing the style of an image makes it disappear from the buffer
            # The solution is to call the code again... it will appear eventually...
            while getImageLocations(self.__getAllImages()) != imagesSorted:
                logSevere("API RichTextImage leak detected, trying again...", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
                for sel_range in selection.GetRanges():
                    sel_range : RichTextRange
                    self.rich_ts.SetStyle(sel_range, attr)
            self.__remapStoredCommands()
            self._isSafeToRead = True
            self._updatePreview()

    def _updatePreview():
        pass

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

    def btnCmdAnimOnButtonClick(self, event):
        newCommand = CommandSwitchAnimation("NONE", 0)
        self.__insertItemAndStoreReference(self.__imageCommandAnimTrigger, newCommand)
        return super().btnCmdAnimOnButtonClick(event)
    
    def btnCmdClearOnButtonClick(self, event):
        newCommand = CommandClear()
        self.__insertItemAndStoreReference(self.__imageCommandClear, newCommand)
        return super().btnCmdClearOnButtonClick(event)
    
    def btnCmdPauseOnButtonClick(self, event):
        newCommand = CommandPause()
        self.__insertItemAndStoreReference(self.__imageCommandPause, newCommand)
        return super().btnCmdPauseOnButtonClick(event)
    
    def btnCmdDelayOnButtonClick(self, event):
        newCommand = CommandDelayPlayback(0)
        self.__insertItemAndStoreReference(self.__imageCommandDelay, newCommand)
        return super().btnCmdDelayOnButtonClick(event)

    def btnCmdLineBreakOnButtonClick(self, event):
        newCommand = CommandLineBreak()
        self.__insertItemAndStoreReference(self.__imageCommandLineBreak, newCommand)
        return super().btnCmdLineBreakOnButtonClick(event)

    def __insertItemAndStoreReference(self, image : Image, command : Command) -> Optional[RichTextImage]:
        self._isSafeToRead = False
        insertion_point = self.rich_ts.GetInsertionPoint()
        self.rich_ts.WriteImage(image)
        buffer : RichTextBuffer = self.rich_ts.GetBuffer()
        image_pointer = None
        for child in buffer.GetChildren():
            image_pointer = child.FindObjectAtPosition(insertion_point)
            if image_pointer != None:
                if len(self.__attributeImages) == 0:
                    self.__attributeImages.append(image_pointer)
                    self.__attributeList.append(command)
                else:
                    has_inserted = False
                    for idx in range(1, len(self.__attributeImages)):
                        if self.__attributeImages[idx].GetRange()[0] > image_pointer.GetRange()[0]:
                            self.__attributeImages.insert(idx, image_pointer)
                            self.__attributeList.insert(idx, command)
                            has_inserted = True
                            break
                    if not(has_inserted):
                        self.__attributeImages.append(image_pointer)
                        self.__attributeList.append(command)
                break
        self._isSafeToRead = True
        return image_pointer

    def __doesRichTextStillExistInTree(self, node : RichTextImage) -> bool:
        for child in self.rich_ts.GetBuffer().GetChildren():
            if child == node:
                return True
            else:
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
                    if len(processed_segment.lines) == 0:
                        processed_segment.lines = [[token]]
                    else:
                        processed_segment.lines[0].append(token)
                
                if idx_line < len(segment.lines) - 1:
                    if len(processed_segment.lines) == 0:
                        processed_segment.lines = [CommandLineBreak()]
                    else:
                        processed_segment.lines[0].append(CommandLineBreak()) # Collapse everything to a single line, but preserve line breaks in case
                                                                            #     we care about the formatting.
            
            output.append(processed_segment)

        # If we have some commands left, add another segment
        if append_command[-1] != []:
            output.append(Segment([]))

        for list_command, segment in zip(append_command[:len(output)], output):
            for command in list_command:    # TODO - Think I need to reverse this...
                if len(segment.lines) == 0:
                    segment.lines.append([])
                segment.lines[0].insert(0, command)

        # Now everything is a single line and we have no commands to run after finishing each segment.
        return output

    def __formRichTextFromSegments(self):
        # Remove line wrapping, rely on autowrap to form segments!
        self._isSafeToRead = False
        self.rich_ts.Clear()
        self.rich_ts.BeginParagraphSpacing(0, 40)
        self.__attributeImages = []
        self.__attributeList = []

        self.rich_ts.BeginTextColour((0, 0, 0))
        for idx_segment, segment in enumerate(self.__segments):
            for idx_line, line in enumerate(segment.lines):
                for token in line:
                    if type(token) == str:
                        self.rich_ts.WriteText(token)
                    elif type(token) == CommandSwitchAnimation:
                        self.__insertItemAndStoreReference(self.__imageCommandAnimTrigger, token)
                    elif type(token) == CommandDelayPlayback:
                        self.__insertItemAndStoreReference(self.__imageCommandDelay, token)
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
        self._isSafeToRead = True
        self._updatePreview()

    def __setupButtons(self):
        anyLineBreaks : bool = False
        for command in self.__attributeList:
            if type(command) == CommandLineBreak:
                anyLineBreaks = True
                break
        
        if anyLineBreaks:
            self.btnCullLineBreaks.Enable()
        else:
            self.btnCullLineBreaks.Disable()

    def __deleteTrackedImages(self, images : List[RichTextImage]) -> bool:
        idx_to_delete = []
        failure = False
        for image in images:
            try:
                idx_to_delete.append(self.__attributeImages.index(image))
            except ValueError:
                failure = True
        
        # Pass through to future control if we delete a tag so they can stop displaying it
        commandsDeleted = []
        for idx in idx_to_delete:
            commandsDeleted.append(self.__attributeList[idx])
        self._doOnTagDeleted(commandsDeleted)

        idx_to_delete.sort()
        idx_to_delete.reverse()
        for idx in idx_to_delete:
            self.__attributeImages.pop(idx)
            self.__attributeList.pop(idx)
        
        return not(failure)

    def _getEncodedSelectedSegment(self) -> str:
        if not(self._isSafeToRead):
            return ""

        location_current = self.rich_ts.GetInsertionPoint()
        self.rich_ts.MoveToParagraphStart()
        location_para_start = self.rich_ts.GetInsertionPoint()
        self.rich_ts.MoveToParagraphEnd()
        location_para_end = self.rich_ts.GetInsertionPoint()
        
        output : str = ""
        buffer : RichTextBuffer = self.rich_ts.GetBuffer()
        objects : List[RichTextObject] = buffer.GetChildren()
        lastColorRgba : Tuple[int,int,int,int] = (0,0,0,255)
        for paragraph in objects:
            if type(paragraph) == RichTextImage:
                if paragraph in self.__attributeImages:
                    paragraphRange : RichTextRange = paragraph.GetRange().FromInternal()
                    if paragraphRange.Start >= location_para_start and paragraphRange.End <= location_para_end:
                        output += self.__attributeList[self.__attributeImages.index(paragraph)].getEncoded()
                else:
                    logSevere("Untracked image", paragraph, "may be destroyed during editing.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
            
            elif type(paragraph) != RichTextParagraph:
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

                    for char_code, start in zip(item.GetText(), range(max(rangeParagraph.Start, location_para_start), min(rangeParagraph.End, location_para_end))):
                        attr = RichTextAttr()
                        self.rich_ts.GetStyle(start, attr)
                        if attr.TextColour != lastColorRgba and char_code != " ":
                            lastColorRgba = (attr.TextColour[0], attr.TextColour[1], attr.TextColour[2], attr.TextColour[3])
                            colorRgb = (lastColorRgba[0], lastColorRgba[1], lastColorRgba[2])
                            if colorRgb in COLOR_ENCODE_MAP:
                                output += "#" + COLOR_ENCODE_MAP[colorRgb]
                            else:
                                logSevere("Unencodable color detected", colorRgb, "will be removed on output.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
                        output += removeBadCharacter(char_code)
                else:
                    item : RichTextImage
                    if item in self.__attributeImages:
                        paragraphRange : RichTextRange = item.GetRange().FromInternal()
                        if paragraphRange.Start >= location_para_start and paragraphRange.End <= location_para_end:
                            output += self.__attributeList[self.__attributeImages.index(item)].getEncoded()
                    else:
                        logSevere("Untracked image", item, "may be destroyed during editing.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)

        self.rich_ts.SetInsertionPoint(location_current)
        return output

    def btnCullLineBreaksOnButtonClick(self, event):
        # TODO - We don't need to deselect the active tag, but just in case, forceably lose focus
        self._doOnTagFocusLost()
        self._isSafeToRead = False

        keysToDelete = []

        if self.checkRestrictOperation.IsChecked():
            location_current = self.rich_ts.GetInsertionPoint()
            self.rich_ts.MoveToParagraphStart()
            location_para_start = self.rich_ts.GetInsertionPoint()
            self.rich_ts.MoveToParagraphEnd()
            location_para_end = self.rich_ts.GetInsertionPoint()
            for image, command in zip(self.__attributeImages, self.__attributeList):
                if type(command) == CommandLineBreak:
                    internalRange : RichTextRange = image.GetRange().FromInternal()
                    if internalRange.Start >= location_para_start and internalRange.End <= location_para_end:
                        self.rich_ts.Replace(internalRange.Start, internalRange.End, " ")
                        keysToDelete.append(image)

            self.rich_ts.SetInsertionPoint(location_current)
        else:
            for image, command in zip(self.__attributeImages, self.__attributeList):
                if type(command) == CommandLineBreak:
                    # TODO - Space replacement isn't foolproof, probably will lead to some duplications in future...
                    self.rich_ts.Replace(image.GetRange().FromInternal().Start, image.GetRange().FromInternal().End, " ")
                    keysToDelete.append(image)
        
        self.__deleteTrackedImages(keysToDelete)
        self.__setupButtons()
        self._isSafeToRead = True
        self._updatePreview()
        return super().btnCullLineBreaksOnButtonClick(event)

    def btnWrapToBreaksOnButtonClick(self, event):
        # TODO - We don't need to deselect the active tag, but just in case, forceably lose focus
        self._doOnTagFocusLost()

        # TODO - Wrap only section
        self.__doWrapping()
        return super().btnWrapToBreaksOnButtonClick(event)

    def __doWrapping(self):
        self.__segments = self.__preprocessSegments(self.__toWrapped())
        self.__formRichTextFromSegments()
        
    def __toWrapped(self) -> List[Segment]:
        # Remove control characters from input

        MAX_LINE_WIDTH = 240

        def doesTextGoBeyondBound(text : str) -> bool:
            testSurface : Surface = generateImageFromString(self._state.fontEvent, text)
            return testSurface.get_width() > MAX_LINE_WIDTH
        
        def doesLineContainStrings(line : List[Union[Command, str]]) -> bool:
            for token in line:
                if type(token) == str:
                    return True
            return False

        def doesTokenNeedSpace(remainingLine : List[Union[Command, str]]) -> bool:
            # TODO - Cover case    "this" -> [ColorChange, "that"]
            #        Works with cases like "th" -> [ColorChange, "is"]
            encounteredNoneBreaking : bool = False
            
            for token in remainingLine:
                if type(token) == str:
                    return not(encounteredNoneBreaking)
                else:
                    encounteredNoneBreaking = True
            return False

        segments = convertTalkStringToSegments(self.__toEncoded())
        tokenizedSegments : List[Segment] = []

        for segment in segments:
            tokenizedSegments.append(Segment([]))
            tokenizedSegments[-1].commandsAfterFinish = segment.commandsAfterFinish
            
            for tokenLine in segment.lines:
                tokenizedSegments[-1].lines.append([])

                wordAndToken : List[Union[Command, str]] = []
                
                for token in tokenLine:
                    if type(token) == str:
                        # Tokenize into words, remove excess spaces for easier handling later
                        words = token.split(" ")
                        for word in words:
                            wordAndToken.append(word)
                    else:
                        wordAndToken.append(token)

                currentLine : str = ""
                for token in wordAndToken:
                    # TODO - There are still some bugs with this, namely color changes in the middle of symbols
                    if type(token) == str:
                        nextLine : str = currentLine + token + " "
                        nextLineStripped = nextLine.strip()

                        # Adding this word to the wrapping line has caused it to go to next line
                        if doesTextGoBeyondBound(nextLineStripped):
                            # If the last line doesn't contain text, continue it with out token
                            if not(doesLineContainStrings(tokenizedSegments[-1].lines[-1])):
                                tokenizedSegments[-1].lines[-1].append(token)
                            else:
                                if token != "":
                                    # If there is text on the line, it is a 'true' new line so must be created
                                    tokenizedSegments[-1].lines.append([token])
                            currentLine = token
                        else:
                            if token == "":
                                if not(doesLineContainStrings(tokenizedSegments[-1].lines[-1])):
                                    continue

                            # This token is okay to add to the current line
                            currentLine = nextLine
                            tokenizedSegments[-1].lines[-1].append(token)
                    else:
                        # If its a token, we just add it to the line
                        tokenizedSegments[-1].lines[-1].append(token)

        for segment in tokenizedSegments:
            for idx_line, line in enumerate(segment.lines):
                # We will now recover the spacing
                newLine = []
                for idx_token, token in enumerate(line):
                    if type(token) == str:
                        if doesTokenNeedSpace(line[idx_token + 1:]):
                            token = token + " "
                        if len(newLine) > 0 and type(newLine[-1]) == str:
                            # Continue strings that are one block
                            newLine[-1] = newLine[-1] + token
                        else:
                            newLine.append(token) 
                    else:
                        newLine.append(token)

                segment.lines[idx_line] = newLine

        return tokenizedSegments

    def __toEncoded(self) -> str:
        # WHY IS THE API SO BAD?
        output = ""
        buffer : RichTextBuffer = self.rich_ts.GetBuffer()
        objects : List[RichTextObject] = buffer.GetChildren()
        lastColorRgba : Tuple[int,int,int,int] = (0,0,0,255)
        for paragraph in objects:
            if type(paragraph) == RichTextImage:
                if paragraph in self.__attributeImages:
                    output += self.__attributeList[self.__attributeImages.index(paragraph)].getEncoded()
                else:
                    logSevere("Untracked image", paragraph, "may be destroyed during editing.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
            
            elif type(paragraph) != RichTextParagraph:
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
                        if attr.TextColour != lastColorRgba and char_code != " ":
                            lastColorRgba = (attr.TextColour[0], attr.TextColour[1], attr.TextColour[2], attr.TextColour[3])
                            colorRgb = (lastColorRgba[0], lastColorRgba[1], lastColorRgba[2])
                            if colorRgb in COLOR_ENCODE_MAP:
                                output += "#" + COLOR_ENCODE_MAP[colorRgb]
                            else:
                                logSevere("Unencodable color detected", colorRgb, "will be removed on output.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
                        output += removeBadCharacter(char_code)
                else:
                    item : RichTextImage
                    if item in self.__attributeImages:
                        output += self.__attributeList[self.__attributeImages.index(item)].getEncoded()
                    else:
                        logSevere("Untracked image", item, "may be destroyed during editing.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)
            
            # At the end of every paragraph, pause and clear
            output += "@p@c"
        
        # TODO - Properly cull remaining sections
        if len(output) >= 4:
            output = output[:-4]

        return output

    def GetValue(self) -> str:
        """Returns the encoded TalkScript for this dialog.

        Returns:
            str: Encoded TalkScript.
        """
        return self.__toEncoded()

    def _doOnTagDeleted(self, commands : List[Command]):
        logVerbose("Deleted", commands, name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)

    def _doOnTagPressed(self, command : Command):
        logVerbose("Pressed", command, name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME) 

    def _doOnTagFocusLost(self):
        logVerbose("Tag was not pressed.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)

    def rich_tsOnRichTextDelete(self, event):
        # When the user does anything that could disrupt our images, we need to deregister them too
        keysToDelete = []
        for key in self.__attributeImages:
            if not(self.__doesRichTextStillExistInTree(key)):
                keysToDelete.append(key)
        self.__deleteTrackedImages(keysToDelete)
        return super().rich_tsOnRichTextDelete(event)

    def rich_tsOnLeftDown(self, event):
        hit_test, hit_char_idx = self.rich_ts.HitTest(event.GetPosition())
        wasTagHit : bool = False
        if hit_test == 0:
            for image in self.__attributeImages:
                if image.GetRange()[0] == hit_char_idx:
                    self._doOnTagPressed(self.__attributeList[self.__attributeImages.index(image)])
                    wasTagHit = True
                    break
        if not(wasTagHit):
            self._doOnTagFocusLost()

        return super().rich_tsOnLeftDown(event)