@echo off
echo ============================================================
echo Time Tracker Pro - Executable Builder
echo Version 2.0.0
echo ============================================================
echo.

echo Installing PyInstaller...
pip install pyinstaller>=6.0.0

echo.
echo Building executable...
python build_exe.py

echo.
echo Build process completed!
echo Check the 'dist' folder for your executable.
echo.
pause
