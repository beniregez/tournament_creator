import os
import sys
from PyQt5.QtWidgets import QApplication
from controller.controller import Controller
from PyQt5.QtGui import QIcon

app = QApplication(sys.argv)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
app.setWindowIcon(QIcon(icon_path))

controller = Controller()
sys.exit(app.exec_())