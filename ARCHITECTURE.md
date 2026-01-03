# Speech-to-Text Keyboard Input Application - Architecture Document

## Project Overview

A system-wide, offline speech-to-text application that captures voice input and types it into any active input field across all applications through keyboard simulation.

## Technology Stack

### Core Language
- **Python 3.10+**
  - Cross-platform compatibility
  - Rich ecosystem for speech recognition and GUI
  - Easy to maintain and extend for open source contributors

### Primary Libraries

#### Speech Recognition
- **Vosk (Primary)**: v0.3.45+
  - Offline speech recognition
  - Small model sizes (50MB compact, 1GB+ for high accuracy)
  - Real-time streaming API
  - Multi-language support (20+ languages)
  - Fast CPU-based inference
  - [Inference] Based on research, Vosk provides best balance of speed, accuracy, and resource usage for real-time applications

#### Keyboard Simulation
- **keyboard**: v0.13.5+
  - Cross-platform keyboard control
  - Text typing simulation with delay control
  - Global hotkey support
  - Works on Windows, macOS, Linux

#### Audio Input
- **sounddevice**: v0.4.6+
  - Cross-platform audio capture
  - Low-latency streaming
  - NumPy integration
- **pyaudio**: Fallback option

#### GUI Framework
- **PyQt6**: v6.6.0+
  - Modern, professional UI components
  - Cross-platform native look and feel
  - System tray integration
  - Rich widget set
  - Better for complex applications than Tkinter
  - [Inference] PyQt6 chosen over PySide6 due to more extensive documentation and community resources

#### System Tray
- **pystray**: v0.19.5+ (Fallback if PyQt6 tray has issues on specific platform)
  - Cross-platform system tray support
  - Menu integration

#### Configuration
- **pyyaml**: v6.0+
  - Human-readable configuration files
- **pydantic**: v2.5+
  - Configuration validation and type safety

#### Audio Processing
- **numpy**: v1.24+
  - Audio buffer manipulation
  - Signal processing

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     System Tray Icon                         │
│                  (Always Running)                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                   Main Application                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Event Loop Manager                     │    │
│  │  - Hotkey monitoring                               │    │
│  │  - State management                                │    │
│  │  - Thread coordination                             │    │
│  └────────────────────────────────────────────────────┘    │
└──────────┬──────────────────────────────────────────────────┘
           │
    ┌──────┴──────┬──────────────┬──────────────┬─────────────┐
    │             │              │              │             │
┌───▼────┐  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐  ┌───▼────┐
│ Audio  │  │  Speech  │  │ Keyboard │  │   GUI    │  │ Config │
│ Capture│  │  Engine  │  │ Simulator│  │ Settings │  │ Manager│
└────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
```

## Core Components

### 1. Audio Capture Module (`audio_capture.py`)

**Purpose**: Capture microphone input in real-time

**Responsibilities**:
- Initialize audio device
- Stream audio data with configurable buffer size
- Voice Activity Detection (VAD)
- Noise reduction preprocessing
- Audio format conversion (16kHz mono for Vosk)

**Key Classes**:
```python
class AudioCaptureManager:
    def __init__(self, sample_rate=16000, channels=1, device_id=None)
    def start_stream(self, callback: Callable)
    def stop_stream(self)
    def get_available_devices(self) -> List[AudioDevice]
    def set_device(self, device_id: int)
```

**Threading**: Runs in separate thread to avoid blocking main application

### 2. Speech Recognition Engine (`speech_engine.py`)

**Purpose**: Convert audio to text using offline models

**Responsibilities**:
- Load Vosk model on initialization
- Process audio chunks in real-time
- Return partial and final transcription results
- Model management (download, cache, switch languages)

**Key Classes**:
```python
class SpeechEngine:
    def __init__(self, model_path: str, language: str)
    def process_audio(self, audio_data: bytes) -> TranscriptionResult
    def set_model(self, model_path: str)
    def get_partial_result(self) -> str
    def get_final_result(self) -> str
    def reset(self)

