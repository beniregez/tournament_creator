from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

class OverviewView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setVerticalSpacing(15)
        self.setLayout(self.layout)
        self.update_ui()

    def update_ui(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        model = self.controller.model
        categories = model.get_categories()
        match_durs = model.get_match_durs()
        num_days = len(model.get_days())

        metrics = [
            "Name",
            "Number of teams",
            "Grouping",
            "Runs",
            "Match duration",
            "Matches per team",
            "Matches per team & day"
        ]

        # First column: metric names
        for row, label in enumerate(metrics, start=0):  # Start at row 0
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", weight=QFont.Bold))
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            lbl.setMinimumHeight(50)
            self.layout.addWidget(lbl, row, 0)

        # Category data. Start at column 1, row 0.
        for col, cat in enumerate(categories, start=1):
            teams = cat.teams
            num_teams = len(teams)
            group = cat.group
            runs = int(cat.runs)
            duration = match_durs.get(group, "N/A")
            matches_per_team = (num_teams - 1) * runs if num_teams > 1 else 0
            matches_per_day = round(matches_per_team / num_days, 2) if num_days > 0 else "N/A"

            values = [
                cat.name,
                str(num_teams),
                group,
                str(runs),
                str(duration),
                str(matches_per_team),
                str(matches_per_day)
            ]

            for row, val in enumerate(values, start=0):
                lbl = QLabel(val)
                lbl.setFont(QFont("Arial", weight=QFont.Bold))
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setMinimumHeight(40)

                # Background Color
                color = QColor(230, 230, 230) if row not in [0, 6] else QColor(200, 200, 200)
                palette = lbl.palette()
                palette.setColor(QPalette.Window, color)
                lbl.setAutoFillBackground(True)
                lbl.setPalette(palette)

                self.layout.addWidget(lbl, row, col)