import datetime as dt
from collections.abc import Iterable
from dataclasses import dataclass

from campx.camp_config import get_validation_config
from campx.model.camp import Camp
from campx.model.enums import EntryType
from campx.model.participant import Participant

from campx.validation.errors import (
    DayOffEntryCountValidationError,
    DayOffWrongEntryTypeValidationError,
    MaxResponsibilitiesPerDayValidationError,
    MaxResponsibilitiesPerEntryTypeValidationError,
    MinResponsibilitiesPerEntryTypeValidationError,
    NoResponsibilitiesValidationError,
    OverlapValidationError,
    TooManyEntriesWhileDayHostValidationError,
    ValidationError,
    MinDaysBetweenEntryTypesValidationError,
)
from campx.validation.rule_types import Validation


@dataclass(frozen=True)
class OverlapRule:
    """Defines an overlap rule between two entry types with optional day shifts."""

    type1: EntryType
    type2: EntryType
    shift1: int = 0
    shift2: int = 0


def get_dates(
    leader: Participant,
    camp: Camp,
    entry_type: EntryType,
    shift_days: int = 0,
) -> set[dt.date]:
    """Return the dates where a leader is responsible for an entry type."""
    days = leader.get_days_with_entry_type(entry_type, camp.schedule)
    return set(day.date + dt.timedelta(days=shift_days) for day in days)


def no_overlap(
    leader: Participant,
    camp: Camp,
    type1: EntryType,
    type2: EntryType,
    shift1: int = 0,
    shift2: int = 0,
) -> Iterable[ValidationError]:
    """Yield an error when the leader violates an overlap rule."""
    dates1 = get_dates(leader, camp, type1, shift1)
    dates2 = get_dates(leader, camp, type2, shift2)
    overlap = dates1 & dates2
    if overlap:
        yield OverlapValidationError(
            leader_name=leader.full_name,
            type1=type1,
            type2=type2,
            dates=tuple(sorted(overlap)),
        )


def max_num_of_responsibilities_per_day(
    leader: Participant, camp: Camp
) -> Iterable[ValidationError]:
    """Yield an error when a leader exceeds the per-day responsibility limit."""
    max_allowed_per_day = get_validation_config(camp.name)["leader_limits"][
        "max_responsibilities_per_day"
    ]
    for day in camp.schedule.days:
        responsibilities = leader.get_responsible_entries(camp.schedule, day)
        if len(responsibilities) > max_allowed_per_day:
            yield MaxResponsibilitiesPerDayValidationError(
                leader_name=leader.full_name,
                day_label=day.as_str(),
                actual=len(responsibilities),
                max_allowed=max_allowed_per_day,
            )


def max_num_of_responsibilities_per_entry_type(
    leader: Participant, camp: Camp
) -> Iterable[ValidationError]:
    """Yield errors when a leader exceeds entry-type allocation limits."""
    combination_limits = get_validation_config(camp.name)["leader_limits"][
        "max_responsibilities_per_entry_type"
    ]

    for entry_types, max_allowed in combination_limits:
        if isinstance(entry_types, EntryType):
            normalized_entry_types = (entry_types,)
            count = len(
                leader.get_responsible_entries(camp.schedule, entry_type=entry_types)
            )
        elif isinstance(entry_types, tuple):
            normalized_entry_types = entry_types
            count = sum(
                len(
                    leader.get_responsible_entries(camp.schedule, entry_type=entry_type)
                )
                for entry_type in entry_types
            )
        else:
            raise ValueError(f"Invalid entry_types in validation config: {entry_types}")
        if count > max_allowed:
            yield MaxResponsibilitiesPerEntryTypeValidationError(
                leader_name=leader.full_name,
                entry_types=normalized_entry_types,
                actual=count,
                max_allowed=max_allowed,
            )


def min_num_of_responsibilities_per_entry_type(
    leader: Participant, camp: Camp
) -> Iterable[ValidationError]:
    """Yield errors when a leader is missing required minimum allocations."""
    min_required = get_validation_config(camp.name)["leader_limits"][
        "min_responsibilities_per_entry_type"
    ]
    for entry_type, min_required_count in min_required.items():
        count = len(
            leader.get_responsible_entries(camp.schedule, entry_type=entry_type)
        )
        if count < min_required_count:
            yield MinResponsibilitiesPerEntryTypeValidationError(
                leader_name=leader.full_name,
                entry_type=entry_type,
                actual=count,
                min_required=min_required_count,
            )


