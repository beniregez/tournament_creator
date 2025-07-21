class Model:
    def __init__(self):
        self.title = ""
        self.days = []
        self.categories = []
        self.match_durs = {}
        self.events = {}

    def set_data(self, data:dict):
        self.title = data.get("title", "")
        self.days = data.get("days", [])
        self.categories = data.get("categories", [])
        self.match_durs = data.get("match_durs", {})
        self.events = data.get("events", {})

    def get_data(self) -> dict:
        return {
            "title": self.title,
            "days": self.days,
            "categories": self.categories,
            "match_durs": self.match_durs,
            "events": self.events
        }

    def set_title(self, title):
        self.title = title
        
    def get_title(self) -> str:
        return self.title

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