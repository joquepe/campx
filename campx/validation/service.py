import logging

from campx.model.camp import Camp
from campx.model.day import Day
from campx.model.participant import Participant
from campx.model.schedule_entry import ScheduleEntry

from campx.validation.entry_rules import ENTRY_VALIDATIONS
from campx.validation.errors import ValidationError
from campx.validation.leader_rules import VALIDATIONS

logger = logging.getLogger(__name__)


def run_entry_validations_on_day(
    schedule_entry: ScheduleEntry, day: Day, camp: Camp
) -> list[ValidationError]:
    """Run all entry validations for a single schedule entry on a given day."""
    validation_errors = []
    for validation in ENTRY_VALIDATIONS:
        validation_errors.extend(validation.validate(schedule_entry, day, camp))
    return validation_errors


def run_entry_validations(camp: Camp) -> list[ValidationError]:
    """Run all entry-level validations for a camp."""
    validation_errors = []
    for day in camp.schedule.days:
        for entry in day.schedule_entries:
            validation_errors.extend(run_entry_validations_on_day(entry, day, camp))
    return validation_errors


def run_leader_validations_for_leader(
    leader: Participant, camp: Camp
) -> list[ValidationError]:
    """Run all leader validations for one leader."""
    validation_errors = []
    for validation in VALIDATIONS:
        validation_errors.extend(validation.validate(leader, camp))
    return validation_errors


def run_leader_validations(camp: Camp) -> list[ValidationError]:
    """Run all leader-level validations for a camp."""
    validation_errors = []
    for leader in camp.leaders_incl_management:
        validation_errors.extend(run_leader_validations_for_leader(leader, camp))
    return validation_errors


def get_errors(camp: Camp) -> list[ValidationError]:
    """Collect all validation errors for a camp."""
    return run_leader_validations(camp) + run_entry_validations(camp)


def run_validations(camp: Camp) -> None:
    """Raise an assertion if any validation errors are present for the camp."""
    logger.info("Validating camp schedule...")
    validation_errors = get_errors(camp)
    if validation_errors:
        raise AssertionError(
            "Validation failed with the following errors:\n"
            + "\n".join(f"- [{error.severity}] {error}" for error in validation_errors)
        )
    logger.info("Validation successful!")