def nothing_on_day_off(leader: Participant, camp: Camp) -> Iterable[ValidationError]:
    """Yield errors when a leader has non-day-off work on a day off."""
    days_off = leader.get_days_with_entry_type(EntryType.DAY_OFF, camp.schedule)
    for day in days_off:
        entries = [
            entry
            for entry in camp.schedule.all_entries(day=day)
            if leader in entry.responsible
        ]
        if len(entries) != 1:
            yield DayOffEntryCountValidationError(
                leader_name=leader.full_name,
                day_date=day.date,
                actual_count=len(entries),
            )
            continue
        if entries[0].entry_type != EntryType.DAY_OFF:
            yield DayOffWrongEntryTypeValidationError(
                leader_name=leader.full_name,
                day_date=day.date,
            )


def no_responsibilities_at_all(
    leader: Participant, camp: Camp
) -> Iterable[ValidationError]:
    """Yield an error when a leader has no responsibilities in the schedule."""
    responsible_entries = leader.get_responsible_entries(camp.schedule)
    if len(responsible_entries) == 0:
        yield NoResponsibilitiesValidationError(leader_name=leader.full_name)


def too_many_entries_while_day_host(
    leader: Participant, camp: Camp
) -> Iterable[ValidationError]:
    """Yield an error when a day host has too many assignments that day."""
    max_allowed = 2
    for day in camp.schedule.days:
        day_host_entries = day.get_entries(entry_type=EntryType.DAY_HOST)
        for entry in day_host_entries:
            if leader in entry.responsible:
                entries_on_day = leader.get_responsible_entries(camp.schedule, day=day)
                if len(entries_on_day) > max_allowed:
                    yield TooManyEntriesWhileDayHostValidationError(
                        leader_name=leader.full_name,
                        day_label=day.as_str(),
                        actual=len(entries_on_day),
                        max_allowed=max_allowed,
                    )


def min_days_between_entry_types(
    leader: Participant, camp: Camp
) -> Iterable[ValidationError]:
    """Yield errors when a leader has certain entry types scheduled too close together."""
    min_days_between = get_validation_config(camp.name)["leader_limits"][
        "min_days_between_entry_types"
    ]
    for entry_type1, entry_type2, min_days in min_days_between:
        dates1 = get_dates(leader, camp, entry_type1)
        dates2 = get_dates(leader, camp, entry_type2)
        for date1 in dates1:
            for date2 in dates2:
                if abs((date1 - date2).days) < min_days:
                    yield MinDaysBetweenEntryTypesValidationError(
                        leader_name=leader.full_name,
                        type1=entry_type1,
                        type2=entry_type2,
                        actual_min_days=abs((date1 - date2).days),
                        required_min_days=min_days,
                    )


def _get_overlap_rules(camp: Camp) -> tuple[OverlapRule, ...]:
    overlap_rule_specs = get_validation_config(camp.name)["leader_limits"][
        "overlap_rules"
    ]
    return tuple(OverlapRule(*rule_spec) for rule_spec in overlap_rule_specs)


def validate_overlap_rules(
    leader: Participant, camp: Camp
) -> Iterable[ValidationError]:
    """Evaluate all configured overlap rules for a leader."""
    for rule in _get_overlap_rules(camp):
        yield from no_overlap(
            leader,
            camp,
            rule.type1,
            rule.type2,
            shift1=rule.shift1,
            shift2=rule.shift2,
        )


VALIDATIONS = [
    Validation(func=nothing_on_day_off),
    Validation(func=validate_overlap_rules),
    Validation(func=max_num_of_responsibilities_per_entry_type),
    Validation(func=max_num_of_responsibilities_per_day),
    Validation(func=no_responsibilities_at_all),
    Validation(func=min_num_of_responsibilities_per_entry_type),
    Validation(func=too_many_entries_while_day_host),
    Validation(func=min_days_between_entry_types),
]
