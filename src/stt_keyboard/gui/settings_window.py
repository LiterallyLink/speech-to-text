"""Settings window implementation"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
    QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt

from ..utils.logger import setup_logger


class SettingsWindow(QMainWindow):
    """Settings configuration window"""

    def __init__(self, config, config_manager):
        """
        Initialize settings window

        Args:
            config: Current configuration
            config_manager: Configuration manager instance
        """
        super().__init__()
        self.logger = setup_logger(__name__)
        self.config = config
        self.config_manager = config_manager

        self.setWindowTitle("STT Keyboard - Settings")
        self.setGeometry(100, 100, 600, 500)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Add sections
        layout.addWidget(self._create_hotkey_section())
        layout.addWidget(self._create_keyboard_section())
        layout.addWidget(self._create_speech_section())

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self._save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _create_hotkey_section(self):
        """Create hotkey configuration section"""
        group = QGroupBox("Hotkeys")
        layout = QVBoxLayout()

        # Toggle recording hotkey
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("Toggle Recording:"))
        self.hotkey_input = QLineEdit(self.config.hotkeys.toggle_recording)
        hotkey_layout.addWidget(self.hotkey_input)
        layout.addLayout(hotkey_layout)

        # Mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["push_to_talk", "toggle", "continuous"])
        self.mode_combo.setCurrentText(self.config.hotkeys.mode)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        group.setLayout(layout)
        return group

    def _create_keyboard_section(self):
        """Create keyboard configuration section"""
        group = QGroupBox("Keyboard")
        layout = QVBoxLayout()

        # Typing speed
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Typing Speed (seconds):"))
        self.typing_speed_input = QDoubleSpinBox()
        self.typing_speed_input.setMinimum(0.01)
        self.typing_speed_input.setMaximum(1.0)
        self.typing_speed_input.setSingleStep(0.01)
        self.typing_speed_input.setValue(self.config.keyboard.typing_speed)
        speed_layout.addWidget(self.typing_speed_input)
        layout.addLayout(speed_layout)

        group.setLayout(layout)
        return group

    def _create_speech_section(self):
        """Create speech recognition configuration section"""
        group = QGroupBox("Speech Recognition")
        layout = QVBoxLayout()

        # Model path
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model Path:"))
        self.model_path_input = QLineEdit(self.config.speech.model_path)
        model_layout.addWidget(self.model_path_input)
        layout.addLayout(model_layout)

        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.language_input = QLineEdit(self.config.speech.language)
        lang_layout.addWidget(self.language_input)
        layout.addLayout(lang_layout)

        group.setLayout(layout)
        return group

    def _save_settings(self):
        """Save settings and close window"""
        # Update config
        self.config.hotkeys.toggle_recording = self.hotkey_input.text()
        self.config.hotkeys.mode = self.mode_combo.currentText()
        self.config.keyboard.typing_speed = self.typing_speed_input.value()
        self.config.speech.model_path = self.model_path_input.text()
        self.config.speech.language = self.language_input.text()

        # Save to file
        self.config_manager.save_config(self.config)

        self.logger.info("Settings saved")
        self.close()
