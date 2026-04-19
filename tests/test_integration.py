import pytest
import datetime as dt
import csv

from campx.repository import Repository
from campx.factory import Factory
from campx.model.participant import Participant
from campx.model.enums import ParticipantType


class TestFactoryIntegration:
    """Integration tests for Factory with real file I/O."""

    def test_create_schedule_template_files(self, tmp_path):
        """Test creating schedule template files."""
        # Create a temporary input directory structure
        camp_name = "Test Camp"
        camp_dir = tmp_path / camp_name
        camp_dir.mkdir()

        factory = Factory(input_base_dir=tmp_path)

        # This test verifies the method structure works
        # Note: full test would require camp config setup
        assert factory.get_camp_input_dir(camp_name) == camp_dir

    def test_get_participants_from_csv(self, tmp_path):
        """Test reading participants from CSV file."""
        camp_name = "Test Camp"
        camp_dir = tmp_path / camp_name
        camp_dir.mkdir()

        # Create a test CSV file
        participants_file = camp_dir / "participants.csv"
        with open(participants_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "participant_id",
                    "first_name",
                    "last_name",
                    "gender",
                    "birth_date",
                    "participant_type",
                    "leader_year_type",
                ],
                delimiter=";",
            )
            writer.writeheader()
            writer.writerow(
                {
                    "participant_id": "1",
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": "M",
                    "birth_date": "1990-01-15",
                    "participant_type": "LEADER",
                    "leader_year_type": "FIRST_YEAR",
                }
            )
            writer.writerow(
                {
                    "participant_id": "2",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "gender": "F",
                    "birth_date": "1995-06-20",
                    "participant_type": "CAMP_MANAGEMENT",
                    "leader_year_type": None,
                }
            )

        factory = Factory(input_base_dir=tmp_path)
        participants = factory.get_participants(camp_name)

        assert len(participants) == 2
        assert participants[0]["first_name"] == "John"
        assert participants[1]["first_name"] == "Jane"

    def test_factory_populate_participants(self, tmp_path):
        """Test populating participants from factory."""
        camp_name = "Test Camp"
        camp_dir = tmp_path / camp_name
        camp_dir.mkdir()

        # Create a test CSV file
        participants_file = camp_dir / "participants.csv"
        with open(participants_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "participant_id",
                    "first_name",
                    "last_name",
                    "gender",
                    "birth_date",
                    "participant_type",
                    "leader_year_type",
                    "nick_name",
                ],
                delimiter=";",
            )
            writer.writeheader()
            writer.writerow(
                {
                    "participant_id": "1",
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": "M",
                    "birth_date": "1990-01-15",
                    "participant_type": "LEADER",
                    "leader_year_type": "FIRST_YEAR",
                    "nick_name": None,
                }
            )

        factory = Factory(input_base_dir=tmp_path)
        repo = Repository(factory)
        participants = factory.populate_participants(repo, camp_name)

        assert len(participants) == 1
        assert participants[0].full_name == "John Doe"
        assert repo.has_participant(1)

    def test_factory_populate_participants_with_multiple_types(self, tmp_path):
        """Test populating participants with different participant types."""
        camp_name = "Test Camp"
        camp_dir = tmp_path / camp_name
        camp_dir.mkdir()

        # Create a test CSV file
        participants_file = camp_dir / "participants.csv"
        with open(participants_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "participant_id",
                    "first_name",
                    "last_name",
                    "gender",
                    "birth_date",
                    "participant_type",
                    "leader_year_type",
                    "nick_name",
                ],
                delimiter=";",
            )
            writer.writeheader()
            for i, p_type in enumerate(
                ["LEADER", "CAMP_MANAGEMENT", "CONFIRMEE", "OTHER"], 1
            ):
                writer.writerow(
                    {
                        "participant_id": str(i),
                        "first_name": f"Person{i}",
                        "last_name": "Test",
                        "gender": "M" if i % 2 == 0 else "F",
                        "birth_date": f"198{i}-01-15",
                        "participant_type": p_type,
                        "leader_year_type": None,
                        "nick_name": None,
                    }
                )

        factory = Factory(input_base_dir=tmp_path)
        repo = Repository(factory)
        participants = factory.populate_participants(repo, camp_name)

        assert len(participants) == 4
        assert participants[0].participant_type == ParticipantType.LEADER
        assert participants[1].participant_type == ParticipantType.CAMP_MANAGEMENT
        assert participants[2].participant_type == ParticipantType.CONFIRMEE
        assert participants[3].participant_type == ParticipantType.OTHER


