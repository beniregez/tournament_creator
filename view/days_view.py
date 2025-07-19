from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QDateEdit, QTimeEdit,
    QHeaderView
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QKeySequence


class DaysView(QWidget):
    MAX_DAYS = 10
    ROWS = ["Title", "Date", "Location", "Responsible", "Start time"]
    CELL_WIDTH = 240
    CELL_HEIGHT = 32

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.clipboard_data = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

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
        result = []
        for col in range(self.MAX_DAYS):
            title_item = self.table.item(0, col)
            location_item = self.table.item(2, col)
            responsible_item = self.table.item(3, col)

            date_widget = self.table.cellWidget(1, col)
            time_widget = self.table.cellWidget(4, col)

            # if not any([title_item, location_item, responsible_item]) and not date_widget and not time_widget:
            if not any([title_item, location_item, responsible_item]): # TODO Also check if a date or a time has been entered
                continue  # Skip empty columns

            data = {
                "Title": title_item.text().strip() if title_item else "",
                "Date": date_widget.date().toString("dd.MM.yyyy") if date_widget else "",
                "Location": location_item.text().strip() if location_item else "",
                "Responsible": responsible_item.text().strip() if responsible_item else "",
                "Start time": time_widget.time().toString("HH:mm") if time_widget else ""
            }
            
            # TODO: Also check for date and time (requires other way of checking)
            if (data["Title"] or data["Location"] or data["Responsible"]):
                result.append(data)
            else:
                continue # Skip empty entries. 

        return result

    def populate_from_model(self, model):
        days_data = model.get_days()  # List of dicts
        self.clear_table()

        for col, day in enumerate(days_data):
            if col >= self.MAX_DAYS:
                break

            # Title
            self.set_text_item(0, col, day.get("Title", ""))

            # Date (in format "dd.MM.yyyy")
            self.set_date_item(1, col, day.get("Date", ""))

            # Location
            self.set_text_item(2, col, day.get("Location", ""))

            # Responsible
            self.set_text_item(3, col, day.get("Responsible", ""))

            # Start time (format "HH:mm")
            self.set_time_item(4, col, day.get("Start time", ""))

    def clear_table(self):
        self.column_colors = {}
        for row in range(len(self.ROWS)):
            for col in range(self.MAX_DAYS):
                self.table.setItem(row, col, QTableWidgetItem(""))

    # Methods to insert formatted QTableWidgetItems into specific cells.
    def set_text_item(self, row, col, text):
        item = QTableWidgetItem(text)
        self.table.setItem(row, col, item)

    def set_date_item(self, row, col, date_str):
        item = QTableWidgetItem(date_str)
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, item)

    def set_time_item(self, row, col, time_str):
        item = QTableWidgetItem(time_str)
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, item)
