from filesystem.low_level.fs_romloader import FilesystemNds
from widebrim.gamemodes.movie.const import PATH_ARCHIVE_MOVIE_SUBTITLES
from widebrim.madhatter.hat_io.asset import LaytonPack, File

def purgeMovie(romFs : FilesystemNds, language):
    # TODO - VFS needs to support deleting empty folders
    # TODO - VFS prune empty folders method
    # TODO - VFS LaytonPack

    romFs.removeFolder("/data_lt2/movie")

    for pathPack in [PATH_ARCHIVE_MOVIE_SUBTITLES.replace("?", language.value), "/data_lt2/script/movie.plz"]:
        if romFs.doesFileExist(pathPack):
            pack = LaytonPack(version=1)
            contents = File(data=romFs.getFile(pathPack))
            contents.decompress()
            pack.load(contents.data)
            pack.files = []
            pack.save()
            pack.compress(addHeader=False)
            romFs.replaceFile(pathPack, pack.data)

    for filepath in romFs.getFilepathsInFolder("/data_lt2/stream/movie/?".replace("?", language.value)):
        romFs.removeFile(filepath)
