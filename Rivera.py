from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

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

    def start_screen_reader(self):
        # Placeholder for the screen reader functionality
        self.welcome_label.setText("Screen Reader Started! (Placeholder)")

if __name__ == "__main__":
    app = QApplication([])
    window = RiveraApp()
    window.show()
    app.exec()
