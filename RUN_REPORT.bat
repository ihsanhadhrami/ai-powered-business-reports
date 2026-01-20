@echo off
REM ===================================================================
REM Email Report App - Quick Launch Script
REM Double-click this file to run the email report
REM ===================================================================

echo.
echo ========================================
echo   EMAIL REPORT APP
echo ========================================
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo Using virtual environment...
    set PYTHON_CMD=.venv\Scripts\python.exe
) else if exist "venv\Scripts\python.exe" (
    echo Using virtual environment...
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    echo Using system Python...
    set PYTHON_CMD=python
)

REM Ask user what they want to do
echo What would you like to do?
echo.
echo [1] Send Email Report Now
echo [2] Preview Report (Dry Run - No Email)
echo [3] Run on Schedule
echo [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Sending email report...
    %PYTHON_CMD% run_report.py
) else if "%choice%"=="2" (
    echo.
    echo Generating preview...
    %PYTHON_CMD% run_report.py --dry-run
    echo.
    echo Opening report in browser...
    start output\report.html
) else if "%choice%"=="3" (
    echo.
    echo Starting scheduled mode...
    %PYTHON_CMD% run_report.py --schedule
) else if "%choice%"=="4" (
    echo.
    echo Exiting...
    exit /b 0
) else (
    echo.
    echo Invalid choice. Please run again.
)

echo.
echo ========================================
pause
