@echo off
REM ===================================================================
REM Run Tests - Execute all unit tests with coverage
REM ===================================================================

echo.
echo ====================================
echo   RUNNING UNIT TESTS
echo ====================================
echo.

REM Use virtual environment if available
if exist ".venv\Scripts\python.exe" (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)

echo Using Python: %PYTHON_CMD%
echo.

REM Run tests with verbose output
%PYTHON_CMD% -m pytest tests/ -v --tb=short

echo.
echo ====================================
echo   Tests Complete
echo ====================================
pause
