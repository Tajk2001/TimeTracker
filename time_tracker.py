"""
Time Tracker Pro - A comprehensive time tracking application
Version 2.0.0
"""

import streamlit as st
import pandas as pd
import datetime
import time
import threading
import csv
import os
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import fcntl  # For file locking on Unix systems
import tempfile
import shutil
import json
import sys
from pathlib import Path

# Import our custom modules
try:
    from config import *
    from logger import setup_logging, log_app_start, log_app_stop, log_user_action, log_error, log_timer_event
    from data_manager import DataManager
    from analytics import AnalyticsEngine
    from settings_manager import SettingsManager
except ImportError as e:
    st.error(f"Failed to import modules: {e}")
    st.stop()

class TimeTracker:
    def __init__(self):
        self.csv_file = "time_logs.csv"
        self.tasks_file = "tasks.csv"
        self.schedule_file = "schedule_blocks.csv"
        self._data_cache = None  # Cache for data to avoid repeated file reads
        self.initialize_files()
        self.cleanup_corrupted_data()
        
    def _safe_file_operation(self, file_path: str, operation: str, data=None):
        """Perform safe file operations with locking and error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if operation == 'read':
                    return pd.read_csv(file_path)
                elif operation == 'write' and data is not None:
                    # Use atomic write with temporary file
                    temp_file = file_path + '.tmp'
                    print(f"Writing {len(data)} rows to temporary file: {temp_file}")
                    data.to_csv(temp_file, index=False)
                    print(f"Moving temporary file to final location: {file_path}")
                    shutil.move(temp_file, file_path)
                    print(f"Successfully wrote {len(data)} rows to {file_path}")
                    return True
                elif operation == 'append' and data is not None:
                    # Safe append operation
                    with open(file_path, 'a', newline='') as f:
                        if os.name != 'nt':  # Unix-like systems
                            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                        writer = csv.writer(f)
                        writer.writerow(data)
                    return True
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {operation} on {file_path}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.1)  # Brief delay before retry
        return None
    
    def cleanup_corrupted_data(self):
        """Clean up corrupted CSV data"""
        try:
            # Fix time_logs.csv
            if os.path.exists(self.csv_file):
                with open(self.csv_file, 'r') as f:
                    lines = f.readlines()
                
                cleaned_lines = []
                expected_header = ['task', 'start_time', 'end_time', 'duration_minutes', 'date', 'session_type']
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(',')
                    
                    if i == 0:  # Header
                        cleaned_lines.append(','.join(expected_header))
                    else:  # Data rows
                        if len(parts) >= 6:
                            # Take only the first 6 columns, ignore extra empty columns
                            clean_parts = parts[:6]
                            # Validate data format
                            if self._validate_log_entry(clean_parts):
                                cleaned_lines.append(','.join(clean_parts))
                            else:
                                print(f"Skipping invalid entry: {clean_parts}")
                
                # Write cleaned data back
                with open(self.csv_file, 'w', newline='') as f:
                    for line in cleaned_lines:
                        f.write(line + '\n')
                
                print(f"✅ Cleaned {self.csv_file} - removed corrupted entries")
                
        except Exception as e:
            print(f"Error cleaning corrupted data: {e}")
    
    def _validate_log_entry(self, parts) -> bool:
        """Validate a log entry before writing"""
        if len(parts) != 6:
            return False
        
        task, start_time, end_time, duration, date, session_type = parts
        
        # Convert all parts to strings for validation
        task = str(task) if task is not None else ""
        start_time = str(start_time) if start_time is not None else ""
        end_time = str(end_time) if end_time is not None else ""
        duration = str(duration) if duration is not None else ""
        date = str(date) if date is not None else ""
        session_type = str(session_type) if session_type is not None else ""
        
        # Check required fields are not empty
        if not all([task.strip(), start_time.strip(), end_time.strip(), duration.strip(), date.strip()]):
            return False
        
        try:
            # Validate datetime formats
            datetime.datetime.strptime(start_time.strip(), '%Y-%m-%d %H:%M:%S')
            datetime.datetime.strptime(end_time.strip(), '%Y-%m-%d %H:%M:%S')
            datetime.datetime.strptime(date.strip(), '%Y-%m-%d')
            
            # Validate duration is a number
            float(duration.strip())
            
            return True
        except (ValueError, TypeError):
            return False
        
    def initialize_files(self):
        """Initialize CSV files if they don't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['task', 'start_time', 'end_time', 'duration_minutes', 'date', 'session_type'])
        
        if not os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['task_name', 'status', 'created_date', 'total_time_minutes'])
        
        if not os.path.exists(self.schedule_file):
            with open(self.schedule_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'start_time', 'end_time', 'task_name', 'block_type', 'notes', 'completed'])
    
    def add_task(self, task_name: str):
        """Add a new task to the tasks CSV"""
        try:
            if not task_name or not task_name.strip():
                raise ValueError("Task name cannot be empty")
            
            # Check if task already exists
            existing_tasks = self.get_tasks()
            if any(task['task_name'] == task_name for task in existing_tasks):
                raise ValueError(f"Task '{task_name}' already exists")
            
            task_data = [
                task_name.strip(),
                'active',
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                0
            ]
            
            self._safe_file_operation(self.tasks_file, 'append', task_data)
            print(f"Successfully added task: {task_name}")
        except Exception as e:
            print(f"Error adding task {task_name}: {e}")
            raise
    
    def get_tasks(self) -> List[Dict]:
        """Get all tasks from CSV"""
        try:
            df = self._safe_file_operation(self.tasks_file, 'read')
            if df is not None:
                return df.to_dict("records")
            return []
        except Exception as e:
            print(f"Error reading tasks: {e}")
            return []
    
    def log_time(self, task: str, start_time: datetime.datetime, end_time: datetime.datetime, session_type: str = "work"):
        """Log time entry to CSV with validation"""
        try:
            # Validate inputs
            if not task or not task.strip():
                raise ValueError("Task name cannot be empty")
            
            if start_time >= end_time:
                raise ValueError("Start time must be before end time")
            
            duration = (end_time - start_time).total_seconds() / 60
            if duration <= 0:
                raise ValueError("Duration must be positive")
            
            # Prepare log entry
            log_entry = [
                task.strip(),
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S'),
                round(duration, 2),
                start_time.strftime('%Y-%m-%d'),
                session_type or "work"
            ]
            
            # Validate the entry before writing
            if not self._validate_log_entry(log_entry):
                raise ValueError("Invalid log entry format")
            
            # Write to file safely
            self._safe_file_operation(self.csv_file, 'append', log_entry)
        
        # Update task total time
            self.update_task_total_time(task, duration)
            
        except Exception as e:
            print(f"Error logging time for task {task}: {e}")
            raise
    
    def delete_task(self, task_name: str):
        """Delete a task from the tasks CSV"""
        try:
            df = self._safe_file_operation(self.tasks_file, 'read')
            if df is not None:
                original_count = len(df)
            df = df[df['task_name'] != task_name]
            if len(df) < original_count:
                self._safe_file_operation(self.tasks_file, 'write', df)
                print(f"Successfully deleted task: {task_name}")
            else:
                print(f"Task not found: {task_name}")
        except Exception as e:
            print(f"Error deleting task {task_name}: {e}")
    
    def update_task_total_time(self, task_name: str, duration: float):
        """Update total time for a task with proper error handling"""
        try:
            df = self._safe_file_operation(self.tasks_file, 'read')
            if df is not None:
                mask = df["task_name"] == task_name
                if mask.any():
                    # Convert to float to avoid dtype warnings
                    df["total_time_minutes"] = pd.to_numeric(df["total_time_minutes"], errors="coerce").fillna(0)
                    df.loc[mask, "total_time_minutes"] += duration
                    self._safe_file_operation(self.tasks_file, "write", df)
                    print(f"Updated total time for {task_name}: +{duration:.2f} minutes")
                else:
                    print(f"Warning: Task '{task_name}' not found in tasks file")
        except Exception as e:
            print(f"Error updating total time for task {task_name}: {e}")
    
