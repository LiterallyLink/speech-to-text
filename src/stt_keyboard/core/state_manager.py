"""State manager for tracking application state and notifying subscribers"""

from enum import Enum
from typing import Callable, List, Tuple
from datetime import datetime


class ApplicationState(Enum):
    """
    Application states for the STT Keyboard.

    State transitions:
    IDLE -> LISTENING -> PROCESSING -> TYPING -> IDLE
    ERROR can occur from any state
    """
    IDLE = "idle"              # Ready for input
    LISTENING = "listening"    # Recording audio
    PROCESSING = "processing"  # Transcribing audio
    TYPING = "typing"         # Typing recognized text
    ERROR = "error"           # Error occurred


class StateManager:
    """
    Manages application state and notifies subscribers of state changes.

    Uses the Observer pattern to allow components to react to state changes
    without tight coupling.

    Example:
        state_mgr = StateManager()

        def on_state_change(old_state, new_state):
            print(f"State changed: {old_state.value} -> {new_state.value}")

        state_mgr.subscribe(on_state_change)
        state_mgr.set_state(ApplicationState.LISTENING)
    """

    def __init__(self, initial_state: ApplicationState = ApplicationState.IDLE):
        """
        Initialize the state manager.

        Args:
            initial_state: The starting state (default: IDLE)
        """
        self._current_state = initial_state
        self._previous_state = None
        self._subscribers: List[Callable[[ApplicationState, ApplicationState], None]] = []
        self._state_history: List[Tuple[datetime, ApplicationState]] = []
        self._error_message: str = ""

        # Record initial state
        self._record_state(initial_state)

    def get_state(self) -> ApplicationState:
        """
        Get the current application state.

        Returns:
            Current ApplicationState
        """
        return self._current_state

    def get_previous_state(self) -> ApplicationState:
        """
        Get the previous application state.

        Returns:
            Previous ApplicationState or None if this is the first state
        """
        return self._previous_state

    def set_state(self, new_state: ApplicationState, error_message: str = ""):
        """
        Change the application state and notify all subscribers.

        Args:
            new_state: The new state to transition to
            error_message: Optional error message if transitioning to ERROR state
        """
        if new_state == self._current_state:
            # No change, don't notify
            return

        old_state = self._current_state
        self._previous_state = old_state
        self._current_state = new_state
        self._record_state(new_state)

        # Store error message if applicable
        if new_state == ApplicationState.ERROR:
            self._error_message = error_message

        # Notify all subscribers
        self._notify_subscribers(old_state, new_state)

    def subscribe(self, callback: Callable[[ApplicationState, ApplicationState], None]):
        """
        Subscribe to state change notifications.

        Args:
            callback: Function to call when state changes.
                     Signature: callback(old_state, new_state)
        """
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[ApplicationState, ApplicationState], None]):
        """
        Unsubscribe from state change notifications.

        Args:
            callback: The callback function to remove
        """
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def handle_error(self, error_message: str):
        """
        Handle an error by transitioning to ERROR state.

        Args:
            error_message: Description of the error
        """
        self.set_state(ApplicationState.ERROR, error_message)

    def get_error_message(self) -> str:
        """
        Get the current error message.

        Returns:
            Error message string (empty if no error)
        """
        return self._error_message

    def reset(self):
        """Reset to IDLE state and clear error message"""
        self._error_message = ""
        self.set_state(ApplicationState.IDLE)

    def get_state_history(self) -> List[Tuple[datetime, ApplicationState]]:
        """
        Get the history of state changes.

        Returns:
            List of (timestamp, state) tuples
        """
        return self._state_history.copy()

    def _record_state(self, state: ApplicationState):
        """
        Record a state change in the history.

        Args:
            state: The state to record
        """
        self._state_history.append((datetime.now(), state))

        # Keep only last 100 entries to prevent memory growth
        if len(self._state_history) > 100:
            self._state_history = self._state_history[-100:]

    def _notify_subscribers(self, old_state: ApplicationState, new_state: ApplicationState):
        """
        Notify all subscribers of a state change.

        Args:
            old_state: The previous state
            new_state: The new state
        """
        for callback in self._subscribers:
            try:
                callback(old_state, new_state)
            except Exception as e:
                # Don't let subscriber errors crash the state manager
                print(f"Error in state change subscriber: {e}")

    def __repr__(self) -> str:
        """String representation of the state manager"""
        return f"StateManager(state={self._current_state.value})"
