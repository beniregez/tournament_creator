import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QLabel, QSpacerItem, QSpinBox,
    QSizePolicy, QCheckBox, QTextEdit
)
from PyQt5.QtCore import Qt

from view.status_label import StatusLabel

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

        # Title input field
        self.title_input = QLineEdit()
        self.title_input.editingFinished.connect(self.update_model)
        self.title_input.setPlaceholderText("Enter title...")
        self.title_input.setMinimumHeight(40)
        self.title_input.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        title_row.addWidget(self.title_input)

        main_layout.addLayout(title_row)
        main_layout.addSpacing(25)

        # Info on Tournament day sheets
        appendix_label = QLabel("Info on Tournament day sheets:")
        main_layout.addWidget(appendix_label)

        self.appendix_input = QTextEdit()
        self.appendix_input.setPlaceholderText("Enter additional info for day sheets...")
        self.appendix_input.setMinimumHeight(100)
        self.appendix_input.textChanged.connect(self.update_model)
        main_layout.addWidget(self.appendix_input)

        main_layout.addSpacing(25)

        # Checkbox: Decide whether referee cards shall be generated when exporting.
        self.ref_checkbox = QCheckBox("Generate referee cards when exporting")
        self.ref_checkbox.setChecked(True)  # Default: Generate referee cards.
        self.ref_checkbox.stateChanged.connect(self.update_model)
        main_layout.addWidget(self.ref_checkbox)
        main_layout.addSpacing(25)

        # Checkbox: Decide whether identical category days shall be prevented or not.
        self.identical_checkbox = QCheckBox("Prevent identical match order for a category on to consecutive days.")
        self.identical_checkbox.setChecked(False)  # Default
        self.identical_checkbox.stateChanged.connect(self.update_model)
        main_layout.addWidget(self.identical_checkbox)
        main_layout.addSpacing(25)

         # Checkbox: Seed to shuffle teams
        shuffle_row = QHBoxLayout()
        self.shuffle_checkbox = QCheckBox("Set seed to shuffle teams")
        self.shuffle_checkbox.stateChanged.connect(self.toggle_seed_input)
        shuffle_row.addWidget(self.shuffle_checkbox)

        self.seed_input = QLineEdit()
        self.seed_input.setPlaceholderText("Enter seed...")
        self.seed_input.setMinimumHeight(30)
        self.seed_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.seed_input.setVisible(False)
        self.seed_input.textChanged.connect(self.update_model)
        shuffle_row.addWidget(self.seed_input)
        main_layout.addLayout(shuffle_row)
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

        # Status label to show messages
        self.status_label = StatusLabel()
        self.status_label.setFixedHeight(60)
        main_layout.addWidget(self.status_label)

    def collect_input_fields(self):
        return {
            "title": self.title_input.text().strip(),
            "appendix_day_info": self.appendix_input.toPlainText().strip(),
            "gen_ref_cards": True if self.ref_checkbox.isChecked() else False,
            "shuffle": self.shuffle_checkbox.isChecked(),
            "prevent_identical_cat_days": True if self.identical_checkbox.isChecked() else False,
            "shuffle_seed": self.seed_input.text().strip() if self.shuffle_checkbox.isChecked() else ""
        }

    def populate_from_model(self, model):
        data = model.get_tournament_info()
        self.title_input.setText(data.get("title", ""))
        self.appendix_input.setPlainText(data.get("appendix_day_info", ""))
        self.ref_checkbox.setChecked(data.get("gen_ref_cards", True))
        self.identical_checkbox.setChecked(data.get("prevent_identical_cat_days", False))
        self.shuffle_checkbox.setChecked(data.get("shuffle", False))
        self.seed_input.setText(data.get("shuffle_seed", ""))
        self.toggle_seed_input()

    def update_model(self):
        self.controller.model.set_tournament_info(self.collect_input_fields())

    def toggle_seed_input(self):
        visible = self.shuffle_checkbox.isChecked()
        self.seed_input.setVisible(visible)
        if not visible:
            self.seed_input.clear()

    def save_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save file", "", "JSON Files (*.json)")
        if filename:
            self.controller.save_model_to_json(filename)
            short_name = os.path.basename(filename)
            self.status_label.show_message(f"✅ {short_name} saved", 4000)

    def load_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load file", "", "JSON Files (*.json)")
        if filename:
            self.controller.load_model_from_json(filename)
            short_name = os.path.basename(filename)
            self.status_label.show_message(f"✅ {short_name} loaded", 4000)