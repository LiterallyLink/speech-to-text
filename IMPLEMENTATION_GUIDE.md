# Implementation Guide - Core Components

## Overview

This document provides detailed implementation examples for the core components of the STT Keyboard application.

## 1. Main Application Entry Point

```python
# src/stt_keyboard/app.py

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
        self.speech_engine = SpeechEngine(
            model_path=speech_config.model_path,
            language=speech_config.language
        )
        self.speech_engine.on_partial_result = self._on_partial_transcription
        self.speech_engine.on_final_result = self._on_final_transcription
        self.logger.info(f"Speech engine initialized: {speech_config.language}")
        
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
        
        # Trigger final transcription
        self.state_manager.set_state(ApplicationState.PROCESSING)
        
    def _on_audio_data(self, audio_data: bytes):
        """Callback for incoming audio data"""
        if self.state_manager.get_state() == ApplicationState.LISTENING:
            self.speech_engine.process_audio(audio_data)
            
    def _on_partial_transcription(self, text: str):
        """Handle partial transcription results"""
        self.logger.debug(f"Partial: {text}")
        # Could show in a small overlay window
        
    def _on_final_transcription(self, text: str):
        """Handle final transcription result"""
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
        """Process text through loaded plugins"""
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
        """Type text using keyboard simulator"""
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
        """Handle application state changes"""
        self.logger.info(f"State change: {old_state} -> {new_state}")
        
        # Update tray icon to reflect state
        if self.tray_icon:
            self.tray_icon.update_state(new_state)
            
    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        self.logger.info(f"Received signal {signum}, shutting down")
        self.shutdown()
        
    def run(self):
        """Run the application"""
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
```

## 2. Audio Capture Implementation

```python
# src/stt_keyboard/core/audio_capture.py

import queue
import threading
import numpy as np
import sounddevice as sd
from typing import Callable, List, Optional
from dataclasses import dataclass

from ..utils.logger import setup_logger


@dataclass
class AudioDevice:
    """Information about an audio input device"""
    id: int
    name: str
    channels: int
    sample_rate: int


class AudioCaptureManager:
    """Manages audio input capture from microphone"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, 
                 device_id: Optional[int] = None):
        self.logger = setup_logger(__name__)
        self.sample_rate = sample_rate
        self.channels = channels
        self.device_id = device_id
        
        self.stream = None
        self.is_recording = False
        self.callback = None
        
        # Buffer for audio data
        self.audio_queue = queue.Queue()
        self.processing_thread = None
        
    def get_available_devices(self) -> List[AudioDevice]:
        """Get list of available audio input devices"""
        devices = []
        for idx, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                devices.append(AudioDevice(
                    id=idx,
                    name=device['name'],
                    channels=device['max_input_channels'],
                    sample_rate=int(device['default_samplerate'])
                ))
        return devices
        
    def set_device(self, device_id: int):
        """Set the audio input device"""
        self.device_id = device_id
        self.logger.info(f"Audio device set to: {device_id}")
        
    def start_stream(self, callback: Callable[[bytes], None]):
        """
        Start capturing audio from microphone
        
        Args:
            callback: Function to call with audio data chunks
        """
        if self.is_recording:
            self.logger.warning("Already recording")
            return
            
        self.callback = callback
        self.is_recording = True
        
        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_audio,
            daemon=True
        )
        self.processing_thread.start()
        
        # Start audio stream
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device_id,
                callback=self._audio_callback,
                blocksize=8000,
                dtype=np.int16
            )
            self.stream.start()
            self.logger.info("Audio stream started")
            
        except Exception as e:
            self.logger.error(f"Failed to start audio stream: {e}")
            self.is_recording = False
            raise
            
    def stop_stream(self):
        """Stop audio capture"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        # Wait for processing thread to finish
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)
            
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        self.logger.info("Audio stream stopped")
        
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback from sounddevice for audio data"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
            
        if self.is_recording:
            # Convert to bytes and add to queue
            audio_bytes = indata.tobytes()
            self.audio_queue.put(audio_bytes)
            
    def _process_audio(self):
        """Process audio from queue in separate thread"""
        while self.is_recording:
            try:
                # Get audio data with timeout
                audio_data = self.audio_queue.get(timeout=0.1)
                
                # Call user callback
                if self.callback:
                    self.callback(audio_data)
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing audio: {e}")
```

