from dataclasses import dataclass, field
import datetime as dt
from campx.model.schedule_entry import ScheduleEntry

from campx.model.enums import EntryType


@dataclass
class Day:
    """Represents a single camp day and its scheduled entries."""

    date: dt.date
    schedule_entries: list[ScheduleEntry] = field(default_factory=list)

    def as_str(self, format: str = "%Y-%m-%d") -> str:
        """Return the day formatted for display or export."""
        return self.date.strftime(format)

    def get_entries(self, entry_type: EntryType) -> list[ScheduleEntry]:
        """Return entries for this day matching a specific entry type."""
        return [e for e in self.schedule_entries if e.entry_type == entry_type]
