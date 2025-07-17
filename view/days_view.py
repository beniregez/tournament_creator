from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QDateEdit, QTimeEdit,
    QHeaderView, QToolBar, QAction
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QKeySequence


class DaysView(QWidget):
    MAX_DAYS = 10
    ROWS = ["Title", "Date", "Location", "Responsible", "Start time"]
    CELL_WIDTH = 180
    CELL_HEIGHT = 32

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.clipboard_data = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # === Toolbar ===
        self.toolbar = QToolBar("Tools")
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_selection)
        self.toolbar.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_selection)
        self.toolbar.addAction(paste_action)

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut_selection)
        self.toolbar.addAction(cut_action)

        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.clear_selection)
        self.toolbar.addAction(delete_action)

        layout.addWidget(self.toolbar)

        # === Table ===
        self.table = QTableWidget(len(self.ROWS), self.MAX_DAYS)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)

        self.table.installEventFilter(self)

        # Set headers
        self.table.setVerticalHeaderLabels(self.ROWS)
        self.table.setHorizontalHeaderLabels([f"Day {i+1}" for i in range(self.MAX_DAYS)])

        # Fix column/row sizes
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        for col in range(self.MAX_DAYS):
            self.table.setColumnWidth(col, self.CELL_WIDTH)
        for row in range(len(self.ROWS)):
            self.table.setRowHeight(row, self.CELL_HEIGHT)

        # Add date/time widgets
        for col in range(self.MAX_DAYS):
            date_edit = QDateEdit()
            date_edit.setDisplayFormat("dd.MM.yyyy")
            date_edit.setCalendarPopup(True)
            self.table.setCellWidget(1, col, date_edit)

            time_edit = QTimeEdit()
            time_edit.setDisplayFormat("HH:mm")
            self.table.setCellWidget(4, col, time_edit)

        layout.addWidget(self.table)
        self.setLayout(layout)

    # === Event Filter for shortcuts ===
    def eventFilter(self, source, event):
        if source is self.table and event.type() == event.KeyPress:
            if event.matches(QKeySequence.Copy):
                self.copy_selection()
                return True
            elif event.matches(QKeySequence.Paste):
                self.paste_selection()
                return True
            elif event.matches(QKeySequence.Cut):
                self.cut_selection()
                return True
            elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                self.clear_selection()
                return True
        return super().eventFilter(source, event)

    # === Copy/Cut/Paste/Delete ===
    def copy_selection(self):
        selected = self.table.selectedRanges()
        if not selected:
            return
        sel = selected[0]
        copied = []
        for row in range(sel.topRow(), sel.bottomRow() + 1):
            row_data = []
            for col in range(sel.leftColumn(), sel.rightColumn() + 1):
                if row == 1:
                    widget = self.table.cellWidget(row, col)
                    row_data.append(widget.date().toString("dd.MM.yyyy") if widget else "")
                elif row == 4:
                    widget = self.table.cellWidget(row, col)
                    row_data.append(widget.time().toString("HH:mm") if widget else "")
                else:
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
            copied.append(row_data)
        self.clipboard_data = copied

    def paste_selection(self):
        if not self.clipboard_data:
            return
        selected = self.table.selectedRanges()
        if not selected:
            return
        start_row = selected[0].topRow()
        start_col = selected[0].leftColumn()

        for r_offset, row_data in enumerate(self.clipboard_data):
            for c_offset, text in enumerate(row_data):
                row = start_row + r_offset
                col = start_col + c_offset
                if row >= self.table.rowCount() or col >= self.table.columnCount():
                    continue
                if row == 1:
                    widget = self.table.cellWidget(row, col)
                    if widget:
                        widget.setDate(QDate.fromString(text, "dd.MM.yyyy"))
                elif row == 4:
                    widget = self.table.cellWidget(row, col)
                    if widget:
                        widget.setTime(QTime.fromString(text, "HH:mm"))
                else:
                    item = self.table.item(row, col)
                    if item is None:
                        item = QTableWidgetItem()
                        self.table.setItem(row, col, item)
                    item.setText(text)

    def cut_selection(self):
        self.copy_selection()
        self.clear_selection()

    def clear_selection(self):
        for item in self.table.selectedItems():
            item.setText("")
        for sel in self.table.selectedRanges():
            for row in range(sel.topRow(), sel.bottomRow() + 1):
                for col in range(sel.leftColumn(), sel.rightColumn() + 1):
                    if row == 1:
                        widget = self.table.cellWidget(row, col)
                        if widget:
                            widget.setDate(QDate.currentDate())
                    elif row == 4:
                        widget = self.table.cellWidget(row, col)
                        if widget:
                            widget.setTime(QTime(0, 0))

    # === Model Methods ===
    def collect_input_fields(self):
        result = {}
        for col in range(self.MAX_DAYS):
            title_item = self.table.item(0, col)
            location_item = self.table.item(2, col)
            responsible_item = self.table.item(3, col)

            date_widget = self.table.cellWidget(1, col)
            time_widget = self.table.cellWidget(4, col)

            if not any([title_item, location_item, responsible_item]) and not date_widget and not time_widget:
                continue  # skip empty

            data = {
                "Title": title_item.text().strip() if title_item else "",
                "Date": date_widget.date().toString("dd.MM.yyyy") if date_widget else "",
                "Location": location_item.text().strip() if location_item else "",
                "Responsible": responsible_item.text().strip() if responsible_item else "",
                "Start time": time_widget.time().toString("HH:mm") if time_widget else ""
            }

            if any(data.values()):
                result[str(col)] = data
        return result

    def populate_from_model(self, model_data):
        for col_str, data in model_data.items():
            col = int(col_str)
            title_item = QTableWidgetItem(data.get("Title", ""))
            self.table.setItem(0, col, title_item)

            location_item = QTableWidgetItem(data.get("Location", ""))
            self.table.setItem(2, col, location_item)

            responsible_item = QTableWidgetItem(data.get("Responsible", ""))
            self.table.setItem(3, col, responsible_item)

            date_widget = self.table.cellWidget(1, col)
            if date_widget and data.get("Date"):
                date_widget.setDate(QDate.fromString(data["Date"], "dd.MM.yyyy"))

            time_widget = self.table.cellWidget(4, col)
            if time_widget and data.get("Start time"):
                time_widget.setTime(QTime.fromString(data["Start time"], "HH:mm"))
