from enum import IntEnum, Enum, StrEnum
from dataclasses import dataclass


@dataclass
class EntryTypeData:
    short: str
    long: str
    emoji: str
    time_independent: bool = False
    order: int = 0
    bottom: bool = False
    show_in_schedule: bool = True
    requires_responsible: bool = True


class EntryType(Enum):
    MORNING_PRAYER = EntryTypeData("M-bön", "Morgonbön", "💒")
    EVENING_PRAYER = EntryTypeData("K-and", "Kvällsandakt", "💒")
    EDUCATION = EntryTypeData("Und", "Undervisning", "📖")
    FEEDBACK = EntryTypeData("Åter", "Återkoppling", "📖")
    LEADER_MEETING = EntryTypeData(
        "Ls", "Ledarsamling", "🌟", requires_responsible=False
    )
    OTHER = EntryTypeData("Övr", "Övrigt", "📌", True, 6, requires_responsible=False)
    INFO = EntryTypeData("Info", "Information", "📌", requires_responsible=False)
    CLEANING = EntryTypeData("Städ", "Städpass", "🧹", requires_responsible=False)
    DAY_HOST = EntryTypeData("Värd", "Dagvärd", "🧑‍✈️", True, 2)
    DAY_OFF = EntryTypeData("Led", "Ledig", "⛱", True, 3, requires_responsible=False)
    THEME = EntryTypeData("Tema", "Tema", "🧠", True, 1, requires_responsible=False)
    WAKE_UP = EntryTypeData("Väck", "Väckning", "⏰")
    PUT_TO_BED = EntryTypeData("Natt", "Nattning", "🛌")
    SLEEP_IN = EntryTypeData(
        "Sov", "Sovmorgon", "😴", True, 4, requires_responsible=False
    )
    NIGHT_DUTY = EntryTypeData("Jour", "Nattjour", "🌛", True, 5, True)
    EVENING_ACTIVITY = EntryTypeData("K-akt", "Kvällsaktivitet", "🕺💃")
    AFTERNOON_ACTIVITY = EntryTypeData(
        "E-akt", "Eftermiddagsaktivitet", "🕺💃", requires_responsible=False
    )
    BREAKFAST = EntryTypeData("Fruk", "Frukost", "🍽️", requires_responsible=False)
    LUNCH = EntryTypeData("Lu", "Lunch", "🍽️", requires_responsible=False)
    DINNER = EntryTypeData("Mi", "Middag", "🍽️", requires_responsible=False)
    EVENING_MEAL = EntryTypeData("Kfi", "Kvällsfika", "🍽️", requires_responsible=False)
    BOAT = EntryTypeData("Båt", "Båtpass", "⛵️", show_in_schedule=False)

    @classmethod
    def time_independent_members(cls):
        return sorted(
            [member for member in cls if member.value.time_independent],
            key=lambda m: m.value.order,
        )

    @classmethod
    def time_independent_top(cls):
        return sorted(
            [
                member
                for member in cls
                if member.value.time_independent and not member.value.bottom
            ],
            key=lambda m: m.value.order,
        )

    @classmethod
    def time_independent_bottom(cls):
        return sorted(
            [
                member
                for member in cls
                if member.value.time_independent and member.value.bottom
            ],
            key=lambda m: m.value.order,
        )


class Role(IntEnum):
    PRIEST = 1
    DEACON = 2
    CAMP_MANAGER = 3
    ASSISTANT_CAMP_MANAGER = 4
    MUSICIAN = 5
    BOAT_LEADER = 6
    SECURITY_OFFICER = 7
    HEALTH_OFFICER = 8


class ParticipantType(IntEnum):
    LEADER = 1
    CAMP_MANAGEMENT = 2
    CONFIRMEE = 3
    OTHER = 4


class LeaderYearType(StrEnum):
    FIRST_YEAR = "1"
    SECOND_YEAR = "2"
    THIRD_YEAR = "3"
    FOURTH_PLUS = "4+"
