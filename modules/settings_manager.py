import json
import os
import logging
from typing import Any, Dict

class SettingsManager:
    """
    Manages user settings and preferences.
    """
    
    def __init__(self, settings_file='settings.json'):
        """
        Initialize the SettingsManager with a specified settings file.
        
        :param settings_file: str - Path to the settings file.
        """
        self.settings_file = settings_file
        self.settings = self.load_settings()
        logging.info(f"SettingsManager initialized with settings file: {settings_file}")
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from the settings file.
        
        :return: Dict[str, Any] - Dictionary of settings.
        """
        if not os.path.exists(self.settings_file):
            default_settings = {
                "language": "English",
                "speech_rate": 150,
                "theme": "Light",
                "font_size": 12,
                "auto_correct": True,
                "correction_mode": "Standard",
                "severity_level": "High",
                "color_scheme": "default",
                "current_language": "English",
                "api_usage": 0,
                "last_api_call": ""
            }
            self.save_settings(default_settings)
            logging.info("Default settings created.")
            return default_settings
        try:
            with open(self.settings_file, 'r') as file:
                settings = json.load(file)
            logging.info("Settings loaded successfully.")
            return settings
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode settings file: {e}")
            return {}
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")
            return {}
    
    def save_settings(self, settings: Dict[str, Any] = None) -> None:
        """
        Save settings to the settings file.
        
        :param settings: Dict[str, Any] - Settings to save. If None, current settings are saved.
        """
        if settings:
            self.settings = settings
        try:
            with open(self.settings_file, 'w') as file:
                json.dump(self.settings, file, indent=4)
            logging.info("Settings saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
    
    def update_setting(self, key: str, value: Any) -> None:
        """
        Update a specific setting.
        
        :param key: str - Setting key.
        :param value: Any - New value for the setting.
        """
        self.settings[key] = value
        self.save_settings()
        logging.info(f"Setting '{key}' updated to '{value}'.")
