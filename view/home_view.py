from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QLabel, QSpacerItem
)
from PyQt5.QtCore import Qt

class HomeView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter title...")
        main_layout.addWidget(QLabel("Title of the tournament"))
        main_layout.addWidget(self.title_input)
        main_layout.addSpacing(10)

        # Buttons in a horizontal layout
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save as JSON")
        self.save_btn.clicked.connect(self.save_to_file)
        button_layout.addWidget(self.save_btn)

        self.load_btn = QPushButton("Load from JSON")
        self.load_btn.clicked.connect(self.load_from_file)
        button_layout.addWidget(self.load_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def save_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save file", "", "JSON Files (*.json)")
        if filename:
            self.controller.save_model_to_json(filename)

    def load_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load file", "", "JSON Files (*.json)")
        if filename:
            self.controller.load_model_from_json(filename)

    def collect_input_fields(self):
        return self.title_input.text().strip()

    def populate_from_model(self, model):
        title = model.get_title()
        self.title_input.setText(title)
