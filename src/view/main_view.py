from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PyQt5.QtCore import QTimer
from view.categories_view import CategoriesView
from view.days_view import DaysView
from view.home_view import HomeView
from view.events_view import EventsView
from view.group_info_view import GroupInfoView
from view.overview_view import OverviewView
from view.create_tourn_view import CreateTourn

class MainView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Tournament Creator")
        self.setGeometry(100, 100, 1500, 1000)

        self.tabs = QTabWidget()
        self.home_tab = HomeView(controller)
        self.categories_tab = CategoriesView(controller)
        self.group_info_tab = GroupInfoView(controller)
        self.days_tab = DaysView(controller)
        self.events_tab = EventsView(controller)
        self.overview_tab = OverviewView(controller)
        self.create_tourn_tab = CreateTourn(controller)
        self.tabs.addTab(self.home_tab, "Start")
        self.tabs.addTab(self.categories_tab, "Categories")
        self.tabs.addTab(self.group_info_tab, "Group Infos")
        self.tabs.addTab(self.days_tab, "Days")
        self.tabs.addTab(self.events_tab, "Events")
        self.tabs.addTab(self.overview_tab, "Overview")
        self.tabs.addTab(self.create_tourn_tab, "Create")
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.setCentralWidget(self.tabs)

    def on_tab_changed(self, index):        
        prev_index = getattr(self, "_prev_tab_index", None)
        self._prev_tab_index = index

        # Before leaving the Home tab: Save to model
        if prev_index == self.tabs.indexOf(self.home_tab):
            self.controller.update_home_from_view()

        # Before leaving the Events tab: Save events!
        if prev_index == self.tabs.indexOf(self.events_tab):
            self.controller.update_other_events_from_view()

        # When leaving the Categories tab
        if prev_index == self.tabs.indexOf(self.categories_tab):
            self.controller.update_categories_from_view()
            # self.controller.validate_grouping_durs_against_categories()
            duplicates = self.controller.model.get_duplicate_team_names()
            # Prevent tab to change if there are duplicate team names
            if duplicates:
                QMessageBox.warning(
                    self,
                    "Duplicate Team Names",
                    f"The following team names are duplicated:\n\n" + "\n".join(duplicates)
                )
                # Undo tab change
                self.tabs.setCurrentIndex(prev_index)
                return

        # When leaving the Days Tab
        if prev_index == self.tabs.indexOf(self.days_tab):
            self.controller.update_days_from_view()
            duplicates = self.controller.model.get_duplicate_day_titles()
            # Prevent tab to change if there are duplicate day titles
            if duplicates:
                QMessageBox.warning(
                    self,
                    "Duplicate Day Titles",
                    f"The following day titles are duplicated:\n\n" + "\n".join(duplicates)
                )
                # Undo tab change
                self.tabs.setCurrentIndex(prev_index)
                return

        # When entering the GroupInfo Tag
        if index == self.tabs.indexOf(self.group_info_tab):
            if self.controller.model.get_groupings_changed():
                self.group_info_tab.populate_from_model(self.controller.model)
                self.controller.model.set_groupings_changed(False)

        # When leaving the GroupInfo Tab
        if prev_index == self.tabs.indexOf(self.group_info_tab):
            self.controller.update_group_info_from_view()
        
        # When entering the Events tab: Show fields
        if index == self.tabs.indexOf(self.events_tab):
            self.events_tab.populate_from_model(self.controller.model)
        
        # When entering the Overview tab: update from model
        if index == self.tabs.indexOf(self.overview_tab):
            self.overview_tab.update_ui()

    def collect_all_inputs(self):
        return {
            "title": self.home_tab.collect_input_fields(),
            "days": self.days_tab.collect_input_fields(),
            "categories": self.categories_tab.collect_input_fields(),
            "group_info": self.group_info_tab.collect_input_fields(),
            "events": self.events_tab.collect_input_fields()
        }

    def populate_from_model(self, model):
        self.home_tab.populate_from_model(model)
        self.categories_tab.populate_from_model(model)
        self.group_info_tab.populate_from_model(model)
        self.days_tab.populate_from_model(model)
        self.events_tab.populate_from_model(model)