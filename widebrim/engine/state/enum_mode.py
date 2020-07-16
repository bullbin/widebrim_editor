from enum import Enum

STRING_TO_GAMEMODE_VALUE = {"drama event":3,
                            "room":1,
                            "movie":6,
                            "narration":13,
                            "puzzle" : 10}

class GAMEMODES(Enum):
    INVALID     = 0
    Room        = 1
    DramaEvent  = 3
    Movie       = 6
    Puzzle      = 10
    Narration   = 13
    SubCamera   = 14
    SubHerbTea  = 15
    SubHamster  = 16
    Menu        = 17
    Staff       = 21
    Challenge   = 24
    Name        = 37
    Passcode    = 40
    Diary       = 43
    Nazoba      = 44