def update_all_task_totals(self):
        """Recalculate all task totals based on current time logs"""
        try:
            # Get all time logs
            logs_df = self.get_time_logs()
            if logs_df.empty:
                return
            
            # Calculate total time per task
            task_totals = logs_df.groupby('task')['duration_minutes'].sum().reset_index()
            task_totals.columns = ['task', 'total_time_minutes']
            
            # Get existing tasks
            tasks_df = self._safe_file_operation(self.tasks_file, 'read')
            if tasks_df is None:
                tasks_df = pd.DataFrame(columns=['task_name', 'total_time_minutes'])
            
            # Update or add task totals
            for _, row in task_totals.iterrows():
                task_name = row['task']
                total_time = row['total_time_minutes']
                
                # Check if task exists
                mask = tasks_df['task_name'] == task_name
                if mask.any():
                    # Update existing task
                    tasks_df.loc[mask, 'total_time_minutes'] = total_time
                else:
                    # Add new task
                    new_task = pd.DataFrame({
                        'task_name': [task_name],
                        'total_time_minutes': [total_time]
                    })
                    tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
            
            # Save updated tasks
            self._safe_file_operation(self.tasks_file, 'write', tasks_df)
            print("Updated all task totals based on current time logs")
            
        except Exception as e:
            print(f"Error updating all task totals: {e}")
    
    def get_time_logs(self, force_reload=False) -> pd.DataFrame:
        """Get all time logs with error handling and caching"""
        try:
            # Force reload if requested or cache is None
            if force_reload or self._data_cache is None:
                print(f"Loading fresh data from {self.csv_file}")
                df = self._safe_file_operation(self.csv_file, 'read')
                if df is not None:
                    # Clean any remaining data issues
                    expected_columns = ['task', 'start_time', 'end_time', 'duration_minutes', 'date', 'session_type']
                    if list(df.columns) == expected_columns:
                        self._data_cache = df  # Cache the data
                        print(f"Loaded and cached {len(df)} rows")
                        return df
                    else:
                        print("Warning: CSV columns don't match expected format, attempting to fix...")
                        # Try to fix column issues
                        df = df.iloc[:, :6]  # Take only first 6 columns
                        df.columns = expected_columns
                        self._data_cache = df  # Cache the data
                        print(f"Fixed columns and cached {len(df)} rows")
                        return df
                df = pd.DataFrame(columns=['task', 'start_time', 'end_time', 'duration_minutes', 'date', 'session_type'])
                self._data_cache = df  # Cache the data
                print("Created empty dataframe and cached")
                return df
            else:
                print(f"Using cached data: {len(self._data_cache)} rows")
                return self._data_cache
                
        except Exception as e:
            print(f"Error reading time logs: {e}")
            df = pd.DataFrame(columns=['task', 'start_time', 'end_time', 'duration_minutes', 'date', 'session_type'])
            self._data_cache = df  # Cache the data
            return df
    
    # Schedule Management Methods
    def add_schedule_block(self, date: str, start_time: str, end_time: str, task_name: str, 
                          block_type: str = "work", notes: str = ""):
        """Add a new schedule block"""
        try:
            # Validate inputs
            if not all([date, start_time, end_time, task_name]):
                raise ValueError("All fields are required")
            
            # Validate time format
            datetime.datetime.strptime(start_time, '%H:%M')
            datetime.datetime.strptime(end_time, '%H:%M')
            datetime.datetime.strptime(date, '%Y-%m-%d')
            
            # Check for time conflicts
            if self._has_time_conflict(date, start_time, end_time):
                raise ValueError("Time conflict with existing schedule block")
            
            block_data = [
                date,
                start_time,
                end_time,
                task_name.strip(),
                block_type,
                notes.strip(),
                False  # completed
            ]
            
            self._safe_file_operation(self.schedule_file, 'append', block_data)
            print(f"Successfully added schedule block: {task_name} at {start_time}-{end_time}")
        except Exception as e:
            print(f"Error adding schedule block: {e}")
            raise
    
    def get_schedule_blocks(self, date: str = None) -> List[Dict]:
        """Get schedule blocks for a specific date or all dates"""
        try:
            df = self._safe_file_operation(self.schedule_file, 'read')
            if df is not None and not df.empty:
                if date:
                    df = df[df['date'] == date]
                return df.to_dict("records")
            return []
        except Exception as e:
            print(f"Error reading schedule blocks: {e}")
            return []
    
    def update_schedule_block(self, date: str, start_time: str, task_name: str, 
                             completed: bool = None, notes: str = None):
        """Update a schedule block"""
        try:
            df = self._safe_file_operation(self.schedule_file, 'read')
            if df is not None:
                # Find the block to update
                mask = (df['date'] == date) & (df['start_time'] == start_time) & (df['task_name'] == task_name)
                if mask.any():
                    if completed is not None:
                        df.loc[mask, 'completed'] = completed
                    if notes is not None:
                        df.loc[mask, 'notes'] = notes
                    
                    self._safe_file_operation(self.schedule_file, 'write', df)
                    return True
            return False
        except Exception as e:
            print(f"Error updating schedule block: {e}")
            return False
    
    def delete_schedule_block(self, date: str, start_time: str, task_name: str):
        """Delete a schedule block"""
        try:
            df = self._safe_file_operation(self.schedule_file, 'read')
            if df is not None:
                original_count = len(df)
                df = df[~((df['date'] == date) & (df['start_time'] == start_time) & (df['task_name'] == task_name))]
                if len(df) < original_count:
                    self._safe_file_operation(self.schedule_file, 'write', df)
                    return True
            return False
        except Exception as e:
            print(f"Error deleting schedule block: {e}")
            return False
    
    def _has_time_conflict(self, date: str, start_time: str, end_time: str) -> bool:
        """Check if there's a time conflict with existing schedule blocks"""
        try:
            blocks = self.get_schedule_blocks(date)
            start_dt = datetime.datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
            end_dt = datetime.datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')
            
            for block in blocks:
                block_start = datetime.datetime.strptime(f"{date} {block['start_time']}", '%Y-%m-%d %H:%M')
                block_end = datetime.datetime.strptime(f"{date} {block['end_time']}", '%Y-%m-%d %H:%M')
                
                # Check for overlap
                if (start_dt < block_end and end_dt > block_start):
                    return True
            return False
        except Exception as e:
            print(f"Error checking time conflict: {e}")
            return False
    
    def get_task_statistics(self) -> Dict:
        """Get comprehensive task statistics with error handling"""
        try:
        logs_df = self.get_time_logs()
        
        if logs_df.empty:
                return {
                    'total_time': 0,
                    'total_sessions': 0,
                    'unique_tasks': 0,
                    'today_time': 0,
                    'today_sessions': 0,
                    'week_time': 0,
                    'week_sessions': 0,
                    'task_breakdown': {}
                }
        
        stats = {}
            
            # Convert duration to numeric, handle any non-numeric values
            logs_df['duration_minutes'] = pd.to_numeric(logs_df['duration_minutes'], errors='coerce').fillna(0)
        
        # Overall statistics
            stats["total_time"] = logs_df["duration_minutes"].sum()
            stats["total_sessions"] = len(logs_df)
            stats["unique_tasks"] = logs_df["task"].nunique()
        
        # Today's statistics
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        today_logs = logs_df[logs_df['date'] == today]
        stats['today_time'] = today_logs['duration_minutes'].sum()
        stats['today_sessions'] = len(today_logs)
        
        # This week's statistics
        week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        week_logs = logs_df[logs_df['date'] >= week_ago]
        stats['week_time'] = week_logs['duration_minutes'].sum()
        stats['week_sessions'] = len(week_logs)
        
            # Task breakdown
            if not logs_df.empty:
        task_stats = logs_df.groupby('task').agg({
            'duration_minutes': ['sum', 'count', 'mean'],
            'date': 'nunique'
        }).round(2)
        
        task_stats.columns = ['total_time', 'sessions', 'avg_session', 'days_worked']
        stats['task_breakdown'] = task_stats.to_dict('index')
            else:
                stats['task_breakdown'] = {}
        
        return stats
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {
                'total_time': 0,
                'total_sessions': 0,
                'unique_tasks': 0,
                'today_time': 0,
                'today_sessions': 0,
                'week_time': 0,
                'week_sessions': 0,
                'task_breakdown': {}
            }

