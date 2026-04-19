from campx.model.camp import Camp
from campx.model.day import Day
from campx.model.participant import Participant
from campx.model.schedule_entry import ScheduleEntry

from campx.validation.service import (
    run_entry_validations_on_day,
    run_leader_validations_for_leader,
)


def is_eligible_participant(
    leader: Participant,
    schedule_entry: ScheduleEntry,
    camp: Camp,
    day: Day,
):
    if leader in schedule_entry.responsible:
        return False, None

    current_leader_errors = set(run_leader_validations_for_leader(leader, camp))
    current_entry_errors = set(run_entry_validations_on_day(schedule_entry, day, camp))

    schedule_entry.responsible.append(leader)
    new_leader_errors = set(run_leader_validations_for_leader(leader, camp))
    new_entry_errors = set(run_entry_validations_on_day(schedule_entry, day, camp))
    schedule_entry.remove_participant(leader)

    added_errors = (new_leader_errors | new_entry_errors) - (
        current_leader_errors | current_entry_errors
    )
    if added_errors:
        return False, " & ".join(
            f"- {error}" for error in sorted(added_errors, key=str)
        )
    return True, None


def get_eligible_participants(
    leaders: list[Participant], schedule_entry: ScheduleEntry, camp: Camp, day: Day
):
    eligible_leaders = []
    for leader in leaders:
        is_eligible, _ = is_eligible_participant(leader, schedule_entry, camp, day)
        if is_eligible:
            eligible_leaders.append(leader)
    return eligible_leaders
