"""Overlay widget that displays on top of all windows"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen


class OverlayWidget(QWidget):
    """
    A floating, transparent overlay window that stays on top of all other windows.

    Features:
    - Always on top
    - Frameless (no window decorations)
    - Semi-transparent background
    - Draggable by clicking and moving
    - Shows status text
    """

    def __init__(self):
        super().__init__()

        # Store drag position for moving the window
        self._drag_position = QPoint()

        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        # Set window flags for overlay behavior
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |      # Always on top
            Qt.WindowType.FramelessWindowHint |       # No title bar/borders
            Qt.WindowType.Tool                        # Don't show in taskbar
        )

        # Make background transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set initial size and position
        self.resize(300, 100)
        self._position_bottom_right()

        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Info label
        self.info_label = QLabel("Press Ctrl+Shift+Space to start")
        self.info_label.setStyleSheet("""
            color: rgba(255, 255, 255, 180);
            font-size: 12px;
        """)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.info_label)

        self.setLayout(layout)

        # Store background color (default: dark gray)
        self.bg_color = QColor(40, 40, 40, 200)

    def _position_bottom_right(self):
        """Position the overlay in the bottom-right corner of the screen"""
        from PyQt6.QtGui import QGuiApplication

        screen = QGuiApplication.primaryScreen().geometry()
        margin = 20
        x = screen.width() - self.width() - margin
        y = screen.height() - self.height() - margin
        self.move(x, y)

    def paintEvent(self, event):
        """Custom paint event to draw the rounded rectangle background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rounded rectangle background
        painter.setBrush(self.bg_color)
        painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
        painter.drawRoundedRect(self.rect(), 10, 10)

    def mousePressEvent(self, event):
        """Handle mouse press to start dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move to drag the window"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def update_status(self, status_text: str):
        """Update the status text displayed"""
        self.status_label.setText(status_text)

    def update_info(self, info_text: str):
        """Update the info text displayed"""
        self.info_label.setText(info_text)

    def set_background_color(self, color: QColor):
        """Change the background color"""
        self.bg_color = color
        self.update()  # Trigger repaint
