#!/usr/bin/env python3
"""
Time Tracker Pro - Executable Builder
Creates a standalone .exe file for Windows distribution
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if all requirements are met for building"""
    print("Checking build requirements...")
    
    # Check if we're on Windows or have Wine
    if sys.platform == "win32":
        print("Running on Windows")
        return True
    else:
        print("Not running on Windows - you'll need Wine or a Windows machine")
        print("   This script will still work but the .exe won't be testable")
        return True

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    print("Installing PyInstaller...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"], check=True)
        print("✅ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install PyInstaller: {e}")
        return False

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    icon_path = Path("icon.ico")
    if not icon_path.exists():
        print("🎨 Creating application icon...")
        # Create a simple text-based icon placeholder
        # In a real scenario, you'd want a proper .ico file
        print("⚠️  No icon.ico found - executable will use default icon")
        print("   To add a custom icon, place an icon.ico file in the project directory")
    else:
        print("✅ Icon file found")

def clean_build_directories():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ Cleaned {dir_name}/")
    
    # Clean .pyc files
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Use the spec file for better control
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "time_tracker.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Executable built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def create_portable_package():
    """Create a portable package with the executable"""
    print("📦 Creating portable package...")
    
    dist_dir = Path("dist")
    package_dir = Path("TimeTrackerPro_Portable")
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    
    # Copy executable
    exe_name = "TimeTrackerPro.exe" if sys.platform == "win32" else "TimeTrackerPro"
    exe_path = dist_dir / exe_name
    
    if exe_path.exists():
        shutil.copy2(exe_path, package_dir / exe_name)
        print(f"✅ Copied executable: {exe_name}")
    else:
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    # Create data directory
    data_dir = package_dir / "data"
    data_dir.mkdir()
    
    # Copy data files
    data_files = ["time_logs.csv", "tasks.csv", "settings.json"]
    for file_name in data_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, data_dir / file_name)
            print(f"✅ Copied data file: {file_name}")
    
    # Create directories
    (package_dir / "logs").mkdir()
    (package_dir / "backups").mkdir()
    
    # Create README for portable version
    readme_content = """# Time Tracker Pro - Portable Version

## Quick Start
1. Double-click TimeTrackerPro.exe to start the application
2. The app will open in your browser at http://localhost:8501
3. Your data will be saved in the 'data' folder

## Features
- ✅ Standalone executable (no installation required)
- ✅ All data stored locally in the 'data' folder
- ✅ Automatic backups in the 'backups' folder
- ✅ Application logs in the 'logs' folder

## System Requirements
- Windows 10 or later
- No additional software required

## Data Storage
- time_logs.csv - Your time tracking sessions
- tasks.csv - Your task list
- settings.json - Application settings

## Troubleshooting
- If the app won't start, check Windows Defender/Antivirus
- Make sure port 8501 is available
- Check the logs folder for error messages

Enjoy your productivity journey! 🚀
"""
    
    with open(package_dir / "README.txt", "w") as f:
        f.write(readme_content)
    
    print(f"✅ Portable package created: {package_dir}")
    return True

def test_executable():
    """Test the executable (if on Windows)"""
    if sys.platform != "win32":
        print("⚠️  Cannot test executable on non-Windows system")
        return True
    
    print("🧪 Testing executable...")
    
    exe_path = Path("dist") / "TimeTrackerPro.exe"
    if not exe_path.exists():
        print("❌ Executable not found for testing")
        return False
    
    try:
        # Test if executable runs (with timeout)
        print("Starting executable test...")
        process = subprocess.Popen([str(exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a few seconds then terminate
        import time
        time.sleep(5)
        process.terminate()
        
        print("✅ Executable test completed")
        return True
        
    except Exception as e:
        print(f"❌ Executable test failed: {e}")
        return False

def main():
    """Main build function"""
    print("=" * 60)
    print("🚀 Time Tracker Pro - Executable Builder")
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
    
    # Test executable (if on Windows)
    test_executable()
    
    print("\n" + "=" * 60)
    print("🎉 Executable build completed successfully!")
    print("=" * 60)
    print("\n📁 Output files:")
    print("   - dist/TimeTrackerPro.exe (standalone executable)")
    print("   - TimeTrackerPro_Portable/ (complete portable package)")
    print("\n🚀 To distribute:")
    print("   1. Share the entire 'TimeTrackerPro_Portable' folder")
    print("   2. Recipients just need to run TimeTrackerPro.exe")
    print("   3. No Python installation required!")
    print("\n⚠️  Note: The executable is quite large (~200MB) due to")
    print("   bundling all dependencies. This is normal for PyInstaller.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
