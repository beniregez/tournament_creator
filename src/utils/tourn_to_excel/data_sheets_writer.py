from xlsxwriter.utility import xl_rowcol_to_cell

from model.model import Model
from utils.tourn_to_excel.day_sheets_writer import DaySheetsWriter

class DataSheetsWriter():

    def __init__(self, wb, model: Model, password: str):
        self.wb = wb

        self.model = model
        self.tourn_generated = self.model.get_tournament_generated()
        self.days = self.model.get_days()
        self.group_info = self.model.get_group_info()

        self.password = password
        self.day_sheet_names = [day["Title"] for day in self.model.get_days()]

        self.team_color_formats = {}

    def write_sheets_to_excel(self):
        self.write_data_sheet_to_excel()
        self.write_scoreboard_sheet_to_excel()


    ##### Pipelines for sheets #####

    def write_data_sheet_to_excel(self):
        self.init_data_sheet()
        self.define_cell_formats_data_sheet()
        self.write_data_headers(row_offset=1)
        self.write_data_rows(row_offset=1)
        self.set_data_sheet_col_widths()

    def write_scoreboard_sheet_to_excel(self):
        self.init_scoreboard_sheet()


    ##### Data sheet functions #####

    def init_data_sheet(self, name: str = "Data"):
        self.data_sheet = self.wb.add_worksheet(name)
        print("Sheet:", self.data_sheet.get_name(), "created.")

    def define_cell_formats_data_sheet(self):
        self.bold_format = self.wb.add_format({'bold': True, 'align': 'center'})

        self.color_font_formats = []
        self.color_font_formats.append(self.wb.add_format({'font_color': "#FF0000", 'align': 'center'}))
        self.color_font_formats.append(self.wb.add_format({'font_color': "#FF9900", 'align': 'center'}))
        self.color_font_formats.append(self.wb.add_format({'font_color': "#FFD500", 'align': 'center'}))
        self.color_font_formats.append(self.wb.add_format({'font_color': "#8CFF00", 'align': 'center'}))
        self.color_font_formats.append(self.wb.add_format({'font_color': "#00C3FF", 'align': 'center'}))
        self.color_font_formats.append(self.wb.add_format({'font_color': "#3700FF", 'align': 'center'}))
        self.color_font_formats.append(self.wb.add_format({'font_color': "#EA00FF", 'align': 'center'}))

        self.standard_format = self.wb.add_format({'align': 'center'})

    def write_data_headers(self, row_offset):
        subtitles = ["Teams", "Rang", "Punkte", "TD", "T", "GT", "S", "U", "N", "Total Sp", "gesp.", "Ber. Rang"]
        for s_idx, s in enumerate(subtitles):
            self.data_sheet.write(0 + row_offset, s_idx, s, self.bold_format)
    
    # Fill in all metrics from day sheets. Compute total metrics for scoreboard.
    def write_data_rows(self, row_offset):
        day_col_offsets = self._get_day_col_offsets()
        day_col_offsets = day_col_offsets[:-1]  # Remove last element

        cats = self.model.get_categories()
        row_idx = 1 + row_offset
        
        # Metric names
        metr_names = ["Pts", "Tore", "GTore", "S", "U", "N", "Sp"]
        
        for cat in cats:            
            # Write metric headers
            for day_idx, day in enumerate(self.tourn_generated):
                for metr in range(7):
                    self.data_sheet.write(row_idx - 1, day_col_offsets[day_idx] + metr, f"{metr_names[metr]}{day_idx + 1}", self.color_font_formats[metr])

            # Get category range for rank computation cells (needed later)
            cat_comp_rank_cell_range = self._get_formula_row_range(row_idx, len(cat.teams) - 1, 11)

            for team_idx, team in enumerate(cat.teams):
                self.data_sheet.write(row_idx, 0, team.name, self._add_and_get_color_format(team.color))
                
                # 1. Collect and sum up metrics per day
                for day_idx, day in enumerate(self.tourn_generated):
                    day_col_offset = day_col_offsets[day_idx]
                    num_fields = day.max_fields()

                    mtrc_col_range = (num_fields * 2)
                    day_num_rows = day.total_events() + 3

                    # Metric sums from one day
                    for metr in range(7):
                        formula = f"SUM({self._get_formula_col_range(row_idx, day_col_offset + 7 + (mtrc_col_range * metr), mtrc_col_range - 1)})"
                        self.data_sheet.write_formula(row_idx, day_col_offset + metr, formula, self.color_font_formats[metr])

                    # Collect metrics from every field
                    day_name = self.day_sheet_names[day_idx]
                    curr_team_cell = xl_rowcol_to_cell(row_idx, 0)
                    for metr in range(7):
                        start_col_idx = day_col_offset + 7 + (mtrc_col_range * metr)
                        for i in range(mtrc_col_range):
                            if metr == 0:   # Points
                                pts_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_point_col_idx(i))
                                teams_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_team_col_idx(i))
                                formula = f"SUMIFS('{day_name}'!{pts_row_range}, '{day_name}'!{teams_row_range}, {curr_team_cell})"
                                self.data_sheet.write_formula(row_idx, start_col_idx + i, formula, self.color_font_formats[metr])
                            elif metr == 1: # Goals
                                res_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_result_col_idx(i))
                                teams_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_team_col_idx(i))
                                formula = f"SUMIFS('{day_name}'!{res_row_range}, '{day_name}'!{teams_row_range}, {curr_team_cell})"
                                self.data_sheet.write_formula(row_idx, start_col_idx + i, formula, self.color_font_formats[metr])
                            elif metr == 2: # Counter Goals
                                if i % 2 == 0:  j = i + 1
                                else:           j = i - 1
                                res_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_result_col_idx(j))
                                teams_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_team_col_idx(i))
                                formula = f"SUMIFS('{day_name}'!{res_row_range}, '{day_name}'!{teams_row_range}, {curr_team_cell})"
                                self.data_sheet.write_formula(row_idx, start_col_idx + i, formula, self.color_font_formats[metr])
                            elif metr == 3: # Wins
                                pts_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_point_col_idx(i))
                                teams_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_team_col_idx(i))
                                formula = f"COUNTIFS('{day_name}'!{teams_row_range}, {curr_team_cell}, '{day_name}'!{pts_row_range}, \"2\")"
                                self.data_sheet.write_formula(row_idx, start_col_idx + i, formula, self.color_font_formats[metr])
                            elif metr == 4: # Draws
                                pts_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_point_col_idx(i))
                                teams_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_team_col_idx(i))
                                formula = f"COUNTIFS('{day_name}'!{teams_row_range}, {curr_team_cell}, '{day_name}'!{pts_row_range}, \"1\")"
                                self.data_sheet.write_formula(row_idx, start_col_idx + i, formula, self.color_font_formats[metr])
                            elif metr == 5: # Losses
                                pts_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_point_col_idx(i))
                                teams_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_team_col_idx(i))
                                formula = f"COUNTIFS('{day_name}'!{teams_row_range}, {curr_team_cell}, '{day_name}'!{pts_row_range}, \"0\")"
                                self.data_sheet.write_formula(row_idx, start_col_idx + i, formula, self.color_font_formats[metr])
                            elif metr == 6: # Games
                                teams_row_range = self._get_formula_row_range(1, day_num_rows, DaySheetsWriter.get_team_col_idx(i))
                                formula = f"COUNTIF('{day_name}'!{teams_row_range}, {curr_team_cell})"
                                self.data_sheet.write_formula(row_idx, start_col_idx + i, formula, self.color_font_formats[metr])
                    
                # TODO: 2. Sum up from all days and compute ranking
                self.data_sheet.write_formula(row_idx, 2, self._get_sum_cells_formula(row_idx, day_col_offsets), self.color_font_formats[0])
                self.data_sheet.write_formula(row_idx, 3, f"{xl_rowcol_to_cell(row_idx, 4)} - {xl_rowcol_to_cell(row_idx, 5)}", self.standard_format)
                for i in range(0, 6):
                    self.data_sheet.write_formula(row_idx, 4 + i, self._get_sum_cells_formula(row_idx, [(x + 1 + i) for x in day_col_offsets]), self.color_font_formats[1 + i])
                self.data_sheet.write_formula(row_idx, 10, f"{self._get_sum_cells_formula(row_idx, [6, 7, 8])}", self.standard_format)
                # Compute rank. Exact same metrics still result in different ranking because of added {team_idx} such that
                # two teams always will have a different ranking.
                comp_rank_formula = f"{xl_rowcol_to_cell(row_idx, 2)} * 10^16" \
                                    f" + {xl_rowcol_to_cell(row_idx, 3)} * 10^12" \
                                    f" + {xl_rowcol_to_cell(row_idx, 4)} * 10^8" \
                                    f" - {xl_rowcol_to_cell(row_idx, 5)} * 10^5" \
                                    f" + {xl_rowcol_to_cell(row_idx, 6)} * 10^2" \
                                    f" + {team_idx}"
                self.data_sheet.write_formula(row_idx, 11, comp_rank_formula, self.standard_format)
                rank_formula = f"RANK({xl_rowcol_to_cell(row_idx, 11)}, {cat_comp_rank_cell_range})"
                self.data_sheet.write_formula(row_idx, 1, rank_formula, self.bold_format)
                

                row_idx += 1
            row_idx += 2    # Spacer of 2 rows between two categories.

    def set_data_sheet_col_widths(self):
        self.data_sheet.set_column(0, 0, 22)

        day_col_offsets = self._get_day_col_offsets()
        for i in range(len(day_col_offsets) - 1):
            self.data_sheet.set_column(day_col_offsets[i], day_col_offsets[i] + 6, 5)
            self.data_sheet.set_column(day_col_offsets[i] + 7, day_col_offsets[i + 1] - 2, 3)

    def _get_day_col_offsets(self):
        num_days = len(self.tourn_generated)
        day_col_offsets = [13]
        for day_idx in range(num_days):
            num_fields = self.tourn_generated[day_idx].max_fields()
            prev_col_idx = day_col_offsets[-1]
            curr_col_idx = prev_col_idx + 7 * (2 * num_fields + 1) + 1  # 7 Metrics, 2 per field (home & away), 1 for sum col. 1 Spacer col.
            day_col_offsets.append(curr_col_idx)
        return day_col_offsets

    # Add format with background color to dict. Return format with background color.
    def _add_and_get_color_format(self, color_hex):
        if color_hex not in self.team_color_formats:
            self.team_color_formats[color_hex] = self.wb.add_format({
                'bg_color': color_hex,
                'font_size': 11,
                'valign': 'vcenter'
                })
        return self.team_color_formats[color_hex]

    def _get_formula_col_range(self, row_idx, col_idx, col_delta, absolute=False):
        """
        Returns a string with a cell range in one row for excel formula.
        """
        start_cell = xl_rowcol_to_cell(row_idx, col_idx, row_abs=absolute, col_abs=absolute)
        end_cell = xl_rowcol_to_cell(row_idx, col_idx + col_delta, row_abs=absolute, col_abs=absolute)
        return f"{start_cell}:{end_cell}"

    def _get_formula_row_range(self, row_idx, row_delta, col_idx, absolute=False):
        """
        Returns a string with a cell range in one column for excel formula.
        """
        start_cell = xl_rowcol_to_cell(row_idx, col_idx, row_abs=absolute, col_abs=absolute)
        end_cell = xl_rowcol_to_cell(row_idx + row_delta, col_idx, row_abs=absolute, col_abs=absolute)
        return f"{start_cell}:{end_cell}"

    def _get_sum_cells_formula(self, row_idx, col_indices):
        """
        Returns a formula that sums up all cells from column indices in one row.
        """
        cells = []
        for col_idx in col_indices:
            cells.append(xl_rowcol_to_cell(row_idx, col_idx))
        return f"=SUM({','.join(cells)})"


    ##### Scoreboard sheet functions #####

    def init_scoreboard_sheet(self, name: str = "Scoreboard"):
        self.scoreboard_sheet = self.wb.add_worksheet(name)
        print("Sheet:", self.scoreboard_sheet.get_name(), "created.")
