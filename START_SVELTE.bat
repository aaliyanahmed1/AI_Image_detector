@echo off
echo Starting Svelte Frontend Development Server...
echo.

cd frontend-svelte

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start frontend
echo.
echo Starting Svelte frontend on http://localhost:3000
echo.
call npm run dev

