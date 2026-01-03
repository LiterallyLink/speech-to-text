# Setup and Development Guide

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+, Fedora 35+)
- **Python**: 3.10 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 500MB for application + 50MB-1GB per language model
- **Microphone**: Any working audio input device

### Recommended Requirements
- **CPU**: Multi-core processor (2+ cores)
- **RAM**: 8GB for smoother operation
- **Microphone**: USB microphone or headset for better accuracy

## Installation

### Option 1: From Source (Developers)

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stt-keyboard.git
cd stt-keyboard
```

#### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Download Language Model

The application requires a Vosk speech recognition model. Download your preferred language:

**English (US) - Lightweight (50MB):**
```bash
python scripts/download_model.py --language en-us --size small
```

**English (US) - High Accuracy (1.8GB):**
```bash
python scripts/download_model.py --language en-us --size large
```

**Other Languages:**
```bash
# Spanish
python scripts/download_model.py --language es --size small

# French
python scripts/download_model.py --language fr --size small

# German
python scripts/download_model.py --language de --size small

# See full list: python scripts/download_model.py --list
```

#### 5. Run the Application

```bash
python -m stt_keyboard
```

Or using the entry point:

```bash
python src/stt_keyboard/__main__.py
```

### Option 2: Standalone Executable (End Users)

[Unverified] Download the latest release for your platform:

**Windows:**
```
stt-keyboard-v1.0.0-windows-x64.exe
```

**macOS:**
```
stt-keyboard-v1.0.0-macos.dmg
```

**Linux:**
```
stt-keyboard-v1.0.0-linux-x64.AppImage
```

Run the executable and follow the setup wizard to download a language model.

## Platform-Specific Setup

### Windows

**1. Audio Permissions:**
- Microphone access is usually granted by default
- Check Settings > Privacy > Microphone if issues occur

**2. Keyboard Simulation:**
- The application requires permission to simulate keyboard input
- Run as administrator if hotkeys don't work

**3. System Tray:**
- Should work automatically with PyQt6

### macOS

**1. Accessibility Permissions:**
macOS requires special permissions for keyboard control.

Go to: **System Preferences > Security & Privacy > Privacy > Accessibility**

Add and enable:
- Terminal (if running from terminal)
- The STT Keyboard app (if using standalone)

**2. Microphone Permissions:**
Go to: **System Preferences > Security & Privacy > Privacy > Microphone**

Enable microphone access for the application.

**3. Menu Bar:**
The app will appear in the menu bar (top right) instead of system tray.

### Linux

**1. Audio Setup:**

Install PortAudio (required for sounddevice):

**Debian/Ubuntu:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Fedora:**
```bash
sudo dnf install portaudio-devel
```

**Arch:**
```bash
sudo pacman -S portaudio
```

**2. Keyboard Access:**

You may need to run with elevated privileges:

```bash
sudo python -m stt_keyboard
```

Or add your user to the input group:

```bash
sudo usermod -a -G input $USER
# Log out and back in
```

**3. System Tray:**

Install AppIndicator support:

**Ubuntu/Debian:**
```bash
sudo apt-get install gir1.2-appindicator3-0.1
```

**Fedora:**
```bash
sudo dnf install libappindicator-gtk3
```

## Configuration

### First Run

On first run, the application creates a default configuration at:

- **Windows:** `%USERPROFILE%\.stt-keyboard\config.yaml`
- **macOS:** `~/.stt-keyboard/config.yaml`
- **Linux:** `~/.stt-keyboard/config.yaml`

### Configuration File

Edit `config.yaml` to customize behavior:

```yaml
application:
  auto_start: false          # Start with system
  minimize_to_tray: true     # Minimize to system tray
  show_notifications: true   # Show status notifications

audio:
  device_id: null           # null = default device
  sample_rate: 16000        # Don't change (required by Vosk)
  buffer_size: 8000         # Audio buffer size

speech:
  model_path: "models/vosk-model-en-us-0.22"
  language: "en-US"
  confidence_threshold: 0.5  # Minimum confidence to accept

keyboard:
  typing_speed: 0.05        # Delay between keystrokes (seconds)
  auto_punctuation: true    # Enable auto-punctuation plugin

hotkeys:
  toggle_recording: "ctrl+shift+space"
  cancel_recording: "escape"
  mode: "push_to_talk"      # "push_to_talk", "toggle", or "continuous"

plugins:
  enabled:
    - "auto_punctuation"
    - "emoji_converter"
  search_paths:
    - "~/.stt-keyboard/plugins"
    - "./plugins"
```

### Changing Hotkeys

Edit the `hotkeys` section in config.yaml:

```yaml
hotkeys:
  # Push-to-talk: Hold key to record
  toggle_recording: "ctrl+shift+space"
  
  # Other options:
  # toggle_recording: "ctrl+alt+r"
  # toggle_recording: "f9"
  # toggle_recording: "ctrl+`"
