# Time Tracker Pro

A comprehensive, modern time tracking application with Pomodoro timer, advanced analytics, and data management features.

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
python scripts/setup.py
python launch.py
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv time_tracker_env

# Activate virtual environment
# On macOS/Linux:
source time_tracker_env/bin/activate
# On Windows:
time_tracker_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run time_tracker.py
```

### Option 3: macOS Double-Click
**Double-click `Start Time Tracker.command` to launch the app!**

## Project Structure

```
TimeTrackerPro/
├── src/                    # Core application modules
│   ├── config.py          # Configuration settings
│   ├── logger.py          # Logging system
│   ├── data_manager.py    # Data management utilities
│   ├── analytics.py       # Advanced analytics engine
│   └── settings_manager.py # Settings management
├── scripts/               # Build and setup scripts
│   ├── setup.py          # Installation script
│   ├── build_exe.py      # Executable builder
│   └── build_exe.bat      # Windows batch file
├── docs/                  # Documentation
│   └── README.md         # Development docs
├── time_tracker.py        # Main application
├── launch.py             # Application launcher
├── requirements.txt      # Python dependencies
├── time_tracker.spec     # PyInstaller spec
├── sample_time_logs.csv  # Sample data
├── sample_tasks.csv      # Sample tasks
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Features

### Time Tracking
- **Task-based tracking** - Add tasks and track time spent
- **Real-time display** - Live elapsed time counter
- **Session management** - Start/stop tracking with one click
- **Data validation** - Robust error handling and data integrity

### Pomodoro Timer
- **Customizable durations** - Work, break, and long break times
- **Session tracking** - Automatic session counting
- **Sound notifications** - Audio alerts for completions
- **Visual celebrations** - Balloons and success messages

### Advanced Analytics
- **Productivity metrics** - Total time, sessions, consistency scores
- **Interactive charts** - Time trends, task distribution, heatmaps
- **Performance analysis** - Task efficiency and session patterns
- **Weekly summaries** - Comprehensive time breakdowns

### Data Management
- **Export/Import** - CSV, JSON, Excel formats
- **Automatic backups** - Scheduled data protection
- **Data validation** - Integrity checks and error detection
- **Backup cleanup** - Automatic old file management

### Settings & Configuration
- **Comprehensive settings** - Pomodoro, UI, data, notifications
- **Persistent storage** - Settings saved between sessions
- **Reset functionality** - Restore defaults when needed
- **Validation** - Settings validation and error handling

### User Interface
- **Dark theme** - Modern, minimalist design
- **Responsive layout** - Works on different screen sizes
- **Intuitive navigation** - Tab-based interface
- **Real-time updates** - Live timer and data refresh

## Sound Features

- **Work Complete**: 3 beeps + celebration sound
- **Break Complete**: Startup sound
- **Background Detection**: Sounds work even when app is not in focus
- **Customizable**: Enable/disable in settings

## Data Storage

Your time tracking data is automatically saved locally:

- **`time_logs.csv`** - Detailed time tracking sessions
- **`tasks.csv`** - Task list and total times  
- **`settings.json`** - Application settings
- **`logs/`** - Application logs (rotated daily)
- **`backups/`** - Automatic backups (configurable frequency)

## Technical Details

- **Python**: 3.8+ required
- **Framework**: Streamlit 1.28+
- **Dependencies**: pandas, plotly, numpy
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Storage**: Local CSV files (no cloud dependency)
- **Security**: All data stays on your device

## Troubleshooting

### Installation Issues
1. **Python not found**: Install Python 3.8+ from [python.org](https://python.org)
2. **Permission errors**: Run as administrator (Windows) or use `sudo` (macOS/Linux)
3. **Virtual environment issues**: Delete `time_tracker_env` folder and run `setup.py` again

### Runtime Issues
1. **App won't start**: Check the terminal output for error messages
2. **Port conflicts**: The app uses port 8501, make sure it's available
3. **Data corruption**: Use the Data Management tab to validate and fix data
4. **Sound issues**: Check system sound settings and app permissions

### Data Issues
1. **Missing data**: Check if CSV files exist and have proper permissions
2. **Corrupted files**: Use the backup/restore feature in Data Management
3. **Import errors**: Ensure CSV files match the expected format

## Usage Tips

### Getting Started
1. **Add tasks** in the sidebar
2. **Start tracking** by clicking "Start" next to a task
3. **Use Pomodoro timer** for focused work sessions
4. **Check analytics** to see your productivity patterns

### Best Practices
1. **Regular backups** - Enable automatic backups in settings
2. **Task organization** - Use descriptive task names
3. **Consistent tracking** - Track time regularly for better insights
4. **Review analytics** - Check your productivity patterns weekly

### Advanced Features
1. **Data export** - Export your data for external analysis
2. **Custom settings** - Adjust timer durations to your preferences
3. **Backup management** - Clean up old backups periodically
4. **Data validation** - Run integrity checks regularly

## Creating Executable (.exe) Files

### Quick Build (Windows)
```bash
# Double-click the batch file
scripts/build_exe.bat

# Or run manually
python scripts/build_exe.py
```

### Manual Build Process
```bash
# Install PyInstaller
pip install pyinstaller>=6.0.0

# Build executable
pyinstaller --clean --noconfirm time_tracker.spec
```

### Output Files
- **`dist/TimeTrackerPro.exe`** - Standalone executable (~200MB)
- **`TimeTrackerPro_Portable/`** - Complete portable package
- **No Python installation required** for end users!

### Distribution
1. Share the entire `TimeTrackerPro_Portable` folder
2. Recipients just run `TimeTrackerPro.exe`
3. All data stored locally in the `data` folder

## Updates & Maintenance

### Updating the Application
1. Download the latest version
2. Run `setup.py` to update dependencies
3. Your data will be preserved

### Data Maintenance
- **Automatic**: Logs rotate daily, backups created weekly
- **Manual**: Use Data Management tab for manual operations
- **Cleanup**: Old backups and logs are cleaned automatically

## License

This application is provided as-is for personal use. Feel free to modify and distribute according to your needs.

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review the application logs in the `logs/` directory
3. Use the Data Management tab to diagnose data issues

## Enjoy Your Productivity Journey!

Time Tracker Pro is designed to help you understand and improve your productivity patterns. Start tracking, stay focused, and achieve your goals!
