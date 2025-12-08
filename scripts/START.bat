@echo off
echo ========================================
echo Learning Buddy - Quick Start Script
echo ========================================
echo.

echo [1/2] Starting Backend Server...
cd ..\backend
if exist venv\Scripts\activate (
    start "Learning Buddy Backend" cmd /k "venv\Scripts\activate && python app.py"
) else (
    start "Learning Buddy Backend" cmd /k "python app.py"
)
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server...
cd ..\frontend
start "Learning Buddy Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173 (Vite default port)
echo ========================================
echo.
echo Press any key to exit...
pause >nul

