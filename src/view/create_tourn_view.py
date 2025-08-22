from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractScrollArea
)
from PyQt5.QtGui import QFont, QBrush, QColor
from PyQt5.QtCore import Qt

from core import MatchEvent, OtherEvent
from view.status_label import StatusLabel

class CreateTourn(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)

        # Container for table
        self.table = QTableWidget(0, 0)
        self.main_layout.addWidget(self.table)

        # Buttons at the bottom
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)

        regenerate_btn = QPushButton("Regenerate")
        export_btn = QPushButton("Export to Excel")

        for btn in [regenerate_btn, export_btn]:
            btn.setFont(QFont("Arial", 10, QFont.Bold))
            btn.setFixedSize(240, 50)

        regenerate_btn.clicked.connect(self.generate_tourn)
        export_btn.clicked.connect(self.export_excel)
        button_layout.addWidget(regenerate_btn)
        button_layout.addWidget(export_btn)

        self.main_layout.addLayout(button_layout)

        # Status label to show messages
        self.status_label = StatusLabel()
        self.status_label.setFixedHeight(60)
        self.main_layout.addWidget(self.status_label)

        self.setLayout(self.main_layout)

        if self.controller.model.get_tournament_generated():
            self.build_schedule_tables()

    def update_ui(self):
        self.build_schedule_tables()

    def generate_tourn(self):
        self.controller.generate_tournament_from_model()    # Generate tournament from Model
        self.build_schedule_tables()                        # Generate table with tournament
        self.status_label.show_message("Tournament regenerated", 3000)

    # Use export module
    def export_excel(self):
        self.controller.export_to_excel()
        self.status_label.show_message("✅ Tournament exported", 4000)

    def build_schedule_tables(self):
        # 1. Prepare days (as flattened list).
        tourn_generated = self.controller.model.get_tournament_generated()
        model_days = self.controller.model.get_days()
        
        # TODO 2. Compute table size
        num_cols = 0
        num_rows = 1
        day_col_start_indices = [0] # We must know for each day at which col to start
        for day in tourn_generated:
            num_cols += 1 + day.max_fields() * 4    # 1 for time, per fields: [home, ":", away, spacer]
            day_col_start_indices.append(num_cols)
            if day.total_events() > num_rows:
                num_rows = day.total_events() + 2   # + 2 because of headers

        self._reset_table(self.table, num_rows, num_cols)
        
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.table.horizontalHeader().setMinimumSectionSize(1)
        self.table.horizontalHeader().setDefaultSectionSize(10)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.table.verticalHeader().setMinimumSectionSize(1)
        self.table.verticalHeader().setDefaultSectionSize(20)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(QFont("Arial", 5))
        
        # 3. Fill table
        font_bold = QFont()
        font_bold.setBold(True)
        for day_idx, day in enumerate(tourn_generated):
            # a) "Headers"
            col_offset = day_col_start_indices[day_idx]
            # Day header
            day_header = QTableWidgetItem(f"{model_days[day_idx]["Title"]} ({model_days[day_idx]["Date"]})")
            day_header.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            day_header.setFont(font_bold)
            self.table.setItem(0, col_offset, day_header)
            self.table.setSpan(0, col_offset, 1, 1 + 4 * day.max_fields() - 1)
            # Time header
            time_header = QTableWidgetItem("Time")
            time_header.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table.setItem(1, col_offset, time_header)
            self.table.setColumnWidth(col_offset, 40)
            # Team headers
            for m_e in range(day.max_fields()):
                home_header = QTableWidgetItem(f"Home {m_e + 1}")
                home_header.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table.setItem(1, col_offset + (m_e * 4) + 1, home_header)
                self.table.setColumnWidth(col_offset + (m_e * 4) + 1, 120)
                away_header = QTableWidgetItem(f"Away {m_e + 1}")
                away_header.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table.setItem(1, col_offset + (m_e * 4) + 3, away_header)
                self.table.setColumnWidth(col_offset + (m_e * 4) + 3, 120)
                if m_e != 0:
                    self.table.setColumnWidth(col_offset + (m_e * 4), 30)   # Spacer between matches

            # b) starting times
            if day.total_events() > 0:
                curr_time = datetime.strptime(model_days[day_idx]["Start time"], "%H:%M")
            else:
                curr_time = datetime.strptime("00:00", "%H:%M")
            for ev_idx, event in enumerate(day.get_all_valid_events()):
                time_item = QTableWidgetItem(f"{curr_time.strftime("%H:%M")}")
                time_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table.setItem(ev_idx + 2, col_offset, time_item)
                curr_time += timedelta(minutes=event.duration)

                # c) OtherEvents
                if isinstance(event, OtherEvent):
                    event_item = QTableWidgetItem(f"{event.label}")
                    event_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.table.setItem(ev_idx + 2, col_offset + 1, event_item)
                    self.table.setSpan(ev_idx + 2, col_offset + 1, 1, 4 * day.max_fields() - 1)

                # d) MatchEvents
                if isinstance(event, MatchEvent):
                    for m_idx, match in enumerate(event.matches):
                        for t_idx, team in enumerate([match.team1, match.team2]):
                            team_item = QTableWidgetItem(f"{team.name}")
                            team_item.setBackground(QBrush(QColor(team.color)))
                            team_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                            self.table.setItem(ev_idx + 2, col_offset + 1 + m_idx * 4 + t_idx * 2, team_item)
                        colon_item = QTableWidgetItem(":")
                        colon_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.table.setItem(ev_idx + 2, col_offset + 1 + m_idx * 4 + 1, colon_item)
        
        # 4. Set boarders around each day for better visibility
        self.table.setItemDelegate(BorderDelegate())
        for day_idx, day in enumerate(tourn_generated):
            self._set_border_around_area(self.table, 0, day_col_start_indices[day_idx], day.total_events() + 1,
                        day_col_start_indices[day_idx + 1] - 2)


    def _reset_table(self, table: QTableWidget, num_rows_new: int, num_cols_new: int):
        """
        Removes all content, items and cell spans in the table.
        Sets new table size.
        """
        # Remove content and items
        table.clear()

        # Remove all Cell Spans
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                if table.rowSpan(row, col) > 1 or table.columnSpan(row, col) > 1:
                    table.setSpan(row, col, 1, 1)

        # Set new size
        table.setRowCount(num_rows_new)
        table.setColumnCount(num_cols_new)


    def _set_border_around_area(self, table: QTableWidget, start_row: int, start_col: int, end_row: int, end_col: int):
        """
        Sets a visible border around an area in the QTableWidget.
        The border is stored via UserRole and later drawn by the delegate.
        """
        visited = set()  # Prevents double processing in spans

        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                # Skip if already processed via span
                if (row, col) in visited:
                    continue

                # Get span info
                row_span = table.rowSpan(row, col)
                col_span = table.columnSpan(row, col)

                # Only process visible (top-left) cell of span
                if row_span > 1 or col_span > 1:
                    # Mark all spanned cells as visited
                    for r in range(row, row + row_span):
                        for c in range(col, col + col_span):
                            visited.add((r, c))
                else:
                    visited.add((row, col))

                item = table.item(row, col)
                if item is None:
                    item = QTableWidgetItem("")
                    table.setItem(row, col, item)

                # Compute actual area of cell (including span)
                cell_end_row = row + row_span - 1
                cell_end_col = col + col_span - 1

                # Define boarder based on total area
                border = ""
                if row == start_row:
                    border += "border-top;"
                if cell_end_row == end_row:
                    border += "border-bottom;"
                if col == start_col:
                    border += "border-left;"
                if cell_end_col == end_col:
                    border += "border-right;"

                item.setData(Qt.UserRole, border)


from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QPainter

class BorderDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        border = index.data(Qt.UserRole)
        if border:
            painter.save()
            painter.setPen(Qt.black)
            rect = option.rect
            if "border-top" in border:
                painter.drawLine(rect.topLeft(), rect.topRight())
            if "border-bottom" in border:
                painter.drawLine(rect.bottomLeft(), rect.bottomRight())
            if "border-left" in border:
                painter.drawLine(rect.topLeft(), rect.bottomLeft())
            if "border-right" in border:
                painter.drawLine(rect.topRight(), rect.bottomRight())
            painter.restore()
