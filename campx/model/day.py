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

SWEDISH_WEEKDAY_NAMES = {
    0: "måndag",
    1: "tisdag",
    2: "onsdag",
    3: "torsdag",
    4: "fredag",
    5: "lördag",
    6: "söndag",
}

SWEDISH_WEEKDAY_ABBREVIATIONS = {
    0: "mån",
    1: "tis",
    2: "ons",
    3: "tor",
    4: "fre",
    5: "lör",
    6: "sön",
}


@dataclass
class Day:
    """Represents a single camp day and its scheduled entries."""

    date: dt.date
    schedule_entries: list[ScheduleEntry] = field(default_factory=list)

    def as_str(
        self,
        format: str = "%Y-%m-%d",
        swedish_month_names: bool = False,
        swedish_weekday_names: bool = False,
    ) -> str:
        """Return the day formatted for display or export."""
        if not swedish_month_names and not swedish_weekday_names:
            return self.date.strftime(format)

        formatted = format
        if swedish_month_names:
            formatted = formatted.replace("%B", "__MONTH_FULL__").replace(
                "%b", "__MONTH_ABBR__"
            )
        if swedish_weekday_names:
            formatted = formatted.replace("%A", "__WEEKDAY_FULL__").replace(
                "%a", "__WEEKDAY_ABBR__"
            )

        rendered = self.date.strftime(formatted)
        if swedish_month_names:
            rendered = rendered.replace(
                "__MONTH_FULL__", SWEDISH_MONTH_NAMES[self.date.month]
            ).replace("__MONTH_ABBR__", SWEDISH_MONTH_ABBREVIATIONS[self.date.month])
        if swedish_weekday_names:
            rendered = rendered.replace(
                "__WEEKDAY_FULL__", SWEDISH_WEEKDAY_NAMES[self.date.weekday()]
            ).replace(
                "__WEEKDAY_ABBR__", SWEDISH_WEEKDAY_ABBREVIATIONS[self.date.weekday()]
            )
        return rendered

    def get_entries(self, entry_type: EntryType) -> list[ScheduleEntry]:
        """Return entries for this day matching a specific entry type."""
        return [e for e in self.schedule_entries if e.entry_type == entry_type]
