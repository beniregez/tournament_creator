from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox,
    QSpinBox, QHeaderView, QLabel
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeySequence

class EventsView(QWidget):
    COL_HEADERS = ["Day", "When", "Index", "Name", "Time"]
    WHEN_OPTIONS = ["before", "during", "after"]
    ROW_COUNT = 8

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.model = None
        self.group_tables = {}  # group_id: table
        self.day_options = []
        self.clipboard_row = None  # For copy/paste

        self.init_ui()

    def init_ui(self):
        # Top-level layout
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.explanation_layout = QVBoxLayout()
        explanation = "How to copy and paste a row: (1) Select a row by double left click on the row index. \
        \n(2) Copy (Ctrl + C) the selected row. (3) Double click again at the target row index abd paste (Ctrl + V)."
        self.explanation_label = QLabel(explanation)
        self.explanation_label.setAlignment(Qt.AlignTop)
        self.explanation_label.setAlignment(Qt.AlignRight)
        self.explanation_layout.addWidget(self.explanation_label)
        self.main_layout.addLayout(self.explanation_layout)

        # Dynamic content area (gets cleared on populate)
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

    def populate_from_model(self, model):
        self.model = model
        self.days = model.days
        self.day_options = ["all"] + [str(i + 1) for i in range(len(self.days))]

        # Remove only dynamic widgets (group tables)
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.group_tables.clear()
        group_ids = sorted(set(int(cat["group"]) for cat in model.categories))
        event_data = getattr(model, "events", {})

        for group_id in group_ids:
            group_names = [cat["name"] for cat in model.categories if int(cat["group"]) == group_id]
            group_label_text = f"Group {group_id}: " + ", ".join(group_names)
            self.content_layout.addWidget(QLabel(group_label_text))
            table = QTableWidget()
            table.setColumnCount(len(self.COL_HEADERS))
            table.setRowCount(self.ROW_COUNT)
            table.setHorizontalHeaderLabels(self.COL_HEADERS)
            table.verticalHeader().setVisible(True)

            table.setColumnWidth(0, 100)
            table.setColumnWidth(1, 100)
            table.setColumnWidth(2, 100)
            table.setColumnWidth(3, 750)
            table.setColumnWidth(4, 100)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

            table.installEventFilter(self)

            self.group_tables[group_id] = table

            rows = event_data.get(str(group_id), [])
            for row_idx in range(self.ROW_COUNT):
                row_data = rows[row_idx] if row_idx < len(rows) else {}
                self._set_row(table, row_idx, row_data)

            for row in range(self.ROW_COUNT):
                table.setRowHeight(row, 20)

            self.content_layout.addWidget(table)

    def _set_row(self, table, row, data):
        # Day (ComboBox)
        day_combo = QComboBox()
        day_combo.addItems(self.day_options)
        if data.get("day") in self.day_options:
            day_combo.setCurrentText(data["day"])
        table.setCellWidget(row, 0, day_combo)

        # When (ComboBox)
        when_combo = QComboBox()
        when_combo.addItems(self.WHEN_OPTIONS)
        if data.get("when") in self.WHEN_OPTIONS:
            when_combo.setCurrentText(data["when"])
        table.setCellWidget(row, 1, when_combo)

        # Index (SpinBox)
        index_spin = QSpinBox()
        index_spin.setRange(0, 999)
        index_spin.setValue(int(data.get("index", 0)))
        table.setCellWidget(row, 2, index_spin)

        # Name (Text)
        name_item = QTableWidgetItem(data.get("name", ""))
        table.setItem(row, 3, name_item)

        # Time (SpinBox)
        time_spin = QSpinBox()
        time_spin.setRange(0, 999)
        time_spin.setValue(int(data.get("time", 0)))
        table.setCellWidget(row, 4, time_spin)

    def collect_input_fields(self):
        events = {}
        for group_id, table in self.group_tables.items():
            group_events = []
            for row in range(table.rowCount()):
                name_item = table.item(row, 3)
                name = name_item.text().strip() if name_item else ""
                if not name:
                    continue

                day = table.cellWidget(row, 0).currentText()
                when = table.cellWidget(row, 1).currentText()
                index = table.cellWidget(row, 2).value()
                time = table.cellWidget(row, 4).value()

                group_events.append({
                    "day": day,
                    "when": when,
                    "index": index,
                    "name": name,
                    "time": time
                })
            events[str(group_id)] = group_events
        return events

    def eventFilter(self, source, event):
        if isinstance(source, QTableWidget):
            if event.type() == QEvent.KeyPress:
                selected_rows = {idx.row() for idx in source.selectedIndexes()}

                if event.matches(QKeySequence.Copy):
                    if len(selected_rows) == 1:
                        row = selected_rows.pop()
                        self.clipboard_row = self._copy_row(source, row)
                    return True

                elif event.matches(QKeySequence.Paste):
                    if self.clipboard_row and len(selected_rows) == 1:
                        target_row = selected_rows.pop()
                        self._paste_row(source, target_row, self.clipboard_row)
                    return True

                elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                    for row in selected_rows:
                        self._clear_row(source, row)
                    return True

        return super().eventFilter(source, event)

    def _copy_row(self, table, row):
        return {
            "day": table.cellWidget(row, 0).currentText(),
            "when": table.cellWidget(row, 1).currentText(),
            "index": table.cellWidget(row, 2).value(),
            "name": table.item(row, 3).text() if table.item(row, 3) else "",
            "time": table.cellWidget(row, 4).value()
        }

    def _paste_row(self, table, row, data):
        table.cellWidget(row, 0).setCurrentText(data["day"])
        table.cellWidget(row, 1).setCurrentText(data["when"])
        table.cellWidget(row, 2).setValue(data["index"])
        table.setItem(row, 3, QTableWidgetItem(data["name"]))
        table.cellWidget(row, 4).setValue(data["time"])

    def _clear_row(self, table, row):
        table.cellWidget(row, 0).setCurrentText("all")
        table.cellWidget(row, 1).setCurrentText("before")
        table.cellWidget(row, 2).setValue(0)
        table.setItem(row, 3, QTableWidgetItem(""))
        table.cellWidget(row, 4).setValue(0)
