from dataclasses import dataclass, field
from typing import List, Optional, Union
from core.event import MatchEvent, OtherEvent
from .event_block import EventBlock

EventType = Union[MatchEvent, OtherEvent]

@dataclass
class EventDay:
    blocks: List[EventBlock] = field(default_factory=list)

    def add_block(self, block: EventBlock) -> None:
        self.blocks.append(block)

    def get_block(self, index: int) -> EventBlock:
        return self.blocks[index]

    def total_events(self) -> int:
        return sum(block.number_of_events() for block in self.blocks)

    def total_duration(self) -> int:
        return sum(block.total_duration() for block in self.blocks)

    def total_matches(self) -> int:
        return sum(block.number_of_matches() for block in self.blocks)

    def max_fields(self) -> int:
        """Returns the maximum of fields across all blocks"""
        max_fields = 0
        for block in self.blocks:
            for ev in block.events:
                if isinstance(ev, MatchEvent):
                    if len(ev.matches) > max_fields:
                        max_fields = len(ev.matches)
        return max_fields

    def get_event(self, index: int) -> Optional[EventType]:
        """Returns the event at index across all blocks."""
        count = 0
        for block in self.blocks:
            for event in block.events:
                if event is not None:
                    if count == index:
                        return event
                    count += 1
        raise IndexError("Global event index out of range.")

    def set_event(self, global_index: int, new_event: EventType) -> None:
        """Sets the event at index across all blocks."""
        count = 0
        for block in self.blocks:
            for i, event in enumerate(block.events):
                if event is not None:
                    if count == global_index:
                        block.events[i] = new_event
                        return
                    count += 1
        raise IndexError("Global event index out of range.")

    def get_all_valid_events(self) -> List[EventType]:
        """Returns all valid events from all blocks."""
        return [event for block in self.blocks for event in block.get_valid_events()]

    def count_team_home(self, team) -> int:
        """Counts how many times the team appears as home (team1) in all matches of the day."""
        count = 0
        for block in self.blocks:
            for ev in block.events:
                if isinstance(ev, MatchEvent):
                    for match in ev.matches:
                        if match.team1 == team:
                            count += 1
        return count

    def count_team_away(self, team) -> int:
        """Counts how many times the team appears as away (team2) in all matches of the day."""
        count = 0
        for block in self.blocks:
            for ev in block.events:
                if isinstance(ev, MatchEvent):
                    for match in ev.matches:
                        if match.team2 == team:
                            count += 1
        return count

    def count_team_total(self, team) -> int:
        """Counts how many times the team appears in total (home or away) in all matches of the day."""
        return self.count_team_home(team) + self.count_team_away(team)

    def to_dict(self) -> dict:
        return {
            "blocks": [block.to_dict() for block in self.blocks]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EventDay":
        blocks_data = data.get("blocks", [])
        blocks = [EventBlock.from_dict(b) for b in blocks_data]
        return cls(blocks=blocks)