class TestRepositoryIntegration:
    """Integration tests for Repository class."""

    def test_repository_with_multiple_participants(self, tmp_path):
        """Test repository managing multiple participants."""
        camp_name = "Test Camp"
        camp_dir = tmp_path / camp_name
        camp_dir.mkdir()

        # Create a test CSV file
        participants_file = camp_dir / "participants.csv"
        with open(participants_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "participant_id",
                    "first_name",
                    "last_name",
                    "gender",
                    "birth_date",
                    "participant_type",
                    "leader_year_type",
                    "nick_name",
                ],
                delimiter=";",
            )
            writer.writeheader()
            for i in range(1, 6):
                writer.writerow(
                    {
                        "participant_id": str(i),
                        "first_name": f"Leader{i}",
                        "last_name": "Test",
                        "gender": "M" if i % 2 == 0 else "F",
                        "birth_date": f"199{i - 1}-01-15",
                        "participant_type": "LEADER",
                        "leader_year_type": "1",
                        "nick_name": None,
                    }
                )

        factory = Factory(input_base_dir=tmp_path)
        repo = Repository(factory)
        factory.populate_participants(repo, camp_name)

        assert repo._participants.__len__() == 5

        for i in range(1, 6):
            assert repo.has_participant(i)
            p = repo.get_participant(i)
            assert p.first_name == f"Leader{i}"

    def test_repository_query_by_name(self, tmp_path):
        """Test querying repository by participant name."""
        camp_name = "Test Camp"
        camp_dir = tmp_path / camp_name
        camp_dir.mkdir()

        participants_file = camp_dir / "participants.csv"
        with open(participants_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "participant_id",
                    "first_name",
                    "last_name",
                    "gender",
                    "birth_date",
                    "participant_type",
                    "leader_year_type",
                    "nick_name",
                ],
                delimiter=";",
            )
            writer.writeheader()
            writer.writerow(
                {
                    "participant_id": "1",
                    "first_name": "Unique",
                    "last_name": "Person",
                    "gender": "M",
                    "birth_date": "1990-01-15",
                    "participant_type": "LEADER",
                    "leader_year_type": None,
                    "nick_name": None,
                }
            )

        factory = Factory(input_base_dir=tmp_path)
        repo = Repository(factory)
        factory.populate_participants(repo, camp_name)

        p = repo.get_participant_by_full_name("Unique Person")
        assert p.participant_id == 1
        assert p.full_name == "Unique Person"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_factory_missing_camp_directory(self, tmp_path):
        """Test factory behavior with missing camp directory."""
        factory = Factory(input_base_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            factory.get_camp_input_dir("NonexistentCamp")

    def test_repository_duplicate_participant_id_add(self):
        """Test that adding participant with same ID updates repository."""
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
        repo.add_participant(p1)

        # Adding another with same ID should replace
        p2 = Participant(
            participant_id=1,
            first_name="Jane",
            last_name="Smith",
            gender="F",
            birthday=dt.date(1995, 6, 20),
            participant_type=ParticipantType.LEADER,
        )
        repo.add_participant(p2)

        assert repo.get_participant(1).first_name == "Jane"

    def test_participant_with_none_leader_year_type(self):
        """Test creating participant with None leader_year_type."""
        p = Participant(
            participant_id=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.CONFIRMEE,
            leader_year_type=None,
        )
        assert p.leader_year_type is None

    def test_participant_initials_with_single_letter_names(self):
        """Test initials with single letter names."""
        p = Participant(
            participant_id=1,
            first_name="X",
            last_name="Y",
            gender="M",
            birthday=dt.date(1990, 1, 15),
            participant_type=ParticipantType.LEADER,
        )
        assert p.initials == "XY"
