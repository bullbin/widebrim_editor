from editor.rom_management.general_purge.wipeout import purgeFilepaths
from widebrim.filesystem.low_level.fs_romloader import FilesystemNds
from widebrim.madhatter.common import logSevere

HARDCODED = ["lukeletter/?/op_message.spr",
"lukeletter/?/message.spr",
"lukeletter/?/message2.spr",
"lukeletter/?/end_message.spr",
"menu/secret/%s/secret_modoru.spr",
"name/cursor.spr",
"name/?/kettei.spr",
"name/?/kesu.spr",
"name/?/bad_code.spr",
"nazo/drawinput/di_cursor.spr",
"name/?/name_ok.spr",
"name/name_btn.spr",
"name/?/bad_name.spr",
"subgame/camera/%s/modoru_btn.spr",
"subgame/camera/%s/mov_rot.spr",
"subgame/camera/camera_parts.spr",
"subgame/camera/camera_p_icon.spr",
"subgame/camera/camera_icon_arrow.spr",
"subgame/camera/?/congratulation.spr",
"subgame/photo/photo_window.spr",
"subgame/tea/%s/yametoku.spr",
"subgame/tea/%s/furumau.spr",
"subgame/tea/%s/chougo.spr",
"subgame/tea/tea_icon.spr",
"subgame/tea/tea_number.spr",
"subgame/tea/icon.spr",
"subgame/tea/%s/touch_window.spr",
"cursor_wait.spr",
"system/prize_window2.spr",
"subgame/tea/?/modoru_btn.spr",
"subgame/tea/modoru_cover.spr",
"subgame/tea/?/return_btn.spr",
"subgame/tea/?/recipe_btn.spr",
"subgame/tea/?/furumau2.spr",
"subgame/tea/?/help_btn.spr",
"subgame/tea/?/name.spr",
"subgame/tea/tea_pot.spr",
"subgame/tea/tea_futa.spr",
"subgame/tea/window.spr",
"subgame/tea/?/touch_window.spr",
"subgame/ham/%s/modoru_btn.spr",
"subgame/ham/%s/start_btn.spr",
"subgame/ham/%s/clear_btn.spr",
"subgame/ham/seticon.spr",
"subgame/ham/iten_num.spr",
"subgame/ham/yerrow_num.spr",
"subgame/ham/ham_face%d.spr",
"subgame/ham/%s/end_btn.spr",
"subgame/ham/white_num.spr",
"subgame/ham/window_ham.spr",
"subgame/ham/hakken_icon.spr",
"subgame/ham/%s/walk_mes.spr",
"subgame/photo/photo_icon.spr",
"subgame/photo/slash.spr",
"subgame/photo/?/clear.spr",
"subgame/photo/%s/album_modoru.spr",
"subgame/photo/%s/re_chosen_btn.spr",
"subgame/photo/%s/yameru_btn.spr",
"subgame/photo/%s/ayashi_icon.spr",
"nazo/system/?/nazo_title.spr",
"subgame/photo/%s/koko_btn.spr",
"subgame/photo/%s/kesu_btn.spr",
"subgame/photo/%s/photo_msg.spr",
"subgame/photo/photo_num.spr",
"subgame/photo/circle.spr",
"subgame/photo/o.spr",
"subgame/photo/fail%i_%i.spr",
"subgame/photo/check_icon.spr",
"menu/bag/reset_window.spr",
"menu/bag/%s/reset_font.spr",
"menu/bag/%s/tojiru.spr",
"menu/bag/reset.spr",
"system/btn/%s/yes.spr",
"system/btn/%s/no.spr",
"menu/bag/%s/memo.spr",
"menu/bag/%s/hukamaru.spr",
"menu/bag/%s/jiten.spr",
"menu/bag/%s/save.spr",
"tobj/window.spr",
"system/btn/?/new_button.spr",
"menu/bag/item_icon.spr",
"menu/bag/?/help_mes.spr",
"menu/bag/%s/diary.spr",
"menu/bag/%s/camera_fix.spr",
"menu/bag/%s/camera.spr",
"menu/bag/no_camera.spr",
"menu/bag/%s/ham_fix.spr",
"menu/bag/%s/ham.spr",
"menu/bag/no_ham.spr",
"menu/bag/%s/tea_fix.spr",
"menu/bag/%s/tea.spr",
"menu/bag/no_tea.spr",
"menu/bag/%s/memo_page_buttons.spr",
"menu/bag/%s/memo_close_buttons.spr",
"menu/bag/%s/memo_gfx.spr",
"system/system_num.spr",
"menu/wifi/%s/wifi_window3.spr",
"menu/jiten/?/jiten_num.spr",
"menu/jiten/%s/jiten_btn.spr",
"menu/bag/%s/jiten_sub.spr",
"menu/wifi/jiten_guard1.spr",
"menu/wifi/jiten_guard2.spr",
"system/btn/%s/cancel.spr",
"menu/jiten/%s/jiten_title.spr",
"menu/jiten/%s/tag.spr",
"menu/jiten/jiten_guard.spr",
"system/btn/?/save_ok.spr",
"event/twindow.spr",
"menu/jiten/jiten_scroll.spr",
"system/file_numbers.spr",
"menu/save/%s/save_window.spr",
"menu/save/%s/load_window.spr",
"system/prize_window.spr",
"menu/bag/%s/info_mode_chr.spr",
"menu/bag/?/fukamaru_ok.spr",
"event/hukmaru_hanko.spr",
"menu/bag/diary_icon.spr",
"menu/secret/%s/secretmenu_btn.spr",
"menu/secret/?/wifimenu_btn.spr",
"system/btn/?/cancel.spr",
"menu/secret/%s/omake_mode.spr",
"menu/secret/artmode_num.spr",
"menu/secret/%s/artmode_btn.spr",
"menu/secret/%s/modoru_btn.spr",
"menu/secret/%s/next_btn.spr",
"menu/secret/chr_file%i.spr",
"menu/secret/omake_music.spr",
"menu/secret/?/modoru_btn.spr",
"menu/secret/voice_icon.spr",
"menu/secret/movie_icon.spr",
"menu/secret/%s/secretcode_btn.spr",
"menu/secret/?/challenge_btn.spr",
"menu/secret/?/secret_modoru.spr",
"menu/secret/challenge_icon.spr",
"menu/secret/?/complite.spr",
"menu/nazoba/?/nazoba_btn.spr",
"system/btn/?/yes.spr",
"system/btn/?/no.spr",
"menu/nazoba/nazoba_win.spr",
"nazo/system/%s/nazo_title.spr",
"nazo/system/picaratBig.spr",
"nazo/system/picaratTotal.spr",
"nazo/system/picaratSmall.spr",
"nazo/system/?/seikai_text.spr",
"nazo/system/?/nazo_text.spr",
"nazo/system/?/touch.spr",
"nazo/system/picaratgetbig.spr",
"nazo/system/picaratgetsmall.spr",
"nazo/system/?/retry.spr",
"nazo/system/?/later.spr",
"nazo/system/?/viewhint.spr",
"system/btn/%s/memo.spr",
"system/btn/%s/modoru_memo.spr",
"system/btn/?/hint_wifi.spr",
"system/btn/?/hint.spr",
"system/btn/%s/atode.spr",
"system/btn/%s/erase.spr",
"nazo/drawinput/%s/di_kaito.spr",
"system/btn/%s/hantei.spr",
"system/btn/%s/reset.spr",
"system/memo_window.spr",
"system/btn/?/hint_pica.spr",
"nazo/system/%s/touch.spr",
"nazo/system/%s/t_next.spr",
"nazo/system/%s/hint1.spr",
"nazo/system/%s/hint2.spr",
"nazo/system/%s/hint3.spr",
"nazo/system/%s/hintlock1.spr",
"nazo/system/%s/hintlock2.spr",
"nazo/system/%s/hintlock3.spr",
"nazo/system/hint_num.spr",
"nazo/match/match.spr",
"nazo/match/matchnum.spr",
"nazo/match/%s/nomoretouch.spr",
"nazo/slide/slidepuzzle2.spr",
"nazo/slide/slidepuzzle.spr",
"nazo/common/counter_number.spr",
"nazo/tracebutton/%s/retry_trace.spr",
"nazo/tracebutton/point_trace.spr",
"nazo/tracebutton/arrow_left.spr",
"nazo/tracebutton/arrow_right.spr",
"nazo/tracebutton/q10_window.spr",
"nazo/connect/connect.spr",
"nazo/cup/cup_numbers.spr",
"nazo/cup/%s/cup_gfx.spr",
"nazo/cut/line_point.spr",
"nazo/cut/line_here.spr",
"nazo/cut/%s/nomorelines.spr",
"nazo/cut/cut_out.spr",
"nazo/tilerotate/pict_puzzle_rot.spr",
"nazo/pancake/pancake_gfx.spr",
"nazo/drawinput/%s/di_erase2.spr",
"nazo/drawinput/inputnumbers.spr",
"nazo/drawinput/%s/di_hantei.spr",
"nazo/drawinput/%s/di_allreset.spr",
"nazo/drawinput/%s/di_modoru.spr",
"nazo/drawinput/%s/inputfail.spr",
"nazo/drawinput/q58_gfx.spr",
"nazo/knight/knight_gfx.spr",
"nazo/rose/rose_gfx.spr",
"nazo/tilerotate/pict_puzzle_rot_q203.spr",
"nazo/tilerotate/q2_button.spr",
"nazo/iceskate/iceskate_gfx.spr",
"menu/wifi/?/wifi_download_msg.spr",
"menu/wifi/wifi_download_gfx.spr",
"menu/wifi/?/wifi_download_btn.spr",
"menu/wifi/?/wifi_download_msg2.spr",
"menu/wifi/?/wifi_window%i.spr",
"nazo/pegsolitaire/solitaire_gfx.spr",
"nazo/couple/couple_gfx.spr",
"nazo/lamp/lamp_gfx.spr",
"nazo/bridge/q99_foot.spr",
"tobj/icon.spr",
"map/movemode.spr",
"map/menu_icon.spr",
"map/camera_icon.spr",
"map/hintcoin.spr",
"map/icon_buttons.spr",
"map/touch_icon.spr",
"map/teaevent_icon.spr",
"map/%s/firsttouch.spr",
"eventobj/obj_%i.spr",
"map/exit_%i.spr",
"map/nazoba_kemuri.spr",
"map/?/nazoba_btn.spr",
"map/nazoba_bottle.spr",
"map/ham_icon.spr",
"menu/bag/piece_icon.spr",
"eventchr/?/chr%i.spr",
"eventchr/chr%i.spr",
"eventchr/%s/chr%i_n.spr",
"event/nazo_icon.spr",
"event/diary_icon.spr",
"title/%s/start.spr",
"title/%s/continue.spr",
"title/%s/secret.spr",
"title/waku.spr",
"title/train.spr",
"title/senro.spr",
"subgame/tea/arrow.sbj",
"subgame/tea/face_luke.sbj",
"subgame/tea/face_layton.sbj",
"subgame/tea/window.sbj",
"subgame/tea/limit_icon.sbj",
"subgame/tea/limit_num.sbj",
"subgame/tea/?/help_mes.sbj",
"subgame/ham/seticon.sbj",
"subgame/ham/level_num.sbj",
"subgame/ham/%s/level_mes.sbj",
"subgame/ham/hukidashi.sbj",
"subgame/ham/count_num.sbj",
"nazo/system/?/nazo_title.sbj",
"menu/bag/status_number2.sbj",
"menu/bag/status_number.sbj",
"menu/bag/medal_icon.sbj",
"menu/bag/dot_layton_walk.sbj",
"menu/jiten/jiten_prize.sbj",
"menu/jiten/%s/jiten_num.sbj",
"menu/jiten/jiten_hintbox.sbj",
"menu/jiten/jiten_q1.sbj",
"menu/jiten/jiten_q%i.sbj",
"ending/staff_bg.sbj",
"menu/secret/omake_music_num.sbj",
"nazo/system/%s/nazo_title.sbj",
"nazo/system/%s/nazo_text.sbj",
"menu/wifi/wifi_ant.sbj",
"menu/wifi/wifi_bar.sbj",
"map/mapicon.sbj",
"map/map_icons.sbj",
"map/%s/toketa_nazo.sbj",
"map/map_number.sbj",
"map/%s/piece_mes.sbj",
"map/piece_num.sbj",
"map/?/map_arrows.sbj",
"title/%s/logo.sbj"]

def purgeSprites(romFs : FilesystemNds, language):
    output = purgeFilepaths(romFs, language, "/data_lt2/ani", [("spr", "arc"), ("sbj", "arj")], HARDCODED)
    logSevere(output[1])