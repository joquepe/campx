from dataclasses import dataclass


from campx.model.enums import ParticipantType
from campx.model.schedule import Schedule
from campx.model.camp_place import CampPlace

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from campx.model.participant import Participant


@dataclass
class Camp:
    """Aggregates camp participants, venue, and schedule."""

    name: str
    camp_place: CampPlace
    participants: list["Participant"]
    schedule: Schedule

    def __repr__(self) -> str:
        """Return a concise representation useful in debugging output."""
        return f"Camp {self.name} at {self.camp_place.name} with {len(self.participants)} participants ({len(self.confirmees)} confirmees)."

    @property
    def confirmees(self) -> list["Participant"]:
        """Return all confirmees participating in the camp."""
        return [
            p
            for p in self.participants
            if p.participant_type == ParticipantType.CONFIRMEE
        ]

    @property
    def leaders(self) -> list["Participant"]:
        """Return leaders sorted by full name."""
        participants = [
            p for p in self.participants if p.participant_type == ParticipantType.LEADER
        ]
        return sorted(participants, key=lambda p: p.full_name)

    @property
    def camp_management(self) -> list["Participant"]:
        """Return camp management participants sorted by full name."""
        participants = [
            p
            for p in self.participants
            if p.participant_type == ParticipantType.CAMP_MANAGEMENT
        ]
        return sorted(participants, key=lambda p: p.full_name)

    @property
    def leaders_incl_management(self) -> list["Participant"]:
        """Return leaders and camp management as one sorted list."""
        participants = self.leaders + self.camp_management
        return sorted(participants, key=lambda p: p.full_name)
