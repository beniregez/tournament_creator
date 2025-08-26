import os
import time
import win32com.client as win32

class ExcelToPDFExporter():
    
    def __init__(self):
        pass

    @staticmethod
    def export_days_to_pdf(first_n_sheets: int, output_path):

        # Wait until file exists
        while not os.path.exists(f"{output_path}.xlsx"):
            time.sleep(1)
        
        # Waiting time for security reasons
        time.sleep(1)

        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = False  # No Popup

        # Enforce absolute paths
        xlsx_path = os.path.abspath(f"{output_path}.xlsx")

        wb = excel.Workbooks.Open(xlsx_path)

        # Create new directory for pdfs
        pdf_folder = os.path.abspath(f"{output_path}_pdfs")
        os.makedirs(pdf_folder, exist_ok=True)

        # All sheets in one pdf file
        sheets = [wb.Sheets(i) for i in range(1, first_n_sheets + 1)]
        wb.Worksheets([s.Name for s in sheets]).Select()
        total_pdf_path = os.path.join(pdf_folder, f"{output_path}.pdf")
        wb.ActiveSheet.ExportAsFixedFormat(0, total_pdf_path)

        # Every sheet as a single pdf
        for sheet in sheets:
            sheet.Select()  # Select only that sheet
            # Remove invalid characters
            safe_name = "".join(c for c in sheet.Name if c not in r'\/:*?"<>|')
            single_pdf_path = os.path.join(pdf_folder, f"{safe_name}.pdf")
            sheet.ExportAsFixedFormat(0, single_pdf_path)

        wb.Close(False)
        excel.Quit()
