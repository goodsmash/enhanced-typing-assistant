"""
Configuration settings for the Enhanced Typing Assistant application.
"""
import os
import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional
from appdirs import user_config_dir, user_cache_dir

# Application paths
APP_NAME = "TypingAssistant"
CONFIG_DIR = Path(user_config_dir(APP_NAME))
CACHE_DIR = Path(user_cache_dir(APP_NAME))
DATA_DIR = CONFIG_DIR / 'data'
LOGS_DIR = CONFIG_DIR / 'logs'
USER_DATA_DIR = CONFIG_DIR / 'user_data'

# Ensure directories exist
for directory in [CONFIG_DIR, CACHE_DIR, DATA_DIR, LOGS_DIR, USER_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File paths
LOG_FILE = LOGS_DIR / 'assistant.log'
USER_SETTINGS_FILE = USER_DATA_DIR / 'settings.json'
CONFIG_FILE = CONFIG_DIR / 'config.ini'
API_KEYS_FILE = CONFIG_DIR / '.env'

# Application settings
APP_VERSION = "2.0.0"
APP_AUTHOR = "Ryan McGinley"
APP_WEBSITE = "https://pepes.dev"
SUPPORT_EMAIL = "support@pepes.dev"
GITHUB_REPO = "https://github.com/goodsmash/typing_assistant"

# Security settings
ENCRYPTION_KEY_LENGTH = 32
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 3
SESSION_TIMEOUT_MINUTES = 30
API_KEY_ROTATION_DAYS = 90

# Performance settings
CACHE_SIZE = 1000
CACHE_EXPIRY_MINUTES = 60
MAX_TEXT_LENGTH = 10000
CORRECTION_DELAY_MS = 1500
BATCH_SIZE = 32

# UI settings
DEFAULT_WINDOW_SIZE = (1000, 800)
MIN_WINDOW_SIZE = (800, 600)
DEFAULT_FONT_SIZE = 14
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 48

# Theme configurations
THEMES = {
    'light': {
        'background': '#ffffff',
        'text': '#000000',
        'primary': '#007bff',
        'secondary': '#6c757d',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8'
    },
    'dark': {
        'background': '#1a1a1a',
        'text': '#ffffff',
        'primary': '#0d6efd',
        'secondary': '#6c757d',
        'success': '#198754',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#0dcaf0'
    }
}

# Feature flags
FEATURES = {
    'spell_check': True,
    'grammar_check': True,
    'style_check': True,
    'voice_input': True,
    'text_to_speech': True,
    'offline_mode': True,
    'auto_save': True,
    'dark_mode': False,
    'high_contrast': False,
    'keyboard_shortcuts': True
}

class ConfigManager:
    """Manages application configuration settings."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config = configparser.ConfigParser()
        self.load_config()
        
    def load_config(self) -> None:
        """Load configuration from the config file."""
        if CONFIG_FILE.exists():
            self.config.read(CONFIG_FILE)
        else:
            self._create_default_config()
            
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        self.config['General'] = {
            'theme': 'light',
            'font_size': str(DEFAULT_FONT_SIZE),
            'window_width': str(DEFAULT_WINDOW_SIZE[0]),
            'window_height': str(DEFAULT_WINDOW_SIZE[1])
        }
        
        self.config['Features'] = {key: str(value) for key, value in FEATURES.items()}
        
        self.save_config()
        
    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)
            
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration setting."""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
            
    def set_setting(self, section: str, key: str, value: Any) -> None:
        """Set a configuration setting."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()
        
    def get_theme(self) -> Dict[str, str]:
        """Get the current theme configuration."""
        theme_name = self.get_setting('General', 'theme', 'light')
        return THEMES.get(theme_name, THEMES['light'])
        
    def get_features(self) -> Dict[str, bool]:
        """Get the current feature flags."""
        features = {}
        if self.config.has_section('Features'):
            for key in FEATURES:
                value = self.get_setting('Features', key, str(FEATURES[key]))
                features[key] = value.lower() == 'true'
        else:
            features = FEATURES
        return features

__all__ = [
    'APP_NAME',
    'CONFIG_DIR',
    'CACHE_DIR',
    'DATA_DIR',
    'LOGS_DIR',
    'USER_DATA_DIR',
    'LOG_FILE',
    'USER_SETTINGS_FILE',
    'CONFIG_FILE',
    'API_KEYS_FILE',
    'APP_VERSION',
    'APP_AUTHOR',
    'APP_WEBSITE',
    'SUPPORT_EMAIL',
    'GITHUB_REPO',
    'THEMES',
    'FEATURES',
    'ConfigManager'
]
