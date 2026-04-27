import datetime as dt
from campx.model.factory import _assign_initials
from campx.model.participant import Participant
from campx.model.schedule_entry import ScheduleEntry
from campx.model.schedule import Schedule
from campx.model.day import Day
from campx.model.camp import Camp
from campx.model.camp_place import CampPlace
from campx.model.enums import ParticipantType, LeaderYearType, EntryType


class TestParticipant:
    """Test suite for the Participant model."""

    def test_participant_creation(self):
        """Test creating a participant with all fields."""
        p = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
            leader_year_type=LeaderYearType.FIRST_YEAR,
        )
        assert p.participant_id == 1
        assert p.first_name == "John"
        assert p.last_name == "Doe"
        assert p.gender == "M"
        assert p.birthday == dt.date(1990, 1, 15)
        assert p.participant_type == ParticipantType.LEADER

    def test_participant_full_name(self):
        """Test that full_name property returns concatenated first and last name."""
        p = Participant(
            participant_id=1,
            first_name="Jane",
            last_name="Smith",
            gender="F",
            birthday=dt.date(1995, 6, 20),
            participant_type=ParticipantType.CAMP_MANAGEMENT,
        )
        assert p.full_name == "Jane Smith"

    def test_participant_initials(self):
        """Test that initials property returns first letter of each name."""
        p = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )
        _assign_initials([p])
        assert p.initials == "JD"

    def test_participant_gender_variants(self):
        """Test that different gender values are accepted."""
        for gender in ["F", "M", "O"]:
            p = Participant(
                participant_id=1,
                first_name="Test",
                last_name="Person",
                gender=gender,
                birthday=dt.date(1990, 1, 1),
                participant_type=ParticipantType.LEADER,
            )
            assert p.gender == gender

    def test_participant_different_types(self):
        """Test creating participants with different participant types."""
        for p_type in ParticipantType:
            p = Participant(
                participant_id=1,
                first_name="Test",
                last_name="Person",
                gender="M",
                birthday=dt.date(1990, 1, 1),
                participant_type=p_type,
            )
            assert p.participant_type == p_type


class TestScheduleEntry:
    """Test suite for the ScheduleEntry model."""

    def test_schedule_entry_creation(self):
        """Test creating a schedule entry."""
        entry = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer",
            start_time="08:00",
            end_time="08:30",
        )
        assert entry.entry_type == EntryType.MORNING_PRAYER
        assert entry.name == "Morning Prayer"
        assert entry.start_time == "08:00"
        assert entry.end_time == "08:30"
        assert entry.responsible == []

    def test_schedule_entry_with_responsible(self):
        """Test schedule entry with responsible participants."""
        p1 = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )
        entry = ScheduleEntry(
            entry_type=EntryType.LUNCH,
            name="Lunch",
            start_time="12:00",
            end_time="13:00",
            responsible=[p1],
        )
        assert len(entry.responsible) == 1
        assert entry.responsible[0] == p1

    def test_remove_participant_from_entry(self):
        """Test removing a participant from schedule entry."""
        p1 = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )
        p2 = Participant(
            participant_id=2,
            first_name="Jane",
            last_name="Smith",
            gender="F",
            birthday=dt.date(1995, 6, 20),
            participant_type=ParticipantType.LEADER,
        )
        entry = ScheduleEntry(
            entry_type=EntryType.LUNCH,
            name="Lunch",
            start_time="12:00",
            end_time="13:00",
            responsible=[p1, p2],
        )
        assert len(entry.responsible) == 2

        entry.remove_participant(p1)
        assert len(entry.responsible) == 1
        assert entry.responsible[0] == p2


class TestDay:
    """Test suite for the Day model."""

    def test_day_creation(self):
        """Test creating a day."""
        date = dt.date(2026, 3, 15)
        day = Day(date=date)
        assert day.date == date
        assert day.schedule_entries == []

    def test_day_as_str(self):
        """Test day string representation."""
        date = dt.date(2026, 3, 15)
        day = Day(date=date)
        assert day.as_str() == "2026-03-15"

    def test_day_as_str_custom_format(self):
        """Test day string representation with custom format."""
        date = dt.date(2026, 3, 15)
        day = Day(date=date)
        assert day.as_str("%d/%m/%Y") == "15/03/2026"

    def test_day_as_str_with_swedish_abbreviated_month(self):
        """Test day string representation with Swedish abbreviated month."""
        date = dt.date(2026, 4, 15)
        day = Day(date=date)
        assert day.as_str("%d %b", swedish_month_names=True) == "15 apr."

    def test_day_as_str_with_swedish_full_month(self):
        """Test day string representation with Swedish full month."""
        date = dt.date(2026, 4, 15)
        day = Day(date=date)
        assert day.as_str("%d %B", swedish_month_names=True) == "15 april"

    def test_day_get_entries_by_type(self):
        """Test retrieving entries by type from a day."""
        date = dt.date(2026, 3, 15)
        day = Day(date=date)

        entry1 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer",
            start_time="08:00",
            end_time="08:30",
        )
        entry2 = ScheduleEntry(
            entry_type=EntryType.LUNCH,
            name="Lunch",
            start_time="12:00",
            end_time="13:00",
        )
        entry3 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer 2",
            start_time="08:00",
            end_time="08:30",
        )

        day.schedule_entries = [entry1, entry2, entry3]

        prayer_entries = day.get_entries(EntryType.MORNING_PRAYER)
        assert len(prayer_entries) == 2
        assert all(e.entry_type == EntryType.MORNING_PRAYER for e in prayer_entries)

        lunch_entries = day.get_entries(EntryType.LUNCH)
        assert len(lunch_entries) == 1
        assert lunch_entries[0] == entry2


