import json
import os
from utils.tourn_ref_card_creator.ref_card_creator import RefCardCreator
from view.main_view import MainView
from model.model import Model
from utils.scheduler.scheduler import create_schedule
from utils.tourn_to_excel.excel_tournament_writer import ExcelTournamentWriter
from utils.tourn_stats.stats_excel_creator import StatsExcelCreator

class Controller:
    def __init__(self):
        self.model = Model()
        self.view = MainView(self)
        self.view.show()

    # Put the data into the model
    def update_model_from_views(self):
        self.update_home_from_view()
        self.update_days_from_view()
        self.update_categories_from_view()
        self.update_group_info_from_view()
        self.update_other_events_from_view()

    def update_home_from_view(self):
        info = self.view.home_tab.collect_input_fields()
        self.model.set_tournament_info(info)


    def update_other_events_from_view(self):
        events = self.view.events_tab.collect_input_fields()
        self.model.set_other_events(events)

    def update_categories_from_view(self):
        categories = self.view.categories_tab.collect_input_fields()
        self.model.set_categories(categories)

    def update_days_from_view(self):
        days = self.view.days_tab.collect_input_fields()
        self.model.set_days(days)
        
    def update_group_info_from_view(self):
        group_info = self.view.group_info_tab.collect_input_fields()
        self.model.set_group_info(group_info)
    
    def generate_tournament_from_model(self):
        self.model.set_tournament_generated(create_schedule(self.model))
    
    def export_to_excel(self):
        base_name = "output"
        folder_name = base_name
        counter = 1

        while os.path.exists(folder_name):
            folder_name = f"{base_name}{counter}"
            counter += 1

        os.makedirs(folder_name)

        tourn_writer = ExcelTournamentWriter(self.model, output_dir=folder_name)
        tourn_writer.write_to_excel()

        stats_writer = StatsExcelCreator(self.model, output_dir=folder_name)
        stats_writer.write_to_excel()

        ref_card_creator = RefCardCreator(self.model, output_path=folder_name)
        ref_card_creator.create_cards()

    def save_model_to_json(self, filename):
        self.update_model_from_views() # Before saving: Update model
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.model.to_serializable_dict(), f, indent=4, ensure_ascii=False)

    def load_model_from_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.model.set_data(data)
            self.view.populate_from_model(self.model)
    
    def reset_model(self):
        self.model = Model()
        self.view.populate_from_model(self.model)