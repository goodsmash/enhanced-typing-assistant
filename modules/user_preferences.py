from typing import Any, Dict, Optional
import json
import os
import logging
from PyQt5.QtCore import QSettings

class UserPreferences:
    """
    Manages user preferences and settings.
    """
    
    DEFAULT_PREFERENCES = {
        'theme': 'Light',
        'font_size': 12,
        'font_family': 'Arial',
        'dyslexia_font': False,
        'correction_mode': 'Standard',
        'correction_severity': 'Medium',
        'language': 'en_US',
        'speech_rate': 150,
        'auto_correction': True,
        'spell_check': True,
        'word_suggestions': True,
        'max_suggestions': 5,
        'ai_provider': 'OpenAI',
        'ai_model': 'GPT-3.5 Turbo',
        'keyboard_shortcuts': {
            'correct_text': 'Ctrl+Return',
            'voice_input': 'Ctrl+Shift+V',
            'text_to_speech': 'Ctrl+Shift+S',
            'clear_text': 'Ctrl+L',
            'save_text': 'Ctrl+S',
            'open_file': 'Ctrl+O',
            'new_file': 'Ctrl+N'
        }
    }
    
    def __init__(self):
        """Initialize UserPreferences."""
        self.settings = QSettings('TypingAssistant', 'Preferences')
        self.preferences = self.load_preferences()
        logging.info("UserPreferences initialized.")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a preference value.
        
        :param key: str - Preference key.
        :param default: Any - Default value if key not found.
        :return: Any - Preference value.
        """
        return self.preferences.get(key, default or self.DEFAULT_PREFERENCES.get(key))
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a preference value.
        
        :param key: str - Preference key.
        :param value: Any - Value to set.
        """
        self.preferences[key] = value
        self.save_preferences()
        logging.info(f"Preference '{key}' set to '{value}'")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all preferences.
        
        :return: Dict[str, Any] - Dictionary of all preferences.
        """
        return self.preferences.copy()
    
    def reset_to_default(self, key: Optional[str] = None) -> None:
        """
        Reset preferences to default values.
        
        :param key: Optional[str] - Specific key to reset, or None for all.
        """
        if key:
            if key in self.DEFAULT_PREFERENCES:
                self.preferences[key] = self.DEFAULT_PREFERENCES[key]
                logging.info(f"Reset preference '{key}' to default value.")
            else:
                logging.warning(f"Invalid preference key: {key}")
        else:
            self.preferences = self.DEFAULT_PREFERENCES.copy()
            logging.info("All preferences reset to default values.")
        self.save_preferences()
    
    def load_preferences(self) -> Dict[str, Any]:
        """
        Load preferences from QSettings.
        
        :return: Dict[str, Any] - Dictionary of preferences.
        """
        preferences = self.DEFAULT_PREFERENCES.copy()
        
        for key in preferences.keys():
            value = self.settings.value(key)
            if value is not None:
                if isinstance(preferences[key], bool):
                    preferences[key] = bool(value)
                elif isinstance(preferences[key], int):
                    preferences[key] = int(value)
                elif isinstance(preferences[key], dict):
                    try:
                        preferences[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        logging.warning(f"Failed to load dictionary preference: {key}")
                else:
                    preferences[key] = value
        
        logging.info("Preferences loaded successfully.")
        return preferences
    
    def save_preferences(self) -> None:
        """Save preferences to QSettings."""
        try:
            for key, value in self.preferences.items():
                if isinstance(value, dict):
                    self.settings.setValue(key, json.dumps(value))
                else:
                    self.settings.setValue(key, value)
            self.settings.sync()
            logging.info("Preferences saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save preferences: {e}")
    
    def get_keyboard_shortcut(self, action: str) -> str:
        """
        Get keyboard shortcut for an action.
        
        :param action: str - Action name.
        :return: str - Keyboard shortcut.
        """
        shortcuts = self.get('keyboard_shortcuts', {})
        return shortcuts.get(action, self.DEFAULT_PREFERENCES['keyboard_shortcuts'].get(action))
    
    def set_keyboard_shortcut(self, action: str, shortcut: str) -> None:
        """
        Set keyboard shortcut for an action.
        
        :param action: str - Action name.
        :param shortcut: str - Keyboard shortcut.
        """
        shortcuts = self.get('keyboard_shortcuts', {}).copy()
        shortcuts[action] = shortcut
        self.set('keyboard_shortcuts', shortcuts)
        logging.info(f"Keyboard shortcut for '{action}' set to '{shortcut}'")
    
    def export_preferences(self, file_path: str) -> None:
        """
        Export preferences to a JSON file.
        
        :param file_path: str - Path to export file.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2)
            logging.info(f"Preferences exported to {file_path}")
        except Exception as e:
            logging.error(f"Failed to export preferences: {e}")
    
    def import_preferences(self, file_path: str) -> None:
        """
        Import preferences from a JSON file.
        
        :param file_path: str - Path to import file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            # Validate imported preferences
            for key, value in imported.items():
                if key in self.DEFAULT_PREFERENCES:
                    if isinstance(value, type(self.DEFAULT_PREFERENCES[key])):
                        self.preferences[key] = value
                    else:
                        logging.warning(f"Invalid type for preference '{key}'")
            
            self.save_preferences()
            logging.info(f"Preferences imported from {file_path}")
        except Exception as e:
            logging.error(f"Failed to import preferences: {e}")
