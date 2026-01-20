@echo off
REM ===================================================================
REM Preview Report - Dry Run (No Email Sent)
REM Double-click to generate and preview HTML report
REM ===================================================================

echo.
echo ====================================
echo   GENERATING PREVIEW...
echo ====================================
echo.

REM Use virtual environment if available
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe run_report.py --dry-run
) else if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe run_report.py --dry-run
) else (
    python run_report.py --dry-run
)

echo.
echo Opening report in browser...
start output\report.html

echo.
echo ====================================
pause