```

## Usage

### Basic Usage

1. **Start the application** - Icon appears in system tray/menu bar
2. **Hold your hotkey** (default: Ctrl+Shift+Space)
3. **Speak clearly** into your microphone
4. **Release the hotkey** when done
5. **Text is typed** into your active application

### Modes

**Push-to-Talk (Recommended):**
- Hold hotkey while speaking
- Release when done
- Text typed automatically

**Toggle:**
- Press hotkey once to start
- Press again to stop
- Text typed when stopped

**Continuous:**
- Always listening
- Press hotkey to type last segment
- [Inference] Higher CPU usage

### Tips for Best Accuracy

1. **Use a good microphone** - USB mics or headsets work best
2. **Minimize background noise** - Close windows, turn off fans
3. **Speak clearly** - Not too fast, not too slow
4. **Use natural speech** - Don't over-enunciate
5. **Add pauses** - Brief pauses help with word boundaries
6. **Say punctuation** - "period", "comma", "question mark"
7. **Use larger models** - More accurate but slower/larger

## Development

### Project Structure

```
stt-keyboard/
├── src/stt_keyboard/      # Main application code
│   ├── core/              # Core functionality
│   ├── gui/               # User interface
│   ├── config/            # Configuration management
│   ├── plugins/           # Plugin system
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docs/                  # Documentation
└── plugins/               # Builtin plugins
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=stt_keyboard --cov-report=html

# Run specific test file
pytest tests/test_audio_capture.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/
```

### Building Standalone Executable

**All Platforms:**
```bash
# Install build tools
pip install pyinstaller

# Build
pyinstaller stt-keyboard.spec

# Output in dist/ directory
```

**Create Installer:**
```bash
# Windows (requires NSIS)
python scripts/create_installer.py --platform windows

# macOS (requires create-dmg)
python scripts/create_installer.py --platform macos

# Linux (AppImage)
python scripts/create_installer.py --platform linux
```

## Troubleshooting

### Audio Issues

**No microphone detected:**
1. Check system audio settings
2. Ensure microphone is not muted
3. Try selecting specific device in config
4. On Linux, check PulseAudio/PipeWire settings

**Poor audio quality:**
1. Test microphone in other applications
2. Reduce background noise
3. Move closer to microphone
4. Check sample rate in config (should be 16000)

### Keyboard Issues

**Hotkey not working:**
1. Check if another app uses the same hotkey
2. Try a different key combination
3. On Windows, try running as administrator
4. On macOS, check Accessibility permissions
5. On Linux, check if input group is set

**Text not typing:**
1. Ensure an input field is focused
2. Try clicking in a text editor first
3. Check keyboard permissions
4. Some applications may block simulated input

### Speech Recognition Issues

**Low accuracy:**
1. Use larger model (trade-off: slower, more disk space)
2. Speak more clearly and slowly
3. Reduce background noise
4. Check microphone positioning
5. Ensure correct language model is loaded

**High latency:**
1. Use smaller model
2. Close other applications
3. Increase buffer size in config
4. Check CPU usage

**Model not loading:**
1. Verify model was downloaded correctly
2. Check model_path in config.yaml
3. Ensure sufficient disk space
4. Try re-downloading model

### GUI Issues

**Tray icon not appearing:**
1. Check system tray settings
2. On Linux, ensure AppIndicator is installed
3. Try pystray fallback mode
4. Restart the application

**Settings window not opening:**
1. Check application logs
2. Ensure PyQt6 is installed correctly
3. Try reinstalling dependencies

## Logs and Debugging

### Log Locations

- **Windows:** `%USERPROFILE%\.stt-keyboard\logs\`
- **macOS:** `~/.stt-keyboard/logs/`
- **Linux:** `~/.stt-keyboard/logs/`

### Enable Debug Logging

Edit config.yaml:

```yaml
logging:
  level: "DEBUG"  # INFO, DEBUG, WARNING, ERROR
  file: "~/.stt-keyboard/logs/app.log"
  max_size: "10MB"
  backup_count: 5
```

### Verbose Mode

Run with debug flag:

```bash
python -m stt_keyboard --debug
```

## Getting Help

1. **Check documentation** in `docs/` directory
2. **Search issues** on GitHub
3. **Ask in discussions** for usage questions
4. **Open issue** for bugs with:
   - Operating system and version
   - Python version
   - Full error message
   - Steps to reproduce
   - Relevant config.yaml sections
   - Log excerpts

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- Commit message format
- Pull request process
- Development workflow

## License

This project is open source under the [LICENSE] (MIT/Apache 2.0 recommended).

## Acknowledgments

- **Vosk** - Offline speech recognition
- **keyboard library** - Cross-platform keyboard control
- **PyQt6** - GUI framework
- All contributors and users of this project
