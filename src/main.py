import sys
from PyQt5.QtWidgets import QApplication
from controller.controller import Controller
from PyQt5.QtGui import QIcon

app = QApplication(sys.argv)

app.setWindowIcon(QIcon("C:/Users/benja/Workspace/2025_Tournament_Creator/tournament_creator/src/assets/icon.ico"))

controller = Controller()
sys.exit(app.exec_())