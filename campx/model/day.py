from dataclasses import dataclass, field
import datetime as dt
from campx.model.schedule_entry import ScheduleEntry

from campx.model.enums import EntryType

SWEDISH_MONTH_NAMES = {
    1: "januari",
    2: "februari",
    3: "mars",
    4: "april",
    5: "maj",
    6: "juni",
    7: "juli",
    8: "augusti",
    9: "september",
    10: "oktober",
    11: "november",
    12: "december",
}

SWEDISH_MONTH_ABBREVIATIONS = {
    1: "jan.",
    2: "feb.",
    3: "mars",
    4: "apr.",
    5: "maj",
    6: "juni",
    7: "juli",
    8: "aug.",
    9: "sep.",
    10: "okt.",
    11: "nov.",
    12: "dec.",
}


@dataclass
class Day:
    """Represents a single camp day and its scheduled entries."""

    date: dt.date
    schedule_entries: list[ScheduleEntry] = field(default_factory=list)

    def as_str(
        self, format: str = "%Y-%m-%d", swedish_month_names: bool = False
    ) -> str:
        """Return the day formatted for display or export."""
        if not swedish_month_names:
            return self.date.strftime(format)

        formatted = format.replace("%B", "__MONTH_FULL__").replace(
            "%b", "__MONTH_ABBR__"
        )
        return (
            self.date.strftime(formatted)
            .replace("__MONTH_FULL__", SWEDISH_MONTH_NAMES[self.date.month])
            .replace("__MONTH_ABBR__", SWEDISH_MONTH_ABBREVIATIONS[self.date.month])
        )

    def get_entries(self, entry_type: EntryType) -> list[ScheduleEntry]:
        """Return entries for this day matching a specific entry type."""
        return [e for e in self.schedule_entries if e.entry_type == entry_type]
