from dataclasses import dataclass
from campx.model.day import Day
from campx.model.schedule_entry import EntryType, ScheduleEntry


@dataclass
class Schedule:
    """Represents the full schedule across all camp days."""

    days: list[Day]

    def all_entries(
        self, day: Day | None = None, entry_type: EntryType | None = None
    ) -> list[ScheduleEntry]:
        """Return all entries, optionally filtered by day and entry type."""
        days_to_consider = [day] if day else self.days

        entries = [
            entry
            for d in days_to_consider
            for entry in d.schedule_entries
            if entry_type is None or entry.entry_type == entry_type
        ]

        return entries
