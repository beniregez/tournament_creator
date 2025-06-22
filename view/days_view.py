from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QSpinBox, QTimeEdit, QDateEdit, QPushButton,
    QGroupBox, QFormLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import QDate, Qt, QTime

class DaysView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel("Choose number of tournament days:"))

        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 20)
        self.count_spin.setValue(1)
        self.count_spin.valueChanged.connect(self.update_fields)
        main_layout.addWidget(self.count_spin)

        # ScrollArea for the input fields
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        # Central Widget in ScrollArea
        self.scroll_widget = QWidget()
        self.fields_layout = QVBoxLayout()
        self.fields_layout.setContentsMargins(10, 10, 10, 10)
        self.fields_layout.setSpacing(12)
        self.scroll_widget.setLayout(self.fields_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.day_fields = []
        self.update_fields()

    def update_fields(self):
        current_count = len(self.day_fields)
        target_count = self.count_spin.value()

        # Additional days wished: Append new fields
        if target_count > current_count:
            for i in range(current_count, target_count):
                group = QGroupBox(f"day {i + 1}")
                form = QFormLayout()

                title = QLineEdit()
                date = QDateEdit()
                date.setDisplayFormat("dd.MM.yyyy")

                location = QLineEdit()
                responsible = QLineEdit()
                start_time = QTimeEdit()
                start_time.setDisplayFormat("HH:mm")

                form.addRow("Title:", title)
                form.addRow("Date:", date)
                form.addRow("Location:", location)
                form.addRow("Responsible:", responsible)
                form.addRow("Start time:", start_time)

                group.setLayout(form)
                self.fields_layout.addWidget(group)

                self.day_fields.append((title, date, location, responsible, start_time))

        # Less days wished: Remove last fields
        elif target_count < current_count:
            for _ in range(current_count - target_count):
                fields = self.day_fields.pop()
                widget = self.fields_layout.takeAt(self.fields_layout.count() - 1).widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

    # Read all input fields.
    def collect_input_fields(self):
        result = []
        for fields in self.day_fields:
            title, date, location, responsible, start_time = fields
            result.append({
                "Title": title.text(),
                "Date": date.date().toString("dd.MM.yyyy"),
                "Location": location.text(),
                "Responsible": responsible.text(),
                "Start time": start_time.time().toString("HH:mm")
            })
        return result

    # Load data from the model and fill GUI fields.
    def populate_from_model(self, model):
        data = model.get_days()
        self.count_spin.setValue(len(data))
        self.update_fields()

        for i, tag in enumerate(data):
            title, date, location, responsible, start_time = self.day_fields[i]
            title.setText(tag.get("Title", ""))
            date.setDate(QDate.fromString(tag.get("Date", ""), "dd.MM.yyyy"))
            location.setText(tag.get("Location", ""))
            responsible.setText(tag.get("Responsible", ""))
            start_time.setTime(QTime.fromString(tag.get("Start time", ""), "HH:mm"))