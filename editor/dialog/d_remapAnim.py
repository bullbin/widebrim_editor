from typing import Any, Dict, List, Optional
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from editor.gui_helpers.anim_bitmap import AnimationUpdater
from ..nopush_editor import PickerRemapAnim
from wx import Window, Timer, EVT_TIMER, EVT_CLOSE, NOT_FOUND, ID_CANCEL, ID_OK, Colour

class DialogRemapAnimation(PickerRemapAnim):
    def __init__(self, parent : Window, animSource : AnimatedImageObject, animDestination : AnimatedImageObject, remapping : Dict[str,Optional[str]]):
        super().__init__(parent)

        self.__animTimer = Timer(self)
        self.__animTimer.Start(1000//60, False)

        self.Bind(EVT_TIMER, self.__updateActiveAnimation, self.__animTimer)
        self.Bind(EVT_CLOSE, self.__onClose)

        self.__mapping = remapping
        self.__managers : List[AnimationUpdater] = []
        self.__managers.append(AnimationUpdater(animSource, self.bitmapSourceAnim))
        self.__managers.append(AnimationUpdater(animDestination, self.bitmapDestinationAnim))
        self.listboxSourceAnim.Clear()
        self.choiceDestinationAnim.Clear()
        
        hasMissing = False
        for key in remapping:
            newIdx = self.listboxSourceAnim.Append(key)
            if remapping[key] != None:
                self.__verifyListboxIndex(newIdx)
            else:
                hasMissing = True

        x = 0
        while True:
            # TODO - Hide bad, remove bad maps from both sides
            if animDestination.setAnimationFromIndex(x):
                self.choiceDestinationAnim.Append(animDestination.animActive.name)
                x += 1
            else:
                break
        
        # TODO - Should be fine to index zero - this shouldn't be called yet...
        if len(remapping) > 0:
            self.listboxSourceAnim.SetSelection(0)
            self.__updateActiveSelection()
        
        if not(hasMissing):
            self.__enableConfirm()

        for manager in self.__managers:
            manager.update()
    
    def __onClose(self, event):
        self.__animTimer.Stop()
        event.Skip()
    
    def btnCancelOnButtonClick(self, event):
        self.__animTimer.Stop()
        self.EndModal(ID_CANCEL)
        return super().btnCancelOnButtonClick(event)
    
    def btnConfirmOnButtonClick(self, event):
        self.__animTimer.Stop()
        self.EndModal(ID_OK)
        return super().btnConfirmOnButtonClick(event)

    def __enableConfirm(self):
        self.btnConfirm.Enable()
        self.btnConfirm.SetLabel("Confirm")
        self.Layout()

    def __verifyListboxIndex(self, idxEntry : int):
        self.listboxSourceAnim.SetItemBackgroundColour(idxEntry, Colour(0,255,0))

    def __updateActiveSelection(self):
        if self.listboxSourceAnim.GetSelection() != NOT_FOUND:
            animNameSource = self.listboxSourceAnim.GetString(self.listboxSourceAnim.GetSelection())
            animNameDest = self.__mapping[animNameSource]
            
            animNameSource, self.__managers[0].setAnimationFromName(animNameSource)
            if animNameDest == None:
                if self.choiceDestinationAnim.GetCount() > 0:
                    self.__managers[1].setAnimationFromIndex(0)
                    self.choiceDestinationAnim.SetSelection(0)
                else:
                    self.choiceDestinationAnim.SetSelection(NOT_FOUND)
            else:
                self.__managers[1].setAnimationFromName(animNameDest)
                self.choiceDestinationAnim.SetSelection(self.choiceDestinationAnim.FindString(animNameDest))

    def choiceDestinationAnimOnChoice(self, event):
        if self.listboxSourceAnim.GetSelection() != NOT_FOUND:
            animNameSource = self.listboxSourceAnim.GetString(self.listboxSourceAnim.GetSelection())
            animNameDest = self.choiceDestinationAnim.GetStringSelection()
            self.__mapping[animNameSource] = animNameDest
            self.__managers[1].setAnimationFromName(animNameDest)
            self.__verifyListboxIndex(self.listboxSourceAnim.GetSelection())

            hasMissing = False
            for key in self.__mapping:
                if self.__mapping[key] == None:
                    hasMissing = True
            if not(hasMissing):
                self.__enableConfirm()
        return super().choiceDestinationAnimOnChoice(event)

    def listboxSourceAnimOnListBox(self, event):
        self.__updateActiveSelection()
        return super().listboxSourceAnimOnListBox(event)

    def __updateActiveAnimation(self, event : Any):
        for manager in self.__managers:
            manager.update()

        if event != None:
            event.Skip()
