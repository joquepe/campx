import pytest
import datetime as dt
from campx.repository import Repository
from campx.factory import Factory
from campx.model.participant import Participant
from campx.model.enums import ParticipantType, LeaderYearType


class TestRepository:
    """Test suite for the Repository class."""

    def test_repository_creation(self):
        """Test creating a repository."""
        factory = Factory()
        repo = Repository(factory)
        assert repo._participants == {}
        assert repo._camps == {}

    def test_add_participant(self):
        """Test adding a participant to repository."""
        factory = Factory()
        repo = Repository(factory)
        p = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )
        repo.add_participant(p)

        assert repo.has_participant(1)
        assert repo.get_participant(1) == p

    def test_get_participant_not_found(self):
        """Test getting a participant that doesn't exist."""
        factory = Factory()
        repo = Repository(factory)

        with pytest.raises(KeyError):
            repo.get_participant(999)

    def test_has_participant(self):
        """Test checking if participant exists."""
        factory = Factory()
        repo = Repository(factory)
        p = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )
        repo.add_participant(p)

        assert repo.has_participant(1)
        assert not repo.has_participant(2)

    def test_get_participant_by_full_name(self):
        """Test retrieving a participant by full name."""
        factory = Factory()
        repo = Repository(factory)
        p = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )
        repo.add_participant(p)

        retrieved = repo.get_participant_by_full_name("John Doe")
        assert retrieved == p

    def test_get_participant_by_full_name_not_found(self):
        """Test retrieving a participant by name that doesn't exist."""
        factory = Factory()
        repo = Repository(factory)

        with pytest.raises(ValueError, match="Could not find participant"):
            repo.get_participant_by_full_name("Jane Smith")

    def test_get_participant_by_full_name_multiple_matches(self):
        """Test that error is raised when multiple participants match."""
        factory = Factory()
        repo = Repository(factory)
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
            first_name="John",
            last_name="Doe",
            gender="F",
            birthday=dt.date(1992, 5, 20),
            participant_type=ParticipantType.LEADER,
        )
        repo.add_participant(p1)
        repo.add_participant(p2)

        with pytest.raises(AssertionError, match="Several participants found"):
            repo.get_participant_by_full_name("John Doe")

    def test_multiple_participants(self):
        """Test adding and retrieving multiple participants."""
        factory = Factory()
        repo = Repository(factory)

        participants = [
            Participant(
                participant_id=i,
                first_name=f"Person{i}",
                last_name="Test",
                gender="M" if i % 2 == 0 else "F",
                birthday=dt.date(1990 + i, 1, 1),
                participant_type=ParticipantType.LEADER,
            )
            for i in range(1, 6)
        ]

        for p in participants:
            repo.add_participant(p)

        assert len(repo._participants) == 5
        for p in participants:
            assert repo.has_participant(p.participant_id)


class TestFactory:
    """Test suite for the Factory class."""

    def test_factory_creation(self):
        """Test creating a factory."""
        factory = Factory()
        assert factory.input_base_dir is not None

    def test_create_participant(self):
        """Test creating a participant from record."""
        factory = Factory()
        repo = Repository(factory)

        record = {
            "participant_id": 1,
            "first_name": "Joakim",
            "last_name": "Persson",
            "gender": "M",
            "birth_date": "1992-05-15",
            "participant_type": "LEADER",
            "leader_year_type": "FIRST_YEAR",
            "nick_name": None,
        }

        p = factory.create_participant(record, repo)
        assert p.participant_id == 1
        assert p.full_name == "Joakim Persson"
        assert p.gender == "M"
        assert p.birthday == dt.date(1992, 5, 15)
        assert p.participant_type == ParticipantType.LEADER
        assert p.leader_year_type == LeaderYearType.FIRST_YEAR

    def test_create_participant_without_leader_year_type(self):
        """Test creating a participant without leader year type."""
        factory = Factory()
        repo = Repository(factory)

        record = {
            "participant_id": 1,
            "first_name": "Jane",
            "last_name": "Smith",
            "gender": "F",
            "birth_date": "1995-06-20",
            "participant_type": "CAMP_MANAGEMENT",
            "leader_year_type": None,
            "nick_name": None,
        }

        p = factory.create_participant(record, repo)
        assert p.leader_year_type is None

    def test_create_participant_caching(self):
        """Test that creating same participant twice returns cached version."""
        factory = Factory()
        repo = Repository(factory)

        record = {
            "participant_id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "gender": "M",
            "birth_date": "1990-01-15",
            "participant_type": "LEADER",
            "leader_year_type": None,
            "nick_name": None,
        }

        p1 = factory.create_participant(record, repo)
        p2 = factory.create_participant(record, repo)

        assert p1 is p2
        assert id(p1) == id(p2)

    def test_factory_with_custom_input_dir(self, tmp_path):
        """Test creating a factory with custom input directory."""
        factory = Factory(input_base_dir=tmp_path)
        assert factory.input_base_dir == tmp_path

    def test_get_camp_input_dir_nonexistent(self):
        """Test that FileNotFoundError is raised for nonexistent camp directory."""
        factory = Factory()

        with pytest.raises(FileNotFoundError):
            factory.get_camp_input_dir("Nonexistent Camp")

    def test_different_participant_types(self):
        """Test creating participants with different types."""
        factory = Factory()
        repo = Repository(factory)

        for p_type in [
            "LEADER",
            "CAMP_MANAGEMENT",
            "CONFIRMEE",
            "OTHER",
        ]:
            record = {
                "participant_id": 1,
                "first_name": "Test",
                "last_name": "Person",
                "gender": "M",
                "birth_date": "1990-01-15",
                "participant_type": p_type,
                "leader_year_type": None,
                "nick_name": None,
            }

            repo = Repository(factory)  # Fresh repo for each test
            p = factory.create_participant(record, repo)
            assert p.participant_type == ParticipantType[p_type]
