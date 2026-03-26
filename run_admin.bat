@echo off
:: Batch script to check for admin privileges and run the Built2Map scanner
NET SESSION >nul 2>&1
if %errorLevel% == 0 (
    echo Administrator privileges confirmed. Starting Built2Map...
    cd /d "%~dp0"
    .\venv\Scripts\python app.py
    pause
) else (
    echo [ERROR] Administrative privileges required!
    echo Please right-click this script and select "Run as administrator".
    pause
    exit /b 1
)
