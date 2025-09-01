import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QLabel, QSpacerItem, QSpinBox,
    QSizePolicy, QCheckBox, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

from view.status_label import StatusLabel

class HomeView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.current_file_path = None

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

        # Checkbox: Decide whether identical category days shall be prevented or not.
        self.identical_checkbox = QCheckBox("Prevent identical match order for a category on to consecutive days.")
        self.identical_checkbox.setChecked(False)
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

        button_row = QHBoxLayout()

        # Left button column (Save as JSON, Save)
        left_col = QVBoxLayout()
        self.save_btn = QPushButton("Save as JSON")
        self.save_btn.clicked.connect(self.save_to_file)
        self.save_btn.setMinimumHeight(40)
        left_col.addWidget(self.save_btn)

        self.quick_save_btn = QPushButton("Save")
        self.quick_save_btn.clicked.connect(self.quick_save)
        self.quick_save_btn.setMinimumHeight(40)
        left_col.addWidget(self.quick_save_btn)

        button_row.addLayout(left_col)

        # Small spacer between
        button_row.addSpacing(20)

        # Right button column (Load from JSON, Reset tournament)
        right_col = QVBoxLayout()
        self.load_btn = QPushButton("Load from JSON")
        self.load_btn.clicked.connect(self.load_from_file)
        self.load_btn.setMinimumHeight(40)
        right_col.addWidget(self.load_btn)

        self.reset_btn = QPushButton("Reset tournament")
        self.reset_btn.clicked.connect(self.reset_tournament)
        self.reset_btn.setMinimumHeight(40)
        right_col.addWidget(self.reset_btn)

        button_row.addLayout(right_col)

        main_layout.addLayout(button_row)

        # Status label
        self.status_label = StatusLabel()
        self.status_label.setFixedHeight(60)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def collect_input_fields(self):
        return {
            "title": self.title_input.text().strip(),
            "appendix_day_info": self.appendix_input.toPlainText().strip(),
            "shuffle": self.shuffle_checkbox.isChecked(),
            "prevent_identical_cat_days": self.identical_checkbox.isChecked(),
            "shuffle_seed": self.seed_input.text().strip() if self.shuffle_checkbox.isChecked() else ""
        }

    def populate_from_model(self, model):
        data = model.get_tournament_info()
        self.title_input.setText(data.get("title", ""))
        self.appendix_input.setPlainText(data.get("appendix_day_info", ""))
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
            self.current_file_path = filename
            short_name = os.path.basename(filename)
            self.status_label.show_message(f"✅ {short_name} saved", 4000)

    def quick_save(self):
        if self.current_file_path:
            # Save
            self.controller.save_model_to_json(self.current_file_path)
            short_name = os.path.basename(self.current_file_path)
            self.status_label.show_message(f"✅ {short_name} saved", 3000)
        else:
            # Fallback: Save as JSON
            self.save_to_file()

    def load_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load file", "", "JSON Files (*.json)")
        if filename:
            self.controller.load_model_from_json(filename)
            self.current_file_path = filename
            short_name = os.path.basename(filename)
            self.status_label.show_message(f"✅ {short_name} loaded", 4000)

    def reset_tournament(self):
        self.controller.reset_model()
        self.populate_from_model(self.controller.model)
        self.current_file_path = None
        self.status_label.show_message("🔄 Tournament reset", 4000)
