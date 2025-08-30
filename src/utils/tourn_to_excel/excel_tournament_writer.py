from datetime import datetime, timedelta
import xlsxwriter
import time, os

from core.event import MatchEvent, OtherEvent
from model.model import Model
from core import EventDay
from utils.tourn_to_excel.data_sheets_writer import DataSheetsWriter
from utils.tourn_to_excel.day_sheets_writer import DaySheetsWriter
from utils.tourn_to_excel.excel_days_to_pdf import ExcelToPDFExporter

class ExcelTournamentWriter():
    def __init__(self, model: Model, output_dir: str = "tourn_output"):
        self.model = model
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.excel_path = os.path.join(self.output_dir, "tournament.xlsx")

        self.wb = xlsxwriter.Workbook(self.excel_path)
        self.day_sheets_writer = DaySheetsWriter(self.wb, self.model)
        self.data_sheets_writer = DataSheetsWriter(self.wb, self.model)

    # Pipeline
    def write_to_excel(self):
        day_sheets = self.day_sheets_writer.write_days_to_excel()
        self.data_sheets_writer.write_sheets_to_excel()
        self.data_sheets_writer.write_scoreboards_on_day_sheets(day_sheets)
        self.wb.close()
        print(f"Tournament exported to Excel at {self.excel_path}")

        ExcelToPDFExporter.export_days_to_pdf(
            len(self.model.get_tournament_generated()), 
            self.output_dir
        )
        print(f"Tournament exported to PDF in {self.output_dir}")