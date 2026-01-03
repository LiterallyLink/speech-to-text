"""Global hotkey management"""

import keyboard
from typing import Callable, Dict

from ..config.models import HotkeyConfig
from ..utils.logger import setup_logger


class HotkeyManager:
    """Manages global hotkeys"""

    def __init__(self, config: HotkeyConfig):
        """
        Initialize hotkey manager

        Args:
            config: Hotkey configuration
        """
        self.logger = setup_logger(__name__)
        self.config = config
        self.registered_hotkeys: Dict[str, Callable] = {}
        self.is_active = False

    def register_hotkey(self, combination: str, callback: Callable):
        """
        Register a global hotkey

        Args:
            combination: Key combination (e.g., "ctrl+shift+space")
            callback: Function to call when hotkey is pressed
        """
        try:
            # Store the callback
            self.registered_hotkeys[combination] = callback

            # Register with keyboard library
            keyboard.add_hotkey(combination, callback)

            self.logger.info(f"Registered hotkey: {combination}")

        except Exception as e:
            self.logger.error(f"Failed to register hotkey {combination}: {e}")
            raise

    def unregister_hotkey(self, combination: str):
        """
        Unregister a hotkey

        Args:
            combination: Key combination to unregister
        """
        try:
            if combination in self.registered_hotkeys:
                keyboard.remove_hotkey(combination)
                del self.registered_hotkeys[combination]
                self.logger.info(f"Unregistered hotkey: {combination}")

        except Exception as e:
            self.logger.error(f"Failed to unregister hotkey {combination}: {e}")

    def start(self):
        """Start the hotkey manager"""
        self.is_active = True
        self.logger.info("Hotkey manager started")

    def stop(self):
        """Stop the hotkey manager and unregister all hotkeys"""
        self.is_active = False

        # Unregister all hotkeys
        for combination in list(self.registered_hotkeys.keys()):
            self.unregister_hotkey(combination)

        self.logger.info("Hotkey manager stopped")
