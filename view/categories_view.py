from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QToolBar, QAction,
    QHeaderView, QColorDialog, QSpinBox
)
from PyQt5.QtGui import QColor, QBrush, QKeySequence, QFont
from PyQt5.QtCore import Qt


class CategoriesView(QWidget):
    MAX_CATEGORIES = 10
    MAX_TEAMS = 30

    CELL_WIDTH = 240
    CELL_HEIGHT = 30

    TITLE_ROW_INDEX = 0
    GROUP_ROW_INDEX = 1
    RUNS_ROW_INDEX = 2
    TEAM_ROW_OFFSET = 3  # Teams beginnen ab dieser Zeile

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.clipboard_data = None
        self.column_colors = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # === Toolbar ===
        self.toolbar = QToolBar("Tools")
        color_action = QAction("Change Cell Color", self)
        color_action.triggered.connect(self.change_cell_color)
        self.toolbar.addAction(color_action)

        clear_action = QAction("Clear Selection", self)
        clear_action.triggered.connect(self.clear_selection)
        self.toolbar.addAction(clear_action)

        layout.addWidget(self.toolbar)

        # === Table ===
        total_rows = self.MAX_TEAMS + self.TEAM_ROW_OFFSET
        self.table = QTableWidget(self)
        self.table.setRowCount(total_rows)
        self.table.setColumnCount(self.MAX_CATEGORIES)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # Vertical headers
        self.table.setVerticalHeaderItem(self.TITLE_ROW_INDEX, QTableWidgetItem("Category Name"))
        self.table.setVerticalHeaderItem(self.GROUP_ROW_INDEX, QTableWidgetItem("Group"))
        self.table.setVerticalHeaderItem(self.RUNS_ROW_INDEX, QTableWidgetItem("Runs"))
        for row in range(self.TEAM_ROW_OFFSET, total_rows):
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(f"Team {row - self.TEAM_ROW_OFFSET + 1}"))

        # Initial header row (bold)
        for col in range(self.MAX_CATEGORIES):
            # Title row
            title_item = QTableWidgetItem("")
            title_item.setFont(QFont("Arial", weight=QFont.Bold))
            self.table.setItem(self.TITLE_ROW_INDEX, col, title_item)

            # Grouping spinbox (1–10)
            group_spin = QSpinBox()
            group_spin.setRange(1, 10)
            group_spin.setFrame(False)
            self.table.setCellWidget(self.GROUP_ROW_INDEX, col, group_spin)

            # Runs spinbox (1–20)
            runs_spin = QSpinBox()
            runs_spin.setRange(1, 20)
            runs_spin.setFrame(False)
            self.table.setCellWidget(self.RUNS_ROW_INDEX, col, runs_spin)

            self.table.setColumnWidth(col, self.CELL_WIDTH)

        # Row height
        for row in range(total_rows):
            self.table.setRowHeight(row, self.CELL_HEIGHT)
        self.table.setRowHeight(self.TITLE_ROW_INDEX, self.CELL_HEIGHT + 20)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.table.installEventFilter(self)

    # ========== Event Handling ==========

    def eventFilter(self, source, event):
        if source is self.table and event.type() == event.KeyPress:
            if event.matches(QKeySequence.Copy):
                self.copy_selection()
                return True
            elif event.matches(QKeySequence.Paste):
                self.paste_selection()
                return True
            elif event.matches(QKeySequence.Cut):
                self.copy_selection()
                self.clear_selection()
                return True
            elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                self.clear_selection()
                return True
        return super().eventFilter(source, event)

    # ========== Copy/Paste ==========

    def copy_selection(self):
        selected = self.table.selectedRanges()
        if not selected:
            return

        sel = selected[0]
        copied_data = []
        copied_colors = []
        for r in range(sel.topRow(), sel.bottomRow() + 1):
            row_data = []
            row_colors = []
            for c in range(sel.leftColumn(), sel.rightColumn() + 1):
                if r == self.GROUP_ROW_INDEX:
                    spin = self.table.cellWidget(r, c)
                    row_data.append(str(spin.value()) if spin else "")
                elif r == self.RUNS_ROW_INDEX:
                    spin = self.table.cellWidget(r, c)
                    row_data.append(str(spin.value()) if spin else "")
                else:
                    item = self.table.item(r, c)
                    row_data.append(item.text() if item else "")
                    color = self.column_colors.get((r, c))
                    row_colors.append(color.name() if color else "")
            copied_data.append(row_data)
            copied_colors.append(row_colors)

        self.clipboard_data = {"data": copied_data, "colors": copied_colors}

    def paste_selection(self):
        if not self.clipboard_data:
            return

        selected = self.table.selectedRanges()
        if not selected:
            return

        start_row = selected[0].topRow()
        start_col = selected[0].leftColumn()
        data = self.clipboard_data["data"]
        colors = self.clipboard_data["colors"]

        for r_offset, row_data in enumerate(data):
            for c_offset, text in enumerate(row_data):
                r = start_row + r_offset
                c = start_col + c_offset
                if r >= self.table.rowCount() or c >= self.table.columnCount():
                    continue

                if r == self.TITLE_ROW_INDEX:
                    item = self.table.item(r, c)
                    if not item:
                        item = QTableWidgetItem()
                        self.table.setItem(r, c, item)
                    item.setText(text)
                elif r == self.GROUP_ROW_INDEX or r == self.RUNS_ROW_INDEX:
                    spin = self.table.cellWidget(r, c)
                    if spin:
                        try:
                            spin.setValue(int(text))
                        except ValueError:
                            pass
                else:
                    item = self.table.item(r, c)
                    if not item:
                        item = QTableWidgetItem()
                        self.table.setItem(r, c, item)
                    item.setText(text)
                    color_hex = colors[r_offset][c_offset]
                    if color_hex:
                        color = QColor(color_hex)
                        item.setBackground(QBrush(color))
                        self.column_colors[(r, c)] = color

    # ========== Edit Tools ==========

    def clear_selection(self):
        for item in self.table.selectedItems():
            item.setText("")
            item.setBackground(QBrush())
            self.column_colors.pop((item.row(), item.column()), None)

    def change_cell_color(self):
        color = QColorDialog.getColor(parent=self)
        if not color.isValid():
            return
        for item in self.table.selectedItems():
            if item.row() == self.TITLE_ROW_INDEX:
                continue
            item.setBackground(QBrush(color))
            self.column_colors[(item.row(), item.column())] = color

    # ========== Model Export/Import ==========

    def collect_input_fields(self):
        data = []
        for col in range(self.table.columnCount()):
            name_item = self.table.item(self.TITLE_ROW_INDEX, col)
            name = name_item.text().strip() if name_item else ""

            group_widget = self.table.cellWidget(self.GROUP_ROW_INDEX, col)
            group = str(group_widget.value()) if group_widget else ""

            runs_widget = self.table.cellWidget(self.RUNS_ROW_INDEX, col)
            runs = str(runs_widget.value()) if runs_widget else ""

            teams = []
            colors = []
            for row in range(self.TEAM_ROW_OFFSET, self.table.rowCount()):
                item = self.table.item(row, col)
                text = item.text().strip() if item else ""
                if text:
                    teams.append(text)
                    color = self.column_colors.get((row, col))
                    colors.append(color.name() if color else "")

            if name or teams:
                data.append({
                    "name": name,
                    "group": group,
                    "runs": runs,
                    "teams": teams,
                    "colors": colors
                })
        return data

    def populate_from_model(self, model):
        categories = model.get_categories()
        self.column_colors = {}

        for col, col_data in enumerate(categories):
            
            if col >= self.MAX_CATEGORIES:
                break

            # Name of category
            self.table.setItem(self.TITLE_ROW_INDEX, col, QTableWidgetItem(col_data.get("name", "")))

            # Group
            group_spin = self.table.cellWidget(self.GROUP_ROW_INDEX, col)
            if group_spin:
                try:
                    group_spin.setValue(int(col_data.get("group", 1)))
                except (ValueError, TypeError):
                    pass

            # Runs
            runs_spin = self.table.cellWidget(self.RUNS_ROW_INDEX, col)
            if runs_spin:
                try:
                    runs_spin.setValue(int(col_data.get("runs", 1)))
                except (ValueError, TypeError):
                    pass

            # Teams & Colors
            for i, (team, color_hex) in enumerate(zip(col_data.get("teams", []), col_data.get("colors", []))):
                row = self.TEAM_ROW_OFFSET + i
                item = QTableWidgetItem(team)
                if color_hex:
                    color = QColor(color_hex)
                    item.setBackground(QBrush(color))
                    self.column_colors[(row, col)] = color
                self.table.setItem(row, col, item)