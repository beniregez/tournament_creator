from PyQt5.QtWidgets import QMainWindow, QTabWidget
from view.categories_view import CategoriesView
from view.days_view import DaysView
from view.home_view import HomeView

class MainView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Tournament Creator")
        self.setGeometry(100, 100, 1200, 800)

        tabs = QTabWidget()
        self.overview_tab = HomeView(controller)
        self.categories_tab = CategoriesView(controller)
        self.days_tab = DaysView(controller)
        tabs.addTab(self.overview_tab, "Home")
        tabs.addTab(self.categories_tab, "Categories")
        tabs.addTab(self.days_tab, "Days")

        self.setCentralWidget(tabs)

    def collect_all_inputs(self):
        return {
            "days": self.days_tab.collect_input_fields(),
            "categories": self.categories_tab.collect_input_fields()
        }

    def populate_from_model(self, model):
        self.days_tab.populate_from_model(model)
        self.categories_tab.populate_from_model(model)