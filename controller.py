import json
from view.main_view import MainView
from model import Model
from excel_writer import ExcelWriter

class Controller:
    def __init__(self):
        self.model = Model()
        self.view = MainView(self)
        self.view.show()

    # Put the data into the model
    def update_model_from_views(self):
         # Get Data from all subviews
        days = self.view.days_tab.collect_input_fields()
        categories = self.view.categories_tab.collect_input_fields()
        events = self.view.events_tab.collect_input_fields()
        self.model.set_data({
            "days": days,
            "categories": categories,
            "events": events
        })

    def update_events_from_view(self):
        events = self.view.events_tab.collect_input_fields()
        self.model.set_events(events)

    def update_categories_from_view(self):
        categories = self.view.categories_tab.collect_input_fields()
        self.model.set_categories(categories)

    def update_days_from_view(self):
        days = self.view.days_tab.collect_input_fields()
        self.model.set_days(days)
    
    # TODO: implement
    def export_to_excel(self, filepath):
        pass
        # ExcelWriter.export(self.model, filepath)

    def save_model_to_json(self, filename):
        self.update_model_from_views() # Before saving: Update model
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.model.get_data(), f, indent=4, ensure_ascii=False)

    def load_model_from_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.model.set_data(data)
            self.view.populate_from_model(self.model)