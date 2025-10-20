#!/usr/bin/env python3
"""
Time Tracker Pro Launcher
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading
from pathlib import Path

def main():
    print("Starting Time Tracker Pro...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if virtual environment exists
    venv_path = script_dir / "time_tracker_env"
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run setup.py first.")
        return
    
    # macOS paths
    python_path = venv_path / "bin" / "python"
    streamlit_path = venv_path / "bin" / "streamlit"
    
    if not python_path.exists():
        print("❌ Python executable not found in virtual environment")
        return
    
    print("The app will open in your browser at: http://localhost:8501")
    print("Your data is saved locally in CSV files")
    print("")
    print("Press Ctrl+C to stop the application")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Streamlit
    try:
        subprocess.run([str(streamlit_path), "run", "time_tracker.py", 
                       "--server.headless", "true", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\nTime Tracker Pro stopped.")

if __name__ == "__main__":
    main()
