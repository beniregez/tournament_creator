from dataclasses import dataclass
from .team import Team


@dataclass(frozen=True)
class Match:
    team1: Team
    team2: Team

    def __str__(self):
        return f"{self.team1} vs {self.team2}"

    def to_dict(self):
        return {
            "team1": self.team1.to_dict(),
            "team2": self.team2.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            team1=Team.from_dict(data["team1"]),
            team2=Team.from_dict(data["team2"])
        )
