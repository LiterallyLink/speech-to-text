"""Keyboard input simulation"""

import time
import keyboard
from typing import Optional

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
        """
        Press a single key

        Args:
            key: Key to press
        """
        keyboard.press_and_release(key)

    def send_backspace(self, count: int = 1):
        """
        Send backspace key multiple times

        Args:
            count: Number of backspaces to send
        """
        for _ in range(count):
            keyboard.press_and_release('backspace')
            time.sleep(0.05)

    def send_enter(self):
        """Send enter/return key"""
        keyboard.press_and_release('enter')
