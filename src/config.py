"""
Configuration settings for Time Tracker App
"""

import os
from pathlib import Path

# Application settings
APP_NAME = "Time Tracker Pro"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "A modern, minimalist time tracking application with Pomodoro timer"

# File paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR
LOGS_DIR = BASE_DIR / "logs"

# CSV file paths
TIME_LOGS_FILE = DATA_DIR / "time_logs.csv"
TASKS_FILE = DATA_DIR / "tasks.csv"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Default Pomodoro settings
DEFAULT_WORK_DURATION = 25  # minutes
DEFAULT_BREAK_DURATION = 5  # minutes
DEFAULT_LONG_BREAK_DURATION = 15  # minutes
DEFAULT_SESSIONS_BEFORE_LONG_BREAK = 4

# Timer settings
MIN_DURATION = 0.05  # minimum 3 seconds
MAX_DURATION = 60.0  # maximum 60 minutes

# UI settings
THEME_COLORS = {
    'primary': '#00ff88',
    'secondary': '#ff6b6b',
    'background': '#0a0a0a',
    'surface': '#1a1a1a',
    'text': '#ffffff',
    'text_secondary': '#cccccc'
}

# Sound settings
SOUND_ENABLED = True
SOUND_FILES = {
    'completion': '/System/Library/Sounds/Glass.aiff',
    'celebration': '/System/Library/Sounds/Frog.aiff',
    'startup': '/System/Library/Sounds/Ping.aiff'
}

# Data validation settings
MAX_TASK_NAME_LENGTH = 100
MAX_SESSION_DURATION = 480  # 8 hours in minutes
MIN_SESSION_DURATION = 0.01  # 0.6 seconds

# Export settings
EXPORT_FORMATS = ['csv', 'json', 'xlsx']
DEFAULT_EXPORT_FORMAT = 'csv'

# Create necessary directories
LOGS_DIR.mkdir(exist_ok=True)
