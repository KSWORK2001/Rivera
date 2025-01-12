from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QRubberBand,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
)
from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QGuiApplication, QPixmap, QIcon, QPainter
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
        """Scale the pixmap to fit the parent label and update display area."""
        self.scaled_pixmap = self.pixmap.scaled(
            self.parent.screenshot_label.size(), Qt.AspectRatioMode.KeepAspectRatio
        )
        label_geometry = self.parent.screenshot_label.geometry()
        self.display_area = QRect(label_geometry.topLeft(), self.scaled_pixmap.size())
        self.move(label_geometry.topLeft())
        self.resize(self.scaled_pixmap.size())

    def paintEvent(self, event):
        """Draw the scaled pixmap on the widget."""
        if self.scaled_pixmap:
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.scaled_pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            global_point = event.globalPosition().toPoint()

            # Adjust the global point to the display area
            local_point = global_point - self.display_area.topLeft()

            if self.display_area.contains(global_point):
                self.origin = local_point
                self.rubber_band.setGeometry(QRect(self.origin, QSize()))
                self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.rubber_band:
            global_point = event.globalPosition().toPoint()

            # Adjust the global point to the display area
            local_point = global_point - self.display_area.topLeft()

            if self.display_area.contains(global_point):
                self.rubber_band.setGeometry(QRect(self.origin, local_point).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            global_point = event.globalPosition().toPoint()

            # Adjust the global point to the display area
            local_point = global_point - self.display_area.topLeft()

            if self.display_area.contains(global_point):
                selected_geometry = QRect(self.origin, local_point).normalized()
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

        # Set the initial size and allow resizing
        self.resize(1000, 600)
        self.setMinimumSize(800, 500)  # Optional: Prevent the window from being too small

        # Central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()  # Horizontal layout to split the screen

        # Left side layout (for text and buttons)
        left_layout = QVBoxLayout()

        # Start Rivera Button
        self.start_button = QPushButton("Start Rivera")
        self.start_button.setStyleSheet(
            "background-color: #0078D7; color: white; font-size: 16px; padding: 10px; border-radius: 5px;"
        )
        self.start_button.clicked.connect(self.start_snipping)
        left_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Text Editor for extracted text
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Extracted text will appear here...")
        self.text_editor.setStyleSheet("font-size: 14px; padding: 5px;")
        left_layout.addWidget(self.text_editor)

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
        # Capture the full screen as a pixmap
        screen = QGuiApplication.primaryScreen()
        self.full_pixmap = screen.grabWindow(0)  # Save the full-screen pixmap

        # Display the full screenshot in the right space and start the snipping tool
        self.display_full_screenshot(self.full_pixmap)

    def display_full_screenshot(self, pixmap):
        self.display_screenshot(pixmap)  # Set up display in label
        self.snipping_tool = SnippingTool(self, pixmap)
        self.snipping_tool.show()

    def process_snip(self, selected_geometry):
        # Capture the selected screen area
        screenshot = self.full_pixmap.copy(selected_geometry)
        screenshot_path = os.path.join(os.getcwd(), "selected_area.png")
        screenshot.save(screenshot_path)
        self.display_screenshot(screenshot)
        self.extract_text_from_image(screenshot_path)

    def display_screenshot(self, pixmap):
        # Display the original or selected screenshot on the right side
        scaled_pixmap = pixmap.scaled(self.screenshot_label.size(), Qt.AspectRatioMode.KeepAspectRatio)  # Scale to fit
        self.screenshot_label.setPixmap(scaled_pixmap)

    def extract_text_from_image(self, image_path):
        try:
            pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update with your Tesseract path
            image = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(image)
            self.display_extracted_text(extracted_text.strip())
        except Exception as e:
            self.text_editor.setText(f"Error: {e}")

    def display_extracted_text(self, text):
        if text:
            self.text_editor.setText(text)
        else:
            self.text_editor.setText("No text detected. Try selecting a different area.")


if __name__ == "__main__":
    app = QApplication([])
    window = RiveraApp()
    window.show()
    sys.exit(app.exec())