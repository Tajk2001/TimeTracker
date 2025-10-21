# Time Tracker Pro

A modern time tracking application with a Pomodoro timer, analytics, and local data management.

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
python setup.py
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
.
├── analytics.py           # Analytics engine
├── build_exe.py          # Executable builder (optional)
├── config.py             # Configuration settings
├── data_manager.py       # Data management utilities
├── docs/                 # Documentation
├── launch.py             # Application launcher
├── logger.py             # Logging setup and helpers
├── requirements.txt      # Python dependencies
├── scripts/              # Additional scripts (optional)
├── settings_manager.py   # Settings management
├── Start Time Tracker.command # macOS launcher (optional)
├── Start Time Tracker.py # Convenience launcher
├── time_tracker.py       # Main Streamlit app
└── README.md             # This file
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

### Analytics
- Task and session summaries
- Time trends and task distribution
- Weekly breakdowns

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
- Dark theme and responsive layout
- Tab-based navigation
- Live timer and data refresh

## Sound Notifications

- Work complete: chime sequence
- Break complete: startup sound
- Configurable in Settings

## Data Storage

Your time tracking data is automatically saved locally:

- **`time_logs.csv`** - Detailed time tracking sessions
- **`tasks.csv`** - Task list and total times  
- **`settings.json`** - Application settings
- **`logs/`** - Application logs (rotated daily)
- **`backups/`** - Automatic backups (configurable frequency)

## Technical Details

- Python 3.8+
- Streamlit 1.28+
- Dependencies: pandas, plotly, numpy
- Local CSV storage (no cloud dependency)

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

## Building an Executable (Windows)

### Quick Build (Windows)
```bash
# Run builder script
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
Share the `TimeTrackerPro_Portable` folder; recipients run `TimeTrackerPro.exe`.

## Updates & Maintenance

### Updating the Application
Run `setup.py` to update dependencies. Your data is preserved.

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
