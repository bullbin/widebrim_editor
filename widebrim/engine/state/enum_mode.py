from enum import Enum

class GAMEMODES(Enum):
    INVALID     = 255

    Reset       = 0
    Room        = 1
    DramaEvent  = 3
    Movie       = 6

    StartPuzzle = 7
    EndPuzzle   = 8
    StayPuzzle  = 9

    Puzzle      = 10
    UnkNazo     = 11
    Title       = 12

    Narration   = 13
    SubCamera   = 14
    SubHerbTea  = 15
    SubHamster  = 16

    Menu        = 17
    Name        = 18

    Jiten0      = 19
    InfoMode    = 20

    Staff       = 21

    Jiten1      = 22
    Memo        = 23

    Challenge   = 24

    EventTea    = 25
    UnkSubPhoto0    = 26
    UnkSubPhoto1    = 27
    SecretMenu  = 28

    OmakeMenu   = 30
    SecretJiten = 31
    ArtMode     = 32
    ChrViewMode = 33
    MusicMode   = 34
    VoiceMode   = 35

    MovieViewMode   = 36

    HamsterName = 37
    Passcode    = 40
    Diary       = 43
    Nazoba      = 44

# Cmd_SetGameMode
STRING_TO_GAMEMODE_VALUE = {"room"          :GAMEMODES.Room,
                            "drama event"   :GAMEMODES.DramaEvent,
                            "puzzle"        :GAMEMODES.Puzzle,
                            "movie"         :GAMEMODES.Movie,
                            "narration"     :GAMEMODES.Narration,
                            "menu"          :GAMEMODES.Menu,
                            "staff"         :GAMEMODES.Staff,
                            "name"          :GAMEMODES.HamsterName,
                            "challenge"     :GAMEMODES.Challenge,
                            "sub herb"      :GAMEMODES.SubHerbTea,
                            "sub camera"    :GAMEMODES.SubCamera,
                            "sub ham"       :GAMEMODES.SubHamster,
                            "passcode"      :GAMEMODES.Passcode,
                            "diary"         :GAMEMODES.Diary,
                            "nazoba"        :GAMEMODES.Nazoba}