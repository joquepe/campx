from campx.repository import Repository
from campx.model.participant import Participant
from campx.model.camp_place import CampPlace
from campx.model.camp import Camp
from campx.model.enums import (
    ParticipantType,
    EntryType,
    LeaderYearType,
)
from campx.model.schedule import Schedule
from campx.model.schedule_entry import ScheduleEntry
from campx.model.day import Day
import datetime as dt
from collections.abc import Iterator
from pathlib import Path
import json
import pandas as pd
from campx.camp_config import get_camp_config
from campx.schedule_config import get_schedule_config

ParticipantRecord = dict[str, object]
ScheduleRow = dict[str, object]
ScheduleConfigEntry = tuple[EntryType, str | None, str | None]


def _assign_nicknames(participants: list[Participant]) -> None:
    """Assign unique nicknames to participants that do not already have one."""
    nicknames = set()
    for participant in participants:
        if participant.nick_name is not None:
            nicknames.add(participant.nick_name)
            continue
        first_names = [
            p.first_name
            for p in participants
            if p.participant_id != participant.participant_id
        ]
        test_nickname = participant.first_name
        if test_nickname not in first_names and test_nickname not in nicknames:
            participant.nick_name = test_nickname
            nicknames.add(test_nickname)
            continue
        first_names_add_surname = [
            f"{p.first_name} {p.last_name_initials}"
            for p in participants
            if p.participant_id != participant.participant_id
        ]
        test_nickname = f"{participant.first_name} {participant.last_name_initials}"
        if (
            test_nickname not in first_names_add_surname
            and test_nickname not in nicknames
        ):
            participant.nick_name = test_nickname
            nicknames.add(test_nickname)
            continue
        raise ValueError(
            f"Could not assign unique nickname for participant {participant.full_name}"
        )
    assert len(nicknames) == len(participants), (
        "Each participant should have a unique nickname"
    )
    assert all(p.nick_name for p in participants), (
        "All participants should have a nickname"
    )


def _assign_initials(participants: list[Participant]) -> None:
    """Assign initials to participants.

    If two participants have the same initials, add the second letter in first name to make them unique.
    If a participant has several words in their last name, use the first letter of each word."""
    initials_set = set()
    for participant in participants:
        last_name_initials = "".join(word[0] for word in participant.last_name.split())
        test_initials = f"{participant.first_name[0]}{last_name_initials}"
        if test_initials not in initials_set:
            participant.first_name_initials = participant.first_name[0]
            participant.last_name_initials = last_name_initials
            initials_set.add(test_initials)
            continue
        test_initials = f"{participant.first_name[:2]}{last_name_initials}"
        if test_initials not in initials_set:
            participant.first_name_initials = participant.first_name[:2]
            participant.last_name_initials = last_name_initials
            initials_set.add(test_initials)
            continue
        raise ValueError(
            f"Could not assign unique initials for participant {participant.full_name}"
        )
    assert len(initials_set) == len(participants), (
        "Each participant should have unique initials"
    )
    assert all(p.first_name_initials and p.last_name_initials for p in participants), (
        "All participants should have initials"
    )


