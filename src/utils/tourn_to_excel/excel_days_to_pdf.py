import os
import time
import win32com.client as win32
import pywintypes

class ExcelToPDFExporter():
    
    @staticmethod
    def export_days_to_pdf(first_n_sheets: int, output_dir: str):

        # Excel file in folder
        xlsx_path = os.path.abspath(os.path.join(output_dir, "tournament.xlsx"))

        # Wait until file exists
        while not os.path.exists(xlsx_path):
            time.sleep(1)
        time.sleep(1)

        try:
            excel = win32.gencache.EnsureDispatch('Excel.Application')
        except pywintypes.com_error as e:
            print("Excel not installed or unavailable.")
            print(f"Details: {e}")
            return

        excel.Visible = False  # No Popup

        try:
            wb = excel.Workbooks.Open(xlsx_path)
        except Exception as e:
            print("Error opening excel file")
            print(f"Details: {e}")
            excel.Quit()
            return


        pdf_folder = os.path.join(output_dir, "pdfs")
        os.makedirs(pdf_folder, exist_ok=True)

        # All sheets in one pdf file
        try:
            sheets = [wb.Sheets(i) for i in range(1, first_n_sheets + 1)]
            wb.Worksheets([s.Name for s in sheets]).Select()

            total_pdf_path = os.path.abspath(os.path.join(pdf_folder, "tournament_all_days.pdf"))
            wb.ActiveSheet.ExportAsFixedFormat(0, total_pdf_path)

            # Every sheet as a single pdf
            for sheet in sheets:
                sheet.Select()  # Select only that sheet
                # Remove invalid characters
                safe_name = "".join(c for c in sheet.Name if c not in r'\/:*?"<>|')
                single_pdf_path = os.path.abspath(os.path.join(pdf_folder, f"{safe_name}.pdf"))
                sheet.ExportAsFixedFormat(0, single_pdf_path)

        except Exception as e:
            print("Error exporting pdfs")
            print(f"Details: {e}")

        finally:
            wb.Close(False)
            excel.Quit()
