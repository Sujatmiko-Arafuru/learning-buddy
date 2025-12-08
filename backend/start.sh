#!/bin/bash

echo "========================================"
echo "Learning Buddy - Backend Server"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[OK] Python found"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "[WARNING] .env file not found!"
    echo "Please create .env file with MongoDB connection string"
    echo ""
    echo "Example .env content:"
    echo "MONGO_URI=your_mongodb_connection_string"
    echo "DB_NAME=learning_buddy_db"
    echo "PORT=5000"
    echo ""
    read -p "Press enter to continue anyway..."
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "[OK] Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "[OK] Activating virtual environment..."
    source .venv/bin/activate
else
    echo "[INFO] No virtual environment found, using system Python"
fi

# Check if requirements are installed
echo "[INFO] Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] Flask not found. Installing requirements..."
    pip3 install -r requirements.txt
fi

echo ""
echo "========================================"
echo "Starting Backend Server..."
echo "========================================"
echo "Backend will run on: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py

