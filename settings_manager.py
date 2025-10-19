"""
Settings management for Time Tracker App
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import SETTINGS_FILE, DEFAULT_WORK_DURATION, DEFAULT_BREAK_DURATION, DEFAULT_LONG_BREAK_DURATION
from logger import log_error, log_user_action

class SettingsManager:
    """Manage application settings with persistence"""
    
    def __init__(self):
        self.settings_file = SETTINGS_FILE
        self.default_settings = {
            'pomodoro': {
                'work_duration': DEFAULT_WORK_DURATION,
                'break_duration': DEFAULT_BREAK_DURATION,
                'long_break_duration': DEFAULT_LONG_BREAK_DURATION,
                'sessions_before_long_break': 4,
                'auto_start_breaks': True,
                'sound_enabled': True
            },
            'ui': {
                'theme': 'dark',
                'auto_refresh_interval': 3,
                'show_notifications': True,
                'compact_mode': False
            },
            'data': {
                'auto_backup_enabled': True,
                'backup_frequency_days': 7,
                'max_backup_files': 10,
                'export_format': 'csv'
            },
            'notifications': {
                'sound_enabled': True,
                'desktop_notifications': True,
                'email_notifications': False,
                'notification_sound': 'default'
            },
            'privacy': {
                'data_retention_days': 365,
                'analytics_enabled': True,
                'crash_reporting': True
            }
        }
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                
                log_user_action('settings_loaded', f'from {self.settings_file}')
                return settings
            else:
                log_user_action('settings_created', 'default settings')
                return self.default_settings.copy()
                
        except Exception as e:
            log_error(f"Failed to load settings: {e}", e)
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Save current settings to file"""
        try:
            # Create directory if it doesn't exist
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            log_user_action('settings_saved', f'to {self.settings_file}')
            return True
            
        except Exception as e:
            log_error(f"Failed to save settings: {e}", e)
            return False
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        try:
            return self.settings.get(category, {}).get(key, default)
        except Exception as e:
            log_error(f"Failed to get setting {category}.{key}: {e}", e)
            return default
    
    def set_setting(self, category: str, key: str, value: Any) -> bool:
        """Set a specific setting value"""
        try:
            if category not in self.settings:
                self.settings[category] = {}
            
            self.settings[category][key] = value
            log_user_action('setting_changed', f'{category}.{key} = {value}')
            return True
            
        except Exception as e:
            log_error(f"Failed to set setting {category}.{key}: {e}", e)
            return False
    
    def get_pomodoro_settings(self) -> Dict[str, Any]:
        """Get Pomodoro-specific settings"""
        return self.settings.get('pomodoro', {})
    
    def set_pomodoro_settings(self, settings: Dict[str, Any]) -> bool:
        """Set Pomodoro settings"""
        try:
            self.settings['pomodoro'].update(settings)
            log_user_action('pomodoro_settings_updated', str(settings))
            return True
        except Exception as e:
            log_error(f"Failed to update Pomodoro settings: {e}", e)
            return False
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI-specific settings"""
        return self.settings.get('ui', {})
    
    def set_ui_settings(self, settings: Dict[str, Any]) -> bool:
        """Set UI settings"""
        try:
            self.settings['ui'].update(settings)
            log_user_action('ui_settings_updated', str(settings))
            return True
        except Exception as e:
            log_error(f"Failed to update UI settings: {e}", e)
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self.settings = self.default_settings.copy()
            log_user_action('settings_reset', 'to defaults')
            return True
        except Exception as e:
            log_error(f"Failed to reset settings: {e}", e)
            return False
    
    def export_settings(self) -> Dict[str, Any]:
        """Export settings for backup"""
        try:
            return {
                'settings': self.settings,
                'exported_at': str(Path().cwd()),
                'version': '2.0.0'
            }
        except Exception as e:
            log_error(f"Failed to export settings: {e}", e)
            return {}
    
    def import_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Import settings from backup"""
        try:
            if 'settings' in settings_data:
                self.settings = settings_data['settings']
                log_user_action('settings_imported', 'from backup')
                return True
            return False
        except Exception as e:
            log_error(f"Failed to import settings: {e}", e)
            return False
    
    def validate_settings(self) -> Dict[str, List[str]]:
        """Validate settings and return any issues"""
        issues = {}
        
        try:
            # Validate Pomodoro settings
            pomodoro = self.settings.get('pomodoro', {})
            if pomodoro.get('work_duration', 0) <= 0:
                issues.setdefault('pomodoro', []).append('Work duration must be positive')
            if pomodoro.get('break_duration', 0) <= 0:
                issues.setdefault('pomodoro', []).append('Break duration must be positive')
            if pomodoro.get('long_break_duration', 0) <= 0:
                issues.setdefault('pomodoro', []).append('Long break duration must be positive')
            
            # Validate UI settings
            ui = self.settings.get('ui', {})
            if ui.get('auto_refresh_interval', 0) < 1:
                issues.setdefault('ui', []).append('Auto refresh interval must be at least 1 second')
            
            # Validate data settings
            data = self.settings.get('data', {})
            if data.get('backup_frequency_days', 0) < 1:
                issues.setdefault('data', []).append('Backup frequency must be at least 1 day')
            if data.get('max_backup_files', 0) < 1:
                issues.setdefault('data', []).append('Max backup files must be at least 1')
            
            return issues
            
        except Exception as e:
            log_error(f"Failed to validate settings: {e}", e)
            return {'error': [str(e)]}
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
    
    def update_settings(self, updates: Dict[str, Any]) -> bool:
        """Update multiple settings at once"""
        try:
            for category, settings in updates.items():
                if category in self.settings:
                    self.settings[category].update(settings)
                else:
                    self.settings[category] = settings
            
            log_user_action('settings_bulk_updated', f'{len(updates)} categories')
            return True
            
        except Exception as e:
            log_error(f"Failed to update settings: {e}", e)
            return False
