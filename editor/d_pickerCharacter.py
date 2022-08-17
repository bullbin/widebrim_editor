from time import perf_counter
from typing import Dict, List, Optional, Any
from editor.asset_management.character import CharacterEntry, computeCharacterNames, getCharacters
from editor.nopush_editor import PickerBgx
from wx import Window, TreeItemId, Timer, EVT_TIMER, NullBitmap, Bitmap, EVT_CLOSE, Sizer, ID_OK, ID_CANCEL
from widebrim.engine.anim.image_anim.image import AnimatedImageObject, AnimatedImageObjectWithSubAnimation
from widebrim.engine.const import PATH_FACE_ROOT
from widebrim.engine.state.manager.state import Layton2GameState
from pygame import Surface
from pygame.image import tostring

from widebrim.madhatter.common import logSevere
from widebrim.madhatter.hat_io.asset_image.image import AnimatedImage

# TODO - Inherit from anim picker (same code)

class DialogPickerCharacter(PickerBgx):

    def __init__(self, parent : Window, state : Layton2GameState, restrictChars : Optional[List[int]] = None, charNames : Optional[List[Optional[str]]] = None, skipCompute : bool = False, allowNone : bool = False, defaultSelection : Optional[int] = None):
        super().__init__(parent)
        self.SetTitle("Change Character")
        self.timerAnimationLastUpdateTime   = 0
        self.timerAnimation                 = Timer(self)
        self.Bind(EVT_TIMER, self.__updateActiveAnimation, self.timerAnimation)
        self.Bind(EVT_CLOSE, self.__onClose)

        self.activeAnimation                : Optional[AnimatedImageObject] = None
        self.activeAnimationFrame           : Optional[Surface]             = None

        self.bitmapPreviewBackground.SetMinSize((256,-1))
        self.btnConfirmSelected.SetLabel("No selection!")
        self.btnConfirmSelected.Disable()

        self._state : Layton2GameState = state
        self._characters = getCharacters(state)
        self._output : Optional[int] = None
        self.__selectionMap : Dict[int, TreeItemId] = {}

        sizer : Sizer = self.btnImportImage.GetParent()
        sizer.Hide()

        if allowNone:
            self.btnRemoveImage.Show()
        else:
            self.btnRemoveImage.Hide()
        
        self.Layout()

        if restrictChars != None:
            for idxChar in reversed(range(len(self._characters))):
                if not(self._characters[idxChar].getIndex() in restrictChars):
                    self._characters.pop(idxChar)
                    if charNames != None:
                        charNames.pop(idxChar)

        if charNames == None:
            if skipCompute:
                charNames : List[Optional[str]] = [None] * len(self._characters)
            else:
                charNames : List[Optional[str]] = computeCharacterNames(state, self._characters)

        storedNames : List[str] = []

        for idxCharName, packCharName in enumerate(zip(self._characters, charNames)):
            char, name = packCharName
            if name == None:
                storedNames.append("Character %i" % char.getIndex())
            else:
                idxName = charNames[:idxCharName + 1].count(name)
                if idxName > 1:
                    storedNames.append("%s (%i)" % (name, idxName - 1))
                else:
                    storedNames.append(name)
    
        # TODO - Hide this
        self._treeRoot : TreeItemId = self.treeFilesystem.AddRoot("Characters")
        for char, name in zip(self._characters, storedNames):
            self.__selectionMap[char.getIndex()] = self.treeFilesystem.AppendItem(self._treeRoot, name, data=char)
        
        if defaultSelection in self.__selectionMap:
            self.treeFilesystem.SelectItem(self.__selectionMap[defaultSelection])
            char = self.treeFilesystem.GetItemData(self.__selectionMap[defaultSelection])
            if self._updatePreviewImage(char.getPathImage()):
                self._updateOutput(char)

        # TODO - Disable add buttons

    def btnConfirmSelectedOnButtonClick(self, event):
        self.EndModal(ID_OK)
        return super().btnConfirmSelectedOnButtonClick(event)

    def btnCancelOnButtonClick(self, event):
        self.EndModal(ID_CANCEL)
        return super().btnCancelOnButtonClick(event)

    def GetSelection(self) -> int:
        return self._output

    def treeFilesystemOnTreeItemActivated(self, event):
        item : TreeItemId = event.GetItem()
        if (data := self.treeFilesystem.GetItemData(item)) != None:
            data : CharacterEntry
            if self._updatePreviewImage(data.getPathImage()):
                self._updateOutput(data)

        return super().treeFilesystemOnTreeItemActivated(event)
    
    def _updateOutput(self, character : CharacterEntry):
        self._output = character.getIndex()
        self.btnConfirmSelected.Enable()
        self.btnConfirmSelected.SetLabel("Choose " + self.treeFilesystem.GetItemText(self.__selectionMap[self._output]))

    def _updatePreviewImage(self, path : str) -> bool:
        dataAnim = self._state.getFileAccessor().getData(path)
        if dataAnim == None:
            logSevere("Failed to fetch character image at", path, str="CharPick")
            return False

        def functionGetAnimationFromName(name):
            name = name.split(".")[0] + ".arc"
            resolvedPath = PATH_FACE_ROOT % name
            return self._state.getFileAccessor().getData(resolvedPath)

        tempImage = AnimatedImage.fromBytesArc(dataAnim, functionGetAnimationFromName)
        self.activeAnimation = AnimatedImageObjectWithSubAnimation.fromMadhatter(tempImage)
        if not(self.activeAnimation.setAnimationFromIndex(2)):
            self.activeAnimation.setAnimationFromIndex(1)

        self.timerAnimation.Stop()
        self.timerAnimationLastUpdateTime = perf_counter()

        self.activeAnimationFrame = None
        self.__updateActiveAnimation(None)
        self.timerAnimation.Start(1000//60, False)
        self._pathOut = path
        self.btnConfirmSelected.Enable()
        self.bitmapPreviewBackground.Show()
        self.bitmapPreviewBackground.SetMinSize((256,self.activeAnimation.getDimensions()[1]))
        self.Layout()
        return True

    def __updateActiveAnimation(self, event : Optional[Any]):
        if self.activeAnimation == None:
            if self.activeAnimationFrame != None:
                self.activeAnimationFrame = None
                self.bitmapPreviewBackground.SetBitmap(NullBitmap)
            return
        
        updateTime = perf_counter()
        
        # TODO - Need more reliable way - face animation can cause no update to happen (in theory)
        newFrame = self.activeAnimation.getActiveFrame()

        if self.activeAnimation.update((updateTime - self.timerAnimationLastUpdateTime) * 1000) or (self.activeAnimationFrame == None and newFrame != None):
            self.activeAnimationFrame = newFrame

            surfCopy = Surface((self.activeAnimationFrame.get_width(), self.activeAnimationFrame.get_height())).convert_alpha()
            surfCopy.fill((255,255,255,0))
            self.activeAnimation.draw(surfCopy)

            if self.activeAnimationFrame == None:
                self.bitmapPreviewBackground.SetBitmap(NullBitmap)
            else:
                bitmap = Bitmap.FromBufferRGBA(surfCopy.get_width(), surfCopy.get_height(), tostring(surfCopy, "RGBA"))
                self.bitmapPreviewBackground.SetBitmap(bitmap)
        
        self.timerAnimationLastUpdateTime = updateTime
        
        if event != None:
            event.Skip()
    
    def __onClose(self, event): 
        self.timerAnimation.Stop()
        event.Skip()