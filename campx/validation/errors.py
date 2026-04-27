from dataclasses import dataclass, field
import datetime as dt
from enum import StrEnum

from campx.model.enums import EntryType


class ValidationSeverity(StrEnum):
    """Severity levels used to classify validation errors."""

    MAJOR = "MAJOR"
    MINOR = "MINOR"


@dataclass(frozen=True)
class ValidationError:
    """Base type for all schedule validation errors."""

    code: str = field(init=False, default="validation_error")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MAJOR)

    def __str__(self) -> str:
        """Render the human-readable validation message."""
        return self.message

    @property
    def message(self) -> str:
        """Return the human-readable message for this error instance."""
        raise NotImplementedError


@dataclass(frozen=True)
class OverlapValidationError(ValidationError):
    """Raised when a leader is assigned overlapping entry types."""

    leader_name: str
    type1: EntryType
    type2: EntryType
    dates: tuple[dt.date, ...]
    code: str = field(init=False, default="overlap")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MAJOR)

    @property
    def message(self) -> str:
        return (
            f"Leader {self.leader_name} has overlapping entries of type "
            f"{self.type1.name} and {self.type2.name} on dates: "
            f"{', '.join(str(date) for date in self.dates)}"
        )


@dataclass(frozen=True)
class MaxResponsibilitiesPerDayValidationError(ValidationError):
    """Raised when a leader exceeds the maximum daily assignment count."""

    leader_name: str
    day_label: str
    actual: int
    max_allowed: int
    code: str = field(init=False, default="max_responsibilities_per_day")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MAJOR)

    @property
    def message(self) -> str:
        return f"Too many entries on {self.day_label} for leader {self.leader_name}: {self.actual} > {self.max_allowed}"


@dataclass(frozen=True)
class MaxResponsibilitiesPerEntryTypeValidationError(ValidationError):
    """Raised when a leader exceeds an entry-type specific allocation limit."""

    leader_name: str
    entry_types: tuple[EntryType, ...]
    actual: int
    max_allowed: int
    code: str = field(init=False, default="max_responsibilities_per_entry_type")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MINOR)

    @property
    def message(self) -> str:
        entry_label = ", ".join(entry_type.name for entry_type in self.entry_types)
        return (
            f"Too many entries of type(s) {entry_label} for leader "
            f"{self.leader_name}: {self.actual} > {self.max_allowed}"
        )


@dataclass(frozen=True)
class MinResponsibilitiesPerEntryTypeValidationError(ValidationError):
    """Raised when a leader falls short of a required allocation minimum."""

    leader_name: str
    entry_type: EntryType
    actual: int
    min_required: int
    code: str = field(init=False, default="min_responsibilities_per_entry_type")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MINOR)

    @property
    def message(self) -> str:
        return (
            f"Not enough entries of type {self.entry_type.name} for leader "
            f"{self.leader_name}: {self.actual} < {self.min_required}"
        )


@dataclass(frozen=True)
class DayOffEntryCountValidationError(ValidationError):
    """Raised when a leader has an unexpected number of entries on a day off."""

    leader_name: str
    day_date: dt.date
    actual_count: int
    code: str = field(init=False, default="day_off_entry_count")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MAJOR)

    @property
    def message(self) -> str:
        return (
            f"Expected exactly one entry for {self.leader_name} on day off "
            f"{self.day_date}, found {self.actual_count}"
        )


@dataclass(frozen=True)
class DayOffWrongEntryTypeValidationError(ValidationError):
    """Raised when a non-day-off entry is assigned on a leader's day off."""

    leader_name: str
    day_date: dt.date
    code: str = field(init=False, default="day_off_wrong_entry_type")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MAJOR)

    @property
    def message(self) -> str:
        return (
            f"Entry on day off {self.day_date} for leader {self.leader_name} "
            "is not DAY_OFF"
        )


@dataclass(frozen=True)
class NoResponsibilitiesValidationError(ValidationError):
    """Raised when a leader has no responsibilities in the schedule."""

    leader_name: str
    code: str = field(init=False, default="no_responsibilities")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MAJOR)

    @property
    def message(self) -> str:
        return f"Leader {self.leader_name} has no responsibilities at all"


@dataclass(frozen=True)
class TooManyResponsibleValidationError(ValidationError):
    """Raised when an entry has more responsibles than allowed."""

    entry_type: EntryType
    day_label: str
    actual: int
    max_allowed: int
    code: str = field(init=False, default="too_many_responsible")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MINOR)

    @property
    def message(self) -> str:
        return (
            f"Too many responsible leaders for entry {self.entry_type.name} on "
            f"{self.day_label}: {self.actual} > {self.max_allowed}"
        )


@dataclass(frozen=True)
class TooFewResponsibleValidationError(ValidationError):
    """Raised when an entry has fewer responsibles than required."""

    entry_type: EntryType
    day_label: str
    actual: int
    min_required: int
    code: str = field(init=False, default="too_few_responsible")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MAJOR)

    @property
    def message(self) -> str:
        return (
            f"Too few responsible leaders for entry {self.entry_type.name} on "
            f"{self.day_label}: {self.actual} < {self.min_required}"
        )


@dataclass(frozen=True)
class DuplicateResponsibleValidationError(ValidationError):
    """Raised when the same participant is assigned multiple times to an entry."""

    entry_type: EntryType
    day_label: str
    code: str = field(init=False, default="duplicate_responsible")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MAJOR)

    @property
    def message(self) -> str:
        return (
            f"Duplicate responsible leaders for entry {self.entry_type.name} on "
            f"{self.day_label}"
        )


@dataclass(frozen=True)
class OnlyFirstYearResponsibleValidationError(ValidationError):
    """Raised when only first-year leaders cover an entry."""

    entry_type: EntryType
    day_label: str
    code: str = field(init=False, default="only_first_year_responsible")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MINOR)

    @property
    def message(self) -> str:
        return (
            f"Entry {self.entry_type.name} on {self.day_label} has only first-year "
            "leaders responsible"
        )


@dataclass(frozen=True)
class NoResponsibleValidationError(ValidationError):
    """Raised when a required entry has no responsible participant."""

    entry_type: EntryType
    day_label: str
    code: str = field(init=False, default="no_responsible")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MAJOR)

    @property
    def message(self) -> str:
        return (
            f"No responsible leaders for entry {self.entry_type.name} on "
            f"{self.day_label}"
        )


@dataclass(frozen=True)
class TooManyEntriesWhileDayHostValidationError(ValidationError):
    """Raised when a day host has more assignments than allowed that day."""

    leader_name: str
    day_label: str
    actual: int
    max_allowed: int
    code: str = field(init=False, default="too_many_entries_while_day_host")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MINOR)

    @property
    def message(self) -> str:
        return (
            f"Leader {self.leader_name} has too many entries on a day they are "
            f"hosting ({self.day_label}): {self.actual} > {self.max_allowed}"
        )


@dataclass(frozen=True)
class MinDaysBetweenEntryTypesValidationError(ValidationError):
    """Raised when a leader has insufficient days between certain entry types."""

    leader_name: str
    type1: EntryType
    type2: EntryType
    actual_min_days: int
    required_min_days: int
    code: str = field(init=False, default="min_days_between_entry_types")
    severity: ValidationSeverity = field(init=False, default=ValidationSeverity.MINOR)

    @property
    def message(self) -> str:
        return (
            f"Leader {self.leader_name} has only {self.actual_min_days} days between "
            f"entries of type {self.type1.name} and {self.type2.name}, but at least "
            f"{self.required_min_days} are required"
        )