class Factory:
    """Builds camps, participants, and schedules from input files."""

    def __init__(self, input_base_dir: Path | None = None):
        """Initialise the factory with an optional base input directory."""
        self.input_base_dir = (
            input_base_dir
            if input_base_dir is not None
            else Path(__file__).resolve().parents[1] / "input"
        )

    def populate_camp(self, camp_name: str, repo: Repository) -> None:
        """Build a full camp object and store it in the repository."""
        camp_config = get_camp_config(camp_name)
        camp_place = CampPlace(camp_config["camp_place_name"])
        participants = self.populate_participants(repo, camp_name)
        schedule = self.populate_schedule(camp_config, repo, camp_name)
        camp = Camp(camp_name, camp_place, participants, schedule)
        repo.add_camp(camp)

    def get_camp_input_dir(self, camp_name: str) -> Path:
        """Return the input directory for a camp and ensure it exists."""
        camp_input_dir = self.input_base_dir / camp_name
        if not camp_input_dir.exists():
            raise FileNotFoundError(f"Camp input directory not found: {camp_input_dir}")
        return camp_input_dir

    def populate_participants(
        self, repo: Repository, camp_name: str
    ) -> list[Participant]:
        """Create participants for a camp from the participants CSV."""
        participant_records = self.get_participants(camp_name)
        participants = []
        for record in participant_records:
            participant = self.create_participant(record, repo)
            participants.append(participant)
        _assign_initials(participants)
        _assign_nicknames(participants)
        return participants

    def create_participant(
        self, record: ParticipantRecord, repo: Repository
    ) -> Participant:
        """Create or retrieve a participant from a raw CSV record."""
        p_id = record["participant_id"]
        if repo.has_participant(p_id):
            return repo.get_participant(p_id)
        first_name = record["first_name"]
        last_name = record["last_name"]
        gender = record["gender"]
        birth_date = dt.datetime.strptime(record["birth_date"], "%Y-%m-%d").date()
        participant_type = ParticipantType[record["participant_type"]]
        if isinstance(record["leader_year_type"], str):
            leader_year_type = LeaderYearType[record["leader_year_type"]]
        else:
            leader_year_type = None
        if isinstance(record["nick_name"], str):
            nick_name = record["nick_name"]
        else:
            nick_name = None

        participant = Participant(
            p_id,
            first_name,
            last_name,
            gender,
            birth_date,
            participant_type,
            leader_year_type=leader_year_type,
            nick_name=nick_name,
        )
        repo.add_participant(participant)
        return participant

    def get_participants(self, camp_name: str) -> list[ParticipantRecord]:
        """Load raw participant records for a camp."""
        file_name = self.get_camp_input_dir(camp_name) / "participants.csv"
        data = pd.read_csv(file_name, sep=";").to_dict("records")
        return data

    def create_schedule_template_files(
        self, camp_name: str, output_base_dir: Path | None = None
    ) -> None:
        """Write blank schedule CSV templates for all entry types in a camp."""
        camp_config = get_camp_config(camp_name)
        output_dir = (
            output_base_dir if output_base_dir is not None else self.input_base_dir
        ) / camp_name
        output_dir.mkdir(parents=True, exist_ok=True)

        schedule_config = get_schedule_config(camp_config["schedule_config_id"])
        for entry_type in EntryType:
            rows = []
            for day in generate_dates(
                camp_config["start_date"], camp_config["end_date"]
            ):
                start_time, end_time = self._get_default_times(
                    schedule_config, entry_type
                )
                rows.append(
                    {
                        "name": "",
                        "entry_type": entry_type.name,
                        "day": day.strftime("%Y-%m-%d"),
                        "responsible": "",
                        "additional_info": "",
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                )

            df = pd.DataFrame(
                rows,
                columns=[
                    "name",
                    "entry_type",
                    "day",
                    "responsible",
                    "additional_info",
                    "start_time",
                    "end_time",
                ],
            )
            file_name = output_dir / f"{entry_type.name.lower()}.csv"
            df.to_csv(file_name, sep=";", index=False)

    def _get_default_times(
        self, schedule_config: list[ScheduleConfigEntry], entry_type: EntryType
    ) -> tuple[str | None, str | None]:
        """Return default start and end times for an entry type."""
        for entry in schedule_config:
            if entry[0] == entry_type:
                return entry[1], entry[2]
        return None, None

    def populate_schedule(
        self, camp_config: dict[str, object], repo: Repository, camp_name: str
    ) -> Schedule:
        """Create a schedule for a camp from CSV input files."""
        schedule_config = get_schedule_config(camp_config["schedule_config_id"])
        camp_input_dir = self.get_camp_input_dir(camp_name)
        schedule_entries = []
        for csv_file in camp_input_dir.glob("*.csv"):
            if csv_file.name != "participants.csv":
                df = pd.read_csv(csv_file, sep=";")
                schedule_entries.extend(df.to_dict("records"))
        days = self.populate_days(
            camp_config["start_date"],
            camp_config["end_date"],
            schedule_config,
            schedule_entries,
            repo,
        )
        schedule = Schedule(days)
        return schedule

    def populate_days(
        self,
        start_date: dt.date,
        end_date: dt.date,
        schedule_config: list[ScheduleConfigEntry],
        schedule_entries: list[ScheduleRow],
        repo: Repository,
    ) -> list[Day]:
        """Build day objects between two dates using schedule data when present."""
        days = []
        for d in generate_dates(start_date, end_date):
            entries = []
            day_entries = [
                e for e in schedule_entries if d.strftime("%Y-%m-%d") == e["day"]
            ]
            if day_entries:
                for day_entry in day_entries:
                    schedule_entry = self._populate_from_day_entry(
                        day_entry, repo, schedule_config
                    )
                    entries.append(schedule_entry)
            else:
                for entry_data in schedule_config:
                    entry_type, start_time, end_time = entry_data
                    schedule_entry = ScheduleEntry(
                        entry_type, "", start_time, end_time, [], ""
                    )
                    entries.append(schedule_entry)
            day = Day(d, entries)
            days.append(day)

        return days

    def _populate_from_day_entry(
        self,
        day_entry: ScheduleRow,
        repo: Repository,
        schedule_config: list[ScheduleConfigEntry],
    ) -> ScheduleEntry:
        """Convert a raw schedule row into a typed schedule entry."""
        entry_type = EntryType[day_entry["entry_type"]]
        name = day_entry["name"] if pd.notna(day_entry["name"]) else ""
        responsible = day_entry["responsible"]
        participants_responsible = []
        if isinstance(responsible, str):
            responsible = responsible.split(",")
            for r in responsible:
                p = repo.get_participant_by_full_name(r)
                participants_responsible.append(p)

        start_time = (
            None if pd.isna(day_entry["start_time"]) else day_entry["start_time"]
        )
        end_time = None if pd.isna(day_entry["end_time"]) else day_entry["end_time"]
        additional_info = day_entry.get("additional_info", "")
        if isinstance(additional_info, float) and pd.isna(additional_info):
            additional_info = ""
        elif additional_info is None:
            additional_info = ""
        elif not isinstance(additional_info, str):
            additional_info = str(additional_info)
        else:
            # Convert literal \n to actual newlines
            additional_info = additional_info.replace("\\n", "\n")

        if not entry_type.value.time_independent:
            if not start_time:
                start_time = find_attr_in_schedule_config(
                    schedule_config, name, entry_type, 1
                )

            if not end_time:
                end_time = find_attr_in_schedule_config(
                    schedule_config, name, entry_type, 2
                )

        schedule_entry = ScheduleEntry(
            entry_type,
            name,
            start_time,
            end_time,
            participants_responsible,
            additional_info,
        )
        return schedule_entry


def find_attr_in_schedule_config(
    schedule_config: list[ScheduleConfigEntry],
    name: str,
    entry_type: EntryType,
    idx: int,
) -> str | None:
    """Look up a configured attribute for an entry type by tuple index."""
    for entry in schedule_config:
        if entry[0] == entry_type:
            return entry[idx]
    raise ValueError(f"Could not find {entry_type}: {name} in schedule config")


def generate_dates(start_date: dt.date, end_date: dt.date) -> Iterator[dt.date]:
    """Yield every date in the inclusive date range."""
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += dt.timedelta(days=1)


def read_json(path: Path) -> list[dict[str, object]]:
    """Read a JSON file containing a list of records."""
    records = []
    with open(path, "r") as f:
        records = json.load(f)
    return records