class ModelManager:
    def download_model(self, language: str) -> str
    def get_installed_models(self) -> List[ModelInfo]
    def delete_model(self, model_id: str)
```

**Threading**: Processes audio in dedicated thread with queue-based communication

### 3. Keyboard Simulator (`keyboard_simulator.py`)

**Purpose**: Type recognized text into active applications

**Responsibilities**:
- Simulate keyboard typing
- Handle special characters and Unicode
- Configurable typing speed
- Backspace correction support
- Platform-specific key mapping

**Key Classes**:
```python
class KeyboardSimulator:
    def __init__(self, typing_speed: float = 0.05)
    def type_text(self, text: str, delay: float = None)
    def press_key(self, key: str)
    def send_backspace(self, count: int)
    def is_compatible_field(self) -> bool
```

**Safety**: Rate limiting to prevent overwhelming target applications

### 4. Hotkey Manager (`hotkey_manager.py`)

**Purpose**: Global hotkey registration and handling

**Responsibilities**:
- Register system-wide hotkeys
- Toggle recording on/off
- Trigger different modes (continuous, push-to-talk)
- Platform-specific implementation

**Key Classes**:
```python
class HotkeyManager:
    def __init__(self, config: HotkeyConfig)
    def register_hotkey(self, combination: str, callback: Callable)
    def unregister_hotkey(self, combination: str)
    def start(self)
    def stop(self)
```

**Modes**:
- Push-to-talk: Hold hotkey to record
- Toggle: Press to start, press again to stop
- Continuous: Always listening until stopped

### 5. State Manager (`state_manager.py`)

**Purpose**: Manage application state and coordinate components

**Responsibilities**:
- Track recording state (idle, listening, processing, typing)
- Coordinate component lifecycle
- Event broadcasting
- Error handling and recovery

**Key Classes**:
```python
class ApplicationState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    TYPING = "typing"
    ERROR = "error"

class StateManager:
    def __init__(self)
    def set_state(self, state: ApplicationState)
    def get_state(self) -> ApplicationState
    def subscribe(self, callback: Callable)
    def handle_error(self, error: Exception)
```

### 6. GUI Module (`gui/`)

**Purpose**: User interface for settings and status

**Components**:
- System tray icon with menu
- Settings window
- Model management window
- Statistics/debug window (optional)

**Key Windows**:

#### Main Settings Window (`settings_window.py`)
```python
class SettingsWindow(QMainWindow):
    - Language/model selection
    - Audio device selection
    - Hotkey configuration
    - Typing speed adjustment
    - Auto-start on boot toggle
```

#### System Tray (`tray_icon.py`)
```python
class TrayIcon(QSystemTrayIcon):
    - Quick start/stop
    - Open settings
    - Model status indicator
    - Exit application
```

### 7. Configuration Manager (`config_manager.py`)

**Purpose**: Load, validate, and save user configuration

**Configuration Structure**:
```yaml
# config.yaml
application:
  auto_start: false
  minimize_to_tray: true
  
audio:
  device_id: null  # null = default device
  sample_rate: 16000
  buffer_size: 8000
  
speech:
  model_path: "models/vosk-model-en-us-0.22"
  language: "en-US"
  confidence_threshold: 0.5
  
keyboard:
  typing_speed: 0.05  # seconds between keystrokes
  auto_punctuation: true
  
hotkeys:
  toggle_recording: "ctrl+shift+space"
  cancel_recording: "escape"
  mode: "push_to_talk"  # or "toggle", "continuous"
  
plugins:
  enabled: []
  search_paths:
    - "~/.stt-keyboard/plugins"
    - "./plugins"
```

**Key Classes**:
```python
class ConfigManager:
    def load_config(self, path: str) -> Config
    def save_config(self, config: Config, path: str)
    def validate_config(self, config: Config) -> ValidationResult
    def get_default_config(self) -> Config
