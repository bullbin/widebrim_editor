class BuilderRomAssetNotAvailable(Exception):
    pass

class FusedPatchFolderNotEmpty(Exception):
    pass

class FusedPatchFailedToInitialise(Exception):
    pass

class FusedPatchOperationInvalidatesFilesystem(Exception):
    pass

class FusedPatchOperationInvalid(Exception):
    pass

class FusedPatchRenameOperationExtensionNotPreserved(Exception):
    pass