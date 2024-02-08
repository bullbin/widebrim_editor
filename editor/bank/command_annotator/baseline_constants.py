from typing import Dict, Optional
from widebrim.madhatter.typewriter.strings_lt2 import OPCODES_LT2

MAP_OPCODE_TO_FRIENDLY : Dict[OPCODES_LT2, Optional[str]]= {OPCODES_LT2.ExitScript : "Stop script execution",
                                                            OPCODES_LT2.TextWindow : "Dialogue",
                                                            OPCODES_LT2.SetPlace : "Set next launched room",
                                                            OPCODES_LT2.SetGameMode : "Choose next game mode",
                                                            OPCODES_LT2.SetEndGameMode : "Choose next game mode submode",
                                                            OPCODES_LT2.SetMovieNum : "Set next played movie ID",
                                                            OPCODES_LT2.SetDramaEventNum : "Set next event ID",
                                                            OPCODES_LT2.SetPuzzleNum : "Set next launched internal puzzle ID",
                                                            OPCODES_LT2.SetFontUserColor : None,
                                                            OPCODES_LT2.LoadBG : "Change background (bottom screen)",
                                                            OPCODES_LT2.LoadSubBG : "Change background (top screen)",
                                                            OPCODES_LT2.SpriteOn : "Show character",
                                                            OPCODES_LT2.SpriteOff : "Hide character",
                                                            OPCODES_LT2.DoSpriteFade : "Fade character",
                                                            OPCODES_LT2.DrawChapter : "Fade in on chapter background on bottom screen",
                                                            OPCODES_LT2.SetSpriteAlpha : None,
                                                            OPCODES_LT2.SetSpritePos : "Change character position",
                                                            OPCODES_LT2.ModifyBGPal : "Modify background colors (bottom screen)",
                                                            OPCODES_LT2.ModifySubBGPal : "Modify background colors (top screen)",
                                                            OPCODES_LT2.SetSpriteAnimation : "Play character animation",
                                                            OPCODES_LT2.AddMemo : "Unlock journal entry",
                                                            OPCODES_LT2.GameOver : "Restart game from logo sequence",
                                                            OPCODES_LT2.SetEventTea : None,
                                                            OPCODES_LT2.ReleaseItem : "Remove item from inventory",
                                                            OPCODES_LT2.SetSpriteShake : "Shake character",
                                                            OPCODES_LT2.CheckCounterAutoEvent : "Set next game mode to event on correct event execution history",
                                                            OPCODES_LT2.SetRepeatAutoEventID : "Repeat room entry event",
                                                            OPCODES_LT2.ReleaseRepeatAutoEventID : "Stop repeating room entry event",
                                                            OPCODES_LT2.SetFirstTouch : 'Enable "TOUCH" animation for next room',
                                                            OPCODES_LT2.EventSelect : "Conditional branch to set next event",

                                                            # Popup
                                                            OPCODES_LT2.DoHukamaruAddScreen : "Trigger new mystery popup",
                                                            OPCODES_LT2.DoSubItemAddScreen : "Trigger reward add screen popup",
                                                            OPCODES_LT2.DoStockScreen : "Trigger last puzzle added to index popup",
                                                            OPCODES_LT2.DoNazobaListScreen : "Trigger puzzles sent to Riddleton's shack popup",
                                                            OPCODES_LT2.DoItemAddScreen : "Trigger item added to inventory popup",
                                                            OPCODES_LT2.SetSubItem : "Preload reward for add screen popup",
                                                            OPCODES_LT2.DoSubGameAddScreen : "Trigger minigame unlock popup",
                                                            OPCODES_LT2.DoSaveScreen : "Trigger save game popup",
                                                            OPCODES_LT2.HukamaruClear : "Trigger solved mystery popup",
                                                            OPCODES_LT2.DoPhotoPieceAddScreen : "Trigger photo piece found popup",
                                                            OPCODES_LT2.MokutekiScreen : "Trigger next goal text popup",
                                                            OPCODES_LT2.DoNamingHamScreen : "Trigger hamster naming popup",
                                                            OPCODES_LT2.DoLostPieceScreen : "Trigger photo pieces lost popup",
                                                            OPCODES_LT2.DoInPartyScreen : "Trigger add character to party popup",
                                                            OPCODES_LT2.DoOutPartyScreen : "Trigger remove character from party popup",
                                                            OPCODES_LT2.EndingMessage : "Do ending dialogue",
                                                            OPCODES_LT2.ReturnStationScreen : None,       # Text removed from release
                                                            OPCODES_LT2.CompleteWindow : "Trigger text popup",
                                                            OPCODES_LT2.EndingAddChallenge : "Trigger bonus challenge unlocked popup",

                                                            # Sound
                                                            
                                                            OPCODES_LT2.SetVoiceID : "Set sound effect ID for next dialogue",
                                                            OPCODES_LT2.PlayStream : "Play streamed sound effect",
                                                            OPCODES_LT2.PlayStream2 : None,
                                                            OPCODES_LT2.StopStream : None,
                                                            OPCODES_LT2.PlaySound : "Play synthesized sound effect",
                                                            OPCODES_LT2.PlayBGM : "Switch BGM (timed by framecount)",
                                                            OPCODES_LT2.PlayBGM2 : "Switch BGM (timed by predefined framecount)",
                                                            OPCODES_LT2.FadeInBGM : "Start fading in BGM (timed by framecount)",
                                                            OPCODES_LT2.FadeInBGM2 : "Start fading in BGM (timed by predefined framecount)",
                                                            OPCODES_LT2.FadeOutBGM : "Start fading out BGM (timed by framecount)",
                                                            OPCODES_LT2.FadeOutBGM2 : "Start fading out BGM (timed by predefined framecount)",
                                                            OPCODES_LT2.SEStop : None,
                                                            OPCODES_LT2.SEPlay : None,
                                                            OPCODES_LT2.EnvPlay : None,
                                                            OPCODES_LT2.EnvStop : None,
                                                            OPCODES_LT2.FadeOutSE : None,

                                                            # Event variable access
                                                            OPCODES_LT2.SetEventCounter : "Modify event variable space (direct)",
                                                            OPCODES_LT2.AddEventCounter : "Modify event variable space (increment byte)",
                                                            OPCODES_LT2.OrEventCounter : "Modify event variable space (OR on byte)",

                                                            # Screen effects
                                                            OPCODES_LT2.FlashScreen : "Flash white on both screens",
                                                            OPCODES_LT2.ShakeBG : "Shake background (bottom screen)",
                                                            OPCODES_LT2.ShakeSubBG : "Shake background (top screen)",

                                                            # Fade commands
                                                            OPCODES_LT2.FadeIn : "Fade in (both screens)",
                                                            OPCODES_LT2.FadeOut : "Fade out (both screens)",
                                                            OPCODES_LT2.FadeInFrame : "Fade in (both screens, timed by framecount)",
                                                            OPCODES_LT2.FadeOutFrame : "Fade out (both screens, timed by framecount)",
                                                            OPCODES_LT2.FadeInFrameMain : "Fade in (bottom screen, timed by framecount)",
                                                            OPCODES_LT2.FadeOutOnlyMain : "Fade out (bottom screen)",
                                                            OPCODES_LT2.FadeOutFrameMain : "Fade out (bottom screen, timed by framecount)",
                                                            OPCODES_LT2.FadeInOnlyMain : "Fade in (bottom screen)",
                                                            OPCODES_LT2.FadeInFrameSub : "Fade in (top screen, timed by framecount)",
                                                            OPCODES_LT2.FadeOutFrameSub : "Fade out (top screen, timed by framecount)",
                                                            
                                                            # Pause commands
                                                            OPCODES_LT2.WaitFrame : "Pause (free on framecount)",
                                                            OPCODES_LT2.WaitFrame2 : "Pause (free on predefined framecount)",
                                                            OPCODES_LT2.DrawFrames : "Pause (free on framecount, keep rendering)",
                                                            OPCODES_LT2.WaitInput : "Pause (free on input)",
                                                            OPCODES_LT2.WaitVSyncOrPenTouch : "Pause (free on input, timeout on framecount)",
                                                            
                                                            # Puzzle commands (ideally shouldn't be visible)
                                                            OPCODES_LT2.SetNumTouch : None,
                                                            OPCODES_LT2.AddMatch : None,
                                                            OPCODES_LT2.AddMatchSolution : None,
                                                            OPCODES_LT2.SetGridPosition : None,
                                                            OPCODES_LT2.SetGridSize : None,
                                                            OPCODES_LT2.SetBlockSize : None,
                                                            OPCODES_LT2.AddBlock : None,
                                                            OPCODES_LT2.AddOnOffButton : None,
                                                            OPCODES_LT2.AddSprite : None,
                                                            OPCODES_LT2.SetShapeSolutionPosition : None,
                                                            OPCODES_LT2.SetMaxDist : None,
                                                            OPCODES_LT2.AddTracePoint : None,
                                                            OPCODES_LT2.SetFillPos : None,
                                                            OPCODES_LT2.AddInPoint : None,
                                                            OPCODES_LT2.AddOutPoint : None,
                                                            OPCODES_LT2.SetTraceCorrectZone : None,
                                                            OPCODES_LT2.GridAddBlock : None,
                                                            OPCODES_LT2.GridAddLetter : None,
                                                            OPCODES_LT2.AddCup : None,
                                                            OPCODES_LT2.SetLiquidColor : None,
                                                            OPCODES_LT2.SetTileOnOff2Info : None,
                                                            OPCODES_LT2.AddTileOnOff2Check : None,
                                                            OPCODES_LT2.SetRoseInfo : None,
                                                            OPCODES_LT2.AddRoseWall : None,
                                                            OPCODES_LT2.SetSlide2Info : None,
                                                            OPCODES_LT2.AddSlide2Range : None,
                                                            OPCODES_LT2.AddSlide2Check : None,
                                                            OPCODES_LT2.AddSlide2Sprite : None,
                                                            OPCODES_LT2.AddSlide2Object : None,
                                                            OPCODES_LT2.AddSlide2ObjectRange : None,
                                                            OPCODES_LT2.Tile2_AddSprite : None,
                                                            OPCODES_LT2.Tile2_AddPoint : None,
                                                            OPCODES_LT2.Tile2_AddPointGrid : None,
                                                            OPCODES_LT2.Tile2_AddObjectNormal : None,
                                                            OPCODES_LT2.Tile2_AddObjectRotate : None,
                                                            OPCODES_LT2.Tile2_AddObjectRange : None,
                                                            OPCODES_LT2.Tile2_AddCheckNormal : None,
                                                            OPCODES_LT2.Tile2_AddCheckRotate : None,
                                                            OPCODES_LT2.SetType : None,
                                                            OPCODES_LT2.SetLineColor : None,
                                                            OPCODES_LT2.SetPenColor : None,
                                                            OPCODES_LT2.SetGridTypeRange : None,
                                                            OPCODES_LT2.EnableNaname : None,
                                                            OPCODES_LT2.AddTouchPoint : None,
                                                            OPCODES_LT2.AddCheckLine : None,
                                                            OPCODES_LT2.AddTouchSprite : None,
                                                            OPCODES_LT2.AddTile : None,
                                                            OPCODES_LT2.AddPoint : None,
                                                            OPCODES_LT2.SetNumSolution : None,
                                                            OPCODES_LT2.AddTileSolution : None,
                                                            OPCODES_LT2.AddTileRotateSolution : None,
                                                            OPCODES_LT2.AddSolution : None,
                                                            OPCODES_LT2.SetPancakeNum : None,
                                                            OPCODES_LT2.SetAnswerBox : None,
                                                            OPCODES_LT2.SetAnswer : None,
                                                            OPCODES_LT2.SetDrawInputBG : None,
                                                            OPCODES_LT2.SetKnightInfo : None,
                                                            OPCODES_LT2.AddDrag2 : None,
                                                            OPCODES_LT2.AddDrag2Anim : None,
                                                            OPCODES_LT2.AddDrag2Point : None,
                                                            OPCODES_LT2.AddDrag2Check : None,
                                                            OPCODES_LT2.Tile2_SwapOn : None,
                                                            OPCODES_LT2.Skate_SetInfo : None,
                                                            OPCODES_LT2.Skate_AddWall : None,
                                                            OPCODES_LT2.PegSol_AddObject : None,
                                                            OPCODES_LT2.Couple_SetInfo : None,
                                                            OPCODES_LT2.Lamp_SetInfo : None,
                                                            OPCODES_LT2.Lamp_AddLine : None,
                                                            OPCODES_LT2.Tile2_AddObjectRange2 : None,
                                                            OPCODES_LT2.AddTileOnOff2Disable : None,
                                                            OPCODES_LT2.Lamp_AddDisable : None,
                                                            OPCODES_LT2.Tile2_AddReplace : None,
                                                            OPCODES_LT2.MaxTraceResult : None,
                                                            OPCODES_LT2.SetSubTitle : None,
                                                            OPCODES_LT2.SetFullScreen : None,
                                                            OPCODES_LT2.SetBridgeInfo : None,
                                                            OPCODES_LT2.SetTraceInfo : None,
                                                            OPCODES_LT2.SetPegSolInfo : None,
                                                            OPCODES_LT2.SetPancakeOffset : None,
                                                            OPCODES_LT2.Tile2_KeyOffset : None,
                                                            OPCODES_LT2.SetTraceArrow : None,
                                                            OPCODES_LT2.Tile2_TouchCounter : None,
                                                            
                                                            # HD
                                                            OPCODES_LT2.SetBandType : None,
                                                            OPCODES_LT2.DrawWaitInput : None,
                                                            OPCODES_LT2.SetEventBandType : None,

                                                            # Stubbed
                                                            OPCODES_LT2.SetAutoEventNum : "noop_0",
                                                            OPCODES_LT2.DoDiaryAddScreen : "noop_1"}

