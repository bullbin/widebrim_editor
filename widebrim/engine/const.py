from enum import Enum

RESOLUTION_NINTENDO_DS          = (256,192)

TIME_FRAMECOUNT_TO_MILLISECONDS = 1000/60

EVENT_ID_START_PUZZLE           = 20000
EVENT_ID_START_TEA              = 30000

PATH_DB_EV_INF2     = "/data_lt2/rc/%s/ev_inf2.dlz"
PATH_DB_GOAL_INF    = "goal_inf.dlz"
PATH_DB_RC_ROOT     = "/data_lt2/rc/%s"

PATH_ANI            = "/data_lt2/ani/%s"
PATH_EXT_BGANI      = "bgani/%s"
PATH_EXT_EXIT       = "map/exit_%i.arc"
PATH_EXT_EVENT      = "eventobj/obj_%i.arc"

PATH_BG_ROOT        = "/data_lt2/bg/%s"
PATH_CHAP_ROOT      = "chapter/?/chapter%i.arc"

PATH_FACE_ROOT      = "/data_lt2/ani/sub/%s"
PATH_BODY_ROOT      = "/data_lt2/ani/eventchr/chr%i.arc"

PATH_EVENT_SCRIPT   = "/data_lt2/event/ev_d%i.plz"
PATH_EVENT_SCRIPT_A = "/data_lt2/event/ev_d%ia.plz"
PATH_EVENT_SCRIPT_B = "/data_lt2/event/ev_d%ib.plz"
PATH_EVENT_SCRIPT_C = "/data_lt2/event/ev_d%ic.plz"
PATH_EVENT_TALK     = "/data_lt2/event/%s/ev_t%i.plz"
PATH_EVENT_TALK_A   = "/data_lt2/event/%s/ev_t%ia.plz"
PATH_EVENT_TALK_B   = "/data_lt2/event/%s/ev_t%ib.plz"
PATH_EVENT_TALK_C   = "/data_lt2/event/%s/ev_t%ic.plz"

PATH_PACK_EVENT_DAT = "d%i_%.3i.dat"
PATH_PACK_EVENT_SCR = "e%i_%.3i.gds"
PATH_PACK_TALK      = "t%i_%.3i_%i.gds"

PATH_PROGRESSION_DB = "/data_lt2/place/data.plz"

PATH_PLACE_A = "/data_lt2/place/plc_data1.plz"
PATH_PLACE_B = "/data_lt2/place/plc_data2.plz"

PATH_PACK_PLACE = "n_place%i_%i.dat"

PATH_PLACE_BG = "map/main%i.bgx"
PATH_PLACE_MAP = "map/map%i.bgx"
PATH_EVENT_BG = "event/sub%i.bgx"

PATH_PACK_PLACE_NAME = "/data_lt2/nazo/%s/jiten.plz"
PATH_PACK_TXT2 = "/data_lt2/txt/%s/txt2.plz"

PATH_TEXT_GOAL = "goal_%i.txt"
PATH_TEXT_PLACE_NAME = "p_%i.txt"

class LANGUAGES(Enum):
    French      = "fr"
    English     = "en"
    Chinese     = "ch"
    German      = "ge"
    Dutch       = "du"
    Italian     = "it"
    Spanish     = "sp"
    Korean      = "ko"
    Japanese    = "jp"