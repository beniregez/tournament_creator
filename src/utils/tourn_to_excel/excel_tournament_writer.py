from datetime import datetime, timedelta
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell


from core.event import MatchEvent, OtherEvent
from model.model import Model
from core import EventDay
from utils.tourn_to_excel.data_sheets_writer import DataSheetsWriter
from utils.tourn_to_excel.day_sheets_writer import DaySheetsWriter

class ExcelTournamentWriter():
    def __init__(self, model: Model, output_path: str = "tourn_output", password: str = "password"):
        self.model = model
        self.output_path = output_path
        self.password = password
        self.wb = xlsxwriter.Workbook(f"{self.output_path}.xlsx")
        self.day_sheets_writer = DaySheetsWriter(self.wb, self.model, self.password)
        self.data_sheets_writer = DataSheetsWriter(self.wb, self.model, self.password)

    # Pipeline
    def write_to_excel(self):
        self.day_sheets_writer.write_days_to_excel()
        self.data_sheets_writer.write_sheets_to_excel()
        self.wb.close()
        print("Tournament exported to Excel.")
