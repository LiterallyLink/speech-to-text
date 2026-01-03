#!/usr/bin/env python3
"""
Test script for the overlay widget.

This script creates a simple application to test the overlay widget functionality:
- Displays the overlay on screen
- Tests dragging
- Tests updating status text
- Tests changing background colors
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor

# Add src to path so we can import our module
sys.path.insert(0, '/home/user/speech-to-text/src')

from stt_keyboard.gui.overlay_widget import OverlayWidget


def test_color_changes(overlay):
    """Test changing overlay colors every 2 seconds"""
    colors = [
        (QColor(40, 40, 40, 200), "Ready", "Idle state"),
        (QColor(255, 0, 0, 180), "Listening...", "Recording audio"),
        (QColor(255, 165, 0, 180), "Processing...", "Transcribing speech"),
        (QColor(0, 255, 0, 180), "Typing...", "Simulating keyboard"),
    ]

    current_index = [0]  # Use list to make it mutable in nested function

    def cycle_colors():
        color, status, info = colors[current_index[0]]
        overlay.set_background_color(color)
        overlay.update_status(status)
        overlay.update_info(info)
        current_index[0] = (current_index[0] + 1) % len(colors)

    # Create timer to cycle colors every 2 seconds
    timer = QTimer()
    timer.timeout.connect(cycle_colors)
    timer.start(2000)  # 2000 ms = 2 seconds

    return timer  # Keep reference to prevent garbage collection


def main():
    """Main test function"""
    print("Starting Overlay Widget Test")
    print("=" * 50)
    print("Test Instructions:")
    print("1. You should see a semi-transparent overlay in the bottom-right")
    print("2. The overlay should cycle through different colors every 2 seconds:")
    print("   - Dark gray (Ready)")
    print("   - Red (Listening)")
    print("   - Orange (Processing)")
    print("   - Green (Typing)")
    print("3. Try dragging the overlay with your mouse")
    print("4. Close the window or press Ctrl+C to exit")
    print("=" * 50)

    # Create Qt application
    app = QApplication(sys.argv)

    # Create and show overlay
    overlay = OverlayWidget()
    overlay.show()

    # Start color cycling test
    timer = test_color_changes(overlay)

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
