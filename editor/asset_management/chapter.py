from editor.asset_management.event import getFreeStoryFlags
from widebrim.engine.const import PATH_DB_STORYFLAG, PATH_PROGRESSION_DB
from widebrim.engine.state.manager.state import Layton2GameState
from widebrim.filesystem.compatibility.compatibilityRom import WriteableRomFileInterface
from widebrim.madhatter.common import logSevere
from widebrim.madhatter.hat_io.asset_storyflag import StoryFlag

def _loadStoryFlag(state : Layton2GameState) -> StoryFlag:
    storyFlag = StoryFlag()
    if (data := state.getFileAccessor().getPackedData(PATH_PROGRESSION_DB, PATH_DB_STORYFLAG)):
        storyFlag.load(data)
    return storyFlag

def _saveStoryFlag(state : Layton2GameState, storyFlag : StoryFlag) -> bool:
    packProgression = state.getFileAccessor().getPack(PATH_PROGRESSION_DB)
    fileNotFound = True
    for file in packProgression.files:
        if file.name == PATH_DB_STORYFLAG:
            storyFlag.save()
            file.data = storyFlag.data
            fileNotFound = False
            break

    if fileNotFound:
        storyFlag.name = PATH_DB_STORYFLAG
        storyFlag.save()
        packProgression.files.append(storyFlag)
    
    packProgression.save()
    packProgression.compress()
    
    accessor : WriteableRomFileInterface = state.getFileAccessor()
    accessor.writeableFs.replaceFile(PATH_PROGRESSION_DB, packProgression.data)
    return True

def correctChapterOrder(storyFlag : StoryFlag):
    initial = storyFlag.getGroupAtIndex(0)
    groups = storyFlag.flagGroups[1:]

    notEmpty = []
    empty = []

    for group in groups:
        if group.getChapter() == 0 and group.isEmpty():
            empty.append(group)
        else:
            notEmpty.append(group)
    
    notEmpty.sort(key=lambda x: x.getChapter())
    storyFlag.flagGroups = [initial] + notEmpty + empty

def createChapter(state : Layton2GameState, chapter : int) -> bool:
    """Creates a new chapter based on the first free story group.

    Args:
        state (Layton2GameState): State used for file access. Needs writeable file accessor.
        chapter (int): Chapter value. Can match another chapter, but shouldn't.

    Returns:
        bool: True if the chapter creation was successful. Reload the storyflag database and get by chapter to access the new group.
    """
    storyFlag = _loadStoryFlag(state)
    wasSuccessful = False

    # TODO - Single pass, isolate target...
    for indexGroup, group in enumerate(storyFlag.flagGroups):
        if group.getChapter() == chapter:
            return False

    for indexGroup, group in enumerate(storyFlag.flagGroups):
        if indexGroup > 0:
            # Don't touch the first group
            if group.getChapter() == 0 and group.isEmpty():
                group.setChapter(chapter)
                correctChapterOrder(storyFlag)
                wasSuccessful = True
                break
    
    if wasSuccessful:
        return _saveStoryFlag(state, storyFlag)
    return False

def deleteChapter(state : Layton2GameState, chapter : int) -> bool:
    """Deletes a chapter based on first matching index. This operation is shallow and will not fix broken references - progression may be broken.

    Args:
        state (Layton2GameState): State used for file access. Needs writeable file accessor.
        chapter (int): Chapter value. Should match chapter in StoryFlag file. If chapter is 0, first match after initial group will be returned.

    Returns:
        bool: True if deletion was successful. False if no match found or file export failed. Reload the storyflag database and get by chapter to access the updated groups.
    """
    storyFlag = _loadStoryFlag(state)

    # TODO - Single pass, isolate target...
    for indexGroup, group in enumerate(storyFlag.flagGroups):
        if not(indexGroup == 0 and group.getChapter() == 0 and chapter == 0):
            if group.getChapter() == chapter:
                group.setChapter(0)
                group.clear()
                correctChapterOrder(storyFlag)
                return _saveStoryFlag(state, storyFlag)
    return False