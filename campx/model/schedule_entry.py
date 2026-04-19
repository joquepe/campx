from dataclasses import dataclass, field
from campx.model.enums import EntryType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from campx.model.participant import Participant


@dataclass
class ScheduleEntry:
    """Represents a single scheduled activity or responsibility slot."""

    entry_type: EntryType
    name: str
    start_time: str | None
    end_time: str | None
    responsible: list["Participant"] = field(default_factory=list)
    additional_info: str = ""

    def remove_participant(self, participant: "Participant") -> None:
        """Remove the first matching responsible participant from the entry."""
        for i, p in enumerate(self.responsible):
            if p.full_name == participant.full_name:
                del self.responsible[i]
                break
