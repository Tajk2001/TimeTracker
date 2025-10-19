# Time Tracker Pro Documentation

## Project Structure

```
TimeTrackerPro/
├── src/                    # Core application modules
│   ├── config.py          # Configuration settings
│   ├── logger.py          # Logging system
│   ├── data_manager.py    # Data management utilities
│   ├── analytics.py       # Analytics engine
│   └── settings_manager.py # Settings management
├── scripts/               # Build and setup scripts
│   ├── setup.py          # Installation script
│   ├── build_exe.py      # Executable builder
│   └── build_exe.bat      # Windows batch file
├── docs/                  # Documentation
│   └── README.md         # This file
├── time_tracker.py        # Main application
├── launch.py             # Application launcher
├── requirements.txt      # Python dependencies
├── time_tracker.spec     # PyInstaller spec
├── sample_time_logs.csv  # Sample data
├── sample_tasks.csv      # Sample tasks
└── .gitignore           # Git ignore rules
```

## Development Setup

1. Clone the repository
2. Run `python scripts/setup.py` to install dependencies
3. Run `python launch.py` to start the application

## Building Executables

1. Run `python scripts/build_exe.py` to create standalone executable
2. Or use `scripts/build_exe.bat` on Windows

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for personal and educational use.
