from typing import Dict, List, Optional, Tuple
from editor.asset_management.room import PlaceGroup, getPackPathForPlaceIndex
from editor.branch_management.branch_event.utils import getNameForEvent
from editor.e_room.main import FramePlaceEditor
from editor.treeUtils import isItemOnPathToItem
from widebrim.engine.const import PATH_DB_AUTOEVENT, PATH_DB_PLACEFLAG, PATH_PROGRESSION_DB
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.filesystem.compatibility.compatibilityBase import WriteableFilesystemCompatibilityLayer
from widebrim.madhatter.common import log, logSevere
from widebrim.madhatter.hat_io.asset import File
from widebrim.madhatter.hat_io.asset_autoevent import AutoEvent
from widebrim.madhatter.hat_io.asset_dat.place import PlaceData, PlaceDataNds
from widebrim.gamemodes.room.const import PATH_PACK_PLACE
from widebrim.madhatter.hat_io.asset_placeflag import PlaceFlag
from wx import TreeItemId, StaticBox
from re import match

# TODO - Remove extra button checks (some cases aren't covered anyways, like deleting wrong item outside of state mode...)
# TODO - When changing events for autoevent, ensure that the event has an EventViewed flag

class FramePlaceConditionalEditor(FramePlaceEditor):

    TEXT_BTN_CONDITION_EXISTS       = "Remove condition..."
    TEXT_BTN_CONDITION_MISSING      = "New condition..."
    
    TEXT_BTN_ADD_STATE_TOO_MANY     = "No more states!"
    TEXT_BTN_ADD_EVENT_TOO_MANY     = "No more events!"
    TEXT_BTN_ADD_STATE_REMAINING    = "Add below..."
    TEXT_BTN_ADD_EVENT_REMAINING    = "Add below..."
    TEXT_BTN_ADD_PLACEHOLDER        = "Add below..."

    TEXT_BTN_DUP_STATE_TOO_MANY     = "No more states!"
    TEXT_BTN_DUP_EVENT_TOO_MANY     = "No more events!"
    TEXT_BTN_DUP_STATE_REMAINING    = "Duplicate below..."
    TEXT_BTN_DUP_EVENT_REMAINING    = "Duplicate below..."
    TEXT_BTN_DUP_PLACEHOLDER        = "Duplicate below..."

    NAME_TREE_ITEM_AUTOEVENT        = "Automatic Events"
    NAME_TREE_ITEM_AUTOEVENT_BAD    = "(Automatic events only available for first 8 states)"

    NAME_ROOM_PROPERTIES_INFILL     = "Room Parameters: %s"

    def __init__(self, parent, filesystem: WriteableFilesystemCompatibilityLayer, state: Layton2GameState, groupPlace: PlaceGroup):
        super().__init__(parent, filesystem, state, groupPlace)
        self.__rootTreeStates       : Optional[TreeItemId] = None
        self.__rootTreeAutoEvent    : Optional[TreeItemId] = None
        self.__activeItemHasCondition : bool = False
        self.updateInterfaceButtons()
    
    def __isSelectedItemTypeState(self) -> bool:
        if self.treeStateProgression: 
            selection = self.treeStateProgression.GetSelection()
            if self.__rootTreeStates != None and isItemOnPathToItem(self.treeStateProgression, selection, self.__rootTreeStates):
                return selection != self.__rootTreeStates
        return False

    def __isSelectedItemTypeAutoEvent(self) -> bool:
        if self.treeStateProgression:            
            selection = self.treeStateProgression.GetSelection()
            if self.__rootTreeAutoEvent != None and isItemOnPathToItem(self.treeStateProgression, selection, self.__rootTreeAutoEvent):
                return selection != self.__rootTreeAutoEvent
        return False

    def updateInterfaceButtons(self):

        def disableAllButtons():
            self.btnAddCondition.Disable()
            self.btnAddState.Disable()
            self.btnMoveUp.Disable()
            self.btnMoveDown.Disable()
            self.btnDelete.Disable()
            self.btnDuplicate.Disable()
            self.btnEditChapter.Disable()
            self.btnAddState.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_ADD_PLACEHOLDER)
            self.btnDuplicate.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_DUP_PLACEHOLDER)

        def updateInterfaceInsideState():
            if self._getActiveState() != None:
                
                indexItem = self._getListPlaceData()[1].index(self._getActiveState())

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

                if 1 <= indexItem < len(self._getListPlaceData()[1]) - 1:
                    self.btnMoveDown.Enable()
                else:
                    self.btnMoveDown.Disable()

                if indexItem != 0:
                    self.btnDelete.Enable()
                else:
                    self.btnDelete.Disable()

                if len(self._getListPlaceData()[1]) < 16:
                    self.btnAddState.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_ADD_STATE_REMAINING)
                    self.btnDuplicate.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_DUP_STATE_REMAINING)
                    self.btnDuplicate.Enable()
                    self.btnAddState.Enable()
                else:
                    self.btnAddState.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_ADD_STATE_TOO_MANY)
                    self.btnDuplicate.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_DUP_STATE_TOO_MANY)
                    self.btnDuplicate.Disable()
                    self.btnAddState.Disable()
            else:
                disableAllButtons()

        def updateInterfaceNoAutoEvent():
            autoEventChildren = self.__getAutoEventChildren()
            countAutoEvent = len(autoEventChildren)
            if countAutoEvent == 0:
                self.btnAddState.Enable()

                self.btnAddCondition.Disable()
                self.btnMoveUp.Disable()
                self.btnMoveDown.Disable()
                self.btnDelete.Disable()
                self.btnDuplicate.Disable()
                self.btnEditChapter.Disable()
                self.btnAddState.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_ADD_EVENT_REMAINING)
                self.btnDuplicate.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_DUP_PLACEHOLDER)
            else:
                disableAllButtons()

        def updateInterfaceInsideAutoEvent():
            selection = self.treeStateProgression.GetSelection()
            while self.treeStateProgression.GetItemParent(selection) != self.__rootTreeAutoEvent:
                selection = self.treeStateProgression.GetItemParent(selection)
            autoEventChildren = self.__getAutoEventChildren()
            countAutoEvent = len(autoEventChildren)
            indexAutoEvent = autoEventChildren.index(selection)

            if countAutoEvent < 8:
                self.btnAddState.Enable()
                self.btnDuplicate.Enable()
                self.btnAddState.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_ADD_EVENT_REMAINING)
                self.btnDuplicate.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_DUP_EVENT_REMAINING)
            else:
                self.btnAddState.Disable()
                self.btnDuplicate.Disable()
                self.btnAddState.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_ADD_EVENT_TOO_MANY)
                self.btnDuplicate.SetLabel(FramePlaceConditionalEditor.TEXT_BTN_DUP_EVENT_TOO_MANY)
            
            if indexAutoEvent < (countAutoEvent - 1):
                self.btnMoveDown.Enable()
            else:
                self.btnMoveDown.Disable()
            
            if indexAutoEvent > 0:
                self.btnMoveUp.Enable()
            else:
                self.btnMoveUp.Disable()
            
            self.btnDelete.Enable()
            self.btnAddCondition.Disable()
            self.btnEditChapter.Enable()

        if self.__isSelectedItemTypeState():
            updateInterfaceInsideState()
        elif self.__isSelectedItemTypeAutoEvent():
            updateInterfaceInsideAutoEvent()
        elif self.treeStateProgression and (selection := self.treeStateProgression.GetSelection()) == self.__rootTreeAutoEvent:
            updateInterfaceNoAutoEvent()
        else:
            disableAllButtons()

    def ensureLoaded(self):
        if self._loaded:
            return

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
            self.__reloadTitle()
        self.updateInterfaceButtons()
        return super().treeStateProgressionOnTreeSelChanged(event)
    
    def __reloadTitle(self):
        item = self.__getItemCorrespondingToState(self._lastValidSuggestion)
        if item != None:
            staticBox : StaticBox = self.treeParam.GetParent()
            staticBox.SetLabel(FramePlaceConditionalEditor.NAME_ROOM_PROPERTIES_INFILL % self.treeStateProgression.GetItemText(item))

    def __getAutoEventChildren(self) -> List[TreeItemId]:
        output = []
        if self.__rootTreeAutoEvent != None:
            child, _cookie = self.treeStateProgression.GetFirstChild(self.__rootTreeAutoEvent)
            while child.IsOk():
                output.append(child)
                child = self.treeStateProgression.GetNextSibling(child)
        return output

    def _getListPlaceData(self) -> Tuple[List[TreeItemId], List[PlaceData]]:
        outputTree = []
        outputPlace = []
        if self.__rootTreeStates != None:
            child, _cookie = self.treeStateProgression.GetFirstChild(self.__rootTreeStates)
            while child.IsOk():
                outputTree.append(child)
                outputPlace.append(self.treeStateProgression.GetItemData(child))
                child = self.treeStateProgression.GetNextSibling(child)
        return (outputTree, outputPlace)

    def __correctTreeItemIndices(self):
        treeItems, treeData = self._getListPlaceData()
        for indexItem, item in enumerate(treeItems):
            chapters = self.__getChaptersFromItem(item)
            if chapters == None:
                self.treeStateProgression.SetItemText(item, "Default State")
            else:
                chapterMin, chapterMax = chapters
                self.treeStateProgression.SetItemText(item, "State %i: Chapter %i to %i" % (indexItem, chapterMin, chapterMax))

    def __getChaptersFromItem(self, item : TreeItemId) -> Optional[Tuple[int,int]]:
        if item.IsOk():
            nameItem = self.treeStateProgression.GetItemText(item)
            matching = match("State [0-9]+: Chapter ([0-9]+) to ([0-9]+)", nameItem)
            if matching != None and matching.lastindex >= 2:
                return (int(matching[1]), int(matching[2]))
            matching = match("Chapter ([0-9]+) to ([0-9]+): ", nameItem)
            if matching != None and matching.lastindex >= 2:
                return (int(matching[1]), int(matching[2]))
        return None

    def __getItemCorrespondingToState(self, placeData : PlaceDataNds) -> Optional[TreeItemId]:
        if self.__rootTreeStates != None:
            treeItems, treeData = self._getListPlaceData()
            if placeData in treeData:
                return treeItems[treeData.index(placeData)]
        return None

    def __getBranchRootFromItem(self, item : TreeItemId) -> Optional[TreeItemId]:
        if item.IsOk():
            treeItems, _treeData = self._getListPlaceData()
            while item != self.treeStateProgression.GetRootItem():
                if item in treeItems:
                    return item
                item = self.treeStateProgression.GetItemParent(item)
        return None

    def __generateList(self):
            
        pathPack = getPackPathForPlaceIndex(self._groupPlace.indexPlace)
        pack = self._filesystem.getPack(pathPack)
        placeData : List[PlaceData] = []

        listStateIndices = self._groupPlace.indicesStates
        if listStateIndices != list(range(self._groupPlace.indicesStates[-1] + 1)):
            # TODO - Read off databases as well to detect "true maximum"
            logSevere("Detected gaps in place details, extra place data will be generated!")
            listStateIndices = list(range(self._groupPlace.indicesStates[-1] + 1))

        for index in listStateIndices:
            loadedPlace = PlaceDataNds()
            if (data := pack.getFile(PATH_PACK_PLACE % (self._groupPlace.indexPlace, index))) != None:
                loadedPlace.load(data)
            placeData.append(loadedPlace)

        self.__activeItemHasCondition = False

        placeFlag = PlaceFlag()
        if (data := self._filesystem.getPackedData(PATH_PROGRESSION_DB, PATH_DB_PLACEFLAG)):
            placeFlag.load(data)

        autoEvent = AutoEvent()
        if (data := self._filesystem.getPackedData(PATH_PROGRESSION_DB, PATH_DB_AUTOEVENT)):
            autoEvent.load(data)

        def generateAutoEventBranch():
            self.__rootTreeAutoEvent = self.treeStateProgression.AppendItem(self.treeStateProgression.GetRootItem(), FramePlaceConditionalEditor.NAME_TREE_ITEM_AUTOEVENT)
            groupAutoEvent = autoEvent.getEntry(self._groupPlace.indexPlace)
            if groupAutoEvent != None:
                for indexAutoEvent in range(8):
                    if (entry := groupAutoEvent.getSubPlaceEntry(indexAutoEvent)) != None:
                        if not(entry.chapterEnd == 0 or entry.chapterStart == 0):
                            self.treeStateProgression.AppendItem(self.__rootTreeAutoEvent,
                                                                ("Chapter %i to %i: " % (entry.chapterStart, entry.chapterEnd)) + getNameForEvent(self._state, entry.idEvent),
                                                                data=entry.idEvent)
                            self.treeStateProgression.Expand(self.__rootTreeAutoEvent)

        self.treeStateProgression.DeleteAllItems()
        rootTreeProgression = self.treeStateProgression.AddRoot("You shouldn't be able to see this!")
        self.__rootTreeStates = self.treeStateProgression.AppendItem(rootTreeProgression, "States")
        
        generateAutoEventBranch()

        selection = None
        for index, placeDataEntry in enumerate(placeData):
            indexData = self._groupPlace.indicesStates[index]
            if index == 0:
                selection = self.treeStateProgression.AppendItem(self.__rootTreeStates, "Default State", data=placeDataEntry)
            else:
                entry = placeFlag.entries[self._groupPlace.indexPlace]
                chapterEntry = entry.getEntry(index)
                chapterMin = chapterEntry.chapterStart
                chapterMax = chapterEntry.chapterEnd

                subroomRoot = self.treeStateProgression.AppendItem(self.__rootTreeStates, "State " + str(index) + (": Chapter %i to %i" % (chapterMin, chapterMax)),
                                                                   data=placeDataEntry)

                if chapterMin == 0 or chapterMax == 0:
                    self.treeStateProgression.AppendItem(subroomRoot, "Terminate subroom discovery on encounter")
                    continue
                
                counterEntry = entry.getCounterEntry(indexData)
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
    
    def _getSelectedWithStateParent(self) -> Optional[Tuple[TreeItemId, TreeItemId]]:
        """Returns key state parent alongside original selection.

        Returns:
            Optional[Tuple(TreeItemId, TreeItemId)]: (KeyItem, SelectedItem) or None if no state was selected.
        """
        # HACK - Method called when tree is broken. Workaround, see https://github.com/wxWidgets/Phoenix/issues/1500
        if self.treeStateProgression:
            selection : TreeItemId = self.treeStateProgression.GetSelection()
            if selection.IsOk():
                treeItems, _treeData = self._getListPlaceData()
                rootItem = self.treeStateProgression.GetRootItem()
                while selection != rootItem:
                    if selection in treeItems:
                        return (selection, self.treeStateProgression.GetSelection())
                    selection = self.treeStateProgression.GetItemParent(selection)
        return None

    def _getActiveState(self) -> Optional[PlaceDataNds]:
        keyItemAndParent = self._getSelectedWithStateParent()
        if keyItemAndParent != None:
            selection, _selected = keyItemAndParent
            treeItems, treeData = self._getListPlaceData()
            suggestion = treeData[treeItems.index(selection)]
            if suggestion != self._lastValidSuggestion:
                if self.treeStateProgression.GetChildrenCount(selection) > 0:
                    self.__activeItemHasCondition = True
                else:
                    self.__activeItemHasCondition = False
                self._lastValidSuggestion = suggestion
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
        
        if self.__rootTreeStates == None:
            return

        rootChild, cookie = self.treeStateProgression.GetFirstChild(self.__rootTreeStates)
        dataOutput : List[PlaceData] = []
        chapterOutput = []
        # TODO - Read state index from items - is it possible that an item will be missing a state? How can we recover from this situation?
        while rootChild.IsOk():
            dataOutput.append(self.treeStateProgression.GetItemData(rootChild))
            nameItem = self.treeStateProgression.GetItemText(rootChild)
            if "Default" in nameItem:
                # Default state - TODO What should this be by default?
                chapterOutput.append((0,0))
            else:
                # Other states
                chapters = self.__getChaptersFromItem(rootChild)
                if chapters == None:
                    logSevere("Failed to decode", nameItem)
                    chapterMin = 0
                    chapterMax = 0
                else:
                    chapterMin, chapterMax = chapters
                chapterOutput.append((chapterMin, chapterMax))
            rootChild = self.treeStateProgression.GetNextSibling(rootChild)
        
        nonDestructiveWritePackChanges(dataOutput)

    def __addBelow(self, above : TreeItemId, duplicateAbove : bool = False):
        treeItems, treeData = self._getListPlaceData()
        if len(treeItems) < 16 and self.__rootTreeStates != None:
            if above not in treeItems:
                logSevere("Failed to find correct sibling state!")
                return

            chapterMin = 999
            chapterMax = 999
            if duplicateAbove:
                chapters = self.__getChaptersFromItem(above)
                if chapters != None:
                    chapterMin, chapterMax = chapters
                else:
                    logSevere("GetChapters called on incorrect item", self.treeStateProgression.GetItemText(above))

            newItem = self.treeStateProgression.InsertItem(self.__rootTreeStates, above, "State 255: Chapter %i to %i" % (chapterMin, chapterMax))
            newPlaceDataEntry = PlaceDataNds()

            if duplicateAbove:
                placeData : PlaceDataNds = treeData[treeItems.index(above)]
                if type(placeData) == PlaceDataNds:
                    placeData.save()
                    newPlaceDataEntry.load(placeData.data)
                    if self.treeStateProgression.GetChildrenCount(above) == 1:
                        child, cookie = self.treeStateProgression.GetFirstChild(above)
                        self.treeStateProgression.AppendItem(newItem, self.treeStateProgression.GetItemText(child))
                else:
                    logSevere("Failed to copy", self.treeStateProgression.GetItemText(above))
            
            self.treeStateProgression.SetItemData(newItem, newPlaceDataEntry)
            self.__correctTreeItemIndices()
            
            # TODO - Optimize calls to this
            self.__reloadTitle()
        else:
            logSevere("Cannot add another place data database entry!")

    # Calling updateInterfaceButtons will ensure these are correct in context, but it doesn't hurt to check
    def btnAddConditionOnButtonClick(self, event):
        return super().btnAddConditionOnButtonClick(event)

    # Below buttons can be called at any point
    def btnAddStateOnButtonClick(self, event):
        if self.__isSelectedItemTypeState():
            if len(self._getListPlaceData()[1]) < 16 and (state := self._getActiveState()) != None and self.__rootTreeStates != None:
                target = self.__getItemCorrespondingToState(state)
                if target != None:
                    self.__addBelow(target, False)
                    self.updateInterfaceButtons()
                else:
                    logSevere("Failed to find AddState target!")

        elif self.__isSelectedItemTypeAutoEvent() and len(self.__getAutoEventChildren()) < 8:
            textDup = ("Chapter %i to %i: " % (999, 999)) + "Configure event..."
            self.treeStateProgression.InsertItem(self.__rootTreeAutoEvent, self.treeStateProgression.GetSelection(), textDup, data=0)
            self.updateInterfaceButtons()

        elif self.treeStateProgression and (self.treeStateProgression.GetSelection() == self.__rootTreeAutoEvent) and len(self.__getAutoEventChildren()) == 0:
            textDup = ("Chapter %i to %i: " % (999, 999)) + "Configure event..."
            self.treeStateProgression.AppendItem(self.__rootTreeAutoEvent, textDup, data=0)
            self.updateInterfaceButtons()

        return super().btnAddStateOnButtonClick(event)
    
    def btnDeleteOnButtonClick(self, event):
        if self.__isSelectedItemTypeState():
            if (state := self._getActiveState()) != None and (indexState := self._getListPlaceData()[1].index(state)) > 0 and self.__rootTreeStates != None:
                item = self.__getItemCorrespondingToState(state)
                if item == None:
                    logSevere("Delete called on bad item!")
                else:
                    self.treeStateProgression.DeleteChildren(item)
                    self.treeStateProgression.Delete(item)
                    self.__correctTreeItemIndices()  

                    # TODO - Optimize calls to this
                    self.__reloadTitle()   

        elif self.__isSelectedItemTypeAutoEvent() and len(self.__getAutoEventChildren()) > 0:
            self.treeStateProgression.Delete(self.treeStateProgression.GetSelection())
            self.updateInterfaceButtons()

        return super().btnDeleteOnButtonClick(event)
    
    def btnDuplicateOnButtonClick(self, event):
        if self.__isSelectedItemTypeState():
            if len(self._getListPlaceData()[1]) < 16 and (state := self._getActiveState()) != None and self.__rootTreeStates:
                target = self.__getItemCorrespondingToState(state)
                if target != None:
                    self.__addBelow(target, True)
                    self.updateInterfaceButtons()
                else:
                    logSevere("Failed to find AddState target!")

        elif self.__isSelectedItemTypeAutoEvent() and len(self.__getAutoEventChildren()) < 8:
            idEvent = self.treeStateProgression.GetItemData(self.treeStateProgression.GetSelection())
            textDup = self.treeStateProgression.GetItemText(self.treeStateProgression.GetSelection())
            self.treeStateProgression.InsertItem(self.__rootTreeAutoEvent, self.treeStateProgression.GetSelection(), textDup, data=idEvent)
            self.updateInterfaceButtons()

        return super().btnDuplicateOnButtonClick(event)
    
    def btnEditChapterOnButtonClick(self, event):
        # TODO - Handle chp_inf here
        if self.__isSelectedItemTypeAutoEvent():
            print(self.__getChaptersFromItem(self.treeStateProgression.GetSelection()))
        elif self.__isSelectedItemTypeState():
            print(self.__getChaptersFromItem(self.__getItemCorrespondingToState(self._getActiveState())))
        return super().btnEditChapterOnButtonClick(event)

    def btnMoveDownOnButtonClick(self, event):
        if self.__isSelectedItemTypeAutoEvent():
            children = self.__getAutoEventChildren()
            selection = self.treeStateProgression.GetSelection()
            above = children[children.index(selection) + 1]

            idEvent = self.treeStateProgression.GetItemData(selection)
            text = self.treeStateProgression.GetItemText(selection)
            self.treeStateProgression.Delete(selection)

            selection = self.treeStateProgression.InsertItem(self.__rootTreeAutoEvent, above, text, data=idEvent)
            self.treeStateProgression.SelectItem(selection)
        
        elif self.__isSelectedItemTypeState():
            treeItems, treeData = self._getListPlaceData()
            indexSelection = treeData.index(self._getActiveState())
            selection = treeItems[indexSelection]
            indexNewAbove = indexSelection + 1
            
            data = self.treeStateProgression.GetItemData(selection)
            text = self.treeStateProgression.GetItemText(selection)

            if indexNewAbove >= 0:
                newItem = self.treeStateProgression.InsertItem(self.__rootTreeStates, treeItems[indexNewAbove], text, data=data)
            else:
                newItem = self.treeStateProgression.PrependItem(self.__rootTreeStates, text, data=data)
            
            if self.treeStateProgression.GetChildrenCount(selection, False) > 0:
                child, _cookie = self.treeStateProgression.GetFirstChild(selection)
                childText = self.treeStateProgression.GetItemText(child)
                self.treeStateProgression.AppendItem(newItem, childText)

            self.Freeze()
            self.treeStateProgression.DeleteChildren(selection)
            self.treeStateProgression.Delete(selection)
            self.__correctTreeItemIndices()
            self.treeStateProgression.SelectItem(newItem)
            self.Thaw()

        return super().btnMoveDownOnButtonClick(event)
    
    def btnMoveUpOnButtonClick(self, event):
        if self.__isSelectedItemTypeAutoEvent():
            children = self.__getAutoEventChildren()
            selection = self.treeStateProgression.GetSelection()
            indexNewAbove = children.index(selection) - 2

            idEvent = self.treeStateProgression.GetItemData(selection)
            text = self.treeStateProgression.GetItemText(selection)
            self.treeStateProgression.Delete(selection)

            if indexNewAbove >= 0:
                selection = self.treeStateProgression.InsertItem(self.__rootTreeAutoEvent, children[indexNewAbove], text, data=idEvent)
            else:
                selection = self.treeStateProgression.PrependItem(self.__rootTreeAutoEvent, text, data=idEvent)
            self.treeStateProgression.SelectItem(selection)

        elif self.__isSelectedItemTypeState():
            treeItems, treeData = self._getListPlaceData()
            indexSelection = treeData.index(self._getActiveState())
            selection = treeItems[indexSelection]
            indexNewAbove = indexSelection - 2
            
            data = self.treeStateProgression.GetItemData(selection)
            text = self.treeStateProgression.GetItemText(selection)

            if indexNewAbove >= 0:
                newItem = self.treeStateProgression.InsertItem(self.__rootTreeStates, treeItems[indexNewAbove], text, data=data)
            else:
                newItem = self.treeStateProgression.PrependItem(self.__rootTreeStates, text, data=data)
            
            if self.treeStateProgression.GetChildrenCount(selection, False) > 0:
                child, _cookie = self.treeStateProgression.GetFirstChild(selection)
                childText = self.treeStateProgression.GetItemText(child)
                self.treeStateProgression.AppendItem(newItem, childText)

            self.Freeze()
            self.treeStateProgression.DeleteChildren(selection)
            self.treeStateProgression.Delete(selection)
            self.__correctTreeItemIndices()
            self.treeStateProgression.SelectItem(newItem)
            self.Thaw()

        return super().btnMoveUpOnButtonClick(event)