def play_sound(sound_type):
    """Play different sounds based on type"""
    print(f"Playing sound: {sound_type}")  # Debug output
    try:
        import os
        if sound_type == "completion":
            # Play 3 beeps for completion
            for _ in range(3):
                os.system('afplay /System/Library/Sounds/Glass.aiff')
                time.sleep(0.3)
        elif sound_type == "celebration":
            # Play celebration sound
            os.system('afplay /System/Library/Sounds/Frog.aiff')
        elif sound_type == "startup":
            # Play startup sound
            os.system('afplay /System/Library/Sounds/Ping.aiff')
        print(f"Sound {sound_type} played successfully")
    except Exception as e:
        print(f"Error playing sound {sound_type}: {e}")

def check_timer_completion():
    """Check if any timer has completed and play sound notification"""
    print("Checking timer completion...")  # Debug output
    
    # Check Pomodoro timer completion
    if st.session_state.pomodoro.is_running:
        st.session_state.pomodoro.update_timer()
        print(f"Timer running, remaining: {st.session_state.pomodoro.remaining_time:.1f}s")  # Debug output
        
        if st.session_state.pomodoro.remaining_time <= 0 and not st.session_state.pomodoro.just_completed:
            print("Timer completed! Playing sounds...")  # Debug output
            st.session_state.pomodoro.complete_session()
            # Play sound notification
            if st.session_state.pomodoro.is_break:
                print("Playing startup sound (break complete)")  # Debug output
                play_sound("startup")  # Break complete - time to work
            else:
                print("Playing completion sounds (work complete)")  # Debug output
                play_sound("completion")  # Work complete
                play_sound("celebration")  # Celebration
    else:
        print("Timer not running")  # Debug output

class PomodoroTimer:
    def __init__(self):
        self.work_duration = 20  # minutes (6 seconds for testing)
        self.break_duration = 5  # minutes (6 seconds for testing)
        self.long_break_duration = 10  # minutes (12 seconds for testing)
        self.is_running = False
        self.is_break = False
        self.session_count = 0
        self.start_time = None
        self.remaining_time = self.work_duration * 60  # seconds
        self.current_session_start = None
        self.just_completed = False  # Flag for completion notification
        
    def start_timer(self):
        """Start the Pomodoro timer"""
        self.is_running = True
        self.start_time = time.time()
        self.current_session_start = datetime.datetime.now()
        
    def stop_timer(self):
        """Stop the Pomodoro timer"""
        self.is_running = False
        
    def reset_timer(self):
        """Reset the Pomodoro timer"""
        self.is_running = False
        self.is_break = False
        self.session_count = 0
        self.remaining_time = self.work_duration * 60
        self.current_session_start = None
        
    def update_timer(self):
        """Update timer state"""
        if self.is_running and self.start_time:
            elapsed = time.time() - self.start_time
            current_duration = self.break_duration if self.is_break else self.work_duration
            if self.is_break and self.session_count >= 4:
                current_duration = self.long_break_duration
                
            self.remaining_time = max(0, current_duration * 60 - elapsed)
            # Don't auto-complete here - let check_timer_completion handle it
    
    def complete_session(self):
        """Complete current session and switch to break/work"""
        self.is_running = False
        self.just_completed = True  # Set completion flag
        
        if not self.is_break:
            # Work session completed
            self.session_count += 1
            self.is_break = True
            self.remaining_time = self.break_duration * 60
            if self.session_count >= 4:
                self.remaining_time = self.long_break_duration * 60
                self.session_count = 0  # Reset after long break
        else:
            # Break completed
            self.is_break = False
            self.remaining_time = self.work_duration * 60

