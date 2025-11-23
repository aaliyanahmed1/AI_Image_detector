@echo off
echo Starting Backend Server...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment (PowerShell/CMD compatible)
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo Checking dependencies...
pip install -q -r requirements.txt

REM Start backend
echo.
echo Starting FastAPI backend on http://localhost:8000
echo.
python app.py

