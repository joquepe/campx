import datetime as dt
import pytest

from campx.camp_config import CAMP_CONFIGS
from campx.model.camp import Camp
from campx.model.camp_place import CampPlace
from campx.model.day import Day
from campx.model.enums import EntryType, ParticipantType, LeaderYearType
from campx.model.participant import Participant
from campx.model.schedule import Schedule
from campx.model.schedule_entry import ScheduleEntry
from campx.validation import (
    DuplicateResponsibleValidationError,
    MinResponsibilitiesPerEntryTypeValidationError,
    OverlapValidationError,
    TooManyResponsibleValidationError,
    ValidationSeverity,
    get_errors,
    is_eligible_participant,
    run_entry_validations,
    run_leader_validations,
    run_validations,
)


def _create_leader(participant_id: int, first_name: str = "Alice") -> Participant:
    return Participant(
        participant_id=participant_id,
        first_name=first_name,
        last_name="Andersson",
        gender="F",
        birthday=dt.date(1995, 1, 1),
        participant_type=ParticipantType.LEADER,
        leader_year_type=LeaderYearType.FIRST_YEAR,
    )


def _create_camp(
    name: str, participants: list[Participant], schedule_entries: list[ScheduleEntry]
) -> Camp:
    day = Day(date=dt.date(2026, 4, 12), schedule_entries=schedule_entries)
    return Camp(
        name=name,
        camp_place=CampPlace("TestPlace"),
        participants=participants,
        schedule=Schedule(days=[day]),
    )


def test_get_errors_collects_multiple_leader_errors():
    leader = _create_leader(1)
    day = Day(
        date=dt.date(2026, 4, 12),
        schedule_entries=[
            ScheduleEntry(
                entry_type=EntryType.WAKE_UP,
                name="",
                start_time="08:00",
                end_time="08:15",
                responsible=[leader],
            ),
            ScheduleEntry(
                entry_type=EntryType.MORNING_PRAYER,
                name="",
                start_time="08:30",
                end_time="09:00",
                responsible=[leader],
            ),
        ],
    )
    camp = Camp(
        name="TestCamp",
        camp_place=CampPlace("TestPlace"),
        participants=[leader],
        schedule=Schedule(days=[day]),
    )

    errors = get_errors(camp)
    assert any(isinstance(error, OverlapValidationError) for error in errors)
    assert any(
        isinstance(error, MinResponsibilitiesPerEntryTypeValidationError)
        and error.entry_type == EntryType.SLEEP_IN
        for error in errors
    )
    messages = {str(error) for error in errors}

    assert any(
        "overlapping entries of type WAKE_UP and MORNING_PRAYER" in message
        for message in messages
    )
    assert any("Not enough entries of type SLEEP_IN" in message for message in messages)
    assert any("Not enough entries of type DAY_OFF" in message for message in messages)
    assert any(
        isinstance(error, OverlapValidationError)
        and error.severity == ValidationSeverity.MAJOR
        for error in errors
    )
    assert any(
        isinstance(error, MinResponsibilitiesPerEntryTypeValidationError)
        and error.severity == ValidationSeverity.MINOR
        for error in errors
    )


def test_get_errors_collects_multiple_entry_errors():
    leader = _create_leader(1)
    entry = ScheduleEntry(
        entry_type=EntryType.MORNING_PRAYER,
        name="",
        start_time="08:00",
        end_time="08:30",
        responsible=[leader, leader],
    )
    day = Day(date=dt.date(2026, 4, 12), schedule_entries=[entry])
    camp = Camp(
        name="TestCamp",
        camp_place=CampPlace("TestPlace"),
        participants=[leader],
        schedule=Schedule(days=[day]),
    )

    errors = get_errors(camp)
    assert any(
        isinstance(error, DuplicateResponsibleValidationError) for error in errors
    )
    messages = {str(error) for error in errors}

    assert any("Duplicate responsible leaders" in message for message in messages)
    assert any("only first-year leaders responsible" in message for message in messages)


def test_run_validations_includes_severity_in_failure_message():
    leader = _create_leader(1)
    entry = ScheduleEntry(
        entry_type=EntryType.MORNING_PRAYER,
        name="",
        start_time="08:00",
        end_time="08:30",
        responsible=[leader, leader],
    )
    camp = _create_camp("TestCamp", [leader], [entry])

    with pytest.raises(AssertionError) as exc_info:
        run_validations(camp)

    message = str(exc_info.value)
    assert "[MAJOR]" in message
    assert "[MINOR]" in message


