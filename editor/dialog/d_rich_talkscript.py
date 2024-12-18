from widebrim.engine.anim.font.scrolling import ScrollingFontHelper
from widebrim.engine.const import RESOLUTION_NINTENDO_DS
from widebrim.madhatter.common import logSevere, logVerbose
from .d_wip_talkscript_rich import DialogTalkScriptTextEditorRich, AnimatedImageObject, Layton2GameState, Command, CommandDelayPlayback, CommandSwitchAnimation
from typing import Dict, Optional, Tuple, List, Any
from editor.gui_helpers.anim_bitmap import AnimationUpdater
from wx import CollapsiblePane, CollapsiblePaneEvent, Window, Timer, EVT_TIMER, EVT_CLOSE, StaticBitmap, Choice, Bitmap, NOT_FOUND, NullBitmap
from pygame import Surface
from pygame.image import tostring

class AnimationManager():
    def __init__(self, anim : Optional[AnimatedImageObject], entryId : int, name : Optional[str] = None):
        # TODO - Not fully representative. Comes from e_script_event
        def isNameGood(name) -> bool:
            if len(name) > 0:
                if name[0] != "*" and name != "Create an Animation":
                    return True
            return False

        self.__anim : Optional[AnimatedImageObject] = anim
        self.__animBridge : AnimationUpdater = AnimationUpdater(self.__anim, None)

        if name == None:
            self.__name = "No name - ID %d" % entryId
        else:
            self.__name = name

        self.__listAnimations : List[str] = ["Create an Animation"]
        self.__idxSafeAnimations : List[int] = []
        
        if self.__anim != None:
            idxAnim = 1
            while self.__anim.setAnimationFromIndex(idxAnim):
                self.__listAnimations.append(self.__anim.animActive.getName())
                if isNameGood(self.__listAnimations[-1]):
                    self.__idxSafeAnimations.append(idxAnim)
                idxAnim += 1

    def setAnimationByIndex(self, idx : int):
        self.__animBridge.setAnimationFromIndex(idx)

    def setDestinationBitmap(self, bitmap : Optional[StaticBitmap]):
        self.__animBridge.changeBitmap(bitmap)
        self.__animBridge.triggerRedraw(True)

    def getName(self) -> str:
        return self.__name

    def getTargetAnimation(self, index : int, wasSafe : bool) -> Optional[int]:
        if wasSafe:
            if 0 <= index < len(self.__idxSafeAnimations):
                return self.__idxSafeAnimations[index]
        else:
            if 0 <= index < len(self.__listAnimations):
                return index
        return None

    def getRawAnimationName(self, index : int, wasSafe : bool) -> Optional[str]:
        idxAnimation : Optional[int] = self.getTargetAnimation(index, wasSafe)
        if idxAnimation == None:
            return None
        return self.__listAnimations[idxAnimation]

    def getListAnimations(self) -> List[str]:
        reference = list(self.__listAnimations)
        reference[0] = "Null Animation"
        return reference

    def getListSafeAnimations(self) -> Optional[List[str]]:
        if len(self.__idxSafeAnimations) == 0:
            return None
        reference : List[str] = []
        for idx in self.__idxSafeAnimations:
            reference.append(self.__listAnimations[idx])
        return reference

    def update(self):
        self.__animBridge.update()

