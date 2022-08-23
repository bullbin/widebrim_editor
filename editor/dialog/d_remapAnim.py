from time import perf_counter
from typing import Any, Dict, List, Optional
from widebrim.engine.anim.image_anim.image import AnimatedImageObject
from ..nopush_editor import PickerRemapAnim
from wx import Window, Bitmap, Timer, EVT_TIMER, EVT_CLOSE, NOT_FOUND, ID_CANCEL, ID_OK, Colour
from pygame import Surface
from pygame.image import tostring

class AnimationUpdater():
    def __init__(self, image : AnimatedImageObject, destBitmap : Bitmap, timer : Timer):
        self.__activeAnimation      : AnimatedImageObject   = image
        self.__timer = timer
        self.__lastUpdateTime : float = perf_counter()
        self.__bitmap = destBitmap

        self.__activeSurf = Surface(image.getDimensions()).convert_alpha()
        self.__activeSurf.fill((0,0,0,0))
        self.__queueRedraw = False
        self.__hidden = False

    def setAnimationFromName(self, name : str) -> bool:
        # TODO - Bugfix, we want True even on changing to same anim (unlike game...)
        self.__activeAnimation.setAnimationFromName(name)
        self.__queueRedraw = True

        output = True
        if self.__activeAnimation.animActive == None:
            output = False
        elif self.__activeAnimation.animActive.name != name:
            output = False

        self.__hidden = not(output)
        return output
    
    def setAnimationFromIndex(self, idx : int) -> bool:
        self.__queueRedraw = True
        self.__hidden = not(self.__activeAnimation.setAnimationFromIndex(idx))
        return not(self.__hidden)

    def update(self):
        updateTime = perf_counter()
        if self.__activeAnimation.update((updateTime - self.__lastUpdateTime) * 1000) or self.__queueRedraw:
            self.__activeSurf.fill((0,0,0,1))
            if not(self.__hidden):
                prevPos = self.__activeAnimation.getPos()
                self.__activeAnimation.setPos((0,0))
                self.__activeAnimation.draw(self.__activeSurf)
                self.__activeAnimation.setPos(prevPos)

            bitmap = Bitmap.FromBufferRGBA(self.__activeSurf.get_width(), self.__activeSurf.get_height(), tostring(self.__activeSurf, "RGBA"))
            self.__bitmap.SetBitmap(bitmap)
        self.__lastUpdateTime = updateTime

class DialogRemapAnimation(PickerRemapAnim):
    def __init__(self, parent : Window, animSource : AnimatedImageObject, animDestination : AnimatedImageObject, remapping : Dict[str,Optional[str]]):
        super().__init__(parent)

        self.__animTimer = Timer(self)

        self.Bind(EVT_TIMER, self.__updateActiveAnimation, self.__animTimer)
        self.Bind(EVT_CLOSE, self.__onClose)

        self.__mapping = remapping
        self.__managers : List[AnimationUpdater] = []
        self.__managers.append(AnimationUpdater(animSource, self.bitmapSourceAnim, self.__animTimer))
        self.__managers.append(AnimationUpdater(animDestination, self.bitmapDestinationAnim, self.__animTimer))
        self.__animTimer.Start(1000//60, False)
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
        animNames = []
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
