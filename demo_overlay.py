#!/usr/bin/env python3
"""
Demo application to showcase the overlay widget with state management.

This demonstrates what we've built so far:
- Overlay widget that displays on screen
- State management system
- Automatic UI updates based on state

Press keyboard shortcuts to simulate different states:
- 1: IDLE state (dark gray)
- 2: LISTENING state (red)
- 3: PROCESSING state (orange)
- 4: TYPING state (green)
- 5: ERROR state (dark red)
- Q: Quit
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QShortcut, QKeySequence

sys.path.insert(0, '/home/user/speech-to-text/src')

from stt_keyboard.gui.overlay_widget import OverlayWidget
from stt_keyboard.core.state_manager import StateManager, ApplicationState


class DemoApp:
    """Demo application to showcase overlay + state management"""

    def __init__(self):
        self.app = QApplication(sys.argv)

        # Create state manager
        self.state_manager = StateManager()

        # Create overlay and connect to state manager
        self.overlay = OverlayWidget(self.state_manager)

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        # Show overlay
        self.overlay.show()

        # Print instructions
        self._print_instructions()

        # Simulate a transcription cycle after 2 seconds
        QTimer.singleShot(2000, self._start_auto_demo)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for state changes"""
        # Note: These shortcuts only work when overlay has focus
        QShortcut(QKeySequence('1'), self.overlay, lambda: self.change_state(ApplicationState.IDLE))
        QShortcut(QKeySequence('2'), self.overlay, lambda: self.change_state(ApplicationState.LISTENING))
        QShortcut(QKeySequence('3'), self.overlay, lambda: self.change_state(ApplicationState.PROCESSING))
        QShortcut(QKeySequence('4'), self.overlay, lambda: self.change_state(ApplicationState.TYPING))
        QShortcut(QKeySequence('5'), self.overlay, lambda: self.state_manager.handle_error("Demo error"))
        QShortcut(QKeySequence('Q'), self.overlay, self.app.quit)

    def change_state(self, new_state):
        """Change to a new state"""
        self.state_manager.set_state(new_state)
        print(f"State changed to: {new_state.value}")

    def _print_instructions(self):
        """Print usage instructions"""
        print("=" * 60)
        print("STT Keyboard - Overlay Demo")
        print("=" * 60)
        print()
        print("What you're seeing:")
        print("  • A semi-transparent overlay window in the bottom-right")
        print("  • The overlay stays on top of all other windows")
        print("  • You can drag it by clicking and moving")
        print()
        print("Automatic demo:")
        print("  • Watch as the overlay cycles through states automatically")
        print("  • Colors and text change based on application state")
        print()
        print("Manual controls (click overlay first to focus):")
        print("  1 - IDLE state (dark gray)")
        print("  2 - LISTENING state (red)")
        print("  3 - PROCESSING state (orange)")
        print("  4 - TYPING state (green)")
        print("  5 - ERROR state (dark red)")
        print("  Q - Quit")
        print()
        print("=" * 60)

    def _start_auto_demo(self):
        """Start automatic state cycling demo"""
        print("\nStarting automatic demo...")
        print("Watch the overlay change colors!\n")

        # Schedule state changes
        QTimer.singleShot(0, lambda: self._demo_step("LISTENING"))
        QTimer.singleShot(2000, lambda: self._demo_step("PROCESSING"))
        QTimer.singleShot(4000, lambda: self._demo_step("TYPING"))
        QTimer.singleShot(6000, lambda: self._demo_step("IDLE"))

        # Show transcription text example
        QTimer.singleShot(2500, lambda: self._show_transcription("Hello world"))
        QTimer.singleShot(3000, lambda: self._show_transcription("Hello world this is a test"))
        QTimer.singleShot(3500, lambda: self._show_transcription("Hello world this is a test of speech"))

        # Repeat the cycle
        QTimer.singleShot(8000, self._start_auto_demo)

    def _demo_step(self, state_name):
        """Execute a demo step"""
        state = ApplicationState[state_name]
        self.state_manager.set_state(state)
        print(f"→ {state.value.upper()}")

    def _show_transcription(self, text):
        """Show transcription text on overlay"""
        self.overlay.set_transcription_text(text)
        print(f"  Transcription: \"{text}\"")

    def run(self):
        """Run the application"""
        return self.app.exec()


def main():
    """Main entry point"""
    # Check if we have a display
    try:
        demo = DemoApp()
        sys.exit(demo.run())
    except Exception as e:
        print("=" * 60)
        print("Cannot run demo (no display available)")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("This is expected in headless environments.")
        print("To test the code without GUI, run:")
        print("  python3 test_state_manager.py")
        print("  python3 test_integration.py")
        print()
        return 1


if __name__ == "__main__":
    main()
