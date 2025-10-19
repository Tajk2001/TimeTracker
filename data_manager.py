"""
Data management utilities for Time Tracker App
"""

import json
import pandas as pd
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from config import TIME_LOGS_FILE, TASKS_FILE, SETTINGS_FILE, EXPORT_FORMATS
from logger import log_data_operation, log_error

class DataManager:
    """Comprehensive data management for the Time Tracker"""
    
    def __init__(self):
        self.time_logs_file = TIME_LOGS_FILE
        self.tasks_file = TASKS_FILE
        self.settings_file = SETTINGS_FILE
        
    def export_data(self, format_type: str = 'csv', include_settings: bool = True) -> Dict[str, Any]:
        """Export all data in specified format"""
        try:
            export_data = {}
            
            # Export time logs
            if self.time_logs_file.exists():
                logs_df = pd.read_csv(self.time_logs_file)
                if format_type == 'csv':
                    export_data['time_logs'] = logs_df.to_csv(index=False)
                elif format_type == 'json':
                    export_data['time_logs'] = logs_df.to_dict('records')
                elif format_type == 'xlsx':
                    # For Excel, we'll return the DataFrame
                    export_data['time_logs'] = logs_df
                    
            # Export tasks
            if self.tasks_file.exists():
                tasks_df = pd.read_csv(self.tasks_file)
                if format_type == 'csv':
                    export_data['tasks'] = tasks_df.to_csv(index=False)
                elif format_type == 'json':
                    export_data['tasks'] = tasks_df.to_dict('records')
                elif format_type == 'xlsx':
                    export_data['tasks'] = tasks_df
                    
            # Export settings if requested
            if include_settings and self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    export_data['settings'] = json.load(f)
                    
            # Add metadata
            export_data['export_info'] = {
                'exported_at': datetime.datetime.now().isoformat(),
                'format': format_type,
                'app_version': '2.0.0'
            }
            
            log_data_operation('export', f'all_data.{format_type}', True, f'format: {format_type}')
            return export_data
            
        except Exception as e:
            log_error(f"Failed to export data: {e}", e)
            return {}
    
    def import_data(self, data: Dict[str, Any], format_type: str = 'json') -> bool:
        """Import data from backup"""
        try:
            # Create backup before import
            self.create_backup()
            
            # Import time logs
            if 'time_logs' in data:
                if format_type == 'json':
                    logs_df = pd.DataFrame(data['time_logs'])
                elif format_type == 'csv':
                    logs_df = pd.read_csv(data['time_logs'])
                else:
                    logs_df = data['time_logs']
                    
                logs_df.to_csv(self.time_logs_file, index=False)
                
            # Import tasks
            if 'tasks' in data:
                if format_type == 'json':
                    tasks_df = pd.DataFrame(data['tasks'])
                elif format_type == 'csv':
                    tasks_df = pd.read_csv(data['tasks'])
                else:
                    tasks_df = data['tasks']
                    
                tasks_df.to_csv(self.tasks_file, index=False)
                
            # Import settings
            if 'settings' in data:
                with open(self.settings_file, 'w') as f:
                    json.dump(data['settings'], f, indent=2)
                    
            log_data_operation('import', 'all_data', True, f'format: {format_type}')
            return True
            
        except Exception as e:
            log_error(f"Failed to import data: {e}", e)
            return False
    
    def create_backup(self) -> str:
        """Create timestamped backup of all data"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = Path('backups')
            backup_dir.mkdir(exist_ok=True)
            
            backup_files = []
            
            # Backup time logs
            if self.time_logs_file.exists():
                backup_file = backup_dir / f"time_logs_backup_{timestamp}.csv"
                backup_file.write_text(self.time_logs_file.read_text())
                backup_files.append(str(backup_file))
                
            # Backup tasks
            if self.tasks_file.exists():
                backup_file = backup_dir / f"tasks_backup_{timestamp}.csv"
                backup_file.write_text(self.tasks_file.read_text())
                backup_files.append(str(backup_file))
                
            # Backup settings
            if self.settings_file.exists():
                backup_file = backup_dir / f"settings_backup_{timestamp}.json"
                backup_file.write_text(self.settings_file.read_text())
                backup_files.append(str(backup_file))
                
            log_data_operation('backup', f'backup_{timestamp}', True, f'{len(backup_files)} files')
            return f"backup_{timestamp}"
            
        except Exception as e:
            log_error(f"Failed to create backup: {e}", e)
            return ""
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get comprehensive data summary"""
        try:
            summary = {
                'time_logs': {'count': 0, 'total_time': 0, 'date_range': None},
                'tasks': {'count': 0, 'active': 0},
                'files': {'time_logs_exists': False, 'tasks_exists': False, 'settings_exists': False}
            }
            
            # Time logs summary
            if self.time_logs_file.exists():
                logs_df = pd.read_csv(self.time_logs_file)
                if not logs_df.empty:
                    logs_df['duration_minutes'] = pd.to_numeric(logs_df['duration_minutes'], errors='coerce').fillna(0)
                    summary['time_logs']['count'] = len(logs_df)
                    summary['time_logs']['total_time'] = logs_df['duration_minutes'].sum()
                    
                    if 'date' in logs_df.columns:
                        dates = pd.to_datetime(logs_df['date'], errors='coerce')
                        valid_dates = dates.dropna()
                        if not valid_dates.empty:
                            summary['time_logs']['date_range'] = {
                                'start': valid_dates.min().strftime('%Y-%m-%d'),
                                'end': valid_dates.max().strftime('%Y-%m-%d')
                            }
                            
            # Tasks summary
            if self.tasks_file.exists():
                tasks_df = pd.read_csv(self.tasks_file)
                if not tasks_df.empty:
                    summary['tasks']['count'] = len(tasks_df)
                    summary['tasks']['active'] = len(tasks_df[tasks_df['status'] == 'active'])
                    
            # File existence
            summary['files']['time_logs_exists'] = self.time_logs_file.exists()
            summary['files']['tasks_exists'] = self.tasks_file.exists()
            summary['files']['settings_exists'] = self.settings_file.exists()
            
            return summary
            
        except Exception as e:
            log_error(f"Failed to get data summary: {e}", e)
            return {}
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> int:
        """Clean up old backup files"""
        try:
            backup_dir = Path('backups')
            if not backup_dir.exists():
                return 0
                
            cutoff_date = datetime.datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            deleted_count = 0
            
            for backup_file in backup_dir.glob("*_backup_*.csv"):
                if backup_file.stat().st_mtime < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    
            for backup_file in backup_dir.glob("*_backup_*.json"):
                if backup_file.stat().st_mtime < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    
            if deleted_count > 0:
                log_data_operation('cleanup', 'old_backups', True, f'{deleted_count} files deleted')
                
            return deleted_count
            
        except Exception as e:
            log_error(f"Failed to cleanup old backups: {e}", e)
            return 0
    
    def validate_data_integrity(self) -> Dict[str, List[str]]:
        """Validate data integrity and return issues"""
        issues = {'time_logs': [], 'tasks': []}
        
        try:
            # Validate time logs
            if self.time_logs_file.exists():
                logs_df = pd.read_csv(self.time_logs_file)
                
                # Check for required columns
                required_columns = ['task', 'start_time', 'end_time', 'duration_minutes', 'date', 'session_type']
                missing_columns = [col for col in required_columns if col not in logs_df.columns]
                if missing_columns:
                    issues['time_logs'].append(f"Missing columns: {missing_columns}")
                
                # Check for invalid durations
                if 'duration_minutes' in logs_df.columns:
                    invalid_durations = logs_df[pd.to_numeric(logs_df['duration_minutes'], errors='coerce').isna()]
                    if not invalid_durations.empty:
                        issues['time_logs'].append(f"Invalid durations in {len(invalid_durations)} rows")
                
                # Check for future dates
                if 'date' in logs_df.columns:
                    future_dates = pd.to_datetime(logs_df['date'], errors='coerce') > datetime.datetime.now()
                    if future_dates.any():
                        issues['time_logs'].append(f"Future dates in {future_dates.sum()} rows")
                        
            # Validate tasks
            if self.tasks_file.exists():
                tasks_df = pd.read_csv(self.tasks_file)
                
                # Check for required columns
                required_columns = ['task_name', 'status', 'created_date', 'total_time_minutes']
                missing_columns = [col for col in required_columns if col not in tasks_df.columns]
                if missing_columns:
                    issues['tasks'].append(f"Missing columns: {missing_columns}")
                
                # Check for invalid total times
                if 'total_time_minutes' in tasks_df.columns:
                    invalid_totals = tasks_df[pd.to_numeric(tasks_df['total_time_minutes'], errors='coerce').isna()]
                    if not invalid_totals.empty:
                        issues['tasks'].append(f"Invalid total times in {len(invalid_totals)} rows")
                        
            return issues
            
        except Exception as e:
            log_error(f"Failed to validate data integrity: {e}", e)
            return {'error': [str(e)]}
