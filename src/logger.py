"""
Logging system for Time Tracker App
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from config import LOGS_DIR

def setup_logging():
    """Setup comprehensive logging system"""
    
    # Create logs directory if it doesn't exist
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    log_file = LOGS_DIR / f"time_tracker_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create logger for the app
    logger = logging.getLogger('TimeTracker')
    logger.setLevel(logging.INFO)
    
    return logger

def log_app_start():
    """Log application startup"""
    logger = logging.getLogger('TimeTracker')
    logger.info("=" * 50)
    logger.info("Time Tracker Pro - Application Started")
    logger.info(f"Version: 2.0.0")
    logger.info(f"Start time: {datetime.now()}")
    logger.info("=" * 50)

def log_app_stop():
    """Log application shutdown"""
    logger = logging.getLogger('TimeTracker')
    logger.info("=" * 50)
    logger.info("Time Tracker Pro - Application Stopped")
    logger.info(f"Stop time: {datetime.now()}")
    logger.info("=" * 50)

def log_error(error_msg, exception=None):
    """Log errors with full context"""
    logger = logging.getLogger('TimeTracker')
    logger.error(f"ERROR: {error_msg}")
    if exception:
        logger.error(f"Exception: {str(exception)}", exc_info=True)

def log_user_action(action, details=None):
    """Log user actions for analytics"""
    logger = logging.getLogger('TimeTracker')
    if details:
        logger.info(f"USER ACTION: {action} - {details}")
    else:
        logger.info(f"USER ACTION: {action}")

def log_data_operation(operation, file_path, success=True, details=None):
    """Log data operations"""
    logger = logging.getLogger('TimeTracker')
    status = "SUCCESS" if success else "FAILED"
    if details:
        logger.info(f"DATA {status}: {operation} on {file_path} - {details}")
    else:
        logger.info(f"DATA {status}: {operation} on {file_path}")

def log_timer_event(event_type, duration=None, task=None):
    """Log timer events"""
    logger = logging.getLogger('TimeTracker')
    if duration and task:
        logger.info(f"TIMER EVENT: {event_type} - {duration:.2f}min for '{task}'")
    elif duration:
        logger.info(f"TIMER EVENT: {event_type} - {duration:.2f}min")
    else:
        logger.info(f"TIMER EVENT: {event_type}")

def log_performance(operation, duration_ms):
    """Log performance metrics"""
    logger = logging.getLogger('TimeTracker')
    logger.info(f"PERFORMANCE: {operation} took {duration_ms:.2f}ms")

def cleanup_old_logs(days_to_keep=30):
    """Clean up old log files"""
    logger = logging.getLogger('TimeTracker')
    try:
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        deleted_count = 0
        
        for log_file in LOGS_DIR.glob("time_tracker_*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                log_file.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"CLEANUP: Deleted {deleted_count} old log files")
            
    except Exception as e:
        logger.error(f"CLEANUP ERROR: Failed to clean old logs - {e}")
