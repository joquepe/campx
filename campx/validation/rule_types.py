from dataclasses import dataclass
from typing import Callable, Iterable

from campx.model.camp import Camp
from campx.model.day import Day
from campx.model.participant import Participant
from campx.model.schedule_entry import ScheduleEntry

from campx.validation.errors import ValidationError


@dataclass
class Validation:
    """Wraps a leader validation callable with a uniform interface."""

    func: Callable[[Participant, Camp], Iterable[ValidationError]]

    def validate(self, leader: Participant, camp: Camp) -> list[ValidationError]:
        """Evaluate the validation and return concrete error instances."""
        return list(self.func(leader, camp))


@dataclass
class EntryValidation:
    """Wraps an entry validation callable with a uniform interface."""

    func: Callable[[ScheduleEntry, Day, Camp], Iterable[ValidationError]]

    def validate(
        self, schedule_entry: ScheduleEntry, day: Day, camp: Camp
    ) -> list[ValidationError]:
        """Evaluate the validation and return concrete error instances."""
        return list(self.func(schedule_entry, day, camp))
