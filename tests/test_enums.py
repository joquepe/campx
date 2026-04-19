from campx.model.enums import (
    EntryType,
    EntryTypeData,
    ParticipantType,
    Role,
    LeaderYearType,
)


class TestEntryTypeEnum:
    """Test suite for the EntryType enum."""

    def test_all_entry_types_defined(self):
        """Test that expected entry types are defined."""
        expected_types = [
            "MORNING_PRAYER",
            "EVENING_PRAYER",
            "EDUCATION",
            "FEEDBACK",
            "LEADER_MEETING",
            "OTHER",
            "CLEANING",
            "DAY_HOST",
            "DAY_OFF",
            "THEME",
            "WAKE_UP",
            "PUT_TO_BED",
            "SLEEP_IN",
            "NIGHT_DUTY",
            "EVENING_ACTIVITY",
            "AFTERNOON_ACTIVITY",
            "BREAKFAST",
            "LUNCH",
            "DINNER",
            "EVENING_MEAL",
            "BOAT",
        ]

        for entry_type_name in expected_types:
            assert hasattr(EntryType, entry_type_name)

    def test_entry_type_data_structure(self):
        """Test that entry type data has expected structure."""
        for entry_type in EntryType:
            data = entry_type.value
            assert isinstance(data, EntryTypeData)
            assert isinstance(data.short, str)
            assert isinstance(data.long, str)
            assert isinstance(data.emoji, str)
            assert isinstance(data.time_independent, bool)
            assert isinstance(data.order, int)
            assert isinstance(data.bottom, bool)

    def test_time_independent_members(self):
        """Test getting time-independent entry types."""
        time_independent = EntryType.time_independent_members()

        # Should include types marked as time_independent=True
        assert any(t == EntryType.OTHER for t in time_independent)
        assert any(t == EntryType.DAY_HOST for t in time_independent)
        assert any(t == EntryType.DAY_OFF for t in time_independent)

        # Should not include time-dependent types
        assert not any(t == EntryType.MORNING_PRAYER for t in time_independent)
        assert not any(t == EntryType.LUNCH for t in time_independent)

    def test_time_independent_top(self):
        """Test getting time-independent entry types that appear at top."""
        time_independent_top = EntryType.time_independent_top()

        # Should be sorted by order
        assert len(time_independent_top) > 0
        orders = [t.value.order for t in time_independent_top]
        assert orders == sorted(orders)

        # Should not include bottom entries
        assert not any(t.value.bottom for t in time_independent_top)

    def test_time_independent_bottom(self):
        """Test getting time-independent entry types that appear at bottom."""
        time_independent_bottom = EntryType.time_independent_bottom()

        # Should be sorted by order
        assert len(time_independent_bottom) > 0
        orders = [t.value.order for t in time_independent_bottom]
        assert orders == sorted(orders)

        # Should only include bottom entries
        assert all(t.value.bottom for t in time_independent_bottom)

    def test_time_independent_ordering(self):
        """Test that time-independent entries are properly ordered."""
        time_independent = EntryType.time_independent_members()
        orders = [t.value.order for t in time_independent]

        # Orders should be unique for time-independent entries
        assert len(orders) == len(set(orders))

    def test_entry_type_emoji(self):
        """Test that each entry type has an emoji."""
        for entry_type in EntryType:
            assert entry_type.value.emoji != ""
            assert len(entry_type.value.emoji) > 0

    def test_entry_type_names(self):
        """Test that each entry type has short and long names."""
        for entry_type in EntryType:
            assert entry_type.value.short != ""
            assert entry_type.value.long != ""
            assert len(entry_type.value.short) > 0
            assert len(entry_type.value.long) > 0

    def test_meal_entry_types(self):
        """Test that all meal entry types are defined."""
        meal_types = [
            EntryType.BREAKFAST,
            EntryType.LUNCH,
            EntryType.DINNER,
            EntryType.EVENING_MEAL,
        ]

        for meal_type in meal_types:
            assert meal_type.value.emoji == "🍽️"

    def test_activity_entry_types(self):
        """Test that all activity entry types have same emoji."""
        activity_types = [
            EntryType.EVENING_ACTIVITY,
            EntryType.AFTERNOON_ACTIVITY,
        ]

        for activity_type in activity_types:
            assert activity_type.value.emoji == "🕺💃"

    def test_prayer_entry_types(self):
        """Test that all prayer entry types have same emoji."""
        prayer_types = [
            EntryType.MORNING_PRAYER,
            EntryType.EVENING_PRAYER,
        ]

        for prayer_type in prayer_types:
            assert prayer_type.value.emoji == "💒"


