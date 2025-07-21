class Model:
    def __init__(self):
        self.tournament_info = {}
        self.days = []
        self.categories = []
        self.match_durs = {}
        self.events = {}

    def set_data(self, data:dict):
        self.tournament_info = data.get("tournament_info", {})
        self.days = data.get("days", [])
        self.categories = data.get("categories", [])
        self.match_durs = data.get("match_durs", {})
        self.events = data.get("events", {})

    def get_data(self) -> dict:
        return {
            "tournament_info": self.tournament_info,
            "days": self.days,
            "categories": self.categories,
            "match_durs": self.match_durs,
            "events": self.events
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
    
    def set_events(self, events):
        self.events = events
        
    def get_events(self) -> dict:
        return self.events