from campx.model.enums import EntryType
from enum import StrEnum

START_HOUR = 8
END_HOUR = 24


class Colors(StrEnum):
    LIGHT_BLUE = "DDEBF7"
    LIGHT_GREEN = "E2EFDA"
    LIGHT_YELLOW = "FFF2CC"
    LIGHT_PURPLE = "D5A6DB"
    ORANGE = "FFC886"
    DARK_PURPLE = "C27BA0"
    YELLOW = "FFEA00"
    BLUE = "6D9EEB"
    GREEN = "B6D7A8"
    GREY = "BFBFBF"
    LIGHT_LIGHT_GREY = "F0F0F0"
    LIGHT_GREY = "F2F2F2"
    DEFAULT = "FFFFFF"
    BLACK = "000000"


ACTIVITY_COLORS = {
    EntryType.BREAKFAST: Colors.LIGHT_BLUE,
    EntryType.LUNCH: Colors.LIGHT_BLUE,
    EntryType.DINNER: Colors.LIGHT_BLUE,
    EntryType.EVENING_MEAL: Colors.LIGHT_BLUE,
    EntryType.EDUCATION: Colors.LIGHT_GREEN,
    EntryType.EVENING_ACTIVITY: Colors.LIGHT_YELLOW,
    EntryType.AFTERNOON_ACTIVITY: Colors.LIGHT_YELLOW,
    EntryType.MORNING_PRAYER: Colors.GREEN,
    EntryType.EVENING_PRAYER: Colors.GREEN,
    EntryType.LEADER_MEETING: Colors.ORANGE,
    EntryType.OTHER: Colors.LIGHT_GREY,
    EntryType.CLEANING: Colors.LIGHT_GREY,
    EntryType.WAKE_UP: Colors.LIGHT_GREY,
    EntryType.PUT_TO_BED: Colors.LIGHT_GREY,
    EntryType.SLEEP_IN: Colors.LIGHT_PURPLE,
    EntryType.DAY_OFF: Colors.DARK_PURPLE,
    EntryType.DAY_HOST: Colors.YELLOW,
    EntryType.BOAT: Colors.BLUE,
    EntryType.FEEDBACK: Colors.LIGHT_GREEN,
    EntryType.INFO: Colors.LIGHT_GREY,
}


def get_activity_color(activity_type: EntryType):
    return ACTIVITY_COLORS.get(activity_type, Colors.DEFAULT)
