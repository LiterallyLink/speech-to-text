# Quick Start Guide

## Installation

1. **Create a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download a speech model**:
```bash
# English (US) - Small model (40MB, recommended for testing)
python scripts/download_model.py --language en-us --size small

# For list of available models:
python scripts/download_model.py --list
```

4. **Run the application**:
```bash
python -m stt_keyboard
```

## Usage

1. The application will start in the system tray
2. Press `Ctrl+Shift+Space` and hold to record
3. Speak clearly into your microphone
4. Release the key when done
5. Your speech will be transcribed and typed automatically!

## Configuration

Configuration is stored at `~/.stt-keyboard/config.yaml`

You can customize:
- Hotkeys
- Typing speed
- Model path
- Enabled plugins

## Troubleshooting

### Model not found error
Make sure you've downloaded a model:
```bash
python scripts/download_model.py --language en-us --size small
```

### Microphone not working
- Check system audio settings
- Ensure microphone is not muted
- Try selecting a specific device in config.yaml

### Hotkey not working
- On Linux: May need to run with sudo or add user to input group
- On macOS: Grant Accessibility permissions
- On Windows: Try running as administrator

### Permission errors on Linux
```bash
# Option 1: Run with sudo (not recommended for regular use)
sudo python -m stt_keyboard

# Option 2: Add user to input group (preferred)
sudo usermod -a -G input $USER
# Log out and back in
```

## Next Steps

- Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions
- See [PLUGIN_GUIDE.md](PLUGIN_GUIDE.md) to create custom plugins
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

## Features

- **Offline**: All processing happens locally
- **System-wide**: Works with any application
- **Customizable**: Hotkeys, typing speed, plugins
- **Multi-language**: Support for 20+ languages
- **Plugins**: Auto-punctuation, emoji converter, and more!

Enjoy using STT Keyboard! 🎤
