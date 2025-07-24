from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox
)
from PyQt5.QtCore import Qt

from core import Category

class MatchDurView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.model = None
        self.group_fields = {}

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
    
    def populate_from_model(self, model):
        self.model = model
        self.group_fields.clear()

        # Cleanup: Delete Widgets and Layouts
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

        # Decide Groupings
        group_ids = sorted(set(cat.group for cat in model.categories))
        
        for group_id in group_ids:
            cat_names = [cat.name for cat in model.get_categories() if int(cat.group) == group_id]
            description = f"Group {group_id}: " + ", ".join(cat_names)

            row_layout = QHBoxLayout()

            label = QLabel(description)
            label.setMinimumWidth(400)
            row_layout.addWidget(label)

            spinbox = QSpinBox()
            spinbox.setMinimum(1)
            spinbox.setMaximum(999)
            # Get duration from model
            group_id_str = str(group_id)
            saved_value = model.get_match_durs().get(group_id_str, 15)
            spinbox.setValue(saved_value)
            self.group_fields[group_id] = spinbox

            row_layout.addWidget(spinbox)
            row_layout.addStretch()

            self.layout.addLayout(row_layout)
    
    def collect_input_fields(self):
        return {str(group_id): self.group_fields[group_id].value() for group_id in self.group_fields}
