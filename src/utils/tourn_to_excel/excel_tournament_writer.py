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
    def __init__(self, model: Model, output_path: str = "tourn_output"):
        self.model = model
        self.output_path = output_path
        self.wb = xlsxwriter.Workbook(f"{self.output_path}.xlsx")
        self.day_sheets_writer = DaySheetsWriter(self.wb, self.model)
        self.data_sheets_writer = DataSheetsWriter(self.wb, self.model)

    # Pipeline
    def write_to_excel(self):
        self.day_sheets_writer.write_days_to_excel()
        self.data_sheets_writer.write_sheets_to_excel()
        self.wb.close()
        print("Tournament exported to Excel.")

        # # Wait until file exists
        # while not os.path.exists(f"{self.output_path}.xlsx"):
        #     time.sleep(1)
        
        # # Waiting time for security reasons
        # time.sleep(1)

        ExcelToPDFExporter.export_days_to_pdf(len(self.model.get_tournament_generated()), self.output_path)
        print("Tournament exported to pdf.")