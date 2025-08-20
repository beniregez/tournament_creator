from dataclasses import dataclass, field
from typing import List, Optional, Union
from .match import Match


@dataclass
class Event:
    duration: int

    def __post_init__(self):
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError("Duration must be a positive integer.")

    def to_dict(self):
        return {
            "duration": self.duration
        }

    @classmethod
    def from_dict(cls, data):
        return cls(duration=data["duration"])


@dataclass
class MatchEvent(Event):
    matches: List[Match] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not all(isinstance(m, Match) for m in self.matches):
            raise TypeError("All matches must be instances of Match.")

    def get_unique_teams(self) -> set:
        """Returns all unique team instances from all matches."""
        teams = {match.team1 for match in self.matches}
        teams.update(match.team2 for match in self.matches)
        return teams

    def to_dict(self):
        return {
            "duration": self.duration,
            "matches": [m.to_dict() for m in self.matches]
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            duration=data["duration"],
            matches=[Match.from_dict(m) for m in data["matches"]]
        )

@dataclass
class OtherEvent(Event):
    label: str
    bold: bool = False
    color: Optional[str] = None
    day_index: Optional[int] = None     # 0 stands for 'takes place at all days'
    bef_dur_aft: Optional[str] = None   # 'before', 'during' or 'after'
    dur_index: Optional[int] = None     # indicates after how many match events it takes place.

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.label, str):
            raise TypeError("Label must be a string.")

    def to_dict(self):
        return {
            "duration": self.duration,
            "label": self.label,
            "bold": self.bold,
            "color": self.color,
            "day_index": self.day_index,
            "bef_dur_aft": self.bef_dur_aft,
            "dur_index": self.dur_index
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            duration=data["duration"],
            label=data["label"],
            bold=data.get("bold", False),
            color=data.get("color"),
            day_index=data.get("day_index"),
            bef_dur_aft=data.get("bef_dur_aft"),
            dur_index=data.get("dur_index")
        )