class DialogTalkScriptEditorRichWithTags(DialogTalkScriptTextEditorRich):
    def __init__(self, parent: Optional[Window], state: Layton2GameState, stringTalkscript: str = "", characters : List[Tuple[int, Optional[str], Optional[AnimatedImageObject]]] = [], targetId : int = 0, targetPitch : int = 0, targetStartAnimation : Optional[str] = None, targetEndAnimation : Optional[str] = None):
        self.__textRenderer = ScrollingFontHelper(state.fontEvent)
        self.__surfPreview = Surface(RESOLUTION_NINTENDO_DS)
        
        super().__init__(parent, state, stringTalkscript, characters)

        self.__targetAnimPreviewIsStart : bool = True

        self.__animTimer = Timer(self)
        self.__animTimer.Start(1000//60, False)
        self.__forceUpdate : bool = False

        self.__animManagers : List[AnimationManager] = []
        self.__animCharIds : List[int] = []
        self.__animManagerCharPreview : Optional[AnimationManager] = None
        self.__animManagerTargetPreview : Optional[AnimationManager] = None
        
        names = []

        for entryId, name, anim in characters:
            self.__animManagers.append(AnimationManager(anim, entryId, name))
            names.append(self.__animManagers[-1].getName())
            self.__animCharIds.append(entryId)
        
        for delay in range(80):
            self.choiceFrames.AppendItems("%d frames" % (delay * 10))
        
        self.choiceChangeAnimCharName.SetItems(names)
        self.choiceTargetCharacter.SetItems(["None"] + names)

        try:
            indexTarget : int = self.__animCharIds.index(targetId) + 1
        except ValueError:
            indexTarget : int = 0
        self.choiceTargetCharacter.Select(indexTarget)
        self.__updateAnimationToggles()

        # TODO - If we have active last animations, apply here then call updateCharacterPreview again
        availableAnimations : List[str] = list(self.choiceAnimOnStart.GetItems())[1:]
        # TODO - This isn't exactly accurate, we aren't using lt2comparestring here
        if targetStartAnimation != None:
            if targetStartAnimation in availableAnimations:
                self.choiceAnimOnStart.Select(availableAnimations.index(targetStartAnimation) + 1)
        if targetEndAnimation != None:
            if targetEndAnimation in availableAnimations:
                self.choiceAnimOnEnd.Select(availableAnimations.index(targetEndAnimation) + 1)
        if targetStartAnimation != None or targetEndAnimation != None:
            self.__updateCharacterPreview()

        if targetPitch <= 0 or targetPitch > 6:
            # Game defaults to low pitch - 2_SetTextSound
            self.choiceMainPitch.Select(0)
        else:
            self.choiceMainPitch.Select(targetPitch - 1)

        self.Bind(EVT_TIMER, self.__updateActiveAnimation, self.__animTimer)
        self.Bind(EVT_CLOSE, self.__onClose)

        self.__activeCommand : Optional[Command] = None
        self.paneCommandParameters.Collapse()
        self.paneStartingParameters.Collapse()
        self.panelSpacing.Hide()
        self.paneStartingParameters.Show()
        self.__onScrollSizeChange(None, True)




    # Additional methods for GetValue-like behaviour (pitch, anim start, anim end, target char index)
    def GetPitch(self) -> int:
        selection = self.choiceMainPitch.GetSelection()
        if selection == NOT_FOUND:
            return 0
        return selection + 1
    
    def __convertInternalToExternalAnimation(self, manager : AnimationManager, nameInternal : str) -> Optional[str]:
        if nameInternal in manager.getListAnimations():
            return manager.getRawAnimationName(manager.getListAnimations().index(nameInternal), False)
        return None

    def GetAnimationStart(self) -> str:
        activeId = self.__getActiveCharId()
        selection = self.choiceAnimOnStart.GetSelection()
        if activeId == None or selection == NOT_FOUND or selection == 0:
            return "NONE"
        
        nameAnimation : Optional[str] = self.__convertInternalToExternalAnimation(self.__animManagers[self.__animCharIds.index(activeId)], self.choiceAnimOnStart.GetStringSelection())
        if nameAnimation == None:
            return "NONE"
        return nameAnimation

    def GetAnimationEnd(self) -> str:
        activeId = self.__getActiveCharId()
        selection = self.choiceAnimOnEnd.GetSelection()
        if activeId == None or selection == NOT_FOUND or selection == 0:
            return "NONE"
        
        nameAnimation : Optional[str] = self.__convertInternalToExternalAnimation(self.__animManagers[self.__animCharIds.index(activeId)], self.choiceAnimOnEnd.GetStringSelection())
        if nameAnimation == None:
            return "NONE"
        return nameAnimation

    def GetCharacterId(self) -> int:
        activeId = self.__getActiveCharId()
        if activeId == None:
            return 0
        return activeId



    def choiceTargetCharacterOnChoice(self, event):
        self.__updateAnimationToggles()
        return super().choiceTargetCharacterOnChoice(event)

    def choiceAnimOnEndOnChoice(self, event):
        self.__updateCharacterPreview()
        return super().choiceAnimOnEndOnChoice(event)
    
    def choiceAnimOnStartOnChoice(self, event):
        self.__updateCharacterPreview()
        return super().choiceAnimOnStartOnChoice(event)

    def __getActiveCharId(self) -> Optional[int]:
        selected = self.choiceTargetCharacter.GetSelection()
        if selected == NOT_FOUND or selected == 0:
            return None
        
        return self.__animCharIds[selected - 1]
    
    def btnTogglePreviewOnButtonClick(self, event):
        self.__targetAnimPreviewIsStart = not(self.__targetAnimPreviewIsStart)
        self.__updateCharacterPreview()
        return super().btnTogglePreviewOnButtonClick(event)

    def __updateCharacterPreview(self):
        targetChoice : Choice = None

        if self.__targetAnimPreviewIsStart:
            self.bitmapCharPreview.GetParent().SetLabel("Character Preview - Start")
            targetChoice = self.choiceAnimOnStart
        else:
            self.bitmapCharPreview.GetParent().SetLabel("Character Preview - End")
            targetChoice = self.choiceAnimOnEnd
        
        if self.__animManagerTargetPreview == None or targetChoice.GetSelection() == NOT_FOUND or targetChoice.GetSelection() == 0:
            # Clear the bitmap
            self.bitmapCharPreview.SetBitmap(NullBitmap)
            if self.__animManagerTargetPreview != None:
                self.__animManagerTargetPreview.setAnimationByIndex(-1)
        else:
            self.__animManagerTargetPreview.setAnimationByIndex(targetChoice.GetSelection() - 1)
            self.__animManagerTargetPreview.setDestinationBitmap(self.bitmapCharPreview)

    def __updateAnimationToggles(self):
        """Updates selectable animations from TalkScript parameter box.
        """
        activeId = self.__getActiveCharId()

        # Fetch last animation names if selected
        lastSelectedStartName : Optional[str] = None
        lastSelectedEndName : Optional[str] = None

        if self.choiceAnimOnStart.GetSelection() != NOT_FOUND:
            lastSelectedStartName = self.choiceAnimOnStart.GetStringSelection()
        if self.choiceAnimOnEnd.GetSelection() != NOT_FOUND:
            lastSelectedEndName = self.choiceAnimOnEnd.GetStringSelection()

        # Clear active ctrl
        self.choiceAnimOnEnd.Clear()
        self.choiceAnimOnStart.Clear()

        choices = ["(Continue last)"]
        if activeId != None:
            manager = self.__animManagers[self.__animCharIds.index(activeId)]
            self.__animManagerTargetPreview = manager
            choices += manager.getListAnimations()
        else:
            self.__animManagerTargetPreview = None
        
        
        self.choiceAnimOnStart.SetItems(list(choices))
        self.choiceAnimOnEnd.SetItems(list(choices))
        
        if lastSelectedStartName in choices:
            self.choiceAnimOnStart.Select(choices.index(lastSelectedStartName))
        else:
            self.choiceAnimOnStart.Select(0)
        
        if lastSelectedEndName in choices:
            self.choiceAnimOnEnd.Select(choices.index(lastSelectedEndName))
        else:
            self.choiceAnimOnEnd.Select(0)

        self.__updateCharacterPreview()

    def btnCancelOnButtonClick(self, event):
        self.__animTimer.Stop()
        return super().btnCancelOnButtonClick(event)
    
    def btnConfirmOnButtonClick(self, event):
        self.__animTimer.Stop()
        return super().btnConfirmOnButtonClick(event)

    def __updateActiveAnimation(self, event : Any):
        if self.__animManagerCharPreview != None:
            self.__animManagerCharPreview.update()
        if self.__animManagerTargetPreview != None:
            self.__animManagerTargetPreview.update()
        if self.__forceUpdate and self._isSafeToRead:
            self._updatePreview()

        if event != None:
            event.Skip()

    def __onClose(self, event):
        self.__animTimer.Stop()
        event.Skip()

    def __enableCommandPane(self):
        self.paneCommandParameters.Show()
        self.staticlinePaneDivider.Show()
        self.__onScrollSizeChange(self.paneCommandParameters, self.paneCommandParameters.IsCollapsed())

    def __disableCommandPane(self):
        self.paneCommandParameters.Hide()
        self.staticlinePaneDivider.Hide()
        self.__onScrollSizeChange(self.paneCommandParameters, True)
    
    def __ensureCommandPaneEnabled(self):
        """Ensures the command pane is visible in the collapsible panel.
        """
        if not(self.paneCommandParameters.IsShown()):
            self.__enableCommandPane()
    
    def __ensureCommandPaneDisabled(self):
        """Ensures the command pane is hidden in the collapsible panel.
        """
        if self.paneCommandParameters.IsShown():
            self.__disableCommandPane()
    
    def __repopulateAnimChoices(self, target : Choice, wasSafe : bool, manager : AnimationManager, defaultAnimationName : Optional[str] = None, defaultAnimationIndex : Optional[int] = None) -> bool:
        defaultAnimation : Optional[str] = defaultAnimationName
        if defaultAnimationIndex != None:
            if 0 <= defaultAnimationIndex < len(manager.getListAnimations()):
                defaultAnimation = manager.getListAnimations()[defaultAnimationIndex]
            else:
                defaultAnimation = None

        safeVerified : bool = False
        target.Clear()
        if (wasSafe and defaultAnimation == None) or (wasSafe and defaultAnimation in manager.getListSafeAnimations()):
            options : List[str] = manager.getListSafeAnimations()
            safeVerified = True
        else:
            options : List[str] = manager.getListAnimations()
        target.SetItems(options)

        if defaultAnimation != None:
            if defaultAnimation not in options:
                idxDefault = 0
            else:
                idxDefault = options.index(defaultAnimation)

            target.Select(idxDefault)
            manager.setAnimationByIndex(manager.getTargetAnimation(idxDefault, safeVerified))
        else:
            manager.setAnimationByIndex(-1)
            if len(options) > 0:
                target.Select(0)
                manager.setAnimationByIndex(0)
        return safeVerified

    def checkSafeAnimOnlyOnCheckBox(self, event):
        isChoiceSafe = self.__repopulateAnimChoices(self.choiceChangeAnimAnimName, self.checkSafeAnimOnly.IsChecked(), self.__animManagerCharPreview, defaultAnimationName=self.__activeCommand.nameAnimation)
        if not(isChoiceSafe) and self.checkSafeAnimOnly.IsChecked():
            # TODO - Warning that we can't switch to safe animations because this animation isn't safe
            pass
        
        self.checkSafeAnimOnly.SetValue(isChoiceSafe)
        return super().checkSafeAnimOnlyOnCheckBox(event)

    def choiceChangeAnimAnimNameOnChoice(self, event):
        newAnimIndex = self.choiceChangeAnimAnimName.GetSelection()
        
        # Our new animation will respect our safe animation list, so don't worry about updating that
        # Get the animation corresponding to that in use
        internalAnimIndex = self.__animManagerCharPreview.getTargetAnimation(newAnimIndex, self.checkSafeAnimOnly.GetValue())
        self.__activeCommand.nameAnimation = self.__animManagerCharPreview.getRawAnimationName(newAnimIndex, self.checkSafeAnimOnly.GetValue())
        self.__animManagerCharPreview.setAnimationByIndex(internalAnimIndex)
        return super().choiceChangeAnimAnimNameOnChoice(event)

    def choiceChangeAnimCharNameOnChoice(self, event):
        newCharIndex = self.choiceChangeAnimCharName.GetSelection()

        # If we haven't changed anything, leave this prompt
        self.__activeCommand : CommandSwitchAnimation
        if self.__activeCommand.idChar == self.__animCharIds[newCharIndex]:
            return
        else:
            self.__activeCommand.idChar = self.__animCharIds[newCharIndex]
        
        self.__setupAnimEditingApplyOptionsForActive()
        return super().choiceChangeAnimCharNameOnChoice(event)

    def __setupAnimEditingApplyOptionsForActive(self):
        # Clear current animation choices, ensure that the active animation is in view
        self.choiceChangeAnimAnimName.Clear()
        self.__animManagerCharPreview = self.__animManagers[self.__animCharIds.index(self.__activeCommand.idChar)]
        self.__animManagerCharPreview.setDestinationBitmap(self.bitmapPreviewAnim)

        # Populate animation choices
        # If the animation name attached to this command isn't valid, force it to be valid
        if self.__activeCommand.nameAnimation not in self.__animManagerCharPreview.getListAnimations():
            self.__activeCommand.nameAnimation = self.__animManagerCharPreview.getRawAnimationName(0, False)
        
        self.checkSafeAnimOnly.SetValue(self.__repopulateAnimChoices(self.choiceChangeAnimAnimName, self.checkSafeAnimOnly.IsChecked(), self.__animManagerCharPreview, defaultAnimationName=self.__activeCommand.nameAnimation))

    def __workaroundSizerBug(self):
        self.Freeze()
        if not(self.paneCommandParameters.IsCollapsed()):
            self.paneCommandParameters.Collapse()
            self.paneCommandParameters.Collapse(collapse=False)
            self.Layout()
        self.Thaw()

    def __setupAnimEditing(self, command : CommandSwitchAnimation):
        self.__workaroundSizerBug()
        if len(self.__animCharIds) == 0:
            return

        # If the character is out of range, force it to be in range
        if command.idChar not in self.__animCharIds:
            command.idChar = self.__animCharIds[0]
            self.choiceChangeAnimCharName.Select(0)
        else:
            self.choiceChangeAnimCharName.Select(self.__animCharIds.index(command.idChar))
        
        self.__activeCommand = command
        self.__setupAnimEditingApplyOptionsForActive()

    def __setupDelayEditing(self, command : CommandDelayPlayback):
        self.__workaroundSizerBug()

        # Correct for bad amount of frames
        if command.frames < 0 or command.frames > 790:
            command.frames = 0
        
        closestFrame = round(command.frames / 10)
        command.frames = closestFrame * 10
        self.choiceFrames.Select(closestFrame)

    def __applyPaneLayoutForCommand(self, command : Optional[Command]):
        """Modifies the active layout to match that of the command.
        This method will not layout the sizers, so call that afterwards.

        Args:
            command (Optional[Command]): Command to be modified. If command is None the pane will be disabled.
        """
        if command == self.__activeCommand:
            return
        
        if type(command) == CommandDelayPlayback:
            self.panelSwitchAnimOptions.Disable()
            self.panelSwitchAnimOptions.Hide()
            self.panelSwitchDelayOptions.Enable()
            self.panelSwitchDelayOptions.Show()
            self.__setupDelayEditing(command)
            
        elif type(command) == CommandSwitchAnimation:
            self.panelSwitchAnimOptions.Enable()
            self.panelSwitchAnimOptions.Show()
            self.panelSwitchDelayOptions.Disable()
            self.panelSwitchDelayOptions.Hide()
            self.__setupAnimEditing(command)

        else:
            self.panelSwitchAnimOptions.Disable()
            self.panelSwitchAnimOptions.Hide()
            self.panelSwitchDelayOptions.Disable()
            self.panelSwitchDelayOptions.Hide()
            command = None

        self.__activeCommand = command

    def __onScrollSizeChange(self, targetPane : Optional[CollapsiblePane], wasPaneCollapsed : bool):
        """Updates the layout of collapsible panels when the state of the pane changes. This method will also ensure only one pane can ever be opened at once.

        Args:
            targetPane (Optional[CollapsiblePane]): Pane that was modified last. If None, the layout will just be refreshed.
            wasPaneCollapsed (bool): True if the pane is collapsed.
        """
        self.Freeze()

        if targetPane == self.paneCommandParameters and not(wasPaneCollapsed):
            # Command pane has been opened, we'll close the talkscript one
            self.paneStartingParameters.Collapse()
            self.__animManagerTargetPreview = None
        elif targetPane == self.paneStartingParameters and not(wasPaneCollapsed):
            # Talkscript pane has been opened, we'll collapse the command one
            self.paneCommandParameters.Collapse()
            self.__animManagerCharPreview = None

        self.Layout()
        self.Refresh()
        self.Thaw()

    def _doOnTagDeleted(self, commands: List[Command]):
        if self.__activeCommand in commands:
            self._doOnTagFocusLost()
        return super()._doOnTagDeleted(commands)

    def _doOnTagFocusLost(self):
        self.__applyPaneLayoutForCommand(None)
        self.__ensureCommandPaneDisabled()
        return super()._doOnTagFocusLost()

    def _doOnTagPressed(self, command: Command):
        self.__applyPaneLayoutForCommand(command)
        if self.__activeCommand != None:
            self.__ensureCommandPaneEnabled()
        else:
            self.__ensureCommandPaneDisabled()
        return super()._doOnTagPressed(command)

    def _updatePreview(self):
        self.__forceUpdate = False
        encoded = self._getEncodedSelectedSegment()
        self.__surfPreview.fill((255,255,255))
        self.__textRenderer.setColor((0,0,0))
        self.__textRenderer.setText(encoded)
        try:
            while self.__textRenderer.getActiveState():
                self.__textRenderer.skip()
                if self.__textRenderer.isWaiting():
                    self.__textRenderer.setTap()
        except IndexError:
            logSevere("TextScroller hit bad dialogue! Check for unclosed commands.", name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)

        self.__textRenderer.draw(self.__surfPreview)
        self.bitmapPreview.SetBitmap(Bitmap.FromBuffer(RESOLUTION_NINTENDO_DS[0], RESOLUTION_NINTENDO_DS[1], tostring(self.__surfPreview, "RGB")))

        # TODO - Enforce wrapping!
        logVerbose("Preview:", self._getEncodedSelectedSegment(), name=DialogTalkScriptTextEditorRich.LOG_MODULE_NAME)

    def rich_tsOnLeftDown(self, event):
        # TODO - This is otherwise broken, it is called before the position changes...
        self.__forceUpdate = True
        super().rich_tsOnLeftDown(event)        

    def rich_tsOnText(self, event):
        super().rich_tsOnText(event)
        if self._isSafeToRead:
            self._updatePreview()

    def paneCommandParametersOnCollapsiblePaneChanged(self, event : CollapsiblePaneEvent):
        self.__onScrollSizeChange(self.paneCommandParameters, event.GetCollapsed())

        # Clear the previewer when collapsed
        if self.paneCommandParameters.IsCollapsed():
            self.__animManagerCharPreview = None

        return super().paneCommandParametersOnCollapsiblePaneChanged(event)

    def paneStartingParametersOnCollapsiblePaneChanged(self, event : CollapsiblePaneEvent):
        self.__onScrollSizeChange(self.paneStartingParameters, event.GetCollapsed())

        # Clear the previewer when collapsed
        if self.paneStartingParameters.IsCollapsed():
            self.__animManagerTargetPreview = None
        else:
            # If we're opening the starting parameter preview, we need to setup the animations
            self.__updateAnimationToggles()

        return super().paneStartingParametersOnCollapsiblePaneChanged(event)