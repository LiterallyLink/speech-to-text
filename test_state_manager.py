#!/usr/bin/env python3
"""
Test script for the state manager.

This tests the state management system without requiring a GUI.
"""

import sys
sys.path.insert(0, '/home/user/speech-to-text/src')

from stt_keyboard.core.state_manager import StateManager, ApplicationState


def test_basic_state_transitions():
    """Test basic state transitions"""
    print("Test 1: Basic State Transitions")
    print("-" * 50)

    state_mgr = StateManager()

    # Verify initial state
    assert state_mgr.get_state() == ApplicationState.IDLE
    print("✓ Initial state is IDLE")

    # Transition to LISTENING
    state_mgr.set_state(ApplicationState.LISTENING)
    assert state_mgr.get_state() == ApplicationState.LISTENING
    assert state_mgr.get_previous_state() == ApplicationState.IDLE
    print("✓ Transitioned to LISTENING")

    # Transition to PROCESSING
    state_mgr.set_state(ApplicationState.PROCESSING)
    assert state_mgr.get_state() == ApplicationState.PROCESSING
    assert state_mgr.get_previous_state() == ApplicationState.LISTENING
    print("✓ Transitioned to PROCESSING")

    # Transition to TYPING
    state_mgr.set_state(ApplicationState.TYPING)
    assert state_mgr.get_state() == ApplicationState.TYPING
    print("✓ Transitioned to TYPING")

    # Back to IDLE
    state_mgr.set_state(ApplicationState.IDLE)
    assert state_mgr.get_state() == ApplicationState.IDLE
    print("✓ Back to IDLE")

    print("✓ All basic transitions passed\n")


def test_subscriber_notifications():
    """Test that subscribers are notified of state changes"""
    print("Test 2: Subscriber Notifications")
    print("-" * 50)

    state_mgr = StateManager()
    notifications = []

    def on_state_change(old_state, new_state):
        notifications.append((old_state, new_state))

    # Subscribe to notifications
    state_mgr.subscribe(on_state_change)
    print("✓ Subscriber registered")

    # Make some state changes
    state_mgr.set_state(ApplicationState.LISTENING)
    state_mgr.set_state(ApplicationState.PROCESSING)
    state_mgr.set_state(ApplicationState.IDLE)

    # Verify notifications were received
    assert len(notifications) == 3
    assert notifications[0] == (ApplicationState.IDLE, ApplicationState.LISTENING)
    assert notifications[1] == (ApplicationState.LISTENING, ApplicationState.PROCESSING)
    assert notifications[2] == (ApplicationState.PROCESSING, ApplicationState.IDLE)
    print(f"✓ Received {len(notifications)} notifications")

    # Test unsubscribe
    state_mgr.unsubscribe(on_state_change)
    state_mgr.set_state(ApplicationState.LISTENING)
    assert len(notifications) == 3  # No new notifications
    print("✓ Unsubscribe works correctly\n")


def test_error_handling():
    """Test error state handling"""
    print("Test 3: Error Handling")
    print("-" * 50)

    state_mgr = StateManager()

    # Simulate an error
    error_msg = "Test error message"
    state_mgr.handle_error(error_msg)

    assert state_mgr.get_state() == ApplicationState.ERROR
    assert state_mgr.get_error_message() == error_msg
    print(f"✓ Error state set with message: '{error_msg}'")

    # Reset from error
    state_mgr.reset()
    assert state_mgr.get_state() == ApplicationState.IDLE
    assert state_mgr.get_error_message() == ""
    print("✓ Reset from error to IDLE\n")


def test_state_history():
    """Test state history tracking"""
    print("Test 4: State History")
    print("-" * 50)

    state_mgr = StateManager()

    # Make several state changes
    state_mgr.set_state(ApplicationState.LISTENING)
    state_mgr.set_state(ApplicationState.PROCESSING)
    state_mgr.set_state(ApplicationState.TYPING)
    state_mgr.set_state(ApplicationState.IDLE)

    history = state_mgr.get_state_history()

    # Should have 5 entries (initial IDLE + 4 changes)
    assert len(history) == 5
    print(f"✓ State history contains {len(history)} entries")

    # Verify the sequence
    states = [state for _, state in history]
    expected = [
        ApplicationState.IDLE,
        ApplicationState.LISTENING,
        ApplicationState.PROCESSING,
        ApplicationState.TYPING,
        ApplicationState.IDLE
    ]
    assert states == expected
    print("✓ State history sequence is correct")

    # Print history
    print("\nState history:")
    for timestamp, state in history:
        print(f"  {timestamp.strftime('%H:%M:%S.%f')[:-3]} - {state.value}")
    print()


def test_multiple_subscribers():
    """Test multiple subscribers"""
    print("Test 5: Multiple Subscribers")
    print("-" * 50)

    state_mgr = StateManager()
    notifications1 = []
    notifications2 = []

    def subscriber1(old, new):
        notifications1.append(f"{old.value}->{new.value}")

    def subscriber2(old, new):
        notifications2.append(f"{old.value}->{new.value}")

    state_mgr.subscribe(subscriber1)
    state_mgr.subscribe(subscriber2)

    state_mgr.set_state(ApplicationState.LISTENING)
    state_mgr.set_state(ApplicationState.IDLE)

    assert len(notifications1) == 2
    assert len(notifications2) == 2
    assert notifications1 == notifications2
    print(f"✓ Both subscribers received {len(notifications1)} notifications")
    print(f"  Subscriber 1: {notifications1}")
    print(f"  Subscriber 2: {notifications2}\n")


def main():
    """Run all tests"""
    print("=" * 50)
    print("State Manager Test Suite")
    print("=" * 50)
    print()

    try:
        test_basic_state_transitions()
        test_subscriber_notifications()
        test_error_handling()
        test_state_history()
        test_multiple_subscribers()

        print("=" * 50)
        print("✓ ALL TESTS PASSED")
        print("=" * 50)
        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
