from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox,
    QSpinBox, QHeaderView, QLabel
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeySequence

from core import OtherEvent

class EventsView(QWidget):
    COL_HEADERS = ["Day", "When", "Index", "Label", "Duration"]
    WHEN_OPTIONS = ["before", "during", "after"]
    ROW_COUNT = 8

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.model = None
        self.group_tables = {}  # group_id: table
        self.day_options = []
        self.clipboard_row = None

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.explanation_layout = QVBoxLayout()
        explanation = "How to copy and paste a row: (1) Select a row by double left click on the row index. \
        \n(2) Copy (Ctrl + C) the selected row. (3) Double click again at the target row index and paste (Ctrl + V)."
        explanation_label = QLabel(explanation)
        explanation_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.explanation_layout.addWidget(explanation_label)
        self.main_layout.addLayout(self.explanation_layout)

        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

    def populate_from_model(self, model):
        self.model = model
        self.days = model.days
        self.day_options = ["all"] + [str(i + 1) for i in range(len(self.days))]

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.group_tables.clear()
        group_ids = sorted(set(int(cat.group) for cat in model.get_categories()))
        event_data = model.get_other_events()

        for group_id in group_ids:
            group_names = [cat.name for cat in model.categories if int(cat.group) == group_id]
            self.content_layout.addWidget(QLabel(f"Group {group_id}: " + ", ".join(group_names)))

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
        if isinstance(data, dict):
            label = data.get("label", "")
            duration = data.get("duration", 0)
            day_index = data.get("day_index", 0)
            bef_dur_aft = data.get("bef_dur_aft", "before")
            dur_index = data.get("dur_index", 0)
        elif isinstance(data, OtherEvent):
            label = data.label
            duration = data.duration
            day_index = data.day_index or 0
            bef_dur_aft = data.bef_dur_aft or "before"
            dur_index = data.dur_index or 0
        else:
            label = ""
            duration = 0
            day_index = 0
            bef_dur_aft = "before"
            dur_index = 0

        day_combo = QComboBox()
        day_combo.addItems(self.day_options)
        day_str = "all" if day_index == 0 else str(day_index)
        if day_str in self.day_options:
            day_combo.setCurrentText(day_str)
        table.setCellWidget(row, 0, day_combo)

        when_combo = QComboBox()
        when_combo.addItems(self.WHEN_OPTIONS)
        when_combo.setCurrentText(bef_dur_aft)
        table.setCellWidget(row, 1, when_combo)

        index_spin = QSpinBox()
        index_spin.setRange(0, 999)
        index_spin.setValue(dur_index)
        table.setCellWidget(row, 2, index_spin)

        label_item = QTableWidgetItem(label)
        table.setItem(row, 3, label_item)

        duration_spin = QSpinBox()
        duration_spin.setRange(0, 999)
        duration_spin.setValue(duration)
        table.setCellWidget(row, 4, duration_spin)

    def collect_input_fields(self):
        events = {}
        for group_id, table in self.group_tables.items():
            group_events = []
            for row in range(table.rowCount()):
                label_item = table.item(row, 3)
                label = label_item.text().strip() if label_item else ""
                if not label:
                    continue

                day_str = table.cellWidget(row, 0).currentText()
                day_index = 0 if day_str == "all" else int(day_str)

                event = OtherEvent(
                    label=label,
                    duration=table.cellWidget(row, 4).value(),
                    day_index=day_index,
                    bef_dur_aft=table.cellWidget(row, 1).currentText(),
                    dur_index=table.cellWidget(row, 2).value(),
                    color=None
                )
                group_events.append(event)
            events[str(group_id)] = group_events
        return events

    def eventFilter(self, source, event):
        if isinstance(source, QTableWidget):
            if event.type() == QEvent.KeyPress:
                selected_rows = {idx.row() for idx in source.selectedIndexes()}

                if event.matches(QKeySequence.Copy) and len(selected_rows) == 1:
                    self.clipboard_row = self._copy_row(source, selected_rows.pop())
                    return True

                elif event.matches(QKeySequence.Paste) and self.clipboard_row and len(selected_rows) == 1:
                    self._paste_row(source, selected_rows.pop(), self.clipboard_row)
                    return True

                elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                    for row in selected_rows:
                        self._clear_row(source, row)
                    return True

        return super().eventFilter(source, event)

    def _copy_row(self, table, row):
        day_str = table.cellWidget(row, 0).currentText()
        day_index = 0 if day_str == "all" else int(day_str)
        return OtherEvent(
            label=table.item(row, 3).text() if table.item(row, 3) else "",
            duration=table.cellWidget(row, 4).value(),
            day_index=day_index,
            bef_dur_aft=table.cellWidget(row, 1).currentText(),
            dur_index=table.cellWidget(row, 2).value(),
            color=None
        )

    def _paste_row(self, table, row, data: OtherEvent):
        table.cellWidget(row, 0).setCurrentText("all" if data.day_index == 0 else str(data.day_index))
        table.cellWidget(row, 1).setCurrentText(data.bef_dur_aft)
        table.cellWidget(row, 2).setValue(data.dur_index or 0)
        table.setItem(row, 3, QTableWidgetItem(data.label))
        table.cellWidget(row, 4).setValue(data.duration)

    def _clear_row(self, table, row):
        table.cellWidget(row, 0).setCurrentText("all")
        table.cellWidget(row, 1).setCurrentText("before")
        table.cellWidget(row, 2).setValue(0)
        table.setItem(row, 3, QTableWidgetItem(""))
        table.cellWidget(row, 4).setValue(0)
