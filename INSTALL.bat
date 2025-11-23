@echo off
echo ========================================
echo Image Authenticity Detector - Installation
echo ========================================
echo.

REM Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo Python found!

REM Check Node.js
echo [2/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
echo Node.js found!

REM Install Python dependencies
echo [3/4] Installing Python dependencies...
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)
echo Creating fresh virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo Python dependencies installed!

REM Install frontend dependencies
echo [4/4] Installing frontend dependencies...
cd frontend-svelte
if not exist "node_modules" (
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        cd ..
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies already installed, skipping...
)
cd ..

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the application:
echo   1. Backend:   START_BACKEND.bat
echo   2. Frontend:  START_SVELTE.bat
echo.
echo Or manually:
echo   1. Backend:   venv\Scripts\activate ^&^& python app.py
echo   2. Frontend:  cd frontend-svelte ^&^& npm run dev
echo.
pause

