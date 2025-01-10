from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QRubberBand, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QGuiApplication, QPixmap, QIcon, QPainter, QCursor
from pytesseract import pytesseract
from PIL import Image
import os
import sys


class SnippingTool(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.setWindowState(Qt.WindowFullScreen)

        self.origin = QPoint()
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.full_screen_pixmap = None

    def set_background_screenshot(self):
        """Capture and set the current screen as a background image."""
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0)
        self.full_screen_pixmap = screenshot

    def paintEvent(self, event):
        """Draw the semi-transparent screenshot as the background."""
        if self.full_screen_pixmap:
            painter = QPainter(self)
            painter.setOpacity(0.6)
            painter.drawPixmap(self.rect(), self.full_screen_pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = QCursor.pos()  # Use QCursor.pos() instead of globalPos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))  # Set initial size to 0
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.rubber_band:
            self.rubber_band.setGeometry(QRect(self.origin, QCursor.pos()).normalized())  # Use QCursor.pos() instead of globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            selected_geometry = QRect(self.origin, QCursor.pos())
            self.rubber_band.hide()
            self.close()
            self.parent().process_snip(selected_geometry)


class RiveraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rivera")

        # Set the application icon
        logo_path = os.path.join(os.getcwd(), "images", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Set the size of the window to be larger
        self.setFixedSize(1000, 600)  # Increased window size for more room

        # Central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()  # Horizontal layout to split the screen

        # Left side layout (for text and buttons)
        left_layout = QVBoxLayout()

        # Welcome Label
        self.welcome_label = QLabel("Welcome to Rivera!", alignment=Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(self.welcome_label)

        # Start Rivera Button
        self.start_button = QPushButton("Start Rivera")
        self.start_button.setStyleSheet(
            "background-color: #0078D7; color: white; font-size: 16px; padding: 10px; border-radius: 5px;"
        )
        self.start_button.clicked.connect(self.start_snipping)
        left_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Right side layout (for screenshot display)
        self.screenshot_label = QLabel()
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_label.setStyleSheet("background-color: #f0f0f0;")  # Light gray background for the screenshot

        # Set fixed width for the screenshot label to always take up the right half of the screen
        self.screenshot_label.setFixedWidth(self.width() // 2)

        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.screenshot_label)

        # Set the central widget and main layout
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Store the screenshot path
        self.screenshot_path = None

    def start_snipping(self):
        self.welcome_label.setText("Select a screen area to read!")
        self.snipping_tool = SnippingTool(self)
        self.snipping_tool.set_background_screenshot()
        self.snipping_tool.show()

    def process_snip(self, selected_geometry):
        # Capture the selected screen area
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0, selected_geometry.x(), selected_geometry.y(),
                                       selected_geometry.width(), selected_geometry.height())
        screenshot_path = os.path.join(os.getcwd(), "selected_area.png")
        screenshot.save(screenshot_path)

        # Display the screenshot on the right side
        self.display_screenshot(screenshot_path)

        # Use OCR to extract text from the screenshot
        self.extract_text_from_image(screenshot_path)

    def display_screenshot(self, screenshot_path):
        # Store the screenshot path to reuse for selecting new areas
        self.screenshot_path = screenshot_path

        # Display the original or selected screenshot on the right side
        pixmap = QPixmap(screenshot_path)
        pixmap = pixmap.scaled(self.screenshot_label.size(), Qt.AspectRatioMode.KeepAspectRatio)  # Scale to fit
        self.screenshot_label.setPixmap(pixmap)

    def extract_text_from_image(self, image_path):
        try:
            pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update with your Tesseract path
            image = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(image)
            self.display_extracted_text(extracted_text.strip())
        except Exception as e:
            self.welcome_label.setText(f"Error: {e}")

    def display_extracted_text(self, text):
        if text:
            self.welcome_label.setText(f"Extracted text:\n{text}")
        else:
            self.welcome_label.setText("No text detected. Try selecting a different area.")


if __name__ == "__main__":
    app = QApplication([])
    window = RiveraApp()
    window.show()
    sys.exit(app.exec())
