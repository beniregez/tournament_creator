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

        self.tabs = QTabWidget()
        self.overview_tab = HomeView(controller)
        self.categories_tab = CategoriesView(controller)
        self.days_tab = DaysView(controller)
        self.tabs.addTab(self.overview_tab, "Home")
        self.tabs.addTab(self.categories_tab, "Categories")
        self.tabs.addTab(self.days_tab, "Days")
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.setCentralWidget(self.tabs)

    def on_tab_changed(self, index):
        # Automatically update the model whenever user changes tab
        self.controller.update_model_from_views()

    def collect_all_inputs(self):
        return {
            "days": self.days_tab.collect_input_fields(),
            "categories": self.categories_tab.collect_input_fields()
        }

    def populate_from_model(self, model):
        self.days_tab.populate_from_model(model)
        self.categories_tab.populate_from_model(model)