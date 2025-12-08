@echo off
echo ========================================
echo Learning Buddy - Backend Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Please create .env file with MongoDB connection string
    echo.
    echo Example .env content:
    echo MONGO_URI=your_mongodb_connection_string
    echo DB_NAME=learning_buddy_db
    echo PORT=5000
    echo.
    pause
)

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo [OK] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [INFO] No virtual environment found, using system Python
)

REM Check if requirements are installed
echo [INFO] Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Flask not found. Installing requirements...
    pip install -r requirements.txt
)

echo.
echo ========================================
echo Starting Backend Server...
echo ========================================
echo Backend will run on: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause

