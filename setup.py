#!/usr/bin/env python3
"""
Time Tracker Pro - Installation and Setup Script
Version 2.0.0
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"Python version: {sys.version.split()[0]}")
    return True

def check_system_requirements():
    """Check system requirements"""
    print("Checking system requirements...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check OS
    system = platform.system()
    print(f"Operating System: {system}")
    
    if system != "Darwin":
        print("Warning: This application is optimized for macOS")
        print("   It may work on other systems but is not officially supported")
    
    # Check available disk space (basic check)
    try:
        statvfs = os.statvfs('.')
        free_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
        if free_space_gb < 1:
            print("Warning: Less than 1GB free disk space")
        else:
            print(f"Free disk space: {free_space_gb:.1f} GB")
    except:
        print("Could not check disk space")
    
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("Setting up virtual environment...")
    
    venv_path = Path("time_tracker_env")
    
    if venv_path.exists():
        print("Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to create virtual environment: {e}")
        return False

def get_pip_path():
    """Get the correct pip path for the virtual environment"""
    venv_path = Path("time_tracker_env")
    
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    pip_path = get_pip_path()
    
    if not pip_path.exists():
        print("Virtual environment not found")
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = ["logs", "backups"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def verify_installation():
    """Verify the installation"""
    print("🔍 Verifying installation...")
    
    try:
        # Test imports
        pip_path = get_pip_path()
        python_path = pip_path.parent / "python"
        
        if platform.system() == "Windows":
            python_path = pip_path.parent / "python.exe"
        
        # Test import of main modules
        test_script = """
import streamlit as st
import pandas as pd
import plotly.express as px
print("All modules imported successfully")
"""
        
        result = subprocess.run([str(python_path), "-c", test_script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Installation verification passed")
            return True
        else:
            print(f"Installation verification failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Installation verification error: {e}")
        return False

def create_launcher_scripts():
    """Create launcher scripts for different platforms"""
    print("Creating launcher scripts...")
    
    # Create Python launcher
    launcher_content = '''#!/usr/bin/env python3
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
        print("Virtual environment not found. Please run setup.py first.")
        return
    
    # Get correct paths
    if sys.platform == "darwin" or sys.platform.startswith("linux"):
        python_path = venv_path / "bin" / "python"
        streamlit_path = venv_path / "bin" / "streamlit"
    else:  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
        streamlit_path = venv_path / "Scripts" / "streamlit.exe"
    
    if not python_path.exists():
        print("Python executable not found in virtual environment")
        return
    
    print("🌐 The app will open in your browser at: http://localhost:8501")
    print("📊 Your data is saved locally in CSV files")
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
        print("\\n🛑 Time Tracker Pro stopped.")

if __name__ == "__main__":
    main()
'''
    
    with open("launch.py", "w") as f:
        f.write(launcher_content)
    
    # Make executable on Unix systems
    if platform.system() != "Windows":
        os.chmod("launch.py", 0o755)
    
    print("Launcher script created: launch.py")

def main():
    """Main installation function"""
    print("=" * 60)
    print("Time Tracker Pro - Installation Script")
    print("   Version 2.0.0")
    print("=" * 60)
    
    # Check system requirements
    if not check_system_requirements():
        print("\nSystem requirements not met. Please fix the issues above.")
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        print("\nFailed to create virtual environment.")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\nFailed to install dependencies.")
        return False
    
    # Create directories
    create_directories()
    
    # Create launcher scripts
    create_launcher_scripts()
    
    # Verify installation
    if not verify_installation():
        print("\nInstallation verification failed.")
        return False
    
    print("\n" + "=" * 60)
    print("Installation completed successfully!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Run the application: python launch.py")
    print("2. Or double-click 'Start Time Tracker.command' (macOS)")
    print("3. The app will open in your browser at http://localhost:8501")
    print("\nYour data will be saved in:")
    print("   - time_logs.csv (time tracking sessions)")
    print("   - tasks.csv (task list)")
    print("   - settings.json (application settings)")
    print("   - logs/ (application logs)")
    print("   - backups/ (automatic backups)")
    print("\nTo uninstall: Delete the entire folder")
    print("\nEnjoy your productivity journey!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
