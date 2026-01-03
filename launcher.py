"""
Launcher script for STT Keyboard
This is used by PyInstaller as the entry point
"""

import sys
from pathlib import Path

# Add src to path if running from source
src_path = Path(__file__).parent / 'src'
if src_path.exists():
    sys.path.insert(0, str(src_path))

# Import and run the app
from stt_keyboard.app import main

if __name__ == '__main__':
    main()
