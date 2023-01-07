from .d_wip_talkscript_rich import DialogTalkScriptTextEditorRich, CharacterEntry, AnimatedImageObject, Layton2GameState, Command, CommandSetPitch, CommandSwitchAnimation
from typing import Dict, Optional, Tuple, List, Any
from editor.gui_helpers.anim_bitmap import AnimationUpdater
from wx import CollapsiblePane, CollapsiblePaneEvent, Window, Timer, EVT_TIMER, EVT_CLOSE

class AnimationManager():
    def __init__(self, anim : Optional[AnimatedImageObject], entry : CharacterEntry, name : Optional[str] = None):
        # TODO - Not fully representative. Comes from e_script_event
        def isNameGood(name) -> bool:
            if len(name) > 0:
                if name[0] != "*" and name != "Create an Animation":
                    return True
            return False

        self.__anim : Optional[AnimatedImageObject] = anim
        self.__entry : CharacterEntry = entry
        if name == None:
            self.__name = "No name - ID %d" % self.__entry.getIndex()
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

class DialogTalkScriptEditorRichWithTags(DialogTalkScriptTextEditorRich):
    def __init__(self, parent: Optional[Window], state: Layton2GameState, stringTalkscript: str = "", characters : List[Tuple[CharacterEntry, Optional[str], Optional[AnimatedImageObject]]] = []):
        super().__init__(parent, state, stringTalkscript, characters)

        self.__animTimer = Timer(self)
        self.__animTimer.Start(1000//60, False)
        
        self.__charAnims        : Optional[AnimatedImageObject] = [None]
        self.__charPreviewAnims : List[AnimationUpdater]        = [AnimationUpdater(None, self.bitmapPreviewAnim)]
        self.__charIds          : List[int]                     = [0]
        self.__charNames        : List[str]                     = ["No character"]

        self.__commandEditCharPreview : Optional[AnimationUpdater] = None

        for entry, name, anim in characters:
            self.__charIds.append(entry.getIndex())
            if name == None:
                self.__charNames.append("No name - ID %s" % entry.getIndex())
            else:
                self.__charNames.append(name)
            self.__charAnims.append(anim)
            self.__charPreviewAnims.append(AnimationUpdater(anim, self.bitmapPreviewAnim))
        
        self.choiceChangeAnimCharName.SetItems(self.__charNames)
        self.choiceTargetCharacter.SetItems(self.__charNames)

        self.Bind(EVT_TIMER, self.__updateActiveAnimation, self.__animTimer)
        self.Bind(EVT_CLOSE, self.__onClose)

        self.__activeCommand : Optional[Command] = None
        self.paneCommandParameters.Collapse()
        self.paneStartingParameters.Collapse()
        self.panelSpacing.Hide()
        self.paneStartingParameters.Show()
        self.__onScrollSizeChange(None, True)
    
    def __updateActiveAnimation(self, event : Any):
        if self.__commandEditCharPreview != None:
            self.__commandEditCharPreview.update()

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

    def choiceChangeAnimAnimNameOnChoice(self, event):
        #newCharId = self.choiceChangeAnimCharName.GetSelection()
        #self.__activeCommand : CommandSwitchAnimation
        #self.__activeCommand.idChar = self




        return super().choiceChangeAnimAnimNameOnChoice(event)
    
    def __repopulateAnimChoices():
        pass

    def choiceChangeAnimCharNameOnChoice(self, event):
        newCharId = self.choiceChangeAnimCharName.GetSelection()
        self.__activeCommand : CommandSwitchAnimation
        self.__activeCommand.idChar = self.__charIds[newCharId]

        

        # TODO - Set animation to blank one
        if self.__commandEditCharPreview != self.__charPreviewAnims[newCharId]:



            #self.__commandEditCharPreview.triggerRedraw()
            pass

        self.__commandEditCharPreview = self.__charPreviewAnims[newCharId]
        
        
        
        #self.__commandEditCharPreview.triggerRedraw()


        return super().choiceChangeAnimCharNameOnChoice(event)

    def __setupAnimEditing(self, command : CommandSwitchAnimation):
        print("Edit anim", command)
        if command.idChar not in self.__charIds:
            command.idChar = 0
        
        indexCharItem = self.__charIds.index(command.idChar)
        self.choiceChangeAnimCharName.Select(indexCharItem)

        dictAnims : Dict[int, str] = {0:"Create an Animation"}
        targetAnimation : Optional[int] = None

        anim : Optional[AnimatedImageObject] = self.__charAnims[indexCharItem]
        if anim == None:
            dictAnims[0] = "Invalid"
        else:
            indexAnim = 1
            while anim.setAnimationFromIndex(indexAnim):
                dictAnims[indexAnim] = anim.animActive.getName()
                if anim.animActive.getName() == command.nameAnimation:
                    targetAnimation = indexAnim
                indexAnim += 1
        
        self.__commandEditCharPreview = self.__charPreviewAnims[indexCharItem]
        self.__commandEditCharPreview.triggerRedraw(True)
        self.choiceChangeAnimAnimName.SetItems(list(dictAnims.values()))
        
        if targetAnimation == None:
            self.choiceChangeAnimAnimName.Select(0)
            self.__commandEditCharPreview.setAnimationFromIndex(-1)
        else:
            self.choiceChangeAnimAnimName.Select(targetAnimation)
            self.__commandEditCharPreview.setAnimationFromIndex(targetAnimation)

    def __setupPitchEditing(self, command : CommandSetPitch):
        print("Edit pitch", command)

    def __applyPaneLayoutForCommand(self, command : Optional[Command]):
        """Modifies the active layout to match that of the command.
        This method will not layout the sizers, so call that afterwards.

        Args:
            command (Optional[Command]): Command to be modified. If command is None the pane will be disabled.
        """
        if command == self.__activeCommand:
            return
        
        if type(command) == CommandSetPitch:
            self.panelSwitchAnimOptions.Disable()
            self.panelSwitchAnimOptions.Hide()
            self.panelSwitchPitchOptions.Enable()
            self.panelSwitchPitchOptions.Show()
            self.__setupPitchEditing(command)
            
        elif type(command) == CommandSwitchAnimation:
            self.panelSwitchAnimOptions.Enable()
            self.panelSwitchAnimOptions.Show()
            self.panelSwitchPitchOptions.Disable()
            self.panelSwitchPitchOptions.Hide()
            self.__setupAnimEditing(command)

        else:
            self.panelSwitchAnimOptions.Disable()
            self.panelSwitchAnimOptions.Hide()
            self.panelSwitchPitchOptions.Disable()
            self.panelSwitchPitchOptions.Hide()
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
        elif targetPane == self.paneStartingParameters and not(wasPaneCollapsed):
            # Talkscript pane has been opened, we'll collapse the command one
            self.paneCommandParameters.Collapse()

        self.Layout()
        self.Refresh()
        self.Thaw()

    def _doOnTagDeleted(self, commands: List[Command]):
        if self.__activeCommand in commands:
            self._doOnTagFocusLost()
        return super()._doOnTagDeleted(commands)

    def _doOnTagFocusLost(self):
        if self.__activeCommand != None:
            print("Tag removed from history!")
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

    def paneCommandParametersOnCollapsiblePaneChanged(self, event : CollapsiblePaneEvent):
        self.__onScrollSizeChange(self.paneCommandParameters, event.GetCollapsed())
        return super().paneCommandParametersOnCollapsiblePaneChanged(event)

    def paneStartingParametersOnCollapsiblePaneChanged(self, event : CollapsiblePaneEvent):
        self.__onScrollSizeChange(self.paneStartingParameters, event.GetCollapsed())
        return super().paneStartingParametersOnCollapsiblePaneChanged(event)