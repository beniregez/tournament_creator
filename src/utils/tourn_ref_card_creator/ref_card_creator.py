from datetime import datetime, timedelta
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

from core.event import MatchEvent
from model.model import Model

class RefCardCreator():
    def __init__(self, model: Model, output_path: str = "ref_cards"):
        self.model = model
        self.output_path = output_path
        self.tourn_generated = self.model.get_tournament_generated()
        self.model_days = self.model.get_days()
        self.wb = xlsxwriter.Workbook(f"{self.output_path}.xlsx")
        self.border_formats = {}
        self.CARD_NUM_ROWS = 12
        self.CARD_NUM_COLS = 13

    def create_cards(self):
        self._initialize_sheets()
        self._define_formats()
        self._write_days()
        self.wb.close()
        print("Ref cards exported to Excel.")

    def _initialize_sheets(self):
        self.worksheets = []
        for day in self.model.get_days():
            sheet = self.wb.add_worksheet(day["Title"])
            print("Sheet:", sheet.get_name(), "created.")
            self.worksheets.append(sheet)
            sheet.hide_gridlines(2)
    
    def _define_formats(self):
        self.header_left_fmt = self.wb.add_format({'font_size': 12, 'valign': 'vcenter', 'align': 'left', 'top': 2, 'bottom': 2})
        self.header_center_fmt = self.wb.add_format({'font_size': 12, 'valign': 'vcenter', 'align': 'center', 'top': 2, 'bottom': 2})
        self.header_right_fmt = self.wb.add_format({'font_size': 12, 'valign': 'vcenter', 'align': 'right', 'top': 2, 'bottom': 2})
        self.header_team_fmt = self.wb.add_format({'font_size': 11, 'valign': 'vcenter', 'align': 'center', 'bold': True})
        self.score_fmt = self.wb.add_format({'font_size': 11, 'valign': 'vcenter', 'align': 'center', 'border': 1})
        self.result_fmt = self.wb.add_format({'font_size': 10, 'valign': 'vcenter', 'align': 'left'})
        self.sign_fmt = self.wb.add_format({'font_size': 8, 'valign': 'vcenter', 'align': 'center', 'top': 1})

    def _write_days(self):
        for day_idx, day in enumerate(self.tourn_generated):
            ws = self.worksheets[day_idx]
            self._set_col_widths(ws)
            date = self.model_days[day_idx]["Date"]
            events = day.get_all_valid_events()
            match_idx = 0
            for field_idx in range(day.max_fields()):
                curr_time = datetime.strptime(self.model_days[day_idx]["Start time"], "%H:%M")
                field = f"Feld {field_idx + 1}"
                for ev in events:
                    if isinstance(ev, MatchEvent) and len(ev.matches) > field_idx:
                        team1 = ev.matches[field_idx].team1.name
                        team2 = ev.matches[field_idx].team2.name
                        time = f"{curr_time.strftime("%H:%M")}"
                        self._write_ref_card(ws, match_idx, field, date, time, team1, team2)
                        match_idx += 1
                    curr_time += timedelta(minutes=ev.duration)
            # Set print area
            end_row_idx = (self.CARD_NUM_ROWS * ((match_idx + 1) // 2)) - 1
            end_col_idx = (2 * self.CARD_NUM_COLS) - 1
            end_cell = xl_rowcol_to_cell(end_row_idx, end_col_idx)
            area = f"{xl_rowcol_to_cell(0, 0)}:{end_cell}"
            ws.print_area(area)
            # Fit to pages
            ws.fit_to_pages(1, 0)   # Width: 1 page. Length: as many pages as needed.
            # Set pagebreaks
            break_rows = []
            num_pages = (match_idx // 8) + 1
            for p in range(num_pages):
                break_rows.append((p + 1) * 4 * self.CARD_NUM_ROWS) 
            ws.set_h_pagebreaks(break_rows)
            # Set margins
            ws.set_margins(left=0.2, right=0.2, top=0.2, bottom=0.2)
            # Center pages
            ws.center_horizontally()
            ws.center_vertically()
            # Set format to A4
            ws.set_paper(9)

    def _write_ref_card(self, ws, position: int, field: str, date: str, time: str, home: str, away: str):
        row_offset = (position // 2) * self.CARD_NUM_ROWS
        col_offset = (position % 2) * self.CARD_NUM_COLS
        # Header lines top & bottom
        for col_idx in range(col_offset + 1, col_offset + 12):
            ws.write(1 + row_offset, col_idx, "", self.header_center_fmt)
            pass
        # Header text
        ws.write(1 + row_offset, 1 + col_offset, field, self.header_left_fmt)
        ws.write(1 + row_offset, 6 + col_offset, date, self.header_center_fmt)
        ws.write(1 + row_offset, 11 + col_offset, time, self.header_right_fmt)
        # Match teams
        ws.write(2 + row_offset, 3 + col_offset, home, self.header_team_fmt)
        ws.write(2 + row_offset, 9 + col_offset, away, self.header_team_fmt)
        # Goal boxes from 1 - 20
        for num in range(20):
            ws.write(row_offset + 3 + (num // 5), col_offset + 1 + (num % 5), num + 1, self.score_fmt)
            ws.write(row_offset + 3 + (num // 5), col_offset + 7 + (num % 5), num + 1, self.score_fmt)
        # End result
        ws.write(row_offset + 8, col_offset + 2, "Endresultat", self.result_fmt)
        ws.write(row_offset + 8, col_offset + 5, "", self.score_fmt)
        ws.write(row_offset + 8, col_offset + 6, ":", self.score_fmt)
        ws.write(row_offset + 8, col_offset + 7, "", self.score_fmt)
        # Signature
        for idx in range(3):
            ws.write(row_offset + 10, col_offset + 2 + idx, "", self.sign_fmt)
            ws.write(row_offset + 10, col_offset + 8 + idx, "", self.sign_fmt)
        ws.write(row_offset + 10, col_offset + 3, "Unterschrift Heim", self.sign_fmt)
        ws.write(row_offset + 10, col_offset + 9, "Unterschrift Gast", self.sign_fmt)
        # Set row heights
        self._set_card_borders(ws, row_offset, col_offset)
        self._set_row_heights(ws, row_offset)

    def _set_row_heights(self, ws, row_offset):
        ws.set_row(row_offset, 10)
        ws.set_row(row_offset + 1, 24)
        ws.set_row(row_offset + 2, 24)
        for row_idx in range(row_offset + 3, row_offset + 7):
            ws.set_row(row_idx, 24)
        ws.set_row(row_offset + 7, 8)
        ws.set_row(row_offset + 8, 21)
        ws.set_row(row_offset + 9, 21)
        ws.set_row(row_offset + 10, 12)
        ws.set_row(row_offset + 11, 8)

    def _set_card_borders(self, ws, row_offset, col_offset):
        # Lines
        for row_idx in range(row_offset + 1, row_offset + 11):
            ws.write(row_idx, col_offset, "", self.get_border_format(False, False, True, False))
            ws.write(row_idx, col_offset + 12, "", self.get_border_format(False, False, False, True))
        for col_idx in range(col_offset + 1, col_offset + 12):
            ws.write(row_offset, col_idx, "", self.get_border_format(True))
            ws.write(row_offset + 11, col_idx, "", self.get_border_format(False, True))
        # Corners
        ws.write(row_offset, col_offset, "", self.get_border_format(True, False, True, False))
        ws.write(row_offset, col_offset + 12, "", self.get_border_format(True, False, False, True))
        ws.write(row_offset + 11, col_offset, "", self.get_border_format(False, True, True, False))
        ws.write(row_offset + 11, col_offset + 12, "", self.get_border_format(False, True, False, True))

    def get_border_format(self, top=False, bottom=False, left=False, right=False, color='#808080'):
        # Generate key based on active sides
        key_parts = []
        if top: key_parts.append('top')
        if bottom: key_parts.append('bottom')
        if left: key_parts.append('left')
        if right: key_parts.append('right')
        key = '_'.join(key_parts) + f'_{color}' if key_parts else f'none_{color}'

        # Return format if already existing
        if key in self.border_formats:
            return self.border_formats[key]

        # Otherwise, create new format
        fmt_dict = {}
        if top:
            fmt_dict['top'] = 1
            fmt_dict['top_color'] = color
        if bottom:
            fmt_dict['bottom'] = 1
            fmt_dict['bottom_color'] = color
        if left:
            fmt_dict['left'] = 1
            fmt_dict['left_color'] = color
        if right:
            fmt_dict['right'] = 1
            fmt_dict['right_color'] = color

        new_format = self.wb.add_format(fmt_dict)
        self.border_formats[key] = new_format
        return new_format


    def _set_col_widths(self, ws):
        for i in range(2):
            offset = self.CARD_NUM_COLS
            ws.set_column(offset * i, offset * i, 1)
            ws.set_column(offset * i + 1, offset * i + 11, 4.5)
            ws.set_column(offset * i + 6, offset * i + 6, 1)
            ws.set_column(offset * i + 12, offset * i + 12, 1)