def format_time(seconds):
    """Format seconds as MM:SS"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def main():
    # Setup logging
    logger = setup_logging()
    log_app_start()
    
    try:
    st.set_page_config(
            page_title=APP_NAME,
            page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded"
    )
        
        # Initialize managers
        data_manager = DataManager()
        settings_manager = SettingsManager()
        
        # Initialize session state
        if 'tracker' not in st.session_state:
            st.session_state.tracker = TimeTracker()
        if 'pomodoro' not in st.session_state:
            st.session_state.pomodoro = PomodoroTimer()
        if 'current_task' not in st.session_state:
            st.session_state.current_task = None
        if 'timer_start' not in st.session_state:
            st.session_state.timer_start = None
        if 'is_tracking' not in st.session_state:
            st.session_state.is_tracking = False
        if 'task_added' not in st.session_state:
            st.session_state.task_added = False
        if 'settings_saved' not in st.session_state:
            st.session_state.settings_saved = False
        if 'data_manager' not in st.session_state:
            st.session_state.data_manager = data_manager
        if 'settings_manager' not in st.session_state:
            st.session_state.settings_manager = settings_manager
        
        # Load settings into Pomodoro timer
        pomodoro_settings = settings_manager.get_pomodoro_settings()
        st.session_state.pomodoro.work_duration = pomodoro_settings.get('work_duration', DEFAULT_WORK_DURATION)
        st.session_state.pomodoro.break_duration = pomodoro_settings.get('break_duration', DEFAULT_BREAK_DURATION)
        st.session_state.pomodoro.long_break_duration = pomodoro_settings.get('long_break_duration', DEFAULT_LONG_BREAK_DURATION)
        
        # Main application UI
        render_main_ui()
        
    except Exception as e:
        log_error(f"Application error: {e}", e)
        st.error(f"Application error: {e}")
    finally:
        log_app_stop()

def render_main_ui():
    """Render the main application UI"""
    
    # Modern minimalist CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    .main {
        background: #0a0a0a;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #0a0a0a;
    }
    
    .stSidebar {
        background: rgba(15, 15, 15, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .metric-card {
        background: rgba(20, 20, 20, 0.8);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin: 0.5rem 0;
    }
    
    .timer-display {
        font-size: 3.5rem;
        font-weight: 300;
        text-align: center;
        margin: 1.5rem 0;
        letter-spacing: -0.02em;
    }
    
    .work-timer {
        color: #00ff88;
    }
    
    .break-timer {
        color: #ff6b6b;
    }
    
    .stButton > button {
        background: rgba(30, 30, 30, 0.8);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.4rem 1rem;
        font-weight: 400;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: rgba(40, 40, 40, 0.9);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .primary-button {
        background: #00ff88 !important;
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    .primary-button:hover {
        background: #00cc6a !important;
    }
    
    .danger-button {
        background: #ff4444 !important;
        color: #ffffff !important;
    }
    
    .danger-button:hover {
        background: #cc3333 !important;
    }
    
    .task-item {
        background: rgba(20, 20, 20, 0.6);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    
    .task-item:hover {
        background: rgba(25, 25, 25, 0.8);
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    .simple-input {
        background: rgba(20, 20, 20, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #ffffff;
    }
    
    .chart-container {
        background: rgba(20, 20, 20, 0.6);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'tracker' not in st.session_state:
        st.session_state.tracker = TimeTracker()
    if 'pomodoro' not in st.session_state:
        st.session_state.pomodoro = PomodoroTimer()
    if 'current_task' not in st.session_state:
        st.session_state.current_task = None
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    if 'is_tracking' not in st.session_state:
        st.session_state.is_tracking = False
    if 'task_added' not in st.session_state:
        st.session_state.task_added = False
    if 'settings_saved' not in st.session_state:
        st.session_state.settings_saved = False
    
    # Check for timer completions (runs on every page load)
    check_timer_completion()
    
    # Add JavaScript auto-refresh for background timer checking
    if st.session_state.pomodoro.is_running or st.session_state.is_tracking:
        st.markdown("""
        <script>
        // Auto-refresh every 3 seconds when timers are running (for testing)
        setTimeout(function() {
            window.location.reload();
        }, 3000);
        </script>
        """, unsafe_allow_html=True)
    
    # Simplified sidebar (MUST be before main content)
    with st.sidebar:
        st.markdown("# Tasks")
        
        # Simple task input with form
        with st.form("add_task_form"):
            new_task = st.text_input("Add task", placeholder="Enter task name...", key="new_task_input", label_visibility="collapsed")
            submitted = st.form_submit_button("Add", key="add_task_button", width='stretch')
            if submitted and new_task:
                try:
                    st.session_state.tracker.add_task(new_task)
                    st.session_state.task_added = True
                    st.success(f"Added task: {new_task}")
                except Exception as e:
                    st.error(f"Error adding task: {e}")
        
        # Handle task addition outside the form
        if st.session_state.get('task_added', False):
            st.session_state.task_added = False
            st.rerun()
        
        # List active tasks
        tasks = st.session_state.tracker.get_tasks()
        active_tasks = [task for task in tasks if task['status'] == 'active']
        
        if active_tasks:
            st.markdown("### Active Tasks")
            for task in active_tasks:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {task['task_name']}")
                with col2:
                    if st.button("Start", key=f"start_{task['task_name']}", width='stretch'):
                        st.session_state.current_task = task['task_name']
                        st.session_state.timer_start = datetime.datetime.now()
                        st.session_state.is_tracking = True
                        st.rerun()
                
                col3, col4 = st.columns([1, 1])
                with col3:
                    if st.button("Delete", key=f"delete_{task['task_name']}", help="Delete task"):
                        st.session_state.tracker.delete_task(task['task_name'])
                        st.rerun()
                with col4:
                    st.write("")  # Empty space for alignment
        else:
            st.info("No active tasks. Add a task to start tracking!")

    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Time Tracker", "Schedule Planner", "Analytics", "Data Management", "Settings", "About"])
    
    with tab1:
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("# Time Tracker")
            
            # Current task tracking
            if st.session_state.is_tracking and st.session_state.current_task:
                st.markdown(f"**Tracking:** {st.session_state.current_task}")
                
                if st.button("Stop", type="primary", key="stop_task_timer", width='stretch'):
                    if st.session_state.timer_start:
                        end_time = datetime.datetime.now()
                        st.session_state.tracker.log_time(
                            st.session_state.current_task,
                            st.session_state.timer_start,
                            end_time
                        )
                        st.session_state.is_tracking = False
                        st.session_state.current_task = None
                        st.session_state.timer_start = None
                        st.success("Time logged successfully!")
                        st.rerun()
                
                # Display elapsed time
                if st.session_state.timer_start:
                    elapsed = datetime.datetime.now() - st.session_state.timer_start
                    elapsed_minutes = elapsed.total_seconds() / 60
                    elapsed_hours = int(elapsed_minutes // 60)
                    elapsed_mins = int(elapsed_minutes % 60)
                    elapsed_secs = int(elapsed.total_seconds() % 60)
                    
                    if elapsed_hours > 0:
                        time_display = f"{elapsed_hours:02d}:{elapsed_mins:02d}:{elapsed_secs:02d}"
                    else:
                        time_display = f"{elapsed_mins:02d}:{elapsed_secs:02d}"
                    
                    st.markdown(f"""
                    <div style="text-align: center; font-size: 2rem; font-weight: bold; color: #00ff88; margin: 1rem 0;">
                        {time_display}
                    </div>
                    """, unsafe_allow_html=True)
                    
            else:
                st.info("Select a task to start tracking")
        
        # Universal refresh button between columns
        if st.session_state.is_tracking or st.session_state.pomodoro.is_running:
            st.markdown("---")
            if st.button("Refresh Timers", key="refresh_timers_main", help="Click to update both timer displays", use_container_width=True):
                st.rerun()
            st.markdown("---")
        
        with col2:
            st.markdown("# Pomodoro")
            
            # Update Pomodoro timer
            st.session_state.pomodoro.update_timer()
            
            # Timer display
            timer_class = "break-timer" if st.session_state.pomodoro.is_break else "work-timer"
            session_type = "Break" if st.session_state.pomodoro.is_break else "Work"
            st.markdown(f'<div class="timer-display {timer_class}">{format_time(st.session_state.pomodoro.remaining_time)}</div>', 
                       unsafe_allow_html=True)
            
            # Simplified timer controls
            col_start, col_reset = st.columns(2)
            
            with col_start:
                if not st.session_state.pomodoro.is_running:
                    if st.button("Start", key="pomo_start_tab1", use_container_width=True):
                        st.session_state.pomodoro.start_timer()
                        st.rerun()
                else:
                    if st.button("Pause", key="pomo_stop_tab1", use_container_width=True):
                        st.session_state.pomodoro.stop_timer()
                        st.rerun()
            
            with col_reset:
                if st.button("Reset", key="pomo_reset_tab1", use_container_width=True):
                    st.session_state.pomodoro.reset_timer()
                    st.rerun()
            
            st.markdown(f"**{session_type}** • {st.session_state.pomodoro.session_count} sessions")
            
            # Check if timer just completed and show celebration
            if st.session_state.pomodoro.just_completed:
                session_type_completed = "Break" if st.session_state.pomodoro.is_break else "Work"
                
                if session_type_completed == "Work":
                    st.success(f"{session_type_completed} session complete! Sounds should be playing!")
                    st.balloons()  # Visual celebration
                else:
                    st.success(f"{session_type_completed} complete! Startup sound should be playing!")
                
                # Reset the completion flag
                st.session_state.pomodoro.just_completed = False
                st.rerun()
        
        # Simplified analytics section
        st.divider()
        st.markdown("# Analytics")
        
        # Get statistics
        stats = st.session_state.tracker.get_task_statistics()
        logs_df = st.session_state.tracker.get_time_logs()
        
        if not logs_df.empty:
            # Clean metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Time", f"{stats.get('total_time', 0):.1f} min")
            
            with col2:
                st.metric("Today", f"{stats.get('today_time', 0):.1f} min")
            
            with col3:
                st.metric("This Week", f"{stats.get('week_time', 0):.1f} min")
            
            with col4:
                st.metric("Tasks", stats.get('unique_tasks', 0))
            
            # Task summary table
            if 'task_breakdown' in stats and stats['task_breakdown']:
                st.markdown("### Task Summary")
                summary_data = []
                for task, data in stats['task_breakdown'].items():
                    summary_data.append({
                        'Task': task,
                        'Total Time': f"{data['total_time']:.1f} min",
                        'Sessions': data['sessions'],
                        'Avg Session': f"{data['avg_session']:.1f} min",
                        'Days Worked': data['days_worked']
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
            
            # Simple data table
            st.markdown("### Recent Sessions")
            recent_logs = logs_df.tail(5)[['task', 'duration_minutes', 'date']]
            st.dataframe(recent_logs, use_container_width=True)
        
        else:
            st.info("No time logs yet. Start tracking tasks to see analytics!")
    
    with tab2:
        render_schedule_planner_tab()
    
    with tab3:
        render_analytics_tab()
    
    with tab4:
        render_data_management_tab()
    
    with tab5:
        render_settings_tab()
    
    with tab6:
        render_about_tab()

def validate_time_log_changes(original_df, edited_df):
    """Validate changes made to time logs"""
    try:
        # Check if all required columns are present
        required_cols = ['task', 'start_time', 'end_time', 'duration_minutes', 'date', 'session_type']
        if not all(col in edited_df.columns for col in required_cols):
            st.error(f"Missing columns. Required: {required_cols}, Found: {list(edited_df.columns)}")
            return False
        
        # Validate each row (skip rows marked for deletion)
        for idx, row in edited_df.iterrows():
            # Skip validation for rows marked for deletion
            if 'delete' in edited_df.columns and row.get('delete', False):
                continue
            
            # Check if this is an empty row (all fields empty or NaN)
            if pd.isna(row['task']) or (not row['task'] or not str(row['task']).strip()):
                # Check if other fields are also empty
                if (pd.isna(row['start_time']) or not row['start_time']) and \
                   (pd.isna(row['end_time']) or not row['end_time']):
                    st.warning(f"Row {idx}: Empty row detected - skipping validation")
                    continue
                else:
                    st.error(f"Row {idx}: Empty task name - please enter a task name or delete this row")
                    return False
            
            # Check time format and logic
            try:
                start_time = pd.to_datetime(row['start_time'])
                end_time = pd.to_datetime(row['end_time'])
                
                if start_time >= end_time:
                    st.error(f"Row {idx}: Start time must be before end time")
                    return False
                
                # Check duration consistency - auto-correct if times were changed
                calculated_duration = (end_time - start_time).total_seconds() / 60
                if abs(calculated_duration - row['duration_minutes']) > 0.1:  # Allow small rounding differences
                    # Auto-correct the duration if times were changed
                    edited_df.loc[idx, 'duration_minutes'] = calculated_duration
                    st.info(f"Row {idx}: Auto-corrected duration from {row['duration_minutes']:.2f} to {calculated_duration:.2f} minutes")
                
            except (ValueError, TypeError) as e:
                st.error(f"Row {idx}: Invalid time format - {e}")
                return False
            
            # Check date format
            try:
                pd.to_datetime(row['date'])
            except (ValueError, TypeError) as e:
                st.error(f"Row {idx}: Invalid date format - {e}")
                return False
            
            # Check session type
            if row['session_type'] not in ['work', 'break', 'long_break']:
                st.error(f"Row {idx}: Invalid session type: {row['session_type']}")
                return False
        
        return True
        
    except Exception as e:
        st.error(f"Validation error: {e}")
        return False

def update_time_logs(edited_df, original_df):
    """Update the time logs CSV file with edited data"""
    try:
        # Get the tracker instance
        tracker = st.session_state.tracker
        
        # Get the complete dataset (not just the recent 50)
        complete_df = tracker.get_time_logs()
        
        # Debug: Show what we're working with
        st.write(f"**Debug: Complete dataset has {len(complete_df)} rows**")
        st.write(f"**Debug: Edited dataset has {len(edited_df)} rows**")
        
        # Process each edited row
        rows_updated = 0
        rows_deleted = 0
        
        for idx in edited_df.index:
            if idx in complete_df.index:
                row = edited_df.loc[idx]
                
                # Check if row is marked for deletion
                if 'delete' in edited_df.columns and row.get('delete', False):
                    # Remove this row
                    complete_df = complete_df.drop(idx)
                    rows_deleted += 1
                    st.write(f"**Debug: Deleted row {idx}**")
                else:
                    # Skip empty rows (rows with no task name and no times)
                    if (pd.isna(row['task']) or not row['task'] or not str(row['task']).strip()) and \
                       (pd.isna(row['start_time']) or not row['start_time']) and \
                       (pd.isna(row['end_time']) or not row['end_time']):
                        # Remove empty rows
                        complete_df = complete_df.drop(idx)
                        rows_deleted += 1
                        st.write(f"**Debug: Removed empty row {idx}**")
                        continue
                    
                    # Update the row with edited data (excluding delete column)
                    update_data = row.drop('delete') if 'delete' in edited_df.columns else row
                    complete_df.loc[idx] = update_data
                    rows_updated += 1
                    st.write(f"**Debug: Updated row {idx}**")
        
        # Recalculate duration for consistency
        complete_df['duration_minutes'] = (
            pd.to_datetime(complete_df['end_time']) - 
            pd.to_datetime(complete_df['start_time'])
        ).dt.total_seconds() / 60
        
        # Round duration to 2 decimal places
        complete_df['duration_minutes'] = complete_df['duration_minutes'].round(2)
        
        # Debug: Show final dataset
        st.write(f"**Debug: Final dataset has {len(complete_df)} rows**")
        st.write(f"**Debug: Updated {rows_updated} rows, deleted {rows_deleted} rows**")
        
        # Save to CSV using the tracker's safe file operation
        tracker._safe_file_operation(tracker.csv_file, 'write', complete_df)
        
        # Debug: Verify the file was written
        st.info(f"✅ Data saved to {tracker.csv_file} - {len(complete_df)} rows")
        
        # Small delay to ensure file write is complete
        import time
        time.sleep(0.2)  # Increased delay
        
        # Update task totals
        tracker.update_all_task_totals()
        
        # Force refresh the session state data
        st.session_state.tracker._data_cache = None
        
        # Additional verification: Read back the file to confirm
        verification_df = pd.read_csv(tracker.csv_file)
        st.write(f"**Debug: Verification - CSV file now has {len(verification_df)} rows**")
        
        # Force a complete refresh of the tracker instance
        st.session_state.tracker = TimeTracker()
        st.write("**Debug: Created fresh TimeTracker instance**")
        
    except Exception as e:
        st.error(f"Failed to update time logs: {e}")
        raise Exception(f"Failed to update time logs: {e}")

def render_schedule_planner_tab():
    """Render the Schedule Planner tab"""
    st.markdown("## Schedule Planner")
    st.markdown("Plan your day with time blocks for efficient work")
    
    # Date selector
    selected_date = st.date_input("Select Date", value=datetime.date.today())
    date_str = selected_date.strftime('%Y-%m-%d')
    
    # Get existing tasks for dropdown
    tasks = st.session_state.tracker.get_tasks()
    active_tasks = [task['task_name'] for task in tasks if task['status'] == 'active']
    
    # Add new schedule block form
    with st.expander("Add Time Block", expanded=True):
        with st.form("add_schedule_block"):
            col1, col2 = st.columns(2)
            
            with col1:
                start_time = st.time_input("Start Time", value=datetime.time(9, 0))
                task_name = st.selectbox("Task", options=active_tasks + ["Break", "Meeting", "Other"])
                if task_name == "Other":
                    task_name = st.text_input("Custom Task Name", placeholder="Enter task name...")
            
            with col2:
                end_time = st.time_input("End Time", value=datetime.time(10, 0))
                block_type = st.selectbox("Block Type", ["work", "break", "meeting", "focus"])
            
            notes = st.text_area("Notes (optional)", placeholder="Add any notes...")
            
            if st.form_submit_button("Add Block"):
                if task_name and task_name.strip():
                    try:
                        st.session_state.tracker.add_schedule_block(
                            date_str,
                            start_time.strftime('%H:%M'),
                            end_time.strftime('%H:%M'),
                            task_name.strip(),
                            block_type,
                            notes.strip()
                        )
                        st.success(f"Added {task_name} from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding schedule block: {e}")
                else:
                    st.error("Please enter a task name")
    
    # Display schedule for selected date
    st.markdown("### Today's Schedule")
    schedule_blocks = st.session_state.tracker.get_schedule_blocks(date_str)
    
    if schedule_blocks:
        # Sort blocks by start time
        schedule_blocks.sort(key=lambda x: x['start_time'])
        
        # Create timeline view
        for i, block in enumerate(schedule_blocks):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    # Visual block representation
                    block_type_color = {
                        'work': '#00ff88',
                        'break': '#ff6b6b', 
                        'meeting': '#4dabf7',
                        'focus': '#9775fa'
                    }
                    
                    color = block_type_color.get(block['block_type'], '#666666')
                    completed = block.get('completed', False)
                    
                    if completed:
                        st.markdown(f"""
                        <div style="background: rgba(0,255,136,0.1); border-left: 4px solid {color}; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                            <strong style="text-decoration: line-through; opacity: 0.7;">{block['task_name']}</strong><br>
                            <small>{block['start_time']} - {block['end_time']} • {block['block_type']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(20,20,20,0.8); border-left: 4px solid {color}; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                            <strong>{block['task_name']}</strong><br>
                            <small>{block['start_time']} - {block['end_time']} • {block['block_type']}</small>
                            {f"<br><em>{block['notes']}</em>" if block.get('notes') else ""}
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                    if not completed:
                        if st.button("Start Timer", key=f"start_timer_{i}"):
                            st.session_state.current_task = block['task_name']
                            st.session_state.timer_start = datetime.datetime.now()
                            st.session_state.is_tracking = True
                            st.rerun()
                
                with col3:
                    if st.button("Complete", key=f"complete_{i}"):
                        st.session_state.tracker.update_schedule_block(
                            date_str, block['start_time'], block['task_name'], completed=True
                        )
                        st.rerun()
                
                with col4:
                    if st.button("Delete", key=f"delete_{i}"):
                        st.session_state.tracker.delete_schedule_block(
                            date_str, block['start_time'], block['task_name']
                        )
                        st.rerun()
    else:
        st.info("No schedule blocks for this date. Add some time blocks to plan your day!")
    
    # Quick stats
    if schedule_blocks:
        total_blocks = len(schedule_blocks)
        completed_blocks = sum(1 for block in schedule_blocks if block.get('completed', False))
        work_blocks = sum(1 for block in schedule_blocks if block['block_type'] == 'work')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Blocks", total_blocks)
        with col2:
            st.metric("Completed", f"{completed_blocks}/{total_blocks}")
        with col3:
            st.metric("Work Blocks", work_blocks)

def render_analytics_tab():
    """Render the Analytics tab with advanced visualizations"""
    st.markdown("# Advanced Analytics")
    
    # Force fresh data loading to ensure we have the latest data
    # Clear cache first to ensure fresh data
    st.session_state.tracker._data_cache = None
    logs_df = st.session_state.tracker.get_time_logs()
    tasks_df = pd.read_csv(st.session_state.tracker.tasks_file) if os.path.exists(st.session_state.tracker.tasks_file) else pd.DataFrame()
    
    # Debug: Show what data was loaded
    st.write(f"**Debug: Loaded {len(logs_df)} time log entries**")
    if not logs_df.empty:
        st.write("Sample of loaded data:")
        st.dataframe(logs_df.head(3), use_container_width=True)
        
        # Debug: Show the actual CSV file contents
        st.write("**Debug: Checking CSV file directly:**")
        try:
            csv_df = pd.read_csv("time_logs.csv")
            st.write(f"CSV file has {len(csv_df)} rows")
            st.write("CSV file sample:")
            st.dataframe(csv_df.head(3), use_container_width=True)
            
            # Compare loaded data with CSV data
            if len(logs_df) == len(csv_df):
                st.write("✅ **Data consistency check: PASSED** - Loaded data matches CSV file")
            else:
                st.write(f"❌ **Data consistency check: FAILED** - Loaded: {len(logs_df)}, CSV: {len(csv_df)}")
                
            # Check if specific rows match
            if not logs_df.empty and not csv_df.empty:
                # Compare first few rows
                logs_sample = logs_df.head(3)[['task', 'start_time', 'end_time', 'duration_minutes']]
                csv_sample = csv_df.head(3)[['task', 'start_time', 'end_time', 'duration_minutes']]
                
                if logs_sample.equals(csv_sample):
                    st.write("✅ **Row content check: PASSED** - Sample rows match exactly")
                else:
                    st.write("❌ **Row content check: FAILED** - Sample rows differ")
                    st.write("Loaded data sample:")
                    st.dataframe(logs_sample, use_container_width=True)
                    st.write("CSV file sample:")
                    st.dataframe(csv_sample, use_container_width=True)
                    
        except Exception as e:
            st.write(f"Error reading CSV file: {e}")
    
    if logs_df.empty:
        st.info("No data available for analytics. Start tracking time to see insights!")
        return
    
    # Initialize analytics engine
    analytics = AnalyticsEngine(logs_df, tasks_df)
    
    # Get productivity metrics
    metrics = analytics.get_productivity_metrics()
    
    if metrics:
        st.markdown("## Productivity Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Time", f"{metrics.get('total_time_hours', 0):.1f} hrs")
            with col2:
                st.metric("Sessions", f"{metrics.get('total_sessions', 0)}")
        with col3:
            st.metric("Avg Session", f"{metrics.get('avg_session_length', 0):.1f} min")
        with col4:
            st.metric("Consistency", f"{metrics.get('consistency_score', 0):.2f}")
    
    # Charts
    st.markdown("## Visualizations")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.plotly_chart(analytics.create_time_trend_chart(), use_container_width=True)
    
    with chart_col2:
        st.plotly_chart(analytics.create_task_distribution_chart(), use_container_width=True)
    
    # Additional charts
    st.plotly_chart(analytics.create_productivity_heatmap(), use_container_width=True)
    
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.plotly_chart(analytics.create_session_length_distribution(), use_container_width=True)
    
    with chart_col4:
        # Task performance analysis
        st.markdown("### Task Performance")
        performance_df = analytics.get_task_performance_analysis()
        if not performance_df.empty:
            st.dataframe(performance_df, use_container_width=True)
        else:
            st.info("No task performance data available")
    
    # Data editing section
    st.markdown("## Edit Time Entries")
    st.markdown("Correct inaccurate time logs or remove unwanted entries.")
    
    # Get recent time logs for editing
    recent_logs = logs_df.tail(50)  # Show last 50 entries
    
    if not recent_logs.empty:
        st.markdown("### Recent Time Entries")
        
        # Add a delete column for better user control
        logs_with_delete = recent_logs.copy()
        logs_with_delete['delete'] = False
        
        # Create editable dataframe
        edited_df = st.data_editor(
            logs_with_delete[['task', 'start_time', 'end_time', 'duration_minutes', 'date', 'session_type', 'delete']],
            num_rows="dynamic",
            use_container_width=True,
            key="time_logs_editor",
            column_config={
                "delete": st.column_config.CheckboxColumn(
                    "Delete",
                    help="Check to mark for deletion",
                    default=False,
                )
            }
        )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.caption("Hint: If you edit start_time or end_time, set both so duration updates correctly before saving.")
            if st.button("Save Changes", type="primary"):
                try:
                    # Validate changes
                    if validate_time_log_changes(recent_logs, edited_df):
                        # Update the CSV file
                        update_time_logs(edited_df, logs_df)
                        st.success("Time entries updated successfully!")
                st.rerun()
                    else:
                        st.error("Invalid data detected. Please check your entries.")
                except Exception as e:
                    st.error(f"Error updating time entries: {e}")
        
        with col2:
            if st.button("Reset Changes"):
                st.rerun()
        
        with col3:
            st.markdown("**Instructions:**")
            st.markdown("- Edit any field to modify entries")
            st.markdown("- Check 'Delete' to remove entries")
            st.markdown("- Click 'Save Changes' to apply")
    
    else:
        st.info("No time entries available for editing.")

def render_data_management_tab():
    """Render the Data Management tab"""
    st.markdown("# Data Management")
    
    data_manager = st.session_state.data_manager
    
    # Data summary
    st.markdown("## Data Summary")
    summary = data_manager.get_data_summary()
    
    if summary:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Time Logs", f"{summary['time_logs']['count']} entries")
        with col2:
            st.metric("Tasks", f"{summary['tasks']['count']} total")
        with col3:
            st.metric("Total Time", f"{summary['time_logs']['total_time']:.1f} min")
    
    # Export/Import section
    st.markdown("## Export & Import")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        st.markdown("### Export Data")
        export_format = st.selectbox("Export Format", EXPORT_FORMATS)
        
        if st.button("Export All Data", type="primary"):
            export_data = data_manager.export_data(export_format)
            if export_data:
                if export_format == 'csv':
                    st.download_button(
                        "Download CSV",
                        export_data.get('time_logs', ''),
                        f"time_tracker_export_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
                else:
                    st.json(export_data)
                st.success("Data exported successfully!")
            else:
                st.error("Failed to export data")
    
    with export_col2:
        st.markdown("### Import Data")
        uploaded_file = st.file_uploader("Choose a file", type=['csv', 'json'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    content = uploaded_file.read().decode('utf-8')
                    import_data = {'time_logs': content}
                else:
                    import_data = json.load(uploaded_file)
                
                if st.button("Import Data"):
                    if data_manager.import_data(import_data):
                        st.success("Data imported successfully!")
                        st.success("Data imported successfully!")
                        st.success("Data imported successfully!")
                    st.rerun()
                    else:
                        st.error("Failed to import data")
            except Exception as e:
                st.error(f"Import error: {e}")
        st.markdown("## Backup Management")
    
    backup_col1, backup_col2 = st.columns(2)
    
    with backup_col1:
        if st.button("Create Backup", type="secondary"):
            backup_name = data_manager.create_backup()
            if backup_name:
                st.success(f"Backup created: {backup_name}")
                else:
                st.error("Failed to create backup")
    
    with backup_col2:
        if st.button("Clean Old Backups"):
            deleted_count = data_manager.cleanup_old_backups()
            st.success(f"Cleaned up {deleted_count} old backup files")
    
    # Data validation
    st.markdown("## Data Validation")
    
    if st.button("Validate Data Integrity"):
        issues = data_manager.validate_data_integrity()
        if issues:
            for category, problems in issues.items():
                if problems:
                    st.warning(f"{category.title()}: {', '.join(problems)}")
        else:
            st.success("Data integrity check passed!")

def render_settings_tab():
    """Render the Settings tab"""
    st.markdown("# Settings")
    
    settings_manager = st.session_state.settings_manager
    
    # Pomodoro settings
    st.markdown("## Pomodoro Timer")
    
    with st.form("pomodoro_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            work_duration = st.number_input(
                "Work Duration (minutes)",
                min_value=MIN_DURATION,
                max_value=MAX_DURATION,
                value=settings_manager.get_setting('pomodoro', 'work_duration', DEFAULT_WORK_DURATION)
            )
            
            break_duration = st.number_input(
                "Break Duration (minutes)",
                min_value=MIN_DURATION,
                max_value=MAX_DURATION,
                value=settings_manager.get_setting('pomodoro', 'break_duration', DEFAULT_BREAK_DURATION)
            )
    
    with col2:
            long_break_duration = st.number_input(
                "Long Break Duration (minutes)",
                min_value=MIN_DURATION,
                max_value=MAX_DURATION,
                value=settings_manager.get_setting('pomodoro', 'long_break_duration', DEFAULT_LONG_BREAK_DURATION)
            )
            
            sessions_before_long_break = st.number_input(
                "Sessions Before Long Break",
                min_value=1,
                max_value=10,
                value=settings_manager.get_setting('pomodoro', 'sessions_before_long_break', 4)
            )
            
            auto_start_breaks = st.checkbox(
                "Auto-start breaks",
                value=settings_manager.get_setting('pomodoro', 'auto_start_breaks', True)
            )
            
            sound_enabled = st.checkbox(
                "Enable sounds",
                value=settings_manager.get_setting('pomodoro', 'sound_enabled', True)
            )
            
            if st.form_submit_button("Save Pomodoro Settings", type="primary"):
                pomodoro_settings = {
                    'work_duration': work_duration,
                    'break_duration': break_duration,
                    'long_break_duration': long_break_duration,
                    'sessions_before_long_break': sessions_before_long_break,
                    'auto_start_breaks': auto_start_breaks,
                    'sound_enabled': sound_enabled
                }
                
                if settings_manager.set_pomodoro_settings(pomodoro_settings):
                    settings_manager.save_settings()
                    st.success("Pomodoro settings saved!")
                    st.rerun()
            else:
                    st.error("Failed to save settings")
    
    # UI settings
    st.markdown("## Interface")
    
    with st.form("ui_settings"):
        theme = st.selectbox("Theme", ["dark", "light"], index=0)
        auto_refresh = st.number_input("Auto-refresh interval (seconds)", min_value=1.0, max_value=60.0, value=3.0)
        show_notifications = st.checkbox("Show notifications", value=True)
        
        if st.form_submit_button("Save UI Settings"):
            ui_settings = {
                'theme': theme,
                'auto_refresh_interval': auto_refresh,
                'show_notifications': show_notifications
            }
            
            if settings_manager.set_ui_settings(ui_settings):
                settings_manager.save_settings()
                st.success("UI settings saved!")
            else:
                st.error("Failed to save settings")
    
    # Data settings
    st.markdown("## Data Management")
    
    with st.form("data_settings"):
        auto_backup = st.checkbox("Enable automatic backups", value=True)
        backup_frequency = st.number_input("Backup frequency (days)", min_value=1.0, max_value=30.0, value=7.0)
        max_backups = st.number_input("Maximum backup files", min_value=1.0, max_value=50.0, value=10.0)
        
        if st.form_submit_button("Save Data Settings"):
            data_settings = {
                'auto_backup_enabled': auto_backup,
                'backup_frequency_days': backup_frequency,
                'max_backup_files': max_backups
            }
            
            settings_manager.set_setting('data', 'auto_backup_enabled', auto_backup)
            settings_manager.set_setting('data', 'backup_frequency_days', backup_frequency)
            settings_manager.set_setting('data', 'max_backup_files', max_backups)
            
            if settings_manager.save_settings():
                st.success("Data settings saved!")
            else:
                st.error("Failed to save settings")
    
    # Reset settings
    st.markdown("## Reset")
    
    if st.button("Reset to Defaults", type="secondary"):
        if settings_manager.reset_to_defaults():
            settings_manager.save_settings()
            st.success("Settings reset to defaults!")
            st.rerun()
        else:
            st.error("Failed to reset settings")

def render_about_tab():
    """Render the About tab"""
    st.markdown(f"# {APP_NAME}")
    st.markdown(f"**Version:** {APP_VERSION}")
    st.markdown(f"**Description:** {APP_DESCRIPTION}")
    
    st.markdown("## Features")
    
    features = [
        "Task-based time tracking",
        "Pomodoro timer with customizable durations",
        "Sound notifications and visual celebrations",
        "Advanced analytics and visualizations",
        "Data export/import functionality",
        "Automatic backups and data validation",
        "Comprehensive settings management",
        "Dark theme with minimalist design"
    ]
    
    for feature in features:
        st.markdown(f"- {feature}")
    
    st.markdown("## Data Storage")
    st.markdown("Your data is stored locally in CSV files:")
    st.markdown("- `time_logs.csv` - Detailed time tracking sessions")
    st.markdown("- `tasks.csv` - Task list and total times")
    st.markdown("- `settings.json` - Application settings")
    st.markdown("- `logs/` - Application logs")
    st.markdown("- `backups/` - Automatic backups")
    
    st.markdown("## Technical Details")
    st.markdown(f"- **Python Version:** {sys.version.split()[0]}")
    st.markdown(f"- **Streamlit Version:** {st.__version__}")
    st.markdown(f"- **Data Directory:** {Path.cwd()}")
    
    st.markdown("## License")
    st.markdown("This application is provided as-is for personal use.")

if __name__ == "__main__":
    main()
