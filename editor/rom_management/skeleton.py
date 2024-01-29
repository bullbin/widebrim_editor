from filesystem import FilesystemNds
from widebrim.madhatter.hat_io.asset import File, LaytonPack
from widebrim.madhatter.hat_io.asset_script import GdScript
from widebrim.madhatter.hat_io.asset_autoevent import AutoEvent
# from widebrim.madhatter.hat_io.asset_dlz

def clearDatabases(romFs : FilesystemNds):

    def createEntrypointEvent():
        pass

    pass

def createSkeletonRom(romFs : FilesystemNds):
    """Reduces contents in ROM to an empty state ready for the creation of a new game.
    This includes deleting all characters and all non-critical assets, for example.

    This process will only touch known paths in the ROM. It will not touch binaries and will not touch files outside of the asset directory.
    Additionally this does not provide a guarantee that all LEVEL-5 assets will be removed. Don't distribute the skeleton ROM.

    WARNING: This is a destructive process and may result in an unplayable ROM.
    This process targets the EU ROM. It may not be safe on other ROMs. It is certainly not safe on the JP ROM.
    Be certain this is what you want to do before starting this process.

    Args:
        romFs (FilesystemNds): ROM filesystem to act upon.
    """
    # What can we delete?
    pass