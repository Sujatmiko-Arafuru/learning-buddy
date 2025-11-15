#!/bin/bash

echo "========================================"
echo "Learning Buddy - Quick Start Script"
echo "========================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "[1/2] Starting Backend Server..."
cd "$PROJECT_ROOT/backend"
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python app.py &
BACKEND_PID=$!
cd "$PROJECT_ROOT"

sleep 3

echo "[2/2] Starting Frontend Server..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

echo ""
echo "========================================"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:5173 (Vite default port)"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait

