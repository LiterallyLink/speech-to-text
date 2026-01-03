# How to Run and Test

This guide shows you how to test what we've built so far.

## Current Status

We've completed **3 incremental steps**:
1. ✅ Overlay Widget (visual UI)
2. ✅ State Manager (application state)
3. ✅ Integration (overlay + state working together)

## Quick Test (No Display Required)

These tests work in any environment, including headless servers:

```bash
# Test 1: State Manager
python3 test_state_manager.py

# Test 2: State Manager + Overlay Integration
python3 test_integration.py
```

Both should show `✓ ALL TESTS PASSED`

## Visual Demo (Requires Display)

If you have a graphical environment (X11, Wayland, Windows, macOS):

```bash
# Run the interactive demo
python3 demo_overlay.py
```

This will:
- Show a semi-transparent overlay in bottom-right corner
- Automatically cycle through all states (colors change)
- Display real-time transcription simulation
- Allow you to drag the overlay around
- Let you manually trigger states with keyboard (1-5, Q to quit)

### What You'll See

- **Dark Gray**: IDLE state - Ready to record
- **Red**: LISTENING state - Recording audio
- **Orange**: PROCESSING state - Transcribing speech
- **Green**: TYPING state - Typing recognized text
- **Dark Red**: ERROR state - Something went wrong

The overlay stays on top of all other windows, just like it will in the final app!

## Installation

First time setup:

```bash
# Install dependencies
pip install PyQt6

# Or install all dependencies
pip install -r requirements.txt
```

## Testing Individual Components

### Test State Manager Only
```bash
python3 test_state_manager.py
```

**Tests:**
- Basic state transitions (IDLE → LISTENING → PROCESSING → TYPING)
- Subscriber notifications (Observer pattern)
- Error handling
- State history tracking
- Multiple subscribers

### Test Integration
```bash
python3 test_integration.py
```

**Tests:**
- State manager notifies overlay
- Complete transcription cycle simulation
- Color/label mappings for all states
- Error handling and recovery

## What's NOT Built Yet

Currently we have:
- ✅ Visual overlay UI
- ✅ State management
- ✅ Integration between them

Still needed:
- ❌ Audio capture (microphone input)
- ❌ Speech recognition (Vosk)
- ❌ Hotkey manager (global keyboard shortcuts)
- ❌ Keyboard simulator (typing text)
- ❌ Main application loop

## Running in Different Environments

### Linux (with X11/Wayland)
```bash
# Should work out of the box
python3 demo_overlay.py
```

### Linux (headless/SSH)
```bash
# Use Xvfb for virtual display
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
python3 demo_overlay.py

# Or just run the non-GUI tests
python3 test_state_manager.py
python3 test_integration.py
```

### Windows
```bash
# Should work if PyQt6 is installed
python demo_overlay.py
```

### macOS
```bash
# Should work if PyQt6 is installed
python3 demo_overlay.py
```

## Troubleshooting

**Error: "libEGL.so.1: cannot open shared object file"**
- You're in a headless environment
- Run the non-GUI tests instead: `test_state_manager.py` and `test_integration.py`

**Error: "No module named 'PyQt6'"**
```bash
pip install PyQt6
```

**Overlay doesn't appear**
- Check you have a display/GUI environment
- Try clicking on your desktop (overlay might be behind windows)
- Look in bottom-right corner of screen

**Keyboard shortcuts don't work**
- Click the overlay first to give it focus
- Then press 1-5 to change states

## Next Steps

Once you've tested the current components, we can build:
1. **Audio Capture** - Microphone input
2. **Hotkey Manager** - Global Ctrl+Shift+Space
3. **Speech Engine** - Vosk speech recognition
4. **Keyboard Simulator** - Type the recognized text
5. **Main App** - Tie everything together

Each will be built incrementally with tests!
