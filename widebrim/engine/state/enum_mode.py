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

    StartPuzzle = 7
    EndPuzzle   = 8
    StayPuzzle  = 9

    Puzzle      = 10

    Title       = 12

    Narration   = 13
    SubCamera   = 14
    SubHerbTea  = 15
    SubHamster  = 16

    Menu        = 17
    Name        = 18 # Break?

    Jiten0      = 19
    InfoMode    = 20

    Staff       = 21

    Jiten1      = 22
    Memo        = 23

    Challenge   = 24

    EventTea    = 25        # EventTea
    UnkSubPhoto0 = 26
    UnkSubPhoto1 = 27
    SecretMenu  = 28

    OmakeMenu = 30
    SecretJiten = 31
    ArtMode     = 32
    ChrViewMode = 33
    MusicMode   = 34
    VoiceMode   = 35

    MovieViewMode = 36

    HamsterName = 37    # Break?
    Passcode    = 40
    Diary       = 43
    Nazoba      = 44