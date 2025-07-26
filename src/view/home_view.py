from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QLabel, QSpacerItem, QSpinBox,
    QSizePolicy
)
from PyQt5.QtCore import Qt

class HomeView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Title input
        title_row = QHBoxLayout()
        title_label = QLabel("Title of the tournament:")
        title_row.addWidget(title_label)

        # Input field
        self.title_input = QLineEdit()
        self.title_input.editingFinished.connect(self.update_model)
        self.title_input.setPlaceholderText("Enter title...")
        self.title_input.setMinimumHeight(40)
        self.title_input.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        title_row.addWidget(self.title_input)

        main_layout.addLayout(title_row)
        main_layout.addSpacing(25)

        # Save and Load Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save as JSON")
        self.save_btn.clicked.connect(self.save_to_file)
        self.save_btn.setMinimumHeight(40)
        button_layout.addWidget(self.save_btn)

        self.load_btn = QPushButton("Load from JSON")
        self.load_btn.clicked.connect(self.load_from_file)
        self.load_btn.setMinimumHeight(40)
        button_layout.addWidget(self.load_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def collect_input_fields(self):
        return {
            "title": self.title_input.text().strip(),
        }

    def populate_from_model(self, model):
        data = model.get_tournament_info()
        self.title_input.setText(data.get("title", ""))

    def update_model(self):
        self.controller.model.set_tournament_info(self.collect_input_fields())

    def save_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save file", "", "JSON Files (*.json)")
        if filename:
            self.controller.save_model_to_json(filename)

    def load_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load file", "", "JSON Files (*.json)")
        if filename:
            self.controller.load_model_from_json(filename)
