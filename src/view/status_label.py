from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, QPropertyAnimation, Qt
from PyQt5.QtGui import QFont

class StatusLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFont(QFont("Arial", 11))
        self.setAlignment(Qt.AlignCenter)
        self.setText(" ")
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: transparent;
            }
        """)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_in_anim = None
        self.fade_out_anim = None

    def show_message(self, message: str, duration: int = 3000):
        self.setText(message)
        self.setVisible(True)

        # Set visible style
        self.setStyleSheet("""
            QLabel {
                background-color: #ffcc00;
                color: #000000;
                border: 1px solid #ffaa00;
                border-radius: 4px;
                padding: 6px;
            }
        """)

        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_anim.setDuration(400)
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)
        self.fade_in_anim.start()

        QTimer.singleShot(duration, self.fade_out)


    def fade_out(self):
        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_anim.setDuration(400)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.finished.connect(self.reset_label)
        self.fade_out_anim.start()


    def reset_label(self):
        self.setText(" ")
        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: transparent;
            }
        """)
        self.setVisible(True)