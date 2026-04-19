import pytest
import datetime as dt
from campx.model.participant import Participant
from campx.model.schedule import Schedule
from campx.model.schedule_entry import ScheduleEntry
from campx.model.day import Day
from campx.model.enums import ParticipantType, EntryType


class TestParticipantScheduleQueries:
    """Test suite for Participant schedule-related methods."""

    @pytest.fixture
    def sample_schedule(self):
        """Create a sample schedule for testing."""
        date1 = dt.date(2026, 3, 15)
        date2 = dt.date(2026, 3, 16)
        date3 = dt.date(2026, 3, 17)

        p1 = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )

        entry1 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer",
            start_time="08:00",
            end_time="08:30",
            responsible=[p1],
        )
        entry2 = ScheduleEntry(
            entry_type=EntryType.LUNCH,
            name="Lunch",
            start_time="12:00",
            end_time="13:00",
            responsible=[p1],
        )
        entry3 = ScheduleEntry(
            entry_type=EntryType.BREAKFAST,
            name="Breakfast",
            start_time="07:00",
            end_time="07:30",
            responsible=[p1],
        )
        entry4 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer",
            start_time="08:00",
            end_time="08:30",
        )

        day1 = Day(date=date1, schedule_entries=[entry1, entry2])
        day2 = Day(date=date2, schedule_entries=[entry3])
        day3 = Day(date=date3, schedule_entries=[entry4])

        schedule = Schedule(days=[day1, day2, day3])
        return schedule, p1, (date1, date2, date3)

    def test_get_responsible_entries_all(self, sample_schedule):
        """Test getting all entries a participant is responsible for."""
        schedule, p1, _ = sample_schedule

        entries = p1.get_responsible_entries(schedule)
        assert len(entries) == 3
        assert all(p1 in e.responsible for e in entries)

    def test_get_responsible_entries_by_day(self, sample_schedule):
        """Test getting responsible entries filtered by day."""
        schedule, p1, (date1, date2, date3) = sample_schedule
        day1 = schedule.days[0]
        day2 = schedule.days[1]

        day1_entries = p1.get_responsible_entries(schedule, day=day1)
        assert len(day1_entries) == 2

        day2_entries = p1.get_responsible_entries(schedule, day=day2)
        assert len(day2_entries) == 1

    def test_get_responsible_entries_by_type(self, sample_schedule):
        """Test getting responsible entries filtered by entry type."""
        schedule, p1, _ = sample_schedule

        prayer_entries = p1.get_responsible_entries(
            schedule, entry_type=EntryType.MORNING_PRAYER
        )
        assert len(prayer_entries) == 1
        assert prayer_entries[0].entry_type == EntryType.MORNING_PRAYER

        lunch_entries = p1.get_responsible_entries(schedule, entry_type=EntryType.LUNCH)
        assert len(lunch_entries) == 1
        assert lunch_entries[0].entry_type == EntryType.LUNCH

    def test_get_responsible_entries_by_day_and_type(self, sample_schedule):
        """Test getting responsible entries filtered by both day and type."""
        schedule, p1, _ = sample_schedule
        day1 = schedule.days[0]

        day1_prayers = p1.get_responsible_entries(
            schedule, day=day1, entry_type=EntryType.MORNING_PRAYER
        )
        assert len(day1_prayers) == 1
        assert day1_prayers[0].entry_type == EntryType.MORNING_PRAYER

    def test_get_days_with_entry_type(self, sample_schedule):
        """Test getting all days where participant has specific entry type."""
        schedule, p1, (date1, date2, date3) = sample_schedule

        prayer_days = p1.get_days_with_entry_type(EntryType.MORNING_PRAYER, schedule)
        assert len(prayer_days) == 1
        assert prayer_days[0].date == date1

        breakfast_days = p1.get_days_with_entry_type(EntryType.BREAKFAST, schedule)
        assert len(breakfast_days) == 1
        assert breakfast_days[0].date == date2

    def test_get_days_with_multiple_same_entry_types(self):
        """Test getting days when participant has multiple same entry types."""
        p1 = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )

        # Two morning prayers on same day, different times
        entry1 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer 1",
            start_time="08:00",
            end_time="08:30",
            responsible=[p1],
        )
        entry2 = ScheduleEntry(
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer 2",
            start_time="08:45",
            end_time="09:15",
            responsible=[p1],
        )

        day = Day(date=dt.date(2026, 3, 15), schedule_entries=[entry1, entry2])
        schedule = Schedule(days=[day])

        prayer_days = p1.get_days_with_entry_type(EntryType.MORNING_PRAYER, schedule)
        assert len(prayer_days) == 1  # Same day, counted once

    def test_get_responsible_entries_empty(self):
        """Test getting responsible entries when participant has none."""
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
            entry_type=EntryType.MORNING_PRAYER,
            name="Morning Prayer",
            start_time="08:00",
            end_time="08:30",
            responsible=[p2],
        )

        day = Day(date=dt.date(2026, 3, 15), schedule_entries=[entry])
        schedule = Schedule(days=[day])

        entries = p1.get_responsible_entries(schedule)
        assert len(entries) == 0

    def test_get_days_with_entry_type_not_present(self):
        """Test getting days for entry type participant doesn't have."""
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

        day = Day(date=dt.date(2026, 3, 15), schedule_entries=[entry])
        schedule = Schedule(days=[day])

        prayer_days = p1.get_days_with_entry_type(EntryType.MORNING_PRAYER, schedule)
        assert len(prayer_days) == 0


class TestParticipantProperties:
    """Test suite for Participant properties and attributes."""

    def test_participant_with_all_leader_year_types(self):
        """Test creating participants with all leader year type options."""
        from campx.model.enums import LeaderYearType

        for year_type in LeaderYearType:
            p = Participant(
                participant_id=1,
                first_name="Test",
                last_name="Person",
                gender="M",
                birthday=dt.date(1990, 1, 1),
                participant_type=ParticipantType.LEADER,
                leader_year_type=year_type,
            )
            assert p.leader_year_type == year_type

    def test_participant_roles_default(self):
        """Test that participant roles default to None."""
        p = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )
        assert p.roles is None

    def test_participant_roles_assignment(self):
        """Test assigning roles to a participant."""
        from campx.model.enums import Role

        p = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
            roles=[Role.PRIEST, Role.BOAT_LEADER],
        )
        assert len(p.roles) == 2
        assert Role.PRIEST in p.roles
        assert Role.BOAT_LEADER in p.roles