class TestParticipantTypeEnum:
    """Test suite for the ParticipantType enum."""

    def test_participant_type_values(self):
        """Test that participant types have expected values."""
        assert ParticipantType.LEADER.value == 1
        assert ParticipantType.CAMP_MANAGEMENT.value == 2
        assert ParticipantType.CONFIRMEE.value == 3
        assert ParticipantType.OTHER.value == 4

    def test_all_participant_types_defined(self):
        """Test that expected participant types are defined."""
        expected_types = ["LEADER", "CAMP_MANAGEMENT", "CONFIRMEE", "OTHER"]

        for p_type_name in expected_types:
            assert hasattr(ParticipantType, p_type_name)

    def test_participant_type_comparison(self):
        """Test comparing participant types."""
        assert ParticipantType.LEADER < ParticipantType.CAMP_MANAGEMENT
        assert ParticipantType.CAMP_MANAGEMENT < ParticipantType.CONFIRMEE


class TestRoleEnum:
    """Test suite for the Role enum."""

    def test_role_values(self):
        """Test that roles have expected values."""
        assert Role.PRIEST.value == 1
        assert Role.DEACON.value == 2
        assert Role.CAMP_MANAGER.value == 3
        assert Role.ASSISTANT_CAMP_MANAGER.value == 4
        assert Role.MUSICIAN.value == 5
        assert Role.BOAT_LEADER.value == 6
        assert Role.SECURITY_OFFICER.value == 7
        assert Role.HEALTH_OFFICER.value == 8

    def test_all_roles_defined(self):
        """Test that expected roles are defined."""
        expected_roles = [
            "PRIEST",
            "DEACON",
            "CAMP_MANAGER",
            "ASSISTANT_CAMP_MANAGER",
            "MUSICIAN",
            "BOAT_LEADER",
            "SECURITY_OFFICER",
            "HEALTH_OFFICER",
        ]

        for role_name in expected_roles:
            assert hasattr(Role, role_name)

    def test_role_comparison(self):
        """Test comparing roles."""
        assert Role.PRIEST < Role.DEACON
        assert Role.CAMP_MANAGER > Role.DEACON


class TestLeaderYearTypeEnum:
    """Test suite for the LeaderYearType enum."""

    def test_leader_year_type_values(self):
        """Test that leader year types have expected string values."""
        assert LeaderYearType.FIRST_YEAR.value == "1"
        assert LeaderYearType.SECOND_YEAR.value == "2"
        assert LeaderYearType.THIRD_YEAR.value == "3"
        assert LeaderYearType.FOURTH_PLUS.value == "4+"

    def test_all_leader_year_types_defined(self):
        """Test that expected leader year types are defined."""
        expected_types = ["FIRST_YEAR", "SECOND_YEAR", "THIRD_YEAR", "FOURTH_PLUS"]

        for year_type_name in expected_types:
            assert hasattr(LeaderYearType, year_type_name)

    def test_leader_year_type_string_conversion(self):
        """Test converting leader year type to string."""
        # LeaderYearType is a StrEnum, so str() returns the value
        assert str(LeaderYearType.FIRST_YEAR) == "1"
        assert LeaderYearType.FIRST_YEAR.value == "1"
