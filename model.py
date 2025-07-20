class Model:
    def __init__(self):
        self.days = []
        self.categories = []
        self.events = {}

    def set_data(self, data:dict):
        self.days = data.get("days", [])
        self.categories = data.get("categories", [])
        self.events = data.get("events", {})

    def get_data(self) -> dict:
        return {
            "days": self.days,
            "categories": self.categories,
            "events": self.events
        }

    def set_days(self, days):
        self.days = days

    def get_days(self) -> list:
        return self.days
    
    def set_categories(self, categories):
        self.categories = categories
    
    def get_categories(self) -> list:
        return self.categories
    
    def set_events(self, events):
        self.events = events
        
    def get_events(self) -> dict:
        return self.events