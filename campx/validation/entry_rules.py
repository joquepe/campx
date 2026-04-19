from campx.camp_config import get_validation_config
from campx.model.camp import Camp
from campx.model.day import Day
from campx.model.enums import LeaderYearType
from campx.model.schedule_entry import ScheduleEntry

from campx.validation.errors import (
    DuplicateResponsibleValidationError,
    NoResponsibleValidationError,
    OnlyFirstYearResponsibleValidationError,
    TooManyResponsibleValidationError,
    ValidationError,
)
from campx.validation.rule_types import EntryValidation


def too_many_responsible(
    schedule_entry: ScheduleEntry, day: Day, camp: Camp
) -> list[ValidationError]:
    """Validate that an entry does not exceed its responsible limit."""
    max_responsible_per_entry_type = get_validation_config(camp.name)["entry_limits"][
        "max_responsible_per_entry_type"
    ]
    max_responsible = max_responsible_per_entry_type.get(schedule_entry.entry_type, 2)
    errors: list[ValidationError] = []
    if len(schedule_entry.responsible) > max_responsible:
        errors.append(
            TooManyResponsibleValidationError(
                entry_type=schedule_entry.entry_type,
                day_label=day.as_str(),
                actual=len(schedule_entry.responsible),
                max_allowed=max_responsible,
            )
        )
    return errors


def duplicate_responsible(
    schedule_entry: ScheduleEntry, day: Day, camp: Camp
) -> list[ValidationError]:
    """Validate that the same participant is not assigned twice to one entry."""
    unique_responsible = set(
        responsible.participant_id for responsible in schedule_entry.responsible
    )
    errors: list[ValidationError] = []
    if len(schedule_entry.responsible) != len(unique_responsible):
        errors.append(
            DuplicateResponsibleValidationError(
                entry_type=schedule_entry.entry_type,
                day_label=day.as_str(),
            )
        )
    return errors


def only_first_year_leaders_responsible(
    schedule_entry: ScheduleEntry, day: Day, camp: Camp
) -> list[ValidationError]:
    """Validate that an entry is not staffed only by first-year leaders."""
    leader_year_types = [
        leader.leader_year_type for leader in schedule_entry.responsible
    ]
    errors: list[ValidationError] = []
    if leader_year_types and all(
        leader_year_type == LeaderYearType.FIRST_YEAR
        for leader_year_type in leader_year_types
    ):
        errors.append(
            OnlyFirstYearResponsibleValidationError(
                entry_type=schedule_entry.entry_type,
                day_label=day.as_str(),
            )
        )
    return errors


def no_responsible_at_all(
    schedule_entry: ScheduleEntry, day: Day, camp: Camp
) -> list[ValidationError]:
    """Validate that required entries have at least one responsible person."""
    errors: list[ValidationError] = []
    if (
        schedule_entry.entry_type.value.requires_responsible
        and len(schedule_entry.responsible) == 0
    ):
        errors.append(
            NoResponsibleValidationError(
                entry_type=schedule_entry.entry_type,
                day_label=day.as_str(),
            )
        )
    return errors


ENTRY_VALIDATIONS = [
    EntryValidation(func=too_many_responsible),
    EntryValidation(func=duplicate_responsible),
    EntryValidation(func=only_first_year_leaders_responsible),
    EntryValidation(func=no_responsible_at_all),
]
