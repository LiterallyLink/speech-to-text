"""Main application class"""

import sys
import signal
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from .core.state_manager import StateManager, ApplicationState
from .core.audio_capture import AudioCaptureManager
from .core.speech_engine import SpeechEngine
from .core.keyboard_simulator import KeyboardSimulator
from .core.hotkey_manager import HotkeyManager
from .gui.tray_icon import TrayIcon
from .config.config_manager import ConfigManager
from .plugins.plugin_loader import PluginLoader
from .utils.logger import setup_logger


class STTKeyboardApp:
    """Main application class coordinating all components"""

    def __init__(self):
        """Initialize the application"""
        self.logger = setup_logger(__name__)
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()

        # Core components
        self.state_manager = StateManager()
        self.audio_capture = None
        self.speech_engine = None
        self.keyboard_sim = None
        self.hotkey_manager = None
        self.plugin_loader = None

        # GUI
        self.tray_icon = None

        # Qt application
        self.app = None

    def initialize(self):
        """Initialize all application components"""
        self.logger.info("Initializing STT Keyboard application")

        # Initialize Qt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Initialize core components
        self._init_audio_capture()
        self._init_speech_engine()
        self._init_keyboard_simulator()
        self._init_hotkey_manager()
        self._init_plugins()

        # Initialize GUI
        self._init_tray_icon()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # State change subscriptions
        self.state_manager.subscribe(self._on_state_change)

        self.logger.info("Application initialized successfully")

    def _init_audio_capture(self):
        """Initialize audio capture component"""
        audio_config = self.config.audio
        self.audio_capture = AudioCaptureManager(
            sample_rate=audio_config.sample_rate,
            channels=1,
            device_id=audio_config.device_id
        )
        self.logger.info(f"Audio capture initialized: {audio_config.sample_rate}Hz")

    def _init_speech_engine(self):
        """Initialize speech recognition engine"""
        speech_config = self.config.speech

        try:
            self.speech_engine = SpeechEngine(
                model_path=speech_config.model_path,
                language=speech_config.language
            )
            self.speech_engine.on_partial_result = self._on_partial_transcription
            self.speech_engine.on_final_result = self._on_final_transcription
            self.logger.info(f"Speech engine initialized: {speech_config.language}")
        except FileNotFoundError as e:
            self.logger.error(f"Speech model not found: {e}")
            self.logger.error("Please download a model using: python scripts/download_model.py --language en-us --size small")
            raise

    def _init_keyboard_simulator(self):
        """Initialize keyboard simulator"""
        kb_config = self.config.keyboard
        self.keyboard_sim = KeyboardSimulator(
            typing_speed=kb_config.typing_speed
        )
        self.logger.info("Keyboard simulator initialized")

    def _init_hotkey_manager(self):
        """Initialize global hotkey manager"""
        hotkey_config = self.config.hotkeys
        self.hotkey_manager = HotkeyManager(hotkey_config)

        # Register hotkeys
        self.hotkey_manager.register_hotkey(
            hotkey_config.toggle_recording,
            self._toggle_recording
        )
        if hotkey_config.cancel_recording:
            self.hotkey_manager.register_hotkey(
                hotkey_config.cancel_recording,
                self._cancel_recording
            )

        self.hotkey_manager.start()
        self.logger.info("Hotkey manager initialized")

    def _init_plugins(self):
        """Initialize plugin system"""
        self.plugin_loader = PluginLoader(self.config.plugins.search_paths)

        # Load enabled plugins
        for plugin_name in self.config.plugins.enabled:
            try:
                self.plugin_loader.load_plugin(plugin_name)
                self.logger.info(f"Loaded plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_name}: {e}")

    def _init_tray_icon(self):
        """Initialize system tray icon"""
        self.tray_icon = TrayIcon(
            app=self,
            config=self.config
        )
        self.tray_icon.show()
        self.logger.info("System tray icon initialized")

    def _toggle_recording(self):
        """Toggle recording on/off based on current state"""
        current_state = self.state_manager.get_state()

        if current_state == ApplicationState.IDLE:
            self.start_recording()
        elif current_state == ApplicationState.LISTENING:
            self.stop_recording()
        else:
            self.logger.warning(f"Cannot toggle in state: {current_state}")

    def _cancel_recording(self):
        """Cancel current recording without typing"""
        if self.state_manager.get_state() == ApplicationState.LISTENING:
            self.state_manager.set_state(ApplicationState.IDLE)
            self.audio_capture.stop_stream()
            self.speech_engine.reset()
            self.logger.info("Recording cancelled")

    def start_recording(self):
        """Start audio capture and transcription"""
        self.logger.info("Starting recording")
        self.state_manager.set_state(ApplicationState.LISTENING)

        # Start audio stream
        self.audio_capture.start_stream(self._on_audio_data)

    def stop_recording(self):
        """Stop audio capture"""
        self.logger.info("Stopping recording")
        self.audio_capture.stop_stream()

        # Get final transcription
        final_text = self.speech_engine.get_final_result()
        if final_text:
            self._on_final_transcription(final_text)

        # Trigger final transcription
        self.state_manager.set_state(ApplicationState.PROCESSING)

    def _on_audio_data(self, audio_data: bytes):
        """
        Callback for incoming audio data

        Args:
            audio_data: Audio bytes from microphone
        """
        if self.state_manager.get_state() == ApplicationState.LISTENING:
            self.speech_engine.process_audio(audio_data)

    def _on_partial_transcription(self, text: str):
        """
        Handle partial transcription results

        Args:
            text: Partial transcription text
        """
        self.logger.debug(f"Partial: {text}")
        # Could show in a small overlay window

    def _on_final_transcription(self, text: str):
        """
        Handle final transcription result

        Args:
            text: Final transcription text
        """
        self.logger.info(f"Final transcription: {text}")

        if not text.strip():
            self.logger.info("Empty transcription, ignoring")
            self.state_manager.set_state(ApplicationState.IDLE)
            return

        # Process through plugins
        processed_text = self._process_through_plugins(text)

        # Type the text
        self._type_text(processed_text)

    def _process_through_plugins(self, text: str) -> str:
        """
        Process text through loaded plugins

        Args:
            text: Original text

        Returns:
            Processed text
        """
        processed = text

        # First check command plugins
        for plugin in self.plugin_loader.get_command_plugins():
            if plugin.match_command(processed):
                if plugin.execute_command(processed, {}):
                    # Command handled, don't type anything
                    return ""

        # Then process through text processors
        for plugin in self.plugin_loader.get_text_processors():
            processed = plugin.process_text(processed, {})

        return processed

    def _type_text(self, text: str):
        """
        Type text using keyboard simulator

        Args:
            text: Text to type
        """
        if not text:
            self.state_manager.set_state(ApplicationState.IDLE)
            return

        self.state_manager.set_state(ApplicationState.TYPING)

        try:
            self.keyboard_sim.type_text(text)
            self.logger.info("Text typed successfully")
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
        finally:
            self.state_manager.set_state(ApplicationState.IDLE)

    def _on_state_change(self, old_state, new_state):
        """
        Handle application state changes

        Args:
            old_state: Previous state
            new_state: New state
        """
        self.logger.info(f"State change: {old_state.value} -> {new_state.value}")

        # Update tray icon to reflect state
        if self.tray_icon:
            self.tray_icon.update_state(new_state)

    def _signal_handler(self, signum, frame):
        """
        Handle system signals

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.logger.info(f"Received signal {signum}, shutting down")
        self.shutdown()

    def run(self):
        """
        Run the application

        Returns:
            Exit code
        """
        self.logger.info("Starting application main loop")
        return self.app.exec()

    def shutdown(self):
        """Clean shutdown of all components"""
        self.logger.info("Shutting down application")

        # Stop components in reverse order
        if self.hotkey_manager:
            self.hotkey_manager.stop()

        if self.audio_capture:
            self.audio_capture.stop_stream()

        if self.plugin_loader:
            self.plugin_loader.unload_all()

        # Save configuration
        self.config_manager.save_config(self.config)

        # Quit Qt application
        if self.app:
            self.app.quit()

        self.logger.info("Shutdown complete")


def main():
    """Application entry point"""
    app = STTKeyboardApp()
    app.initialize()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
