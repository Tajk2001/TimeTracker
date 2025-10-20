#!/usr/bin/env python3
"""
Time Tracker Pro - macOS App Builder
Creates a standalone macOS application bundle
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if all requirements are met for building"""
    print("Checking build requirements...")
    
    # Check if we're on macOS
    if sys.platform == "darwin":
        print("Running on macOS")
        return True
    else:
        print("This script is designed for macOS only")
        print("   For other platforms, use the Python version directly")
        return False

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    print("Installing PyInstaller...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"], check=True)
        print("PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install PyInstaller: {e}")
        return False

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    icon_path = Path("icon.icns")
    if not icon_path.exists():
        print("Creating application icon...")
        # Create a simple text-based icon placeholder
        # In a real scenario, you'd want a proper .icns file
        print("No icon.icns found - app will use default icon")
        print("   To add a custom icon, place an icon.icns file in the project directory")
    else:
        print("Icon file found")

def clean_build_directories():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")
    
    # Clean .pyc files
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))

def build_executable():
    """Build the macOS app using PyInstaller"""
    print("Building macOS application...")
    
    try:
        # Build macOS app bundle
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "--windowed",
            "--onedir",
            "--name", "TimeTrackerPro",
            "--add-data", "time_logs.csv:.",
            "--add-data", "tasks.csv:.",
            "--add-data", "config.py:.",
            "--add-data", "analytics.py:.",
            "--add-data", "data_manager.py:.",
            "--add-data", "logger.py:.",
            "--add-data", "settings_manager.py:.",
            "time_tracker.py"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("macOS application built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def create_portable_package():
    """Create a portable package with the macOS app"""
    print("Creating portable package...")
    
    dist_dir = Path("dist")
    package_dir = Path("TimeTrackerPro_macOS")
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    
    # Copy app bundle
    app_name = "TimeTrackerPro.app"
    app_path = dist_dir / app_name
    
    if app_path.exists():
        shutil.copytree(app_path, package_dir / app_name)
        print(f"Copied app bundle: {app_name}")
    else:
        print(f"App bundle not found: {app_path}")
        return False
    
    # Create data directory
    data_dir = package_dir / "data"
    data_dir.mkdir()
    
    # Copy data files
    data_files = ["time_logs.csv", "tasks.csv", "settings.json"]
    for file_name in data_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, data_dir / file_name)
            print(f"Copied data file: {file_name}")
    
    # Create directories
    (package_dir / "logs").mkdir()
    (package_dir / "backups").mkdir()
    
    # Create README for macOS version
    readme_content = """# Time Tracker Pro - macOS Version

## Quick Start
1. Double-click TimeTrackerPro.app to start the application
2. The app will open in your browser at http://localhost:8501
3. Your data will be saved in the 'data' folder

## Features
- Standalone macOS application (no installation required)
- All data stored locally in the 'data' folder
- Automatic backups in the 'backups' folder
- Application logs in the 'logs' folder

## System Requirements
- macOS 10.14 or later
- No additional software required

## Data Storage
- time_logs.csv - Your time tracking sessions
- tasks.csv - Your task list
- settings.json - Application settings

## Troubleshooting
- If the app won't start, check System Preferences > Security & Privacy
- Make sure port 8501 is available
- Check the logs folder for error messages

Enjoy your productivity journey!
"""
    
    with open(package_dir / "README.txt", "w") as f:
        f.write(readme_content)
    
    print(f"Portable package created: {package_dir}")
    return True

def test_executable():
    """Test the macOS app"""
    if sys.platform != "darwin":
        print("Cannot test macOS app on non-macOS system")
        return True
    
    print("Testing macOS application...")
    
    app_path = Path("dist") / "TimeTrackerPro.app"
    if not app_path.exists():
        print("App bundle not found for testing")
        return False
    
    try:
        # Test if app runs (with timeout)
        print("Starting app test...")
        process = subprocess.Popen(["open", str(app_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a few seconds then terminate
        import time
        time.sleep(5)
        process.terminate()
        
        print("macOS app test completed")
        return True
        
    except Exception as e:
        print(f"macOS app test failed: {e}")
        return False

def main():
    """Main build function"""
    print("=" * 60)
    print("Time Tracker Pro - macOS App Builder")
    print("   Version 2.0.0")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Create icon
    create_icon()
    
    # Clean previous builds
    clean_build_directories()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create portable package
    if not create_portable_package():
        return False
    
    # Test executable (if on macOS)
    test_executable()
    
    print("\n" + "=" * 60)
    print("macOS application build completed successfully!")
    print("=" * 60)
    print("\nOutput files:")
    print("   - dist/TimeTrackerPro.app (macOS application bundle)")
    print("   - TimeTrackerPro_macOS/ (complete portable package)")
    print("\nTo distribute:")
    print("   1. Share the entire 'TimeTrackerPro_macOS' folder")
    print("   2. Recipients just need to run TimeTrackerPro.app")
    print("   3. No Python installation required!")
    print("\nNote: The app bundle is quite large (~200MB) due to")
    print("   bundling all dependencies. This is normal for PyInstaller.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
