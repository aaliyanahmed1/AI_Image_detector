@echo off
echo ========================================
echo Starting Image Authenticity Detector
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run INSTALL.bat first
    pause
    exit /b 1
)

REM Check if frontend dependencies are installed
if not exist "frontend-svelte\node_modules" (
    echo ERROR: Frontend dependencies not installed!
    echo Please run INSTALL.bat first
    pause
    exit /b 1
)

echo Starting Backend Server...
start "Backend Server" cmd /k "venv\Scripts\activate.bat && python app.py"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
cd frontend-svelte
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo Servers Started!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Close the command windows to stop the servers.
echo.
pause

