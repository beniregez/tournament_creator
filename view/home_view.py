from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog

class HomeView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout()

        self.save_btn = QPushButton("Save as JSON")
        self.save_btn.clicked.connect(self.save_to_file)
        layout.addWidget(self.save_btn)

        self.load_btn = QPushButton("Load from JSON")
        self.load_btn.clicked.connect(self.load_from_file)
        layout.addWidget(self.load_btn)

        self.setLayout(layout)

    def save_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save file", "", "JSON Files (*.json)")
        if filename:
            self.controller.save_model_to_json(filename)

    def load_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load file", "", "JSON Files (*.json)")
        if filename:
            self.controller.load_model_from_json(filename)
