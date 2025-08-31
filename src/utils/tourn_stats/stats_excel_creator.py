from datetime import datetime, timedelta
import xlsxwriter
import time, os

from core.event import MatchEvent, OtherEvent
from model.model import Model
from core import EventDay
from utils.tourn_to_excel.day_sheets_writer import DaySheetsWriter

class StatsExcelCreator():
    def __init__(self, model: Model, output_dir: str):
        self.model = model
        self.output_dir = output_dir
        self.excel_path = os.path.join(self.output_dir, "stats.xlsx")
        self.wb = xlsxwriter.Workbook(self.excel_path)
        self.team_color_formats = {}   # Cache for team colors

    def write_to_excel(self):
        self.set_formats()
        self.write_days_overview()
        self.write_stats()
        self.wb.close()
        print(f"Stats exported to Excel at {self.excel_path}")

    def _add_and_get_color_format(self, color_hex):
        if not color_hex:
            color_hex = "#FFFFFF"  # fallback weiß
        if color_hex not in self.team_color_formats:
            self.team_color_formats[color_hex] = self.wb.add_format({
                'bg_color': color_hex,
                'font_size': 11,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
        return self.team_color_formats[color_hex]
    
    def set_formats(self):
        self.title_fmt = self.wb.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'font_size': 14, 'top': 2, 'bottom': 2
        })
        self.header_fmt = self.wb.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'font_size': 11, 'bottom': 1
        })
        self.time_fmt = self.wb.add_format({'align': 'center', 'valign': 'vcenter'})
        self.team_fmt = self.wb.add_format({'align': 'left', 'valign': 'vcenter'})
        self.other_fmt = self.wb.add_format({
            'italic': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#F0F0F0'
        })

    ##### days overview sheet #####
    def write_days_overview(self):
        ws = self.wb.add_worksheet("Overview")
        ws.hide_gridlines(2)

        model_days = self.model.get_days()
        tourn_days = self.model.get_tournament_generated()

        start_col = 0
        for day_idx, day in enumerate(tourn_days):
            max_num_fields = day.max_fields()

            total_cols_for_day = max_num_fields * 3
            end_col = start_col + total_cols_for_day - 1
            header_text = f"{model_days[day_idx]['Date']} ({model_days[day_idx]['Title']}) in {model_days[day_idx]['Location']}"
            ws.merge_range(0, start_col, 0, end_col, header_text, self.title_fmt)

            for field_idx in range(max_num_fields):
                col_offset = start_col + field_idx * 3
                ws.write(1, col_offset, "Time", self.header_fmt)
                ws.write(1, col_offset+1, "Home", self.header_fmt)
                ws.write(1, col_offset+2, "Away", self.header_fmt)

                ws.set_column(col_offset, col_offset, 8)
                ws.set_column(col_offset+1, col_offset+1, 20)
                ws.set_column(col_offset+2, col_offset+2, 20)

            row_idx = 2
            curr_time = datetime.strptime(model_days[day_idx]["Start time"], "%H:%M")
            for ev in day.get_all_valid_events():
                if isinstance(ev, MatchEvent):
                    for field_idx in range(max_num_fields):
                        col_offset = start_col + field_idx * 3
                        if field_idx < len(ev.matches):
                            m = ev.matches[field_idx]
                            ws.write(row_idx, col_offset, curr_time.strftime("%H:%M"), self.time_fmt)
                            home_fmt = self._add_and_get_color_format(m.team1.color)
                            away_fmt = self._add_and_get_color_format(m.team2.color)
                            ws.write(row_idx, col_offset+1, m.team1.name, home_fmt)
                            ws.write(row_idx, col_offset+2, m.team2.name, away_fmt)
                        else:
                            ws.write(row_idx, col_offset,   curr_time.strftime("%H:%M"), self.time_fmt)
                            ws.write(row_idx, col_offset+1, "", self.team_fmt)
                            ws.write(row_idx, col_offset+2, "", self.team_fmt)
                    row_idx += 1
                elif isinstance(ev, OtherEvent):
                    ws.write(row_idx, start_col, curr_time.strftime("%H:%M"), self.time_fmt)
                    ws.merge_range(row_idx, start_col+1, row_idx, end_col, ev.label, self.other_fmt)
                    row_idx += 1

                curr_time += timedelta(minutes=ev.duration)

            start_col = end_col + 2


    ##### days overview sheet #####
    def write_stats(self):
        ws = self.wb.add_worksheet("Stats")
        ws.hide_gridlines(2)

        model_days = self.model.get_days()
        tourn_days = self.model.get_tournament_generated()
        cats = self.model.get_categories()
        num_days = len(tourn_days)

        col_idx = 0
        row_idx = 2

        col_offset = 4

        # total metric headers
        ws.merge_range(0, col_idx, 0, col_idx + col_offset, "Entire tournament", self.title_fmt)
        ws.write(1, col_idx, "Team", self.header_fmt)
        ws.write(1, col_idx + 1, "Total", self.header_fmt)
        ws.write(1, col_idx + 2, "Home", self.header_fmt)
        ws.write(1, col_idx + 3, "Away", self.header_fmt)
        ws.write(1, col_idx + 4, "M. per day", self.header_fmt)

        ws.set_column(col_idx, col_idx, 20)

        for cat in cats:
            for team in cat.teams:
                home = 0
                away = 0
                for day in tourn_days:
                    home += day.count_team_home(team)
                    away += day.count_team_away(team)
                ws.write(row_idx, col_idx, team.name, self._add_and_get_color_format(team.color))
                ws.write(row_idx, col_idx + 1, home + away)
                ws.write(row_idx, col_idx + 2, home)
                ws.write(row_idx, col_idx + 3, away)
                ws.write(row_idx, col_idx + 4, (home + away) / num_days)
                row_idx += 1
            row_idx += 1

        col_idx += col_offset + 2

        for day_idx, day in enumerate(tourn_days):
            header_text = f"{model_days[day_idx]['Date']} ({model_days[day_idx]['Title']})"            
            ws.merge_range(0, col_idx, 0, col_idx + col_offset - 1, header_text, self.title_fmt)

            # metric headers
            ws.write(1, col_idx, "Team", self.header_fmt)
            ws.write(1, col_idx + 1, "Total", self.header_fmt)
            ws.write(1, col_idx + 2, "Home", self.header_fmt)
            ws.write(1, col_idx + 3, "Away", self.header_fmt)

            ws.set_column(col_idx, col_idx, 20)

            row_idx = 2
            for cat in cats:
                for team in cat.teams:
                    ws.write(row_idx, col_idx, team.name, self._add_and_get_color_format(team.color))
                    ws.write(row_idx, col_idx + 1, day.count_team_total(team))
                    ws.write(row_idx, col_idx + 2, day.count_team_home(team))
                    ws.write(row_idx, col_idx + 3, day.count_team_away(team))

                    row_idx += 1
                row_idx += 1

            col_idx += col_offset + 1
