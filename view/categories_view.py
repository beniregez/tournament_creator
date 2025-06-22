from PyQt5.QtWidgets import QWidget

class CategoriesView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        # TODO
        pass

    def collect_input_fields(self):
        # TODO Read all input fields.
        return {}

    def populate_from_model(self, model):
        # TODO Load data from the model and fill GUI fields.
        pass