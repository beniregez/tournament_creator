from typing import List
from core import OtherEvent, Team, Category, EventDay

class Model:
    def __init__(self):
        self.tournament_info = {}
        self.days = []
        self.categories: List[Category] = []
        self.groupings_changed: bool = False
        self._prev_group_ids: set[str] = set()

        self.match_durs = {}
        self.group_info = {}
        self.other_events = {}
        self.tournament_generated = []
    
    def set_data(self, data: dict):
        self.tournament_info = data.get("tournament_info", {})
        self.days = data.get("days", [])
        self.categories = [Category.from_dict(cat) for cat in data["categories"]]
        self.match_durs = data.get("match_durs", {})
        self.group_info = data.get("group_info", {})
        self.other_events = {
            group_id: [OtherEvent.from_dict(e) for e in group_events]
            for group_id, group_events in data.get("events", {}).items()
        }
        if "tournament_generated" in data:
            self.tournament_generated = [EventDay.from_dict(event_day) for event_day in data["tournament_generated"]]
        else:
            self.tournament_generated = []

        # After set_data: Check, if groupings have changed.
        self._update_groupings_changed()

    def get_data(self) -> dict:
        return {
            "tournament_info": self.tournament_info,
            "days": self.days,
            "categories": self.categories,
            "match_durs": self.match_durs,
            "group_info": self.group_info,
            "events": {
                group_id: [e.to_dict() for e in group_events]
                for group_id, group_events in self.other_events.items()
            },
            "tournament_generated": self.tournament_generated
        }

    def to_serializable_dict(self) -> dict:
        return {
            "tournament_info": self.tournament_info,
            "days": self.days,
            "categories": [category.to_dict() for category in self.categories],
            "match_durs": self.match_durs,
            "group_info": self.group_info,
            "events": {
                group_id: [event.to_dict() for event in group_events]
                for group_id, group_events in self.other_events.items()
            },
            "tournament_generated": [event_day.to_dict() for event_day in self.tournament_generated]
        }
    
    def set_tournament_info(self, tournament_info):
        self.tournament_info = tournament_info
        
    def get_tournament_info(self) -> dict:
        return self.tournament_info

    def set_days(self, days):
        self.days = days

    def get_days(self) -> list:
        return self.days
    
    def set_categories(self, categories: List[Category]):
        """Set categories and check if groupings have changed."""
        self.categories = categories
        self._update_groupings_changed()
    
    def get_categories(self) -> list:
        return self.categories

    def get_unique_groups(self) -> List[str]:
        return sorted({category.group for category in self.categories})
    
    def set_match_durs(self, match_durs):
        self.match_durs = match_durs
    
    def get_match_durs(self) -> dict:
        return self.match_durs
    
    def set_group_info(self, group_info):
        self.group_info = group_info
        
    def get_group_info(self) -> dict:
        return self.group_info
    
    def set_other_events(self, events):
        self.other_events = events
        
    def get_other_events(self) -> dict:
        return self.other_events
    
    def set_tournament_generated(self, tournament_generated):
        self.tournament_generated = tournament_generated
    
    def get_tournament_generated(self) -> List[EventDay]:
        return self.tournament_generated

    # Groupings Changed Flag
    def _update_groupings_changed(self):
        """Internal method: Check, if number of groupings has changed."""
        new_group_ids = {cat.group for cat in self.categories}
        if new_group_ids != self._prev_group_ids:
            self.groupings_changed = True
        self._prev_group_ids = new_group_ids

    def get_groupings_changed(self) -> bool:
        return self.groupings_changed

    def set_groupings_changed(self, value: bool):
        self.groupings_changed = value
