from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, QComboBox,
    QSpinBox, QLineEdit, QPushButton, QScrollArea, QHBoxLayout
)
from PyQt5.QtCore import Qt
from functools import partial


class EventsView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.group_event_fields = {}
        self.group_boxes = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        self.scroll_widget = QWidget()
        self.groups_layout = QVBoxLayout()
        self.groups_layout.setAlignment(Qt.AlignTop)
        self.scroll_widget.setLayout(self.groups_layout)
        self.scroll_area.setWidget(self.scroll_widget)

    # Update groups and their boxes from the model, but preserve data.
    def update_fields(self):
        categories_data = self.controller.model.get_categories()
        days_data = self.controller.model.get_days()
        saved_events = self.controller.model.get_events()

        group_map = {}
        for cat in categories_data.values():
            group_id = cat.get("group", "1")
            group_map.setdefault(group_id, []).append(cat["name"])

        current_groups = set(self.group_event_fields.keys())
        new_groups = set(group_map.keys())

        # Remove groups that no longer exist
        for obsolete in current_groups - new_groups:
            box = self.group_boxes.get(obsolete)
            if box:
                self.groups_layout.removeWidget(box)
                box.setParent(None)
            self.group_event_fields.pop(obsolete, None)
            self.group_boxes.pop(obsolete, None)

        # Add or update group boxes
        for group_id in sorted(group_map.keys(), key=lambda x: int(x) if x.isdigit() else 9999):
            category_names = group_map[group_id]
            group_title = f"Group {group_id}: {', '.join(category_names)}" if group_id != "None" else "Invalid Group (please assign)"
            if group_id not in self.group_boxes:
                box = QGroupBox(group_title)
                vbox = QVBoxLayout()
                vbox.setAlignment(Qt.AlignTop)
                box.setLayout(vbox)
                self.group_event_fields[group_id] = []
                self.group_boxes[group_id] = box

                add_button = QPushButton("Add Event")
                add_button.clicked.connect(partial(self.add_event_row, group_id))
                vbox.addWidget(add_button)

                self.groups_layout.addWidget(box)
            else:
                self.group_boxes[group_id].setTitle(group_title)

            # Clear old rows
            for row in self.group_event_fields[group_id]:
                row.setParent(None)
            self.group_event_fields[group_id] = []

            # Re-add from saved model
            for event in saved_events.get(group_id, []):
                self.add_event_row(group_id, prefill=event)

        # Handle invalid groupings ("None")
        if "None" in saved_events:
            title = "Invalid group (please assign)"
            if "None" not in self.group_boxes:
                box = QGroupBox(title)
                vbox = QVBoxLayout()
                vbox.setAlignment(Qt.AlignTop)
                box.setLayout(vbox)
                self.group_event_fields["None"] = []
                self.group_boxes["None"] = box

                add_button = QPushButton("Add Event")
                add_button.clicked.connect(partial(self.add_event_row, "None"))
                vbox.addWidget(add_button)
                self.groups_layout.addWidget(box)

            for row in self.group_event_fields["None"]:
                row.setParent(None)
            self.group_event_fields["None"] = []

            for event in saved_events["None"]:
                self.add_event_row("None", prefill=event)

    def add_event_row(self, group_id, prefill=None):
        box = self.group_boxes[group_id]
        vbox = box.layout()
        add_button = vbox.itemAt(vbox.count() - 1).widget()

        num_days = len(self.controller.model.get_days())

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        # Day selection
        day_combo = QComboBox()
        day_combo.addItem("All Days")

        valid_days = [f"Day {i + 1}" for i in range(num_days)]
        for day in valid_days:
            day_combo.addItem(day)

        if prefill:
            day = prefill.get("day", "All Days")
            if day not in [day_combo.itemText(i) for i in range(day_combo.count())]:
                day_combo.addItem("None")  # Add if invalid
                day_combo.setCurrentText("None")
            else:
                day_combo.setCurrentText(day)

        # Timing
        timing_combo = QComboBox()
        timing_combo.addItems(["Before", "During", "After"])
        if prefill:
            timing_combo.setCurrentText(prefill.get("timing", "Before"))

        # Game offset
        game_offset_spin = QSpinBox()
        game_offset_spin.setRange(1, 100)
        game_offset_spin.setFixedWidth(60)
        if prefill and prefill.get("timing") == "During":
            game_offset_spin.setValue(prefill.get("game_offset", 1))
        else:
            game_offset_spin.setValue(1)

        def update_game_offset_visibility():
            game_offset_spin.setVisible(timing_combo.currentText() == "During")

        timing_combo.currentIndexChanged.connect(update_game_offset_visibility)
        update_game_offset_visibility()

        # Duration
        duration_spin = QSpinBox()
        duration_spin.setRange(1, 240)
        duration_spin.setValue(prefill.get("duration", 10) if prefill else 10)
        duration_spin.setFixedWidth(60)

        # Description
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Event name or description")
        if prefill:
            name_edit.setText(prefill.get("description", ""))

        # Delete
        delete_button = QPushButton("Delete")
        delete_button.setFixedWidth(60)

        def delete_this():
            vbox.removeWidget(row_widget)
            row_widget.setParent(None)
            self.group_event_fields[group_id].remove(row_widget)

        delete_button.clicked.connect(delete_this)

        # Add widgets
        row_layout.addWidget(QLabel("Day:"))
        row_layout.addWidget(day_combo)
        row_layout.addWidget(QLabel("When:"))
        row_layout.addWidget(timing_combo)
        row_layout.addWidget(QLabel("After N Games:"))
        row_layout.addWidget(game_offset_spin)
        row_layout.addWidget(QLabel("Duration:"))
        row_layout.addWidget(duration_spin)
        row_layout.addWidget(name_edit)
        row_layout.addWidget(delete_button)

        # Add to layout
        vbox.insertWidget(vbox.count() - 1, row_widget)
        self.group_event_fields[group_id].append(row_widget)

    def collect_input_fields(self):
        result = {}
        for group_id, rows in self.group_event_fields.items():
            group_events = []
            for row in rows:
                layout = row.layout()
                if not layout:
                    continue
                day = layout.itemAt(1).widget().currentText()
                timing = layout.itemAt(3).widget().currentText()
                game_offset = layout.itemAt(5).widget().value()
                duration = layout.itemAt(7).widget().value()
                description = layout.itemAt(8).widget().text()

                event_data = {
                    "day": day,
                    "timing": timing,
                    "duration": duration,
                    "description": description
                }
                if timing == "During":
                    event_data["game_offset"] = game_offset
                group_events.append(event_data)
            result[group_id] = group_events
        return result

    def populate_from_model(self, model):
        self.update_fields()
