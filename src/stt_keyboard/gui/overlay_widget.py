"""Overlay widget that displays on top of all windows"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen

from stt_keyboard.core.state_manager import StateManager, ApplicationState


class OverlayWidget(QWidget):
    """
    A floating, transparent overlay window that stays on top of all other windows.

    Features:
    - Always on top
    - Frameless (no window decorations)
    - Semi-transparent background
    - Draggable by clicking and moving
    - Shows status text
    - Automatically updates based on application state
    """

    # State-to-color mapping
    STATE_COLORS = {
        ApplicationState.IDLE: QColor(40, 40, 40, 200),       # Dark gray
        ApplicationState.LISTENING: QColor(255, 0, 0, 180),   # Red
        ApplicationState.PROCESSING: QColor(255, 165, 0, 180), # Orange
        ApplicationState.TYPING: QColor(0, 255, 0, 180),      # Green
        ApplicationState.ERROR: QColor(139, 0, 0, 200),       # Dark red
    }

    # State-to-text mapping
    STATE_LABELS = {
        ApplicationState.IDLE: "🎤 Ready",
        ApplicationState.LISTENING: "🔴 Listening...",
        ApplicationState.PROCESSING: "⚙️ Processing...",
        ApplicationState.TYPING: "⌨️ Typing...",
        ApplicationState.ERROR: "❌ Error",
    }

    def __init__(self, state_manager: Optional[StateManager] = None):
        super().__init__()

        # Store drag position for moving the window
        self._drag_position = QPoint()

        # Store reference to state manager
        self._state_manager = state_manager

        # Initialize UI
        self._init_ui()

        # Connect to state manager if provided
        if self._state_manager:
            self.connect_state_manager(self._state_manager)

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

    def connect_state_manager(self, state_manager: StateManager):
        """
        Connect this overlay to a state manager.

        The overlay will automatically update its appearance based on state changes.

        Args:
            state_manager: The StateManager instance to connect to
        """
        self._state_manager = state_manager
        self._state_manager.subscribe(self._on_state_changed)

        # Update to current state immediately
        current_state = self._state_manager.get_state()
        self._update_for_state(current_state)

    def disconnect_state_manager(self):
        """Disconnect from the state manager"""
        if self._state_manager:
            self._state_manager.unsubscribe(self._on_state_changed)
            self._state_manager = None

    def _on_state_changed(self, old_state: ApplicationState, new_state: ApplicationState):
        """
        Callback for state manager state changes.

        Args:
            old_state: Previous application state
            new_state: New application state
        """
        self._update_for_state(new_state)

    def _update_for_state(self, state: ApplicationState):
        """
        Update the overlay's appearance for a given state.

        Args:
            state: The ApplicationState to display
        """
        # Update background color
        if state in self.STATE_COLORS:
            self.set_background_color(self.STATE_COLORS[state])

        # Update status label
        if state in self.STATE_LABELS:
            self.update_status(self.STATE_LABELS[state])

        # Update info label based on state
        if state == ApplicationState.IDLE:
            self.update_info("Press Ctrl+Shift+Space to start")
        elif state == ApplicationState.LISTENING:
            self.update_info("Speak clearly into your microphone")
        elif state == ApplicationState.PROCESSING:
            self.update_info("Transcribing your speech...")
        elif state == ApplicationState.TYPING:
            self.update_info("Typing recognized text")
        elif state == ApplicationState.ERROR:
            # Show error message if available
            if self._state_manager:
                error_msg = self._state_manager.get_error_message()
                self.update_info(error_msg or "An error occurred")

    def set_transcription_text(self, text: str):
        """
        Display partial transcription text in the info label.

        This is useful for showing real-time transcription results.

        Args:
            text: The partial transcription to display
        """
        if text:
            # Limit to 50 characters to avoid overflow
            display_text = text[-50:] if len(text) > 50 else text
            self.update_info(f'"{display_text}"')
        else:
            # Reset to state-appropriate message
            if self._state_manager:
                self._update_for_state(self._state_manager.get_state())
