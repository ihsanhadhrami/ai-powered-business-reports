@echo off
REM ===================================================================
REM Quick Start - Send Report Immediately (No Questions)
REM Double-click for instant email sending
REM ===================================================================

echo.
echo ====================================
echo   SENDING EMAIL REPORT NOW...
echo ====================================
echo.

REM Use virtual environment if available
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe run_report.py
) else if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe run_report.py
) else (
    python run_report.py
)

echo.
echo ====================================
pause
