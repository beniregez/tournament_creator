from dataclasses import dataclass, field
from typing import List

from core import Team

@dataclass
class Category:
    name: str
    group: str
    runs: str
    teams: List[Team]
    bg_color: str = field(default="#FFFFFF")

    def to_dict(self):
        return {
            "name": self.name,
            "group": self.group,
            "runs": self.runs,
            "teams": [team.to_dict() for team in self.teams],
            "bg_color": self.bg_color
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            group=data["group"],
            runs=data["runs"],
            teams=[Team.from_dict(t) for t in data.get("teams", [])],
            bg_color=data.get("bg_color", "#FFFFFF")
        )