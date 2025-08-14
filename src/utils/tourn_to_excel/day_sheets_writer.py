from datetime import datetime, timedelta
from core.event import MatchEvent, OtherEvent
from model.model import Model

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

class DaySheetsWriter():
    def __init__(self, wb, model: Model, password: str):
        self.wb = wb
        self.model = model
        self.password = password
        self.tourn_generated = self.model.get_tournament_generated()
        self.team_color_formats = {}

    def write_days_to_excel(self):
        self.initialize_sheets()
        self.define_cell_formats()
        self.set_col_widths()
        self.write_title_rows()
        self.write_header_rows()
        self.write_time_slots(start_row_idx=2)
        self.write_events(start_row_idx=2)

    def initialize_sheets(self):
        self.worksheets = []
        for day in self.model.get_days():
            sheet = self.wb.add_worksheet(day["Title"])
            print("Sheet:", sheet.get_name(), "created.")
            # self.worksheets.append(day["Title"])
            self.worksheets.append(sheet)
            sheet.hide_gridlines(2)


    def define_cell_formats(self):
        # Title row
        self.title_format = self.wb.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'top': 2, 'bottom': 2
        })
        self.title_left_format = self.wb.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'top': 2, 'bottom': 2, 'left': 2
        })
        self.title_right_format = self.wb.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'top': 2, 'bottom': 2, 'right': 2
        })
        # Header row
        self.header_format = self.wb.add_format({
            'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1
        })
        self.header_left_fat_format = self.wb.add_format({
            'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1, 'left': 2
        })
        self.header_right_fat_format = self.wb.add_format({
            'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1, 'right': 2
        })
        self.header_left_format = self.wb.add_format({
            'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1, 'left': 1
        })
        self.header_right_format = self.wb.add_format({
            'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1, 'right': 1
        })

        self.standard_format = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter'
        })

        self.standard_border_format = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1
        })
        self.standard_left_border_format = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1, 'left': 1
        })
        self.standard_right_border_format = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1, 'right': 1
        })
        # Start time cells
        self.standard_format_all_borders = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        self.standard_format_all_borders_left_fat = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1, 'left': 2, 'right': 1
        })
        self.standard_format_all_borders_right_fat = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1, 'bottom': 1, 'left': 1, 'right': 2
        })
        # Bottom row border
        self.bottom_row_fat_border_format = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 2
        })
        self.bottom_row_border_format = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'top': 1
        })
        # Right col border
        self.lef_col_border_format = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'left': 1
        })


        self.bold_format = self.wb.add_format({
            'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter'
        })
        self.result_cell_format = self.wb.add_format({
            'bg_color': '#B7FFFF', 'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        self.ref_cell_format = self.wb.add_format({
            'bg_color': '#F9F9F9', 'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        self.colon_cell_format = self.wb.add_format({
            'bold': False, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1
        })

    def set_col_widths(self):
        for day_idx, day in enumerate(self.tourn_generated):
            ws = self.worksheets[day_idx]
            for field_idx in range(day.max_fields()):
                center_col_idx = self._get_field_center_col_idx(field_idx)
                ws.set_column(center_col_idx, center_col_idx, 1)    # Field center col
                for col_idx in [center_col_idx - 1, center_col_idx + 1]:
                    ws.set_column(col_idx, col_idx, 2)   # Result cols
                for col_idx in [center_col_idx - 2, center_col_idx + 2]:
                    ws.set_column(col_idx, col_idx, 22)   # Team cols
                for col_idx in [center_col_idx - 3, center_col_idx + 3]:
                    ws.set_column(col_idx, col_idx, None, None, {'hidden': True})   # Hide point cols
                for col_idx in [center_col_idx - 4, center_col_idx + 4]:
                    ws.set_column(col_idx, col_idx, 5)   # Time cols
                ref_col_idx = self._get_ref_col_idx(day.max_fields(), field_idx)
                ws.set_column(ref_col_idx, ref_col_idx, 10)

    # Write first row with title, date and location
    def write_title_rows(self):
        days = self.model.get_days()
        for day_idx, day in enumerate(days):
            ws = self.worksheets[day_idx]
            num_fields = self.tourn_generated[day_idx].max_fields()
            # Top and bottom border for all rows without first and last
            for col_idx in range(1, self._get_time_col_idx(num_fields) - 1):
                ws.write(0, col_idx, "", self.title_format)
            ws.write(0, 0, "", self.title_left_format)  # Borders for first col
            ws.write(0, self._get_time_col_idx(num_fields), "", self.title_right_format)  # Borders for last col
            # Header text
            col_idx = self._get_center_col_idx(num_fields)
            header_text = f"{days[day_idx]["Date"]} ({days[day_idx]["Title"]}) in {days[day_idx]["Location"]}"
            ws.write(0, col_idx, header_text, self.title_format)

    # Write second row with headers (time, field numbers, referee)
    def write_header_rows(self):
        # Iterate over every day
        for day_idx, day in enumerate(self.tourn_generated):
            num_fields = day.max_fields()
            ws = self.worksheets[day_idx]

            # Top and bottom border for all rows without first and last
            for col_idx in range(1, self._get_time_col_idx(num_fields) - 1):
                ws.write(1, col_idx, "", self.header_format)

            # Time for every field + in last row
            for n in range(num_fields + 1):
                col_idx = self._get_time_col_idx(n)
                if n == 0:
                    ws.write(1, col_idx, "Zeit", self.header_left_fat_format)
                elif n == (num_fields):
                    ws.write(1, col_idx, "Zeit", self.header_right_fat_format)
                else:
                    ws.write(1, col_idx, "Zeit", self.header_format)

            # Field + number for every field
            for n in range(num_fields):
                col_idx = self._get_field_center_col_idx(n)
                ws.write(1, col_idx, f"Feld {n + 1}", self.header_format)

            # Referee + number for every field
            for n in range(num_fields):
                col_idx = self._get_ref_col_idx(num_fields, n)
                if n == 0:
                    ws.write(1, col_idx, f"Schiri Feld {n + 1}", self.header_left_format)
                elif n == num_fields - 1:
                    ws.write(1, col_idx, f"Schiri Feld {n + 1}", self.header_right_format)
                else:
                    ws.write(1, col_idx, f"Schiri Feld {n + 1}", self.header_format)

    # Write all starting times
    def write_time_slots(self, start_row_idx):
        model_days = self.model.get_days()
        for day_idx, day in enumerate(self.tourn_generated):
            num_fields = day.max_fields()
            ws = self.worksheets[day_idx]
            curr_time = datetime.strptime(model_days[day_idx]["Start time"], "%H:%M")
            # Time for every field + in last row
            for ev_idx, event in enumerate(day.get_all_valid_events()):
                for n in range(num_fields + 1):
                    col_idx = self._get_time_col_idx(n)
                    if n == 0:
                        ws.write(start_row_idx + ev_idx, col_idx, f"{curr_time.strftime("%H:%M")}", self.standard_format_all_borders_left_fat)
                    elif n == num_fields:
                        ws.write(start_row_idx + ev_idx, col_idx, f"{curr_time.strftime("%H:%M")}", self.standard_format_all_borders_right_fat)
                    else:
                        ws.write(start_row_idx + ev_idx, col_idx, f"{curr_time.strftime("%H:%M")}", self.standard_format_all_borders)
                curr_time += timedelta(minutes=event.duration)
            # Add ending time
            for n in range(num_fields + 1):
                col_idx = self._get_time_col_idx(n)
                if n == 0:
                    ws.write(start_row_idx + ev_idx + 1, col_idx, f"{curr_time.strftime("%H:%M")}", self.standard_format_all_borders_left_fat)
                elif n == num_fields:
                    ws.write(start_row_idx + ev_idx + 1, col_idx, f"{curr_time.strftime("%H:%M")}", self.standard_format_all_borders_right_fat)
                else:
                    ws.write(start_row_idx + ev_idx + 1, col_idx, f"{curr_time.strftime("%H:%M")}", self.standard_format_all_borders)

    # Write all events + bottom row border
    def write_events(self, start_row_idx):
        for day_idx, day in enumerate(self.tourn_generated):
            num_fields = day.max_fields()
            ws = self.worksheets[day_idx]
            for ev_idx, ev in enumerate(day.get_all_valid_events()):
                if isinstance(ev, OtherEvent):
                    self._write_other_event(ws, ev, ev_idx + start_row_idx, num_fields)
                elif isinstance(ev, MatchEvent):
                    self._write_match_event(ws, ev, ev_idx + start_row_idx, num_fields)
                self._draw_right_col_border(ws, ev_idx + start_row_idx, num_fields)
            self._draw_bottom_row_borders(ws, ev_idx + start_row_idx + 2, num_fields)
            self._draw_right_col_border(ws, ev_idx + start_row_idx + 1, num_fields)

    def _write_other_event(self, worksheet, event: OtherEvent, row_idx, num_fields):
        for col_idx in range(1, self._get_time_col_idx(num_fields)):
            worksheet.write(row_idx, col_idx, "", self.standard_border_format)
        col_idx = self._get_center_col_idx(num_fields)
        worksheet.write(row_idx, col_idx, event.label, self.standard_border_format)

    # Write match_event including ref cells
    def _write_match_event(self, worksheet, event: MatchEvent, row_idx, num_fields):
        for m_idx, match in enumerate(event.matches):
            center_col_idx = self._get_field_center_col_idx(m_idx)
            home_format = self._add_and_get_color_format(match.team1.color)
            worksheet.write(row_idx, center_col_idx - 2, match.team1.name, home_format)   # Home team
            away_format = self._add_and_get_color_format(match.team2.color)
            worksheet.write(row_idx, center_col_idx + 2, match.team2.name, away_format)   # Away team
            self._write_points_cells(worksheet, row_idx, center_col_idx)
            self._write_result_cells(worksheet, row_idx, center_col_idx)
            self._write_ref_cells(worksheet, row_idx, num_fields, m_idx)

    def _write_points_cells(self, worksheet, row_idx, center_col_idx):
        home_res_cell = xl_rowcol_to_cell(row_idx, center_col_idx - 1)
        away_res_cell = xl_rowcol_to_cell(row_idx, center_col_idx + 1)
        # left points cell
        left_formula = f'=IF(AND(NOT(ISBLANK({home_res_cell})), NOT(ISBLANK({away_res_cell}))), IF({home_res_cell}>{away_res_cell}, 2, IF({home_res_cell}<{away_res_cell}, 0, IF({home_res_cell}={away_res_cell}, 1, " "))), " ")'
        worksheet.write_formula(row_idx, center_col_idx - 3, left_formula)
        # right points cell
        right_formula = f'=IF(AND(NOT(ISBLANK({home_res_cell})), NOT(ISBLANK({away_res_cell}))), IF({home_res_cell}<{away_res_cell}, 2, IF({home_res_cell}>{away_res_cell}, 0, IF({home_res_cell}={away_res_cell}, 1, " "))), " ")'
        worksheet.write_formula(row_idx, center_col_idx + 3, right_formula)

    def _write_result_cells(self, worksheet, row_idx, center_col_idx):
        for col_idx in [center_col_idx - 1, center_col_idx + 1]:
            worksheet.write(row_idx, col_idx, "", self.result_cell_format)
        worksheet.write(row_idx, center_col_idx, ":", self.colon_cell_format)

    def _write_ref_cells(self, worksheet, row_idx, num_fields, field_idx):
        # for field_idx in range(0, num_fields):
        col_idx = self._get_ref_col_idx(num_fields, field_idx)
        worksheet.write(row_idx, col_idx, "", self.ref_cell_format)

    def _draw_bottom_row_borders(self, worksheet, row_idx, num_fields):
        for col_idx in range(0, self._get_time_col_idx(num_fields) + 1):
            worksheet.write(row_idx, col_idx, "", self.bottom_row_fat_border_format)
        for field_idx in range(num_fields):
            col_idx = self._get_ref_col_idx(num_fields, field_idx)
            worksheet.write(row_idx, col_idx, "", self.bottom_row_border_format)

    def _draw_right_col_border(self, worksheet, row_idx, num_fields):
        col_idx = self._get_ref_col_idx(num_fields, num_fields)
        worksheet.write(row_idx, col_idx, "", self.lef_col_border_format)

    # Add format with background color to dict (including borders). Return format with background color.
    def _add_and_get_color_format(self, color_hex):
        if color_hex not in self.team_color_formats:
            self.team_color_formats[color_hex] = self.wb.add_format({
                'bg_color': color_hex,
                'font_size': 11,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
                })
        return self.team_color_formats[color_hex]


    ###############   Helper methods for column indexing   ###############

    # Get center column index: graphical, not arithmetical
    def _get_center_col_idx(self, max_fields: int):
        return 4 + 4 * (max_fields - 1)

    # Get time col index for the n-th field
    def _get_time_col_idx(self, field_idx):
        return 0 + (field_idx * 8)

    # Get center col index for the n-th field
    def _get_field_center_col_idx(self, field_idx):
        return 4 + (field_idx * 8)

    # Get index for n-th referee column 
    def _get_ref_col_idx(self, num_fields, field_idx):
        return (num_fields * 8) + 1 + field_idx