```

## File Structure

```
stt-keyboard/
├── README.md
├── LICENSE (MIT or Apache 2.0)
├── requirements.txt
├── setup.py
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── architecture.md (this file)
│   ├── user_guide.md
│   ├── plugin_development.md
│   └── api_reference.md
│
├── src/
│   └── stt_keyboard/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py                    # Main application entry
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── audio_capture.py
│       │   ├── speech_engine.py
│       │   ├── keyboard_simulator.py
│       │   ├── hotkey_manager.py
│       │   └── state_manager.py
│       │
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── tray_icon.py
│       │   ├── settings_window.py
│       │   ├── model_manager_window.py
│       │   └── resources/
│       │       ├── icons/
│       │       └── styles/
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   ├── config_manager.py
│       │   ├── models.py            # Pydantic models
│       │   └── default_config.yaml
│       │
│       ├── plugins/
│       │   ├── __init__.py
│       │   ├── plugin_interface.py
│       │   ├── plugin_loader.py
│       │   └── builtin/
│       │       ├── __init__.py
│       │       ├── auto_punctuation.py
│       │       └── command_parser.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logger.py
│           ├── platform_utils.py
│           └── model_downloader.py
│
├── models/                           # Downloaded Vosk models
│   └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   ├── test_audio_capture.py
│   ├── test_speech_engine.py
│   ├── test_keyboard_simulator.py
│   └── test_config_manager.py
│
└── scripts/
    ├── download_models.py
    ├── create_installer.py
    └── setup_dev_env.py
```

## Plugin Architecture

### Plugin Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class PluginInterface(ABC):
    """Base interface for all plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @abstractmethod
    def initialize(self, app_context: 'ApplicationContext') -> None:
        """Called when plugin is loaded"""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Called when plugin is unloaded"""
        pass


class TextProcessorPlugin(PluginInterface):
    """Plugin for processing transcribed text before typing"""
    
    @abstractmethod
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """
        Process text before it's typed
        
        Args:
            text: Original transcribed text
            context: Additional context (app name, timestamp, etc.)
            
        Returns:
            Processed text to be typed
        """
        pass


class CommandPlugin(PluginInterface):
    """Plugin for voice commands"""
    
    @abstractmethod
    def match_command(self, text: str) -> bool:
        """Check if text matches this plugin's command"""
        pass
    
    @abstractmethod
    def execute_command(self, text: str, context: Dict[str, Any]) -> bool:
        """
        Execute the command
        
        Returns:
            True if command was handled, False otherwise
        """
        pass
```

### Example Plugin

```python
# plugins/builtin/auto_punctuation.py

from stt_keyboard.plugins import TextProcessorPlugin

class AutoPunctuationPlugin(TextProcessorPlugin):
    """Automatically add punctuation based on voice markers"""
    
    name = "Auto Punctuation"
    version = "1.0.0"
    
    def initialize(self, app_context):
        self.markers = {
            "period": ".",
            "comma": ",",
            "question mark": "?",
            "exclamation point": "!",
            "new line": "\n",
            "new paragraph": "\n\n"
        }
    
    def shutdown(self):
        pass
    
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        # Replace spoken punctuation with symbols
        result = text
        for marker, symbol in self.markers.items():
            result = result.replace(f" {marker}", symbol)
        
        # Capitalize first letter after sentence endings
        result = self._capitalize_sentences(result)
        
        return result
    
    def _capitalize_sentences(self, text: str) -> str:
        # Implementation here
        pass
```

## Threading Model

```
Main Thread (Qt Event Loop)
│
├── Audio Capture Thread
│   └── Continuously captures audio
│
├── Speech Processing Thread
│   ├── Receives audio from queue
│   ├── Processes with Vosk
│   └── Emits results via signals
│
└── Keyboard Typing Thread
    └── Types text when triggered
```

**Thread Communication**:
- Audio → Speech: Thread-safe queue
- Speech → Main: Qt signals/slots
- Main → Keyboard: Direct calls (keyboard library handles threading)
- State changes: Event system with callbacks

## Data Flow

```
User speaks into microphone
    ↓
Audio Capture captures raw audio
    ↓
Audio preprocessed (noise reduction, VAD)
    ↓
Audio chunks sent to Speech Engine
    ↓
Vosk processes audio, returns partial results
    ↓
Final transcription completed
    ↓
Text sent to Plugin chain (optional)
    ↓
Processed text sent to Keyboard Simulator
    ↓
Text typed into active application
```

