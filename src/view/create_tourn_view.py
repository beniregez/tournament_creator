from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CreateTourn(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # TODO: replace with actual tournament schedule
        self.tournament_frame = QFrame()
        self.tournament_frame.setFrameShape(QFrame.Box)
        self.tournament_frame.setFixedHeight(400)

        placeholder = QLabel("TODO: Insert Tournament Plan here")
        placeholder.setFont(QFont("Arial", 12, QFont.Bold))
        placeholder.setAlignment(Qt.AlignCenter)

        frame_layout = QVBoxLayout()
        frame_layout.addWidget(placeholder)
        self.tournament_frame.setLayout(frame_layout)

        main_layout.addWidget(self.tournament_frame)

        # Buttons at the bottom
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)

        regenerate_btn = QPushButton("Regenerate")
        export_btn = QPushButton("Export to Excel")

        for btn in [regenerate_btn, export_btn]:
            btn.setFont(QFont("Arial", 10, QFont.Bold))
            btn.setFixedSize(240, 50)

        regenerate_btn.clicked.connect(self.update_tourn)
        export_btn.clicked.connect(self.export_excel)

        button_layout.addWidget(regenerate_btn)
        button_layout.addWidget(export_btn)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    # TODO Use scheduling module
    def update_tourn(self):
        print("update_tourn() not implemented yet")

    # TODO Use scheduling / export module
    def export_excel(self):
        print("export_excel() not implemented yet")