## 3. Speech Engine Implementation

```python
# src/stt_keyboard/core/speech_engine.py

import json
import queue
import threading
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass

from vosk import Model, KaldiRecognizer

from ..utils.logger import setup_logger


@dataclass
class TranscriptionResult:
    """Result from speech recognition"""
    text: str
    confidence: float
    is_final: bool


class SpeechEngine:
    """Offline speech recognition using Vosk"""
    
    def __init__(self, model_path: str, language: str):
        self.logger = setup_logger(__name__)
        self.model_path = Path(model_path)
        self.language = language
        
        # Callbacks
        self.on_partial_result: Optional[Callable] = None
        self.on_final_result: Optional[Callable] = None
        
        # Vosk components
        self.model = None
        self.recognizer = None
        
        # Processing
        self.audio_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False
        
        self._load_model()
        self._start_processing_thread()
        
    def _load_model(self):
        """Load Vosk model from disk"""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Please download a model first."
            )
            
        self.logger.info(f"Loading model from {self.model_path}")
        self.model = Model(str(self.model_path))
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)
        self.logger.info("Model loaded successfully")
        
    def _start_processing_thread(self):
        """Start background thread for audio processing"""
        self.is_processing = True
        self.processing_thread = threading.Thread(
            target=self._process_loop,
            daemon=True
        )
        self.processing_thread.start()
        
    def process_audio(self, audio_data: bytes):
        """
        Add audio data to processing queue
        
        Args:
            audio_data: Raw audio bytes (16-bit PCM)
        """
        self.audio_queue.put(audio_data)
        
    def _process_loop(self):
        """Background processing loop"""
        while self.is_processing:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                self._process_chunk(audio_data)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                
    def _process_chunk(self, audio_data: bytes):
        """Process a chunk of audio data"""
        if self.recognizer.AcceptWaveform(audio_data):
            # Final result
            result = json.loads(self.recognizer.Result())
            text = result.get('text', '')
            
            if text and self.on_final_result:
                self.on_final_result(text)
        else:
            # Partial result
            partial = json.loads(self.recognizer.PartialResult())
            text = partial.get('partial', '')
            
            if text and self.on_partial_result:
                self.on_partial_result(text)
                
    def get_final_result(self) -> str:
        """Get final result and reset recognizer"""
        result = json.loads(self.recognizer.FinalResult())
        text = result.get('text', '')
        return text
        
    def reset(self):
        """Reset recognizer state"""
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)
        
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
    def set_model(self, model_path: str):
        """Switch to a different model"""
        self.model_path = Path(model_path)
        self._load_model()
        
    def shutdown(self):
        """Shutdown the speech engine"""
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
```

## 4. Keyboard Simulator Implementation

```python
# src/stt_keyboard/core/keyboard_simulator.py

import time
import keyboard

from ..utils.logger import setup_logger


class KeyboardSimulator:
    """Simulates keyboard input to type text"""
    
    def __init__(self, typing_speed: float = 0.05):
        """
        Initialize keyboard simulator
        
        Args:
            typing_speed: Delay between keystrokes in seconds
        """
        self.logger = setup_logger(__name__)
        self.typing_speed = typing_speed
        
    def type_text(self, text: str, delay: Optional[float] = None):
        """
        Type text character by character
        
        Args:
            text: Text to type
            delay: Optional override for typing speed
        """
        if not text:
            return
            
        actual_delay = delay if delay is not None else self.typing_speed
        
        try:
            # Use keyboard library's write function
            # It handles special characters and Unicode
            keyboard.write(text, delay=actual_delay)
            
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            raise
            
    def press_key(self, key: str):
        """Press a single key"""
        keyboard.press_and_release(key)
        
    def send_backspace(self, count: int = 1):
        """Send backspace key multiple times"""
        for _ in range(count):
            keyboard.press_and_release('backspace')
            time.sleep(0.05)
            
    def send_enter(self):
        """Send enter/return key"""
        keyboard.press_and_release('enter')
```

This implementation guide provides working code for the core components. The actual implementation would need additional error handling, logging, and platform-specific adaptations, but this provides a solid foundation for development.
