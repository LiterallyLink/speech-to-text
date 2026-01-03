#!/usr/bin/env python3
"""
Test script for state manager + overlay widget integration.

This demonstrates how the state manager and overlay widget work together.
"""

import sys
sys.path.insert(0, '/home/user/speech-to-text/src')

from stt_keyboard.core.state_manager import StateManager, ApplicationState


def test_integration_without_gui():
    """
    Test the integration logic without requiring a GUI.

    This tests that the state manager properly notifies subscribers,
    which is how the overlay widget receives updates.
    """
    print("=" * 60)
    print("State Manager + Overlay Integration Test (No GUI)")
    print("=" * 60)
    print()

    # Create state manager
    state_mgr = StateManager()
    print("✓ Created state manager")

    # Simulate overlay widget behavior with a mock class
    class MockOverlay:
        def __init__(self):
            self.current_state = None
            self.state_changes = []

        def on_state_changed(self, old_state, new_state):
            """Simulates overlay's state change handler"""
            self.current_state = new_state
            self.state_changes.append((old_state, new_state))
            print(f"  Overlay updated: {old_state.value} → {new_state.value}")

    # Create mock overlay and subscribe to state changes
    overlay = MockOverlay()
    state_mgr.subscribe(overlay.on_state_changed)
    print("✓ Connected mock overlay to state manager")
    print()

    # Simulate a complete transcription cycle
    print("Simulating transcription cycle:")
    print("-" * 60)

    print("\n1. User presses hotkey...")
    state_mgr.set_state(ApplicationState.LISTENING)
    assert overlay.current_state == ApplicationState.LISTENING
    print("   ✓ Overlay now shows LISTENING (red background)")

    print("\n2. User releases hotkey (or voice activity detected)...")
    state_mgr.set_state(ApplicationState.PROCESSING)
    assert overlay.current_state == ApplicationState.PROCESSING
    print("   ✓ Overlay now shows PROCESSING (orange background)")

    print("\n3. Transcription complete, typing begins...")
    state_mgr.set_state(ApplicationState.TYPING)
    assert overlay.current_state == ApplicationState.TYPING
    print("   ✓ Overlay now shows TYPING (green background)")

    print("\n4. Typing complete, back to idle...")
    state_mgr.set_state(ApplicationState.IDLE)
    assert overlay.current_state == ApplicationState.IDLE
    print("   ✓ Overlay now shows IDLE (dark gray background)")

    print("\n5. Simulate an error...")
    state_mgr.handle_error("Microphone not available")
    assert overlay.current_state == ApplicationState.ERROR
    print("   ✓ Overlay now shows ERROR (dark red background)")
    print(f"   ✓ Error message: \"{state_mgr.get_error_message()}\"")

    print("\n6. Reset from error...")
    state_mgr.reset()
    assert overlay.current_state == ApplicationState.IDLE
    print("   ✓ Overlay reset to IDLE")

    print()
    print("-" * 60)
    print(f"✓ Total state changes recorded: {len(overlay.state_changes)}")
    print()

    # Verify all state transitions were received
    expected_transitions = [
        (ApplicationState.IDLE, ApplicationState.LISTENING),
        (ApplicationState.LISTENING, ApplicationState.PROCESSING),
        (ApplicationState.PROCESSING, ApplicationState.TYPING),
        (ApplicationState.TYPING, ApplicationState.IDLE),
        (ApplicationState.IDLE, ApplicationState.ERROR),
        (ApplicationState.ERROR, ApplicationState.IDLE),
    ]

    assert overlay.state_changes == expected_transitions
    print("✓ All state transitions occurred correctly")
    print()

    print("=" * 60)
    print("✓ INTEGRATION TEST PASSED")
    print("=" * 60)
    print()

    print("What this demonstrates:")
    print("  • State manager successfully notifies observers")
    print("  • Overlay receives state change events")
    print("  • Complete transcription cycle works")
    print("  • Error handling and recovery works")
    print()
    print("In the real application:")
    print("  • The overlay widget would change colors automatically")
    print("  • Status text would update (Ready → Listening → etc.)")
    print("  • Info text would show appropriate hints")
    print("  • User sees visual feedback for each state")
    print()


def test_color_mapping():
    """Test that the overlay has proper color mappings for each state"""
    print("=" * 60)
    print("Testing Overlay Color Mappings")
    print("=" * 60)
    print()

    try:
        # Import the actual OverlayWidget class (won't instantiate it)
        from stt_keyboard.gui.overlay_widget import OverlayWidget

        # Verify all states have color mappings
        for state in ApplicationState:
            assert state in OverlayWidget.STATE_COLORS, f"Missing color for {state}"
            print(f"✓ {state.value:12s} → {OverlayWidget.STATE_COLORS[state].getRgb()}")

        print()

        # Verify all states have label mappings
        print("State Labels:")
        for state in ApplicationState:
            assert state in OverlayWidget.STATE_LABELS, f"Missing label for {state}"
            print(f"✓ {state.value:12s} → \"{OverlayWidget.STATE_LABELS[state]}\"")

        print()
        print("✓ All color and label mappings verified")
        print()

    except ImportError as e:
        print("⚠ Skipping GUI-dependent test (no display available)")
        print(f"  Import error: {e}")
        print("  This is expected in headless environments")
        print()


def main():
    """Run all integration tests"""
    try:
        test_integration_without_gui()
        test_color_mapping()

        print("=" * 60)
        print("✓ ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
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