MAP_OPCODE_TO_DESC : Dict[OPCODES_LT2, Optional[str]]= {OPCODES_LT2.ExitScript          : "Immediately stops script execution. All instructions after will not be executed.",
                                                        OPCODES_LT2.TextWindow          : "Creates an animated pop-up textbox containing dialog and targetting a single character. Pauses script execution until dismissed.",
                                                        OPCODES_LT2.SetPlace            : "Sets next room ID. Change will not be visible until Place gamemode is executed. Does not pause script execution.",
                                                        OPCODES_LT2.SetGameMode         : "Sets next game mode. Change will not be visible until script execution is finished; may be overridden. Does not pause script execution.",
                                                        OPCODES_LT2.SetEndGameMode      : "Sets next game mode submode. Change will not be visible until script execution is finished; may be ignored since this only applies to certain gamemodes when combined with changes to the next gamemode, e.g., Movie. Does not pause script execution.",
                                                        OPCODES_LT2.SetMovieNum         : "Sets next played movie ID. Change will not be visible until Movie gamemode is executed. Does not pause script execution.",
                                                        OPCODES_LT2.SetDramaEventNum    : "Set snext event ID. Change will not be visible until DramaEvent gamemode is executed; may be overridden. Does not pause script execution.",
                                                        OPCODES_LT2.SetPuzzleNum        : "Sets next launched internal puzzle ID. Change will not be visible until Puzzle gamemode(s) are executed; may be overridden. Does not pause script execution.",
                                                        OPCODES_LT2.SetFontUserColor    : None,
                                                        OPCODES_LT2.LoadBG              : "Sets the background on the bottom screen. No animation is provided. Does not pause script execution.",
                                                        OPCODES_LT2.LoadSubBG           : "Sets the background on the top screen. No animation is provided. Does not pause script execution.",
                                                        OPCODES_LT2.SpriteOn            : "Shows a character. If called on an invalid character, nothing will happen. Does not pause script execution.",
                                                        OPCODES_LT2.SpriteOff           : "Hides a character. If called on an invalid character, nothing will happen. Does not pause script execution.",
                                                        OPCODES_LT2.DoSpriteFade        : "Transitions a character from visible to invisible or vice versa. If called on an invalid character, nothing will happen. Pauses script execution until done animating.",
                                                        OPCODES_LT2.DrawChapter         : "Triggers a fade in and changes the background on the bottom screen to a chapter introduction background. If called on an invalid background, the fade in will still happen. Pauses script execution until done animating.",
                                                        OPCODES_LT2.SetSpriteAlpha      : None,
                                                        OPCODES_LT2.SetSpritePos        : "Changes a character's position by slot. Does not pause script execution.",
                                                        OPCODES_LT2.ModifyBGPal         : "Tints the bottom screen background palette. This is non-destructive and reversible. Does not pause script execution.",
                                                        OPCODES_LT2.ModifySubBGPal      : "Tints the top screen background palette. This is non-destructive and reversible. Does not pause script execution.",
                                                        OPCODES_LT2.SetSpriteAnimation  : "Changes a character's animation by name. Does not pause script execution.",
                                                        
                                                        OPCODES_LT2.AddMemo                     : "Unlocks a journal entry. If it is already unlocked or out of bounds, nothing will happen. Does not pause script execution.",
                                                        OPCODES_LT2.GameOver                    : "Fades both screens out and sets the next game mode to restart from the title sequence; may be overridden. Pauses script execution until sounds and transitions are complete.",
                                                        OPCODES_LT2.SetEventTea                 : None,
                                                        OPCODES_LT2.ReleaseItem                 : "Removes an item from the inventory. If it isn't present, nothing will happen. Does not pause script execution.",
                                                        OPCODES_LT2.SetSpriteShake              : "Shakes character for a given duration. If called on an invalid character, nothing will happen. Does not pause script execution.",
                                                        OPCODES_LT2.CheckCounterAutoEvent       : "Set next game mode to event on correct event execution history",
                                                        OPCODES_LT2.SetRepeatAutoEventID        : None,
                                                        OPCODES_LT2.ReleaseRepeatAutoEventID    : None,
                                                        OPCODES_LT2.SetFirstTouch               : 'Enable tutorial flag to hint user to tap the screen when entering the Room gamemode. This cannot be disabled by scripting. Does not pause script execution.',
                                                        OPCODES_LT2.EventSelect                 : "Sets next event ID only if the solved puzzle count reaches a threshold. Change will not be visible until DramaEvent gamemode is executed; may be overridden. Does not pause script execution.",

                                                        # Popup
                                                        OPCODES_LT2.DoHukamaruAddScreen     : "Switches to the mystery addition screen. Bad mysteries will be handled gracefully; all characters will be hidden and backgrounds will be changed. Pauses script execution until interaction is complete; end state will leave screen faded out.",
                                                        OPCODES_LT2.DoSubItemAddScreen      : "Shows the puzzle reward addition popup. Bad rewards will be handled gracefully. Pauses script execution until interaction is complete.",
                                                        OPCODES_LT2.DoStockScreen           : "Shows popup relating to last-solved puzzle. Pauses script execution until interaction is complete.",
                                                        OPCODES_LT2.DoNazobaListScreen      : None,
                                                        OPCODES_LT2.DoItemAddScreen         : None,
                                                        OPCODES_LT2.SetSubItem              : None,
                                                        OPCODES_LT2.DoSubGameAddScreen      : None,
                                                        OPCODES_LT2.DoSaveScreen            : None,
                                                        OPCODES_LT2.HukamaruClear           : None,
                                                        OPCODES_LT2.DoPhotoPieceAddScreen   : None,
                                                        OPCODES_LT2.MokutekiScreen          : None,
                                                        OPCODES_LT2.DoNamingHamScreen       : None,
                                                        OPCODES_LT2.DoLostPieceScreen       : None,
                                                        OPCODES_LT2.DoInPartyScreen         : None,
                                                        OPCODES_LT2.DoOutPartyScreen        : None,
                                                        OPCODES_LT2.EndingMessage           : None,
                                                        OPCODES_LT2.ReturnStationScreen     : None,       # Text removed from release
                                                        OPCODES_LT2.CompleteWindow          : None,
                                                        OPCODES_LT2.EndingAddChallenge      : None,

                                                        # Event variable access
                                                        OPCODES_LT2.SetEventCounter : "Sets a byte at a given index in the event storage space to a certain value. Partially ignores out-of-bounds indices; keep values in range. Does not pause script execution.",
                                                        OPCODES_LT2.AddEventCounter : "Adds a value to a byte at a given index in the event storage space. Partially ignores out-of-bounds indices; keep values in range. Does not pause script execution.",
                                                        OPCODES_LT2.OrEventCounter  : "ORs a value to a byte at a given index in the event storage space. Partially ignores out-of-bounds indices; keep values in range. Does not pause script execution.",

                                                        # Screen effects
                                                        OPCODES_LT2.FlashScreen     : "Flashes white on both screens. Pauses script execution while animating.",
                                                        OPCODES_LT2.ShakeBG         : "Shakes the background on the bottom screen. Does not pause script execution.",
                                                        OPCODES_LT2.ShakeSubBG      : "Shakes the background on the top screen. Does not pause script execution.",

                                                        # Fade commands
                                                        OPCODES_LT2.FadeIn              : "Fades in both screens. Pauses script execution while animating.",
                                                        OPCODES_LT2.FadeOut             : "Fades out both screens. Pauses script execution while animating.",
                                                        OPCODES_LT2.FadeInFrame         : "Fades in both screens for the given amount of frames. Pauses script execution while animating.",
                                                        OPCODES_LT2.FadeOutFrame        : "Fades out both screens for the given amount of frames. Pauses script execution while animating.",
                                                        OPCODES_LT2.FadeInFrameMain     : "Fades in the bottom screen for the given amount of frames. Pauses script execution while animating.",
                                                        OPCODES_LT2.FadeOutOnlyMain     : "Fades out the bottom screen. Pauses script execution while animating.",
                                                        OPCODES_LT2.FadeOutFrameMain    : "Fades out the bottom screen for the given amount of frames. Pauses script execution while animating.",
                                                        OPCODES_LT2.FadeInOnlyMain      : "Fades in the bottom screen. Pauses script execution while animating.",
                                                        OPCODES_LT2.FadeInFrameSub      : "Fades in the top screen for the given amount of frames. Pauses script execution while animating.",
                                                        OPCODES_LT2.FadeOutFrameSub     : "Fades out the top screen for the given amount of frames. Pauses script execution while animating.",
                                                        
                                                        # Pause commands
                                                        OPCODES_LT2.WaitFrame           : "Pauses script execution until enough frames pass.",
                                                        OPCODES_LT2.WaitFrame2          : "Pauses script execution until enough frames pass. This is restricted to predefined timings.",
                                                        OPCODES_LT2.DrawFrames          : "Pauses script execution until enough frames pass. Rendering will continue in the meantime.",
                                                        OPCODES_LT2.WaitInput           : "Pauses script execution until the screen is touched.",
                                                        OPCODES_LT2.WaitVSyncOrPenTouch : "Pauses script execution until either the screen is touched or enough frames pass."}