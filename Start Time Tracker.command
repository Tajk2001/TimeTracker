#!/bin/bash

# Time Tracker App Launcher
# Double-click this file to start the Time Tracker application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Time Tracker App..."
echo "📁 App directory: $SCRIPT_DIR"

# Kill any existing Streamlit processes
echo "🛑 Stopping any existing Time Tracker instances..."
pkill -f streamlit 2>/dev/null || true

# Check if virtual environment exists
if [ ! -d "time_tracker_env" ]; then
    echo "⚙️ Setting up virtual environment..."
    python3 -m venv time_tracker_env
    source time_tracker_env/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
    source time_tracker_env/bin/activate
fi

# Start the application
echo "🎯 Launching Time Tracker..."
echo "🌐 The app will open in your browser at: http://localhost:8501"
echo "📊 Your data is saved in: tasks.csv and time_logs.csv"
echo ""
echo "Press Ctrl+C to stop the application"

# Start Streamlit
streamlit run time_tracker.py --server.headless true --server.port 8501
