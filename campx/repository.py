from campx.model.participant import Participant
from campx.model.camp import Camp

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from campx.factory import Factory


class Repository:
    """Caches and serves camps and participants built by the factory."""

    def __init__(self, factory: "Factory"):
        """Initialise an empty repository backed by a factory."""
        self._participants: dict[int, Participant] = {}
        self._camps: dict[str, Camp] = {}
        self.factory: "Factory" = factory

    def has_camp(self, camp_name: str) -> bool:
        """Return whether a camp is already cached."""
        return camp_name in self._camps

    def get_camp(self, camp_name: str) -> Camp:
        """Return a cached camp, populating it on first access."""
        if not self.has_camp(camp_name):
            self.factory.populate_camp(camp_name, self)
        return self._camps[camp_name]

    def add_camp(self, camp: Camp) -> None:
        """Store a camp in the repository."""
        if self.has_camp(camp.name):
            raise ValueError(f"Camp {camp.name} already exists in repo")
        self._camps[camp.name] = camp

    def has_participant(self, participant_id: int) -> bool:
        """Return whether a participant is already cached."""
        return participant_id in self._participants

    def get_participant(self, participant_id: int) -> Participant:
        """Return a participant by identifier."""
        return self._participants[participant_id]

    def get_participant_by_full_name(self, full_name: str) -> Participant:
        """Return the uniquely matching participant for a full name."""
        matches = [p for _, p in self._participants.items() if p.full_name == full_name]
        if not matches:
            raise ValueError(f"Could not find participant with {full_name=}")
        assert len(matches) == 1, f"Several participants found with {full_name=}"
        return matches[0]

    def add_participant(self, participant: Participant) -> None:
        """Store or replace a participant in the repository."""
        self._participants[participant.participant_id] = participant
