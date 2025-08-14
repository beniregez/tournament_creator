from model.model import Model


class DataSheetsWriter():

    def __init__(self, wb, model: Model, password: str):
        self.wb = wb
        self.model = model
        self.password = password

    def write_data_sheets_to_excel(self):
        print("TODO: implement data sheet writer")