from typing import Dict, List, Optional, Tuple
from editor.asset_management.room import PlaceGroup, getPackPathForPlaceIndex
from editor.e_room.main import FramePlaceEditor
from widebrim.engine.const import PATH_DB_PLACEFLAG, PATH_PROGRESSION_DB
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.common import log, logSevere
from widebrim.madhatter.hat_io.asset import File
from widebrim.madhatter.hat_io.asset_dat.place import PlaceData, PlaceDataNds
from widebrim.gamemodes.room.const import PATH_PACK_PLACE
from widebrim.madhatter.hat_io.asset_placeflag import PlaceFlag
from wx import TreeItemId
from re import match

class FramePlaceConditionalEditor(FramePlaceEditor):

    TEXT_BTN_CONDITION_EXISTS       = "Edit condition..."
    TEXT_BTN_CONDITION_MISSING      = "New condition..."
    TEXT_BTN_ADD_STATE_TOO_MANY     = "No more states!"
    TEXT_BTN_ADD_STATE_REMAINING    = "Add state below..."

    def __init__(self, parent, filesystem: WriteableFilesystemCompatibilityLayer, state: Layton2GameState, groupPlace: PlaceGroup):
        super().__init__(parent, filesystem, state, groupPlace)
        self.__treeToPlaceData : Dict[TreeItemId, PlaceData] = {}
        self.__activeItemHasCondition : bool = False
        self.updateInterfaceButtons()
    
    def updateInterfaceButtons(self):

        if self._getActiveState() != None:
            
            indexItem = self._dataPlace.index(self._getActiveState())

            if indexItem != 0:
                self.btnAddCondition.Enable()
                self.btnEditChapter.Enable()
            else:
                self.btnAddCondition.Disable()
                self.btnEditChapter.Disable()

            if self.__activeItemHasCondition:
                self.btnAddCondition.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_CONDITION_EXISTS)
            else:
                self.btnAddCondition.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_CONDITION_MISSING)
            
            if 1 < indexItem:
                self.btnMoveUp.Enable()
            else:
                self.btnMoveUp.Disable()

            if 1 <= indexItem < len(self._dataPlace) - 1:
                self.btnMoveDown.Enable()
            else:
                self.btnMoveDown.Disable()

            if indexItem != 0:
                self.btnDelete.Enable()
            else:
                self.btnDelete.Disable()

            if len(self._dataPlace) < 16:
                self.btnAddState.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_ADD_STATE_REMAINING)
                self.btnDuplicate.Enable()
                self.btnAddState.Enable()
            else:
                self.btnAddState.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_ADD_STATE_REMAINING)
                self.btnDuplicate.Disable()
                self.btnAddState.Disable()
        else:
            self.btnAddCondition.Disable()
            self.btnAddState.Disable()
            self.btnMoveUp.Disable()
            self.btnMoveDown.Disable()
            self.btnDelete.Disable()
            self.btnDuplicate.Disable()
            self.btnEditChapter.Disable()

    def ensureLoaded(self):
        if self._loaded:
            return

        pathPack = getPackPathForPlaceIndex(self._groupPlace.indexPlace)
        pack = self._filesystem.getPack(pathPack)
        for index in self._groupPlace.indicesStates:
            loadedPlace = PlaceDataNds()
            if (data := pack.getFile(PATH_PACK_PLACE % (self._groupPlace.indexPlace, index))) != None:
                loadedPlace.load(data)
            self._dataPlace.append(loadedPlace)

        self.Freeze()
        self.__generateList()
        self.reloadActivePlaceData()
        self.refreshExitImages()
        self._loaded = True
        self.Thaw()
    
    def treeStateProgressionOnTreeSelChanged(self, event):
        if self._lastValidSuggestion != self._getActiveState():
            self.btnRoomCreateNew.Disable()
            self.btnRoomDelete.Disable()
            self.checkRoomApplyToAll.Disable()
            self.reloadActivePlaceData()
            self.updateInterfaceButtons()
        return super().treeStateProgressionOnTreeSelChanged(event)
    
    def getChaptersFromItem(self, item : TreeItemId) -> Optional[Tuple[int,int]]:
        if item.IsOk():
            nameItem = self.treeStateProgression.GetItemText(item)
            matching = match("State [0-9]+: Chapter ([0-9]+) to ([0-9]+)", nameItem)
            if matching != None and matching.lastindex >= 2:
                return (int(matching[1]), int(matching[2]))
        return None

    def __generateList(self):
        self.__activeItemHasCondition = False

        placeFlag = PlaceFlag()
        if (data := self._filesystem.getPackedData(PATH_PROGRESSION_DB, PATH_DB_PLACEFLAG)):
            placeFlag.load(data)

        self.treeStateProgression.DeleteAllItems()
        rootTreeProgression = self.treeStateProgression.AddRoot("You shouldn't be able to see this!")
        
        print(self._dataPlace)
        selection = None
        for trueIndex, index in enumerate(self._groupPlace.indicesStates):
            if index == 0:
                selection = self.treeStateProgression.AppendItem(rootTreeProgression, "Default State", data=self._dataPlace[trueIndex])
                self.__treeToPlaceData[selection] = self._dataPlace[trueIndex]
            else:
                
                entry = placeFlag.entries[self._groupPlace.indexPlace]
                chapterEntry = entry.getEntry(index)
                chapterMin = chapterEntry.chapterStart
                chapterMax = chapterEntry.chapterEnd

                subroomRoot = self.treeStateProgression.AppendItem(rootTreeProgression, "State " + str(index) + (": Chapter %i to %i" % (chapterMin, chapterMax)),
                                                                   data=self._dataPlace[trueIndex])
                self.__treeToPlaceData[subroomRoot] = self._dataPlace[trueIndex]

                if chapterMin == 0 or chapterMax == 0:
                    self.treeStateProgression.AppendItem(subroomRoot, "Terminate subroom discovery on encounter")
                    continue
                
                counterEntry = entry.getCounterEntry(index)
                if counterEntry.indexEventCounter != 0:
                    if counterEntry.decodeMode == 0:
                        # Value same as val at index
                        self.treeStateProgression.AppendItem(subroomRoot, "Variable " + str(counterEntry.indexEventCounter) + " equals " + str(counterEntry.unk1))
                    elif counterEntry.decodeMode == 1:
                        # Value different than val at index
                        self.treeStateProgression.AppendItem(subroomRoot, "Variable " + str(counterEntry.indexEventCounter) + " doesn't equal " + str(counterEntry.unk1))
                    elif counterEntry.decodeMode == 2:
                        # Value less than val at index
                        self.treeStateProgression.AppendItem(subroomRoot, "Variable " + str(counterEntry.indexEventCounter) + " greater than or equal to " + str(counterEntry.unk1))
                    else:
                        self.treeStateProgression.AppendItem(subroomRoot, "Misconfigured counter condition")

        if selection != None:
            self.treeStateProgression.SelectItem(selection)
    
    def _getActiveState(self) -> Optional[PlaceDataNds]:
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if not(self.treeStateProgression):
            return self._lastValidSuggestion

        selection : TreeItemId = self.treeStateProgression.GetSelection()
        if selection.IsOk() and selection in self.__treeToPlaceData:
            # print(self.treeStateProgression.GetItemData(selection), self.__treeToPlaceData[selection])
            # TODO - Variable branch mapping
            self._lastValidSuggestion = self.__treeToPlaceData[selection]
            if self.treeStateProgression.GetChildrenCount(selection) > 0:
                self.__activeItemHasCondition = True
            else:
                self.__activeItemHasCondition = False
        return self._lastValidSuggestion
    
    def syncChanges(self):

        def nonDestructiveWritePackChanges(dataOutput : List[PlaceData]):
            # Preserve all other files (potentially changed) while changing ours
            # Get pack to overwrite
            pathPack = getPackPathForPlaceIndex(self._groupPlace.indexPlace)
            pack = self._filesystem.getPack(pathPack)

            datPlace = PATH_PACK_PLACE.replace("%i", "([0-9]*)")

            contents : Dict[int, Dict[int, File]] = {}
            for file in pack.files:
                # Remove files to be overwritten from data
                if (result := match(datPlace, file.name)) != None:
                    indexPlace = int(result.group(1))
                    indexSubPlace = int(result.group(2))
                    
                    if indexPlace != self._groupPlace.indexPlace:
                        if indexPlace not in contents:
                            contents[indexPlace] = {}
                        
                        contents[indexPlace][indexSubPlace] = file

            contents[self._groupPlace.indexPlace] = {}
            for indexSubPlace, fileData in enumerate(dataOutput):
                fileData.save()
                contents[self._groupPlace.indexPlace][indexSubPlace] = File(name=PATH_PACK_PLACE % (self._groupPlace.indexPlace, indexSubPlace), data=fileData.data)

            pack.files = []
            indicesPlaces = list(contents.keys())
            indicesPlaces.sort()
            for indexPlace in indicesPlaces:
                indicesSubPlaces = list(contents[indexPlace].keys())
                indicesSubPlaces.sort()
                for indexSubPlace in indicesSubPlaces:
                    pack.files.append(contents[indexPlace][indexSubPlace])

            pack.save()
            pack.compress()
            self._filesystem.writeableFs.replaceFile(pathPack, pack.data)
            log("Updated room information -", pathPack)

        def nonDestructiveWriteAutoEvent():
            pass

        def nonDestructiveWritePlaceFlag():
            pass

        rootChild, cookie = self.treeStateProgression.GetFirstChild(self.treeStateProgression.GetRootItem())
        dataOutput : List[PlaceData] = []
        chapterOutput = []
        while rootChild.IsOk():
            dataOutput.append(self.treeStateProgression.GetItemData(rootChild))
            nameItem = self.treeStateProgression.GetItemText(rootChild)
            if "Default" in nameItem:
                # Default state - TODO What should this be by default?
                chapterOutput.append((0,0))
            else:
                # Other states
                chapters = self.getChaptersFromItem(rootChild)
                if chapters == None:
                    logSevere("Failed to decode", nameItem)
                    chapterMin = 0
                    chapterMax = 0
                else:
                    chapterMin, chapterMax = chapters
                chapterOutput.append((chapterMin, chapterMax))
            rootChild = self.treeStateProgression.GetNextSibling(rootChild)
        
        nonDestructiveWritePackChanges(dataOutput)

    # Calling updateInterfaceButtons will ensure these are correct in context, but it doesn't hurt to check
    def btnAddConditionOnButtonClick(self, event):
        return super().btnAddConditionOnButtonClick(event)

    def __addBelow(self, above : TreeItemId, duplicateAbove : bool = False):
        if len(self._dataPlace) < 16:
            rootChild, cookie = self.treeStateProgression.GetFirstChild(self.treeStateProgression.GetRootItem())
            target : Tuple[int, TreeItemId] = (-1, None)
            indexItem = 0
            while rootChild.IsOk():
                if rootChild == above:
                    target = (indexItem, rootChild)
                elif target[1] != None:
                    nameItem = self.treeStateProgression.GetItemText(rootChild)
                    nameItem = ("State %i:" % (indexItem + 1)) + nameItem.split(":")[1]
                    self.treeStateProgression.SetItemText(rootChild, nameItem)
                rootChild = self.treeStateProgression.GetNextSibling(rootChild)
                indexItem += 1

            if target[0] == -1:
                logSevere("Failed to find correct sibling state!")
                return

            chapterMin = 999
            chapterMax = 999
            if duplicateAbove:
                chapters = self.getChaptersFromItem(above)
                if chapters != None:
                    chapterMin, chapterMax = chapters
                else:
                    logSevere("GetChapters called on incorrect item", self.treeStateProgression.GetItemText(above))

            newItem = self.treeStateProgression.InsertItem(self.treeStateProgression.GetRootItem(), above, "State %i: Chapter %i to %i" % (target[0] + 1, chapterMin, chapterMax))
            newPlaceDataEntry = PlaceDataNds()

            if duplicateAbove:
                placeData : PlaceDataNds = self.treeStateProgression.GetItemData(above)
                if type(placeData) == PlaceDataNds:
                    placeData.save()
                    newPlaceDataEntry.load(placeData.data)
                    if self.treeStateProgression.GetChildrenCount(above) == 1:
                        child, cookie = self.treeStateProgression.GetFirstChild(above)
                        self.treeStateProgression.AppendItem(newItem, self.treeStateProgression.GetItemText(child))
                else:
                    logSevere("Failed to copy", self.treeStateProgression.GetItemText(above))
            
            self.treeStateProgression.SetItemData(newItem, newPlaceDataEntry)
            self._dataPlace.insert(indexItem + 1, newPlaceDataEntry)
            self.__treeToPlaceData[newItem] = newPlaceDataEntry
        else:
            logSevere("Cannot add another place data database entry!")

    def btnAddStateOnButtonClick(self, event):
        if len(self._dataPlace) < 16 and (state := self._getActiveState()) != None:
            rootChild, cookie = self.treeStateProgression.GetFirstChild(self.treeStateProgression.GetRootItem())
            target : TreeItemId = None
            while rootChild.IsOk():
                if self.treeStateProgression.GetItemData(rootChild) == state:
                    target = rootChild
                    break
                rootChild = self.treeStateProgression.GetNextSibling(rootChild)

            if target != None:
                self.__addBelow(target, False)
                self.updateInterfaceButtons()
            else:
                logSevere("Failed to find AddState target!")
        return super().btnAddStateOnButtonClick(event)
    
    def btnDeleteOnButtonClick(self, event):
        if (state := self._getActiveState()) != None and (indexState := self._dataPlace.index(state)) > 0:
            
            rootChild, cookie = self.treeStateProgression.GetFirstChild(self.treeStateProgression.GetRootItem())
            rootChild = self.treeStateProgression.GetNextSibling(rootChild)
            target = None
            indexItem = 1
            while rootChild.IsOk():
                if self.treeStateProgression.GetItemData(rootChild) == state:
                    target = rootChild
                elif target != None:
                    nameItem = self.treeStateProgression.GetItemText(rootChild)
                    nameItem = ("State %i:" % (indexItem - 1)) + nameItem.split(":")[1]
                    self.treeStateProgression.SetItemText(rootChild, nameItem)
                rootChild = self.treeStateProgression.GetNextSibling(rootChild)
                indexItem += 1

            self._dataPlace.pop(indexState)
            del self.__treeToPlaceData[rootChild]
            self.treeStateProgression.DeleteChildren(target)
            self.treeStateProgression.Delete(target)     
        return super().btnDeleteOnButtonClick(event)
    
    def btnDuplicateOnButtonClick(self, event):
        if len(self._dataPlace) < 16 and (state := self._getActiveState()) != None:
            rootChild, cookie = self.treeStateProgression.GetFirstChild(self.treeStateProgression.GetRootItem())
            target : TreeItemId = None
            while rootChild.IsOk():
                if self.treeStateProgression.GetItemData(rootChild) == state:
                    target = rootChild
                    break
                rootChild = self.treeStateProgression.GetNextSibling(rootChild)

            if target != None:
                self.__addBelow(target, True)
                self.updateInterfaceButtons()
            else:
                logSevere("Failed to find AddState target!")
        return super().btnDuplicateOnButtonClick(event)
    
    def btnMoveDownOnButtonClick(self, event):
        return super().btnMoveDownOnButtonClick(event)
    
    def btnMoveUpOnButtonClick(self, event):
        return super().btnMoveUpOnButtonClick(event)