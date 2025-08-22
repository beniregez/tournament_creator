from dataclasses import dataclass
from typing import Optional


@dataclass(unsafe_hash=True)
class Team:
    name: str
    color: str = "#FFFFFF"
    font_color: Optional[str] = None

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "color": self.color,
            "font_color": self.font_color
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            color=data["color"],
            font_color=data.get("font_color")
        )