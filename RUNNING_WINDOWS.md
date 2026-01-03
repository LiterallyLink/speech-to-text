# How to Run and Test on Windows

## Quick Start

On Windows, use `python` instead of `python3`:

### **Run All Tests**
```powershell
# Using batch file
.\run_tests.bat

# Or manually
python test_state_manager.py
python test_integration.py
```

### **Run Visual Demo**
```powershell
python demo_overlay.py
```

This will show the overlay window on your screen!

## Installation (First Time)

```powershell
# Install PyQt6
pip install PyQt6

# Or install all dependencies
pip install -r requirements.txt
```

## What You'll See

When you run `python demo_overlay.py`:

1. **A floating overlay appears** in the bottom-right corner
2. **Colors automatically cycle** every 2 seconds:
   - 🌑 Dark Gray = Ready (IDLE)
   - 🔴 Red = Listening (recording)
   - 🟠 Orange = Processing (transcribing)
   - 🟢 Green = Typing (output)
3. **Real-time text updates** showing simulated transcription
4. **You can drag it** by clicking and moving

### Manual Controls

Click the overlay first, then press:
- `1` - IDLE state (dark gray)
- `2` - LISTENING state (red)
- `3` - PROCESSING state (orange)
- `4` - TYPING state (green)
- `5` - ERROR state (dark red)
- `Q` - Quit

## PowerShell Commands

```powershell
# Test state manager only
python test_state_manager.py

# Test integration only
python test_integration.py

# Run visual demo
python demo_overlay.py

# Run all tests
.\run_tests.bat
```

## Troubleshooting

### "python3 is not recognized"
Windows uses `python` not `python3`. Use:
```powershell
python test_state_manager.py  # ✓ Correct
python3 test_state_manager.py # ✗ Wrong on Windows
```

### "No module named 'PyQt6'"
Install PyQt6:
```powershell
pip install PyQt6
```

### ".sh is not recognized"
`.sh` files are for Linux/Mac. Use `.bat` files on Windows:
```powershell
.\run_tests.bat  # ✓ Correct for Windows
./run_tests.sh   # ✗ Linux/Mac only
```

### Overlay doesn't appear
- Make sure you have PyQt6 installed
- Check your taskbar - it might be minimized
- Look in bottom-right corner of your screen

## Next Steps

After testing, we can continue building:
1. Audio Capture - Microphone input
2. Hotkey Manager - Global keyboard shortcuts
3. Speech Recognition - Vosk integration
4. Keyboard Typing - Automated text input
5. Complete App - Everything together!

Let me know which component to build next! 🚀
