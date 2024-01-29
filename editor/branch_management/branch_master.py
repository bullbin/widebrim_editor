from typing import Optional, Any
from widebrim.engine.state.manager.state import Layton2GameState

from widebrim.madhatter.common import logSevere
from editor.treeUtils import isItemOnPathToItem
from wx import TreeItemId, TreeCtrl

class BranchManager():
    
    def __init__(self, state : Layton2GameState, treeCtrl : TreeCtrl, hideEditControls=False):
        self._state                             = state
        self._disableEditControls               = hideEditControls
        self._treeCtrl                          = treeCtrl
        self._branchRoot : Optional[TreeItemId] = None

    def _isItemWithinPathToItem(self, itemOnPath : TreeItemId, itemParent : TreeItemId) -> bool:
        """Returns True if there exists some path from the child to the parent. Will return True if the item is the parent.

        Args:
            itemOnPath (TreeItemId): Child item.
            itemParent (TreeItemId): Parent item.

        Returns:
            bool: True if the item is either the parent itself or has a path to the parent.
        """
        return isItemOnPathToItem(self._treeCtrl, itemOnPath, itemParent)

    def _getComparativeItemData(self, treeItem : TreeItemId) -> Optional[int]:
        """Gets comparison value from item. Override this if your tree cannot use the data field for ordering.

        Args:
            treeItem (TreeItemId): TreeItemId being compared against.

        Returns:
            Optional[int]: Value corresponding to ordering, or None if no value can be given.
        """
        data = self._treeCtrl.GetItemData(treeItem)
        if data == None or type(data) == int:
            return data
        else:
            logSevere("No item match found for data", str(data))
            return data

    def _addIntoTreeAtCorrectId(self, identifier : int, name : str, branchRoot : TreeItemId, data : Optional[Any] = None, icon : int = -1) -> TreeItemId:
        """Inserts a new item in the tree while preserving the ordering of current items.

        Args:
            identifier (int): Ordered index providing information on where to insert the new item.
            name (str): Label to apply to new tree item.
            branchRoot (TreeItemId): Parent for tree insertion.
            data (Optional[Any]): Data to insert the item. If unordered, override self._getComparativeItemData to provide order. Defaults to None, which copies the identifier.
            icon (int, optional): Icon for insertion. Must correspond to icon pack already applied to tree. Defaults to -1 (no icon).

        Returns:
            TreeItemId: TreeItemId for new item. If adding fails, this will be the last child item.
        """
        # TODO - This will be slow for random adding - because we reference last object it shouldn't be too painful, but still...
        # TODO - Quit if no comparison item found!
        # TODO - Add to docstring about behaviour if item is same value order.
        if data == None:
            data = identifier

        lastChild : TreeItemId = self._treeCtrl.GetLastChild(branchRoot)
        if lastChild.IsOk():
            # Last item is before
            if type(self._getComparativeItemData(lastChild)) == int and self._getComparativeItemData(lastChild) < identifier:
                return self._treeCtrl.AppendItem(branchRoot, name, data=data, image=icon)
        else:
            # Has no items in the branch, so append is fine
            return self._treeCtrl.AppendItem(branchRoot, name, data=data, image=icon)

        # At this point, we know that the item sits somewhere between being the first item and being before the last
        priorChild, cookie = self._treeCtrl.GetFirstChild(branchRoot)
        if type(self._getComparativeItemData(priorChild)) == int and self._getComparativeItemData(priorChild) >= identifier:
            # Prepend before this item
            return self._treeCtrl.PrependItem(branchRoot, name, data=data, image=icon)
        
        while priorChild.IsOk():
            nextChild, cookie = self._treeCtrl.GetNextChild(priorChild, cookie)
            if type(self._getComparativeItemData(priorChild)) == int and self._getComparativeItemData(priorChild) < identifier:
                if type(self._getComparativeItemData(nextChild)) == int and self._getComparativeItemData(nextChild) >= identifier:
                    # Insert between items where possible
                    # Under this manager two items shouldn't have same ID (checked at start) so condition is ok
                    return self._treeCtrl.InsertItem(branchRoot, priorChild, name, data=data, image=icon)
            priorChild = nextChild
        
        logSevere("Failed to insert child in correct place!")
        return self._treeCtrl.AppendItem(branchRoot, name, data=data, image=icon)
    
    def remove(self):
        """Removes the created branch from the working tree. If called before branch was created, nothing will happen.
        """
        if self._branchRoot != None:
            pass

    def getCorrespondingItem(self, identifier : int) -> Optional[TreeItemId]:
        """Returns the tree item corresponding to this identifier.

        Args:
            identifier (int): Ordered value corresponding to item.

        Returns:
            Optional[TreeItemId]: TreeItemId if value was found, else None.
        """
        return None
    
    def createTreeBranches(self, branchParent : TreeItemId):
        """Creates tree representation from provided parent.

        Args:
            branchParent (TreeItemId): Tree item to use as parent for new branch.
        """
        self._branchRoot = branchParent