def test_leader_validation_uses_camp_specific_minimums():
    leader = _create_leader(1)
    camp = _create_camp(
        "Karlberg 4 2026",
        [leader],
        [
            ScheduleEntry(
                entry_type=EntryType.SLEEP_IN,
                name="",
                start_time=None,
                end_time=None,
                responsible=[leader],
            ),
            ScheduleEntry(
                entry_type=EntryType.DAY_OFF,
                name="",
                start_time=None,
                end_time=None,
                responsible=[leader],
            ),
        ],
    )

    messages = {str(error) for error in run_leader_validations(camp)}

    assert not any(
        "Not enough entries of type SLEEP_IN" in message for message in messages
    )


def test_entry_validation_uses_camp_specific_maximums():
    leaders = [
        _create_leader(index, first_name=f"Leader{index}") for index in range(1, 9)
    ]
    day_off_entry = ScheduleEntry(
        entry_type=EntryType.DAY_OFF,
        name="",
        start_time=None,
        end_time=None,
        responsible=leaders.copy(),
    )

    default_camp = _create_camp("TestCamp", leaders, [day_off_entry])
    default_errors = run_entry_validations(default_camp)
    assert any(
        isinstance(error, TooManyResponsibleValidationError)
        and error.entry_type == EntryType.DAY_OFF
        and error.max_allowed == 5
        for error in default_errors
    )
    default_messages = {str(error) for error in default_errors}
    assert any(
        "Too many responsible leaders for entry DAY_OFF" in message
        for message in default_messages
    )

    overridden_camp = _create_camp("Karlberg 4 2026", leaders, [day_off_entry])
    overridden_messages = {
        str(error) for error in run_entry_validations(overridden_camp)
    }
    assert not any(
        "Too many responsible leaders for entry DAY_OFF" in message
        for message in overridden_messages
    )


def test_is_eligible_participant_uses_typed_error_diffing():
    leader = _create_leader(1)
    wake_up_entry = ScheduleEntry(
        entry_type=EntryType.WAKE_UP,
        name="",
        start_time="08:00",
        end_time="08:15",
        responsible=[leader],
    )
    morning_prayer_entry = ScheduleEntry(
        entry_type=EntryType.MORNING_PRAYER,
        name="",
        start_time="08:30",
        end_time="09:00",
        responsible=[],
    )
    day = Day(
        date=dt.date(2026, 4, 12),
        schedule_entries=[wake_up_entry, morning_prayer_entry],
    )
    camp = Camp(
        name="TestCamp",
        camp_place=CampPlace("TestPlace"),
        participants=[leader],
        schedule=Schedule(days=[day]),
    )

    is_eligible, reason = is_eligible_participant(
        leader, morning_prayer_entry, camp, day
    )

    assert not is_eligible
    assert reason is not None
    assert "overlapping entries of type WAKE_UP and MORNING_PRAYER" in reason


def test_leader_validation_uses_camp_specific_overlap_rules():
    test_camp_name = "Test Camp Overlap Override"
    original_config = CAMP_CONFIGS.get(test_camp_name)
    CAMP_CONFIGS[test_camp_name] = {
        "camp_place_name": "TestPlace",
        "start_date": dt.date(2026, 4, 12),
        "end_date": dt.date(2026, 4, 12),
        "schedule_config_id": 1,
        "validation_overrides": {
            "leader_limits": {
                "overlap_rules": (),
                "min_responsibilities_per_entry_type": {},
            },
        },
    }

    try:
        leader = _create_leader(1)
        camp = _create_camp(
            test_camp_name,
            [leader],
            [
                ScheduleEntry(
                    entry_type=EntryType.WAKE_UP,
                    name="",
                    start_time="08:00",
                    end_time="08:15",
                    responsible=[leader],
                ),
                ScheduleEntry(
                    entry_type=EntryType.MORNING_PRAYER,
                    name="",
                    start_time="08:30",
                    end_time="09:00",
                    responsible=[leader],
                ),
            ],
        )

        errors = run_leader_validations(camp)

        assert not any(isinstance(error, OverlapValidationError) for error in errors)
    finally:
        if original_config is None:
            del CAMP_CONFIGS[test_camp_name]
        else:
            CAMP_CONFIGS[test_camp_name] = original_config
