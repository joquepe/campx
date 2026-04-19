from campx.repository import Repository
from campx.factory import Factory


def test_create_participant():
    factory = Factory()
    repository = Repository(factory)

    record = {
        "participant_id": 1,
        "first_name": "Joakim",
        "last_name": "Persson",
        "gender": "M",
        "birth_date": "1992-05-15",
        "participant_type": "CAMP_MANAGEMENT",
        "leader_year_type": None,
        "nick_name": None,
    }

    p = factory.create_participant(record, repository)
    assert p.full_name == "Joakim Persson"
