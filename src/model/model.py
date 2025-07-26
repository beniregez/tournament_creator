from core import OtherEvent, Team, Category

class Model:
    def __init__(self):
        self.tournament_info = {}
        self.days = []
        self.categories = []
        self.match_durs = {}
        self.group_info = {}
        self.other_events = {}
    
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
            }
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
            }
        }
    
    def set_tournament_info(self, tournament_info):
        self.tournament_info = tournament_info
        
    def get_tournament_info(self) -> dict:
        return self.tournament_info

    def set_days(self, days):
        self.days = days

    def get_days(self) -> list:
        return self.days
    
    def set_categories(self, categories):
        self.categories = categories
    
    def get_categories(self) -> list:
        return self.categories
    
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