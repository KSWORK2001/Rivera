from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QRubberBand
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QGuiApplication

class RiveraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rivera")
        self.setFixedSize(400, 300)

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Welcome Label
        self.welcome_label = QLabel("Welcome to Rivera!", alignment=Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.welcome_label)

        # Start Rivera Button
        self.start_button = QPushButton("Start Rivera")
        self.start_button.setStyleSheet(
            "background-color: #0078D7; color: white; font-size: 16px; padding: 10px; border-radius: 5px;"
        )
        self.start_button.clicked.connect(self.start_screen_reader)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Set layout
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Variables for frame selection
        self.origin = QPoint()
        self.rubber_band = None

    def start_screen_reader(self):
        self.welcome_label.setText("Select a screen area to read!")
        self.setWindowOpacity(0.5)  # Make the window semi-transparent for clarity
        self.grabMouse()  # Start capturing mouse events

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.globalPos()
            self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
            self.rubber_band.setGeometry(QRect(self.origin, QSize(1, 1)))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.rubber_band:
            self.rubber_band.setGeometry(QRect(self.origin, event.globalPos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rubber_band:
            selected_area = self.rubber_band.geometry()
            self.rubber_band.hide()
            self.rubber_band.deleteLater()
            self.rubber_band = None
            self.releaseMouse()
            self.setWindowOpacity(1.0)  # Restore window opacity

            # Placeholder for OCR functionality
            self.welcome_label.setText(f"Selected area: {selected_area}")

if __name__ == "__main__":
    app = QApplication([])
    window = RiveraApp()
    window.show()
    app.exec()
