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
    
    # Check all events and set invalid groupings to None.
    def validate_events_against_categories(self):
        valid_group_ids = set()
        for cat in self.categories:
            group = cat.get("group", "None")
            valid_group_ids.add(group)

        # Remove events for groups that no longer exist
        self.events = {
            group_id: events
            for group_id, events in self.events.items()
            if group_id in valid_group_ids or group_id == "None"
        }

    def validate_events_against_days(self):
        valid_days = {f"Day {i + 1}" for i in range(len(self.days))}
        valid_days.add("All Days")

        for group_id in self.events:
            for event in self.events[group_id]:
                if event.get("day") not in valid_days:
                    event["day"] = "None"