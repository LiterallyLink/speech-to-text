"""System tray icon implementation"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

from ..core.state_manager import ApplicationState
from ..utils.logger import setup_logger


class TrayIcon(QSystemTrayIcon):
    """System tray icon with menu"""

    def __init__(self, app, config):
        """
        Initialize tray icon

        Args:
            app: Main application instance
            config: Application configuration
        """
        super().__init__()
        self.logger = setup_logger(__name__)
        self.app = app
        self.config = config

        # Create menu
        self.menu = QMenu()

        # Add menu items
        self.recording_action = QAction("Start Recording", self.menu)
        self.recording_action.triggered.connect(self._toggle_recording)
        self.menu.addAction(self.recording_action)

        self.menu.addSeparator()

        self.settings_action = QAction("Settings", self.menu)
        self.settings_action.triggered.connect(self._show_settings)
        self.menu.addAction(self.settings_action)

        self.menu.addSeparator()

        self.quit_action = QAction("Quit", self.menu)
        self.quit_action.triggered.connect(self._quit_application)
        self.menu.addAction(self.quit_action)

        # Set menu
        self.setContextMenu(self.menu)

        # Set icon (using a simple text representation for now)
        # In production, you would use an actual icon file
        self.setToolTip("STT Keyboard - Ready")

        # Connect activation
        self.activated.connect(self._on_activation)

    def _toggle_recording(self):
        """Toggle recording on/off"""
        if hasattr(self.app, '_toggle_recording'):
            self.app._toggle_recording()

    def _show_settings(self):
        """Show settings window"""
        self.logger.info("Settings window not yet implemented")
        # TODO: Implement settings window

    def _quit_application(self):
        """Quit the application"""
        self.app.shutdown()

    def _on_activation(self, reason):
        """
        Handle tray icon activation

        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Left click
            pass
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click
            self._show_settings()

    def update_state(self, state: ApplicationState):
        """
        Update icon based on application state

        Args:
            state: New application state
        """
        if state == ApplicationState.IDLE:
            self.setToolTip("STT Keyboard - Ready")
            self.recording_action.setText("Start Recording")
        elif state == ApplicationState.LISTENING:
            self.setToolTip("STT Keyboard - Listening...")
            self.recording_action.setText("Stop Recording")
        elif state == ApplicationState.PROCESSING:
            self.setToolTip("STT Keyboard - Processing...")
        elif state == ApplicationState.TYPING:
            self.setToolTip("STT Keyboard - Typing...")
        elif state == ApplicationState.ERROR:
            self.setToolTip("STT Keyboard - Error")
