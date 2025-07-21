from PyQt5.QtWidgets import QMainWindow, QTabWidget
from view.categories_view import CategoriesView
from view.days_view import DaysView
from view.home_view import HomeView
from view.events_view import EventsView
from view.match_dur_view import MatchDurView

class MainView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Tournament Creator")
        self.setGeometry(100, 100, 1500, 1000)

        self.tabs = QTabWidget()
        self.home_tab = HomeView(controller)
        self.categories_tab = CategoriesView(controller)
        self.match_dur_tab = MatchDurView(controller)
        self.days_tab = DaysView(controller)
        self.events_tab = EventsView(controller)
        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.categories_tab, "Categories")
        self.tabs.addTab(self.match_dur_tab, "Match Durations")
        self.tabs.addTab(self.days_tab, "Days")
        self.tabs.addTab(self.events_tab, "Events")
        
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
            self.controller.update_events_from_view()

        # When leaving the Categories tab: Check consistency
        if prev_index == self.tabs.indexOf(self.categories_tab):
            self.controller.update_categories_from_view()
            self.controller.validate_grouping_durs_against_categories()

        # When leaving the Days Tab
        if prev_index == self.tabs.indexOf(self.days_tab):
            self.controller.update_days_from_view()

        # When leaving the MatchDuration Tab
        if prev_index == self.tabs.indexOf(self.match_dur_tab):
            self.controller.update_match_durs_from_view()
        
        # When entering the MatchDuration Tab
        if index == self.tabs.indexOf(self.match_dur_tab):
            self.match_dur_tab.populate_from_model(self.controller.model)

        # When entering the Events tab: Show fields
        if index == self.tabs.indexOf(self.events_tab):
            self.events_tab.populate_from_model(self.controller.model)
            
    def collect_all_inputs(self):
        return {
            "title": self.home_tab.collect_input_fields(),
            "days": self.days_tab.collect_input_fields(),
            "categories": self.categories_tab.collect_input_fields(),
            "match_durs": self.match_dur_tab.collect_input_fields(),
            "events": self.events_tab.collect_input_fields()
        }

    def populate_from_model(self, model):
        self.home_tab.populate_from_model(model)
        self.days_tab.populate_from_model(model)
        self.categories_tab.populate_from_model(model)
        self.match_dur_tab.populate_from_model(model)
        self.events_tab.populate_from_model(model)