## Platform-Specific Considerations

### Windows
- Use Windows API for reliable global hotkeys
- System tray via Qt or win32
- Audio device access via sounddevice/pyaudio
- [Inference] May need elevated privileges for some hotkey combinations

### macOS
- Accessibility permissions required
- Menu bar icon instead of system tray
- May need to use PyObjC for better macOS integration
- [Inference] macOS security features may require additional user permissions

### Linux
- X11/Wayland compatibility
- Different desktop environments (GNOME, KDE, XFCE)
- Use pystray with AppIndicator backend
- [Inference] May have different behavior across desktop environments

## Performance Targets

- **Latency**: < 500ms from speech end to typing start
- **CPU Usage**: < 5% when idle, < 25% when actively transcribing
- **Memory**: < 200MB base, < 500MB with large model loaded
- **Typing Speed**: Configurable, default 50ms between characters
- **Accuracy**: Dependent on Vosk model (70-95% WER depending on model size)

## Security & Privacy

- **All processing offline**: No data sent to external servers
- **No persistent audio recording**: Audio discarded after processing
- **Configuration encryption**: Optional password protection for settings
- **Plugin sandboxing**: [Unverified - would require research] Plugins may run in restricted environment to prevent malicious behavior

## Installation & Distribution

### Requirements
```
# requirements.txt
PyQt6>=6.6.0
vosk>=0.3.45
sounddevice>=0.4.6
numpy>=1.24.0
keyboard>=0.13.5
pyyaml>=6.0
pydantic>=2.5.0
pystray>=0.19.5
pillow>=10.0.0
```

### Installation Methods

1. **pip install** (recommended for developers)
```bash
pip install stt-keyboard
```

2. **Standalone executable** (for end users)
   - PyInstaller for Windows/Linux
   - py2app for macOS
   - Includes bundled Python runtime and dependencies

3. **Package managers**
   - Snap (Linux)
   - Homebrew (macOS)
   - Chocolatey (Windows)

## Build & Release Process

```bash
# Development setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .

# Run tests
pytest tests/

# Build standalone executable
pyinstaller stt-keyboard.spec

# Create installer
python scripts/create_installer.py
```

## Future Enhancements

[Inference] Potential features for future versions:

1. **Multi-language switching**: Dynamic language detection/switching
2. **Custom wake words**: "Computer, start dictation"
3. **Application-specific configurations**: Different settings per app
4. **Cloud sync**: Optional config sync across devices
5. **Advanced post-processing**: Grammar correction, formatting
6. **Whisper integration**: Alternative to Vosk for higher accuracy
7. **Speaker diarization**: Multiple speaker support
8. **Macro system**: Complex text insertion patterns
9. **Integration APIs**: REST API for third-party integration

## Testing Strategy

### Unit Tests
- Audio capture buffer handling
- Speech engine model loading
- Keyboard simulator text processing
- Config validation

### Integration Tests
- End-to-end audio → text → typing flow
- Plugin loading and execution
- Hotkey registration and triggering

### Manual Testing
- Cross-platform compatibility
- Different audio devices
- Various input fields (browsers, text editors, etc.)
- Long-running stability

## Contributing Guidelines

For open source contributors:

1. **Code Style**: Follow PEP 8, use type hints
2. **Documentation**: Docstrings for all public methods
3. **Testing**: Add tests for new features
4. **Commits**: Conventional commit messages
5. **PRs**: Reference issues, provide clear description
6. **Plugin Development**: Use provided plugin template

## License

Recommended: MIT or Apache 2.0 for maximum open source compatibility

Note: PyQt6 is GPL licensed, which may require GPL for the application or a commercial Qt license. Alternative: Use PySide6 (LGPL) instead for more permissive licensing.

---

This architecture provides a solid foundation for building a professional, extensible speech-to-text keyboard input application. The modular design allows contributors to work on isolated components while maintaining a clean overall structure.
