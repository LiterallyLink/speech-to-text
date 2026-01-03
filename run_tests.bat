@echo off
REM Run all tests for STT Keyboard on Windows

echo ==========================================
echo STT Keyboard Test Suite
echo ==========================================
echo.

set FAILED=0

REM Test 1: State Manager
echo Running State Manager Tests...
python test_state_manager.py
if %errorlevel% equ 0 (
    echo [32m✓ State Manager: PASSED[0m
) else (
    echo [31m✗ State Manager: FAILED[0m
    set /a FAILED+=1
)
echo.

REM Test 2: Integration
echo Running Integration Tests...
python test_integration.py
if %errorlevel% equ 0 (
    echo [32m✓ Integration: PASSED[0m
) else (
    echo [31m✗ Integration: FAILED[0m
    set /a FAILED+=1
)
echo.

REM Summary
echo ==========================================
if %FAILED% equ 0 (
    echo [32m✓ ALL TESTS PASSED[0m
) else (
    echo [31m✗ %FAILED% TEST(S) FAILED[0m
)
echo ==========================================

exit /b %FAILED%
