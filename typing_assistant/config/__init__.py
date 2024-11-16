"""
Configuration settings for the Enhanced Typing Assistant application.
"""
import os
from pathlib import Path
from typing import Dict, Any
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
    'ENCRYPTION_KEY_LENGTH',
    'PASSWORD_MIN_LENGTH',
    'MAX_LOGIN_ATTEMPTS',
    'SESSION_TIMEOUT_MINUTES',
    'API_KEY_ROTATION_DAYS',
    'CACHE_SIZE',
    'CACHE_EXPIRY_MINUTES',
    'MAX_TEXT_LENGTH',
    'CORRECTION_DELAY_MS',
    'BATCH_SIZE',
    'DEFAULT_WINDOW_SIZE',
    'MIN_WINDOW_SIZE',
    'DEFAULT_FONT_SIZE',
    'MIN_FONT_SIZE',
    'MAX_FONT_SIZE',
    'THEMES',
    'FEATURES'
]
