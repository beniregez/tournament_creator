import sys
from PyQt5.QtWidgets import QApplication
from controller.controller import Controller

app = QApplication(sys.argv)
controller = Controller()
sys.exit(app.exec_())