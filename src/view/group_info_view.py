from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox
)
from PyQt5.QtCore import Qt

class GroupInfoView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.group_fields = {}  # group_id -> {"match_dur": QSpinBox, "num_fields": QSpinBox}

        self.layout = QVBoxLayout()
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
            label = QLabel(description)
            label.setMinimumWidth(300)
            row_layout.addWidget(label)

            # Match Duration
            spin_match = QSpinBox()
            spin_match.setMinimum(1)
            spin_match.setMaximum(999)
            spin_match.setValue(group_info.get(group_id_str, {}).get("match_dur", 1))
            row_layout.addWidget(QLabel("Match Duration:"))
            row_layout.addWidget(spin_match)

            # Number of Fields
            spin_fields = QSpinBox()
            spin_fields.setMinimum(1)
            spin_fields.setMaximum(2)
            spin_fields.setValue(group_info.get(group_id_str, {}).get("num_fields", 1))
            row_layout.addWidget(QLabel("Fields:"))
            row_layout.addWidget(spin_fields)

            self.group_fields[group_id] = {"match_dur": spin_match, "num_fields": spin_fields}
            row_layout.addStretch()
            self.layout.addLayout(row_layout)

    def collect_input_fields(self):
        group_info = {}
        for group_id, widgets in self.group_fields.items():
            group_info[str(group_id)] = {
                "match_dur": widgets["match_dur"].value(),
                "num_fields": widgets["num_fields"].value()
            }
        return group_info