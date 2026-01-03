"""Overlay widget that stays on top of other windows"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from ..core.state_manager import ApplicationState
from ..utils.logger import setup_logger


class OverlayWidget(QWidget):
    """
    Transparent overlay widget that shows recording status and transcription
    Similar to handcam/facecam overlays
    """

    def __init__(self):
        super().__init__()
        self.logger = setup_logger(__name__)

        # State
        self.current_state = ApplicationState.IDLE
        self.partial_text = ""
        self.dragging = False
        self.drag_position = QPoint()

        self._setup_ui()

    def _setup_ui(self):
        """Setup the overlay UI"""
        # Window flags - stay on top, frameless, transparent
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Size and position
        self.setFixedSize(400, 150)

        # Position in bottom-right corner by default
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 420, screen.height() - 200)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # State label
        self.state_label = QLabel("Ready")
        self.state_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(self.state_label)

        # Transcription label
        self.text_label = QLabel("")
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 14px;
                background: transparent;
            }
        """)
        layout.addWidget(self.text_label)

        # Hotkey hint
        self.hint_label = QLabel("Press Ctrl+Shift+Space to speak")
        self.hint_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                background: transparent;
            }
        """)
        layout.addWidget(self.hint_label)

        layout.addStretch()

    def paintEvent(self, event):
        """Custom paint event for rounded background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background color based on state
        if self.current_state == ApplicationState.LISTENING:
            bg_color = QColor(255, 0, 0, 180)  # Red when listening
        elif self.current_state == ApplicationState.PROCESSING:
            bg_color = QColor(255, 165, 0, 180)  # Orange when processing
        elif self.current_state == ApplicationState.TYPING:
            bg_color = QColor(0, 255, 0, 180)  # Green when typing
        else:
            bg_color = QColor(40, 40, 40, 200)  # Dark gray when idle

        # Draw rounded rectangle background
        painter.setBrush(bg_color)
        painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
        painter.drawRoundedRect(self.rect(), 15, 15)

    def update_state(self, state: ApplicationState):
        """Update the overlay based on application state"""
        self.current_state = state

        # Update state label
        state_text = {
            ApplicationState.IDLE: "🎤 Ready",
            ApplicationState.LISTENING: "🔴 Listening...",
            ApplicationState.PROCESSING: "⚙️ Processing...",
            ApplicationState.TYPING: "⌨️ Typing...",
            ApplicationState.ERROR: "❌ Error"
        }
        self.state_label.setText(state_text.get(state, "Ready"))

        # Clear text when not listening
        if state != ApplicationState.LISTENING:
            self.partial_text = ""
            self.text_label.setText("")

        # Trigger repaint for background color change
        self.update()

    def update_partial_text(self, text: str):
        """Update the partial transcription text"""
        self.partial_text = text
        # Limit to ~50 characters for display
        display_text = text[-50:] if len(text) > 50 else text
        self.text_label.setText(display_text)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.dragging = False

    def mouseDoubleClickEvent(self, event):
        """Double-click to hide/show"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
