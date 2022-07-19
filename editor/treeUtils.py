from wx import TreeCtrl, TreeItemId

def isItemOnPathToItem(treeCtrl : TreeCtrl, itemOnPath : TreeItemId, itemParent : TreeItemId) -> bool:
    """Returns True if the item given is somewhere on the path to the parent. Will also return true if the items are equivalent.

    Args:
        treeCtrl (TreeCtrl): TreeCtrl containing both items.
        itemOnPath (TreeItemId): Item existing as a child of the parent (or equivalent)
        itemParent (TreeItemId): Parent item.

    Returns:
        bool: True if the item is a child of the parent or the parent itself.
    """
    if not(treeCtrl.GetRootItem().IsOk()):
        return False

    if itemOnPath == itemParent:
        return True
    elif itemOnPath == treeCtrl.GetRootItem():
        return False
    elif not(itemOnPath.IsOk()):
        return False
    treeParent = treeCtrl.GetItemParent(itemOnPath)
    while treeParent != treeCtrl.GetRootItem():
        if treeParent == itemParent:
            return True
        treeParent = treeCtrl.GetItemParent(treeParent)
    return False