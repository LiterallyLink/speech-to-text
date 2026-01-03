#!/bin/bash
# Run all tests for STT Keyboard

echo "=========================================="
echo "STT Keyboard Test Suite"
echo "=========================================="
echo ""

# Track test results
FAILED=0

# Test 1: State Manager
echo "📋 Running State Manager Tests..."
python3 test_state_manager.py
if [ $? -eq 0 ]; then
    echo "✅ State Manager: PASSED"
else
    echo "❌ State Manager: FAILED"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 2: Integration
echo "🔗 Running Integration Tests..."
python3 test_integration.py
if [ $? -eq 0 ]; then
    echo "✅ Integration: PASSED"
else
    echo "❌ Integration: FAILED"
    FAILED=$((FAILED + 1))
fi
echo ""

# Summary
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
else
    echo "❌ $FAILED TEST(S) FAILED"
fi
echo "=========================================="

exit $FAILED
