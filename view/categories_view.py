from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QGroupBox, QScrollArea, QLabel,
    QComboBox, QFormLayout, QLineEdit, QPushButton, QColorDialog, QDialog, QDialogButtonBox
)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

class CategoriesView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        # Main vertical layout for the entire view
        main_layout = QVBoxLayout(self)

        # SpinBox to set the number of categories
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 20)
        self.count_spin.setValue(1)
        self.count_spin.valueChanged.connect(self.update_fields)
        main_layout.addWidget(QLabel("Number of categories:"))
        main_layout.addWidget(self.count_spin)

        # Scroll area to hold category boxes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        # Inner widget to contain all categories in horizontal layout
        self.scroll_widget = QWidget()
        self.categories_layout = QHBoxLayout(self.scroll_widget)
        self.scroll_widget.setLayout(self.categories_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        # List to keep track of all category input fields
        self.category_fields = []

        # Initialize fields for default value
        self.update_fields()

    # Adds or removes team input rows inside a category, depending on team_spin's value.
    def update_teams(self, team_spin, team_fields_layout):
        current_count = team_fields_layout.count()
        target_count = team_spin.value()

        # Add missing team fields
        for t in range(current_count, target_count):
            # Horizontal layout for one team row
            team_row = QHBoxLayout()
            team_row.setContentsMargins(0, 0, 0, 0)
            team_row.setSpacing(8)

            # Team name input
            team_name = QLineEdit()
            team_name.setFixedWidth(300)
            team_name.setFixedHeight(24)
            team_name.setPlaceholderText(f"Team {t + 1}")

            # Button to pick color
            color_button = QPushButton("Color")
            color_button.setFixedWidth(100)
            color_button.setFixedHeight(24)

            # Closure to open color dialog and set background color
            def make_color_picker(name_field=team_name):
                def pick_color():
                    color = QColorDialog.getColor(parent=self)
                    if color.isValid():
                        pal = name_field.palette()
                        pal.setColor(QPalette.Base, color)
                        name_field.setPalette(pal)
                return pick_color

            color_button.clicked.connect(make_color_picker())

            team_row.addWidget(team_name)
            team_row.addWidget(color_button)

            # Wrap team_row in QWidget
            row_container = QWidget()
            row_container.setLayout(team_row)
            team_fields_layout.addWidget(row_container)

        # Remove excess team fields
        while team_fields_layout.count() > target_count:
            item = team_fields_layout.takeAt(team_fields_layout.count() - 1)
            if item.widget():
                item.widget().deleteLater()

    def update_fields(self):
        # Synchronizes the number of category input groups with the SpinBox value.
        current_count = len(self.category_fields)
        target_count = self.count_spin.value()

        # Add missing category blocks
        if target_count > current_count:
            for i in range(current_count, target_count):
                category_box = QGroupBox(f"Category {i + 1}")
                category_box.setFixedWidth(500)

                outer_layout = QVBoxLayout(category_box)

                # Scrollable form for each category
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

                scroll_content = QWidget()
                form_layout = QFormLayout(scroll_content)

                # Category-level inputs
                name_edit = QLineEdit()
                group_combo = QComboBox()
                for g in range(1, 21):
                    group_combo.addItem(str(g))

                runs_spin = QSpinBox()
                runs_spin.setRange(1, 100)

                duration_spin = QSpinBox()
                duration_spin.setRange(1, 240)

                # Team count and layout
                team_spin = QSpinBox()
                team_spin.setRange(1, 30)
                team_fields_layout = QVBoxLayout()
                team_fields_layout.setSpacing(8)

                # Connect team count to team fields updater
                team_spin.valueChanged.connect(lambda _, ts=team_spin, tf=team_fields_layout: self.update_teams(ts, tf))
                self.update_teams(team_spin, team_fields_layout)

                # Assemble form layout
                form_layout.addRow("Name:", name_edit)
                form_layout.addRow("Grouping:", group_combo)
                form_layout.addRow("Runs:", runs_spin)
                form_layout.addRow("Play time (incl. rotation):", duration_spin)
                form_layout.addRow("Number of teams:", team_spin)
                form_layout.addRow(team_fields_layout)

                scroll_area.setWidget(scroll_content)
                outer_layout.addWidget(scroll_area)
                self.categories_layout.addWidget(category_box)

                # Save field references for later access
                self.category_fields.append((name_edit, group_combo, runs_spin, duration_spin, team_spin, team_fields_layout))

        # Remove excess category blocks
        elif target_count < current_count:
            for _ in range(current_count - target_count):
                self.category_fields.pop()
                widget = self.categories_layout.takeAt(self.categories_layout.count() - 1).widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

    # Collects current user input from the form into a structured data dictionary.
    def collect_input_fields(self):
        data = {}
        for idx, (name_edit, group_combo, runs_spin, duration_spin, team_spin, team_layout) in enumerate(self.category_fields):
            teams = []
            for i in range(team_layout.count()):
                row = team_layout.itemAt(i).widget()
                if row:
                    name_field = row.layout().itemAt(0).widget()
                    name = name_field.text()
                    color = name_field.palette().color(QPalette.Base).name()
                    teams.append((name, color))

            cat_name = name_edit.text().strip() or f"category{idx}"
            data[idx] = {
                "name": cat_name,
                "group": group_combo.currentText(),
                "runs": runs_spin.value(),
                "duration": duration_spin.value(),
                "teams": teams
            }
        return data

    # Populates the form based on saved data from the model.
    def populate_from_model(self, model):
        categories_data = model.get_categories()

        self.count_spin.blockSignals(True)
        self.count_spin.setValue(len(categories_data))
        self.count_spin.blockSignals(False)
        self.update_fields()

        for idx_str, data in categories_data.items():
            idx = int(idx_str)
            if idx < len(self.category_fields):
                name_edit, group_combo, runs_spin, duration_spin, team_spin, team_layout = self.category_fields[idx]

                name_edit.setText(data.get("name", f"category{idx + 1}"))
                group = data.get("group", "1")
                group_index = group_combo.findText(group)
                if group_index != -1:
                    group_combo.setCurrentIndex(group_index)
                runs_spin.setValue(data.get("runs", 1))
                duration_spin.setValue(data.get("duration", 1))

                teams = data.get("teams", [])
                team_spin.blockSignals(True)
                team_spin.setValue(len(teams))
                team_spin.blockSignals(False)
                self.update_teams(team_spin, team_layout)

                for t_index, (team_name, color_hex) in enumerate(teams):
                    if t_index < team_layout.count():
                        team_row = team_layout.itemAt(t_index).widget()
                        if team_row:
                            name_field = team_row.layout().itemAt(0).widget()
                            name_field.setText(team_name)
                            color = QColor(color_hex)
                            pal = name_field.palette()
                            pal.setColor(QPalette.Base, color)
                            name_field.setPalette(pal)

# Dialog window to choose a color.
class ColorPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose a color")
        self.selected_color = QColor("#FFFFFF")

        self.layout = QVBoxLayout(self)

        self.color_dialog = QColorDialog(self)
        self.color_dialog.setOptions(QColorDialog.ShowAlphaChannel | QColorDialog.DontUseNativeDialog)
        self.color_dialog.setCurrentColor(self.selected_color)

        self.layout.addWidget(self.color_dialog)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    # Returns the selected color if OK is pressed, else None.
    def get_color(self):
        if self.exec_() == QDialog.Accepted:
            self.selected_color = self.color_dialog.currentColor()
            return self.selected_color
        return None
