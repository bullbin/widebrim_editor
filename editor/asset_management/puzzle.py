from typing import List
from widebrim.engine.const import PATH_NAZO_A, PATH_NAZO_B, PATH_NAZO_C, PATH_PACK_NAZO, PATH_PUZZLE_SCRIPT, PATH_PACK_PUZZLE
from widebrim.madhatter.common import log
from widebrim.madhatter.hat_io.asset_dat import NazoDataNds
from widebrim.engine.file import FileInterface
from widebrim.engine.state.state import Layton2GameState
from widebrim.engine_ext.utils import substituteLanguageString
from widebrim.madhatter.hat_io.asset_dat.nazo import NazoData

class PuzzleEntry():
    # TODO - Maybe just inherit nazodata and use that instead...
    def __init__(self, idInternal, idExternal, name):
        self.idInternal = idInternal
        self.idExternal = idExternal
        self.name = name

def getPuzzles(state : Layton2GameState) -> List[List[PuzzleEntry]]:
    """Gets a list of every puzzle stored inside ROM and bundles them according to access rules.
    
    Note that this approach does not take into account engine edits or forced behaviours.
    This is exhaustive but groups may not be accurate to execution.

    Args:
        state (Layton2GameState): Game state used for language pathing.

    Returns:
        List[List[PuzzleEntry]]: List structured as [Normal puzzles, WiFi puzzles, Challenge puzzles]
    """
    # Normal
    # WiFi
    # Challenge (?)

    # However, data is stored as shorts...
    # 153 puzzles allowed in jiten list
    # 33 puzzles allowed in wifi list
    # Only 160 puzzles can have stored data, however.
    # TODO - Madhatter, get external id
    # TODO - is widebrim intro correct on 153?

    puzzlesNormal = []
    puzzlesWifi = []
    puzzlesChallenge = []

    def addPuzzle(idInternal : int, data : NazoData):
        # TODO - Not exactly perfect, uses nzlst. But nzlst prevents more than 153 puzzles.
        entry = PuzzleEntry(idInternal, data.idExternal, data.getTextName())
        if idInternal == 206:
            puzzlesChallenge.append(entry)
        else:
            idExternal = data.idExternal
            if idExternal > 153:
                puzzlesWifi.append(entry)
            else:
                puzzlesNormal.append(entry)
                

    # TODO - vfs rewrite allows proper access to archives to prevent this brokenness
    packA = FileInterface.getPack(substituteLanguageString(state, PATH_NAZO_A))
    packB = FileInterface.getPack(substituteLanguageString(state, PATH_NAZO_B))
    packC = FileInterface.getPack(substituteLanguageString(state, PATH_NAZO_C))
    packPuzzleScript = FileInterface.getPack(PATH_PUZZLE_SCRIPT)

    for idInternal in range(1, 256):
        if idInternal < 60:
            pack = packA
        elif idInternal < 120:
            pack = packB
        else:
            pack = packC

        if (data := pack.getData(PATH_PACK_NAZO % idInternal)) != None:
            puzzleDat = NazoDataNds()
            if puzzleDat.load(data):
                if packPuzzleScript.getData(PATH_PACK_PUZZLE % idInternal) != None:
                    addPuzzle(idInternal, puzzleDat)
                else:
                    log("Puzzle missing script", idInternal)

    return [puzzlesNormal, puzzlesWifi, puzzlesChallenge]