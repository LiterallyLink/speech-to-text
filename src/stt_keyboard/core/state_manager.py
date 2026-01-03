"""Application state management"""

from enum import Enum
from typing import Callable, List
from ..utils.logger import setup_logger


class ApplicationState(Enum):
    """Application states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    TYPING = "typing"
    ERROR = "error"


class StateManager:
    """Manages application state and notifies subscribers"""

    def __init__(self):
        """Initialize state manager"""
        self.logger = setup_logger(__name__)
        self._state = ApplicationState.IDLE
        self._subscribers: List[Callable] = []

    def get_state(self) -> ApplicationState:
        """
        Get current state

        Returns:
            Current application state
        """
        return self._state

    def set_state(self, new_state: ApplicationState):
        """
        Set new state and notify subscribers

        Args:
            new_state: New application state
        """
        old_state = self._state
        self._state = new_state

        self.logger.debug(f"State transition: {old_state.value} -> {new_state.value}")

        # Notify subscribers
        for callback in self._subscribers:
            try:
                callback(old_state, new_state)
            except Exception as e:
                self.logger.error(f"Error in state change callback: {e}")

    def subscribe(self, callback: Callable[[ApplicationState, ApplicationState], None]):
        """
        Subscribe to state changes

        Args:
            callback: Function to call on state change with (old_state, new_state)
        """
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable):
        """
        Unsubscribe from state changes

        Args:
            callback: Callback function to remove
        """
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def handle_error(self, error: Exception):
        """
        Handle error and transition to error state

        Args:
            error: Exception that occurred
        """
        self.logger.error(f"Error occurred: {error}")
        self.set_state(ApplicationState.ERROR)