class TestSchedule:
    """Test suite for the Schedule model."""

    def test_schedule_creation(self):
        """Test creating a schedule."""
        day1 = Day(date=dt.date(2026, 3, 15))
        day2 = Day(date=dt.date(2026, 3, 16))
        schedule = Schedule(days=[day1, day2])

        assert len(schedule.days) == 2
        assert schedule.days[0] == day1
        assert schedule.days[1] == day2

    def test_all_entries_no_filters(self):
        """Test retrieving all entries from schedule without filters."""
        day1 = Day(date=dt.date(2026, 3, 15))
        day2 = Day(date=dt.date(2026, 3, 16))

        entry1 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer",
            start_time="08:00",
            end_time="08:30",
        )
        entry2 = ScheduleEntry(
            entry_type=EntryType.LUNCH,
            name="Lunch",
            start_time="12:00",
            end_time="13:00",
        )
        entry3 = ScheduleEntry(
            entry_type=EntryType.DINNER,
            name="Dinner",
            start_time="18:00",
            end_time="19:00",
        )

        day1.schedule_entries = [entry1, entry2]
        day2.schedule_entries = [entry3]

        schedule = Schedule(days=[day1, day2])
        all_entries = schedule.all_entries()

        assert len(all_entries) == 3

    def test_all_entries_filtered_by_day(self):
        """Test retrieving entries filtered by day."""
        day1 = Day(date=dt.date(2026, 3, 15))
        day2 = Day(date=dt.date(2026, 3, 16))

        entry1 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer",
            start_time="08:00",
            end_time="08:30",
        )
        entry2 = ScheduleEntry(
            entry_type=EntryType.LUNCH,
            name="Lunch",
            start_time="12:00",
            end_time="13:00",
        )
        entry3 = ScheduleEntry(
            entry_type=EntryType.DINNER,
            name="Dinner",
            start_time="18:00",
            end_time="19:00",
        )

        day1.schedule_entries = [entry1, entry2]
        day2.schedule_entries = [entry3]

        schedule = Schedule(days=[day1, day2])
        day1_entries = schedule.all_entries(day=day1)

        assert len(day1_entries) == 2

    def test_all_entries_filtered_by_type(self):
        """Test retrieving entries filtered by entry type."""
        day1 = Day(date=dt.date(2026, 3, 15))

        entry1 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer",
            start_time="08:00",
            end_time="08:30",
        )
        entry2 = ScheduleEntry(
            entry_type=EntryType.LUNCH,
            name="Lunch",
            start_time="12:00",
            end_time="13:00",
        )
        entry3 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer 2",
            start_time="08:00",
            end_time="08:30",
        )

        day1.schedule_entries = [entry1, entry2, entry3]

        schedule = Schedule(days=[day1])
        prayer_entries = schedule.all_entries(entry_type=EntryType.MORNING_PRAYER)

        assert len(prayer_entries) == 2


class TestCampPlace:
    """Test suite for the CampPlace model."""

    def test_camp_place_creation(self):
        """Test creating a camp place."""
        place = CampPlace("Karlberg")
        assert place.name == "Karlberg"


class TestCamp:
    """Test suite for the Camp model."""

    def test_camp_creation(self):
        """Test creating a camp."""
        place = CampPlace("Karlberg")
        participant = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )
        day = Day(date=dt.date(2026, 3, 15))
        schedule = Schedule(days=[day])

        camp = Camp(
            name="Camp 2026",
            camp_place=place,
            participants=[participant],
            schedule=schedule,
        )

        assert camp.name == "Camp 2026"
        assert camp.camp_place == place
        assert len(camp.participants) == 1
        assert camp.schedule == schedule
