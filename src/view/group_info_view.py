from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt


class GroupInfoView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.group_fields = {}
        
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

    def populate_from_model(self, model):
        self.group_fields.clear()

        # Clear UI
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    while sub_layout.count():
                        sub_item = sub_layout.takeAt(0)
                        sub_widget = sub_item.widget()
                        if sub_widget:
                            sub_widget.deleteLater()

        # Create fields for each group
        group_ids = sorted(set(cat.group for cat in model.categories))
        group_info = model.get_group_info()

        for group_id in group_ids:
            group_id_str = str(group_id)
            cat_names = [cat.name for cat in model.get_categories() if int(cat.group) == group_id]
            description = f"Group {group_id}: " + ", ".join(cat_names)

            row_layout = QHBoxLayout()

            # --- Description Label ---
            label = QLabel(description)
            label.setMinimumWidth(250)
            row_layout.addWidget(label)

            # --- Match Duration ---
            spin_match = QSpinBox()
            spin_match.setMinimum(1)
            spin_match.setMaximum(999)
            spin_match.setValue(group_info.get(group_id_str, {}).get("match_dur", 1))
            row_layout.addWidget(QLabel("Match Duration:"))
            row_layout.addWidget(spin_match)

            # --- Number of Fields ---
            spin_fields = QSpinBox()
            spin_fields.setMinimum(1)
            spin_fields.setMaximum(2)
            spin_fields.setValue(group_info.get(group_id_str, {}).get("num_fields", 1))
            row_layout.addWidget(QLabel("Fields:"))
            row_layout.addWidget(spin_fields)

            # --- Double Missions Dropdown ---
            combo_double = QComboBox()
            combo_double.addItems(["Empty fields", "Pause", "Ignore"])
            default_value = group_info.get(group_id_str, {}).get("double_missions", "Empty fields")
            combo_double.setCurrentText(
                "Pause" if default_value == "pause" else
                "Ignore" if default_value == "ignore" else
                "Empty fields"
            )

            row_layout.addWidget(QLabel("Double missions:"))
            row_layout.addWidget(combo_double)

            # Pause Container (Label + SpinBox together in Widget) ---
            pause_container = QWidget(row_layout.parentWidget())  # Hand over Parent as well!
            pause_layout = QHBoxLayout(pause_container)
            pause_layout.setContentsMargins(0, 0, 0, 0)
            pause_layout.setSpacing(5)

            pause_label = QLabel("Pause (min):", pause_container)
            spin_pause = QSpinBox(pause_container)
            spin_pause.setMinimum(1)
            spin_pause.setMaximum(30)
            spin_pause.setValue(group_info.get(group_id_str, {}).get("pause_dur", 1))

            pause_layout.addWidget(pause_label)
            pause_layout.addWidget(spin_pause)

            pause_container.setVisible(combo_double.currentText() == "Pause")
            row_layout.addWidget(pause_container)


            # Show/Hide pause container dynamically
            combo_double.currentIndexChanged.connect(
                lambda _, cb=combo_double, pc=pause_container: pc.setVisible(cb.currentText() == "Pause")
            )

            # Save widgets
            self.group_fields[group_id] = {
                "match_dur": spin_match,
                "num_fields": spin_fields,
                "double_missions": combo_double,
                "pause_dur": spin_pause,
            }

            row_layout.addStretch()

            # Add row + spacing between groupings
            self.layout.addLayout(row_layout)
            self.layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

    def collect_input_fields(self):
        group_info = {}
        for group_id, widgets in self.group_fields.items():
            combo_value = widgets["double_missions"].currentText()
            mapped_value = (
                "empty_field" if combo_value == "Empty fields" else
                "pause" if combo_value == "Pause" else
                "ignore"
            )

            group_info[str(group_id)] = {
                "match_dur": widgets["match_dur"].value(),
                "num_fields": widgets["num_fields"].value(),
                "double_missions": mapped_value,
                "pause_dur": widgets["pause_dur"].value() if mapped_value == "pause" else 0,
            }
        return group_info
