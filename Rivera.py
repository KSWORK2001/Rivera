from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QRubberBand, QPushButton, QHBoxLayout, QToolBar
from PySide6.QtGui import QAction

from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QGuiApplication, QPixmap, QIcon, QPainter, QCursor
from pytesseract import pytesseract
from PIL import Image
import os
import sys


class SnippingTool(QWidget):
    def __init__(self, parent, pixmap):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.parent = parent

        self.origin = QPoint()
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.pixmap = pixmap
        self.scaled_pixmap = None
        self.display_area = QRect()

    def resizeEvent(self, event):
        """Scale the pixmap to fit the parent label."""
        self.scaled_pixmap = self.pixmap.scaled(
            self.parent.screenshot_label.size(), Qt.AspectRatioMode.KeepAspectRatio
        )
        label_geometry = self.parent.screenshot_label.geometry()
        self.display_area = QRect(label_geometry.topLeft(), self.scaled_pixmap.size())
        self.move(label_geometry.topLeft())
        self.resize(self.scaled_pixmap.size())

    def paintEvent(self, event):
        """Draw the pixmap on the widget."""
        if self.scaled_pixmap:
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.scaled_pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.display_area.contains(event.position().toPoint()):
            self.origin = event.position().toPoint()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.rubber_band and self.display_area.contains(event.position().toPoint()):
            self.rubber_band.setGeometry(QRect(self.origin, event.position().toPoint()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            selected_geometry = QRect(self.origin, event.position().toPoint())
            self.rubber_band.hide()
            self.close()
            # Map selected_geometry to the original pixmap coordinates
            scaled_rect = QRect(
                selected_geometry.x() * self.pixmap.width() / self.scaled_pixmap.width(),
                selected_geometry.y() * self.pixmap.height() / self.scaled_pixmap.height(),
                selected_geometry.width() * self.pixmap.width() / self.scaled_pixmap.width(),
                selected_geometry.height() * self.pixmap.height() / self.scaled_pixmap.height(),
            )
            self.parent.process_snip(scaled_rect)


class RiveraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rivera")

        # Set the application icon
        logo_path = os.path.join(os.getcwd(), "images", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Set a default size for the window
        self.resize(1200, 800)

        # Central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left side layout
        left_layout = QVBoxLayout()
        self.welcome_label = QLabel("Welcome to Rivera!", alignment=Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(self.welcome_label)

        self.start_button = QPushButton("Start Rivera")
        self.start_button.setStyleSheet(
            "background-color: #0078D7; color: white; font-size: 16px; padding: 10px; border-radius: 5px;"
        )
        self.start_button.clicked.connect(self.start_snipping)
        left_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Full-screen and minimize buttons
        self.fullscreen_button = QPushButton("Toggle Fullscreen")
        self.fullscreen_button.setStyleSheet("padding: 8px;")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        left_layout.addWidget(self.fullscreen_button, alignment=Qt.AlignCenter)

        self.minimize_button = QPushButton("Minimize")
        self.minimize_button.setStyleSheet("padding: 8px;")
        self.minimize_button.clicked.connect(self.showMinimized)
        left_layout.addWidget(self.minimize_button, alignment=Qt.AlignCenter)

        # Right side layout for screenshot
        self.screenshot_label = QLabel()
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_label.setStyleSheet("background-color: #f0f0f0;")
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.screenshot_label)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def start_snipping(self):
        screen = QGuiApplication.primaryScreen()
        self.full_pixmap = screen.grabWindow(0)
        self.display_full_screenshot(self.full_pixmap)

    def display_full_screenshot(self, pixmap):
        self.screenshot_label.setPixmap(pixmap.scaled(self.screenshot_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.snipping_tool = SnippingTool(self, pixmap)
        self.snipping_tool.show()

    def process_snip(self, selected_geometry):
        screenshot = self.full_pixmap.copy(selected_geometry)
        screenshot_path = os.path.join(os.getcwd(), "selected_area.png")
        screenshot.save(screenshot_path)
        self.screenshot_label.setPixmap(screenshot.scaled(self.screenshot_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.extract_text_from_image(screenshot_path)

    def extract_text_from_image(self, image_path):
        try:
            pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
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

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


if __name__ == "__main__":
    app = QApplication([])
    window = RiveraApp()
    window.show()
    sys.exit(app.exec())
