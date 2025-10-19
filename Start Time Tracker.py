#!/usr/bin/env python3
"""
Time Tracker App Launcher
Double-click this file to start the Time Tracker application
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading

def main():
    print("🚀 Starting Time Tracker App...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 App directory: {script_dir}")
    
    # Check if virtual environment exists
    venv_path = os.path.join(script_dir, "time_tracker_env")
    if not os.path.exists(venv_path):
        print("⚙️ Setting up virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_path])
    
    # Activate virtual environment and install dependencies
    if sys.platform == "darwin":  # macOS
        pip_path = os.path.join(venv_path, "bin", "pip")
        streamlit_path = os.path.join(venv_path, "bin", "streamlit")
    else:  # Windows
        pip_path = os.path.join(venv_path, "Scripts", "pip")
        streamlit_path = os.path.join(venv_path, "Scripts", "streamlit")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    
    # Start Streamlit
    print("🎯 Launching Time Tracker...")
    print("🌐 The app will open in your browser at: http://localhost:8501")
    print("📊 Your data is saved in: tasks.csv and time_logs.csv")
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
        subprocess.run([streamlit_path, "run", "time_tracker.py", "--server.headless", "true", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\n🛑 Time Tracker stopped.")

if __name__ == "__main__":
    main()
