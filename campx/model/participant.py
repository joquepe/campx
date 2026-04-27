from dataclasses import dataclass
from campx.model.enums import ParticipantType, Role, LeaderYearType
from campx.model.schedule import Schedule
from campx.model.schedule_entry import EntryType, ScheduleEntry
import datetime as dt
from typing import Literal
from campx.model.day import Day

Gender = Literal["F", "M", "O"]


@dataclass
class Participant:
    """Represents a person participating in the camp schedule."""

    participant_id: int
    first_name: str
    last_name: str
    gender: Gender
    birthday: dt.date
    participant_type: ParticipantType

    roles: list[Role] | None = None
    leader_year_type: LeaderYearType | None = None
    nick_name: str | None = None
    first_name_initials: str | None = None
    last_name_initials: str | None = None

    @property
    def full_name(self) -> str:
        """Return the participant's full display name."""
        return self.first_name + " " + self.last_name

    @property
    def age(self) -> int:
        """Return the participant's current age in years."""
        today = dt.date.today()
        age = today.year - self.birthday.year
        if (today.month, today.day) < (self.birthday.month, self.birthday.day):
            age -= 1
        return age

    @property
    def initials(self) -> str:
        """Return the participant's initials for display."""
        return self.first_name_initials + self.last_name_initials

    def get_responsible_entries(
        self,
        schedule: Schedule,
        day: Day | None = None,
        entry_type: EntryType | None = None,
    ) -> list[ScheduleEntry]:
        """Return schedule entries this participant is responsible for."""
        return [
            entry
            for entry in schedule.all_entries(day=day, entry_type=entry_type)
            if self in entry.responsible
        ]

    def get_days_with_entry_type(
        self, entry_type: EntryType, schedule: Schedule
    ) -> list[Day]:
        """Return days where this participant is responsible for a given entry type."""
        return [
            d
            for d in schedule.days
            if any(self in e.responsible for e in d.get_entries(entry_type))
        ]
