from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from core.event import MatchEvent, OtherEvent

EventType = Union[MatchEvent, OtherEvent]

@dataclass
class EventBlock:
    events: List[Optional[EventType]] = field(default_factory=list)

    def add_event(self, event: EventType) -> None:
        if not isinstance(event, (MatchEvent, OtherEvent)):
            raise TypeError("Only MatchEvent or OtherEvent instances are allowed.")
        self.events.append(event)

    def remove_event(self, index: int) -> None:
        if 0 <= index < len(self.events):
            del self.events[index]
        else:
            raise IndexError("Event index out of range.")

    def get_event(self, index: int) -> EventType:
        if 0 <= index < len(self.events):
            return self.events[index]
        else:
            raise IndexError("Event index out of range.")

    def add_event_at_position(self, event: EventType, position: int) -> None:
        if not isinstance(event, (MatchEvent, OtherEvent)):
            raise TypeError("Only MatchEvent or OtherEvent instances are allowed.")
        if position < 0:
            raise IndexError("Negative position is not allowed.")
        while len(self.events) <= position:
            self.events.append(None)
        self.events[position] = event

    def insert_event_at_position(self, event: EventType, position: int) -> None:
        if not isinstance(event, (MatchEvent, OtherEvent)):
            raise TypeError("Only MatchEvent or OtherEvent instances are allowed.")
        if position < 0:
            raise IndexError("Negative position is not allowed.")

        # Make sure the list is long enough
        while len(self.events) < position:
            self.events.append(None)

        # Insert event without overwriting
        self.events.insert(position, event)

    def add_event_after_n_nones(self, n: int, event: EventType) -> None:
        """Inserts an event after a total of n None entries,
        but only after all subsequent real events have been processed.
        Adds missing Nones before the event."""
        
        if not isinstance(event, (MatchEvent, OtherEvent)):
            raise TypeError("Only MatchEvent or OtherEvent instances are allowed.")
        if n < 0:
            raise ValueError("n must be non-negative.")

        # Count the existing None entries
        current_none_count = sum(1 for e in self.events if e is None)

        # Add missing nones at the end
        if current_none_count < n:
            self.events.extend([None] * (n - current_none_count))

        # Find the position after the nth None
        none_seen = 0
        idx = 0
        while idx < len(self.events):
            if self.events[idx] is None:
                none_seen += 1
                if none_seen == n:
                    idx += 1
                    break
            idx += 1

        # Skip all the following real events
        while idx < len(self.events) and self.events[idx] is not None:
            idx += 1

        # Make sure the list is long enough
        while len(self.events) < idx:
            self.events.append(None)

        # Add the event
        if idx == len(self.events):
            self.events.append(event)
        else:
            self.events.insert(idx, event)

    def add_event_to_next_available_slot(self, event: EventType) -> None:
        if not isinstance(event, (MatchEvent, OtherEvent)):
            raise TypeError("Only MatchEvent or OtherEvent instances are allowed.")
        
        try:
            # Find first None-Slot
            index = self.events.index(None)
            self.events[index] = event
        except ValueError:
            # If no Nones: Append at the end
            self.events.append(event)

    def get_valid_events(self) -> List[EventType]:
        return [event for event in self.events if event is not None]

    def total_duration(self) -> int:
        return sum(event.duration for event in self.events if event is not None)
    
    def number_of_events(self) -> int:
        return sum(1 for event in self.events if event is not None)
    
    def number_of_matches(self) -> int:
        return sum(len(event.matches) for event in self.events if isinstance(event, MatchEvent))

    def to_dict(self) -> Dict[str, Any]:
        """Serializes EventBlock into a dict."""
        serialized_events = []
        for e in self.events:
            if e is None:
                serialized_events.append(None)
            elif isinstance(e, MatchEvent):
                serialized_events.append({
                    "type": "match",
                    "data": e.to_dict()
                })
            elif isinstance(e, OtherEvent):
                serialized_events.append({
                    "type": "other",
                    "data": e.to_dict()
                })
            else:
                raise TypeError(f"Unsupported event type: {type(e).__name__}")
        return {"events": serialized_events}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventBlock":
        """Creates an EventBlock from a dict."""
        events: List[Optional[EventType]] = []
        for e in data.get("events", []):
            if e is None:
                events.append(None)
            else:
                etype = e.get("type")
                edata = e.get("data", {})
                if etype == "match":
                    events.append(MatchEvent.from_dict(edata))
                elif etype == "other":
                    events.append(OtherEvent.from_dict(edata))
                else:
                    raise ValueError(f"Unknown event type: {etype}")
        return cls(events=events)