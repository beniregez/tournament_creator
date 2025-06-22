class Model:
    def __init__(self):
        self.days = []
        self.categories = {}

    def set_data(self, data:dict):
        self.days = data.get("days", [])
        self.categories = data.get("categories", {})

    def get_data(self) -> dict:
        return {
            "days": self.days,
            "categories": self.categories
        }

    def set_days(self, days):
        self.days = days

    def get_days(self) -> list:
        return self.days
    
    def set_categories(self, categories):
        self.categories = categories
    
    def get_categories(self) -> dict:
        return self.categories