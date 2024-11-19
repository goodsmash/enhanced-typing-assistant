"""Configuration package for the Enhanced Typing Assistant."""

from .config_manager import ConfigManager
from .default_config import (
    APP_NAME, APP_VERSION, APP_AUTHOR, APP_WEBSITE,
    THEMES, ACCESSIBILITY, ERROR_MESSAGES, API_CONFIG, FEATURES
)

"""Configuration module for the Typing Assistant application."""

import os
from pathlib import Path

# Base paths
APP_DIR = Path.home() / ".typing_assistant"
CONFIG_DIR = APP_DIR / "config"
CACHE_DIR = APP_DIR / "cache"
LOG_DIR = APP_DIR / "logs"
DATA_DIR = APP_DIR / "data"

# File paths
CONFIG_FILE = CONFIG_DIR / "config.json"
API_KEYS_FILE = CONFIG_DIR / "api_keys.json"
CACHE_FILE = CACHE_DIR / "correction_cache.db"
LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"
USER_DATA_FILE = DATA_DIR / "user_data.json"

# Create directories if they don't exist
for directory in [CONFIG_DIR, CACHE_DIR, LOG_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "correction": {
        "delay": 200,
        "severity": "medium",
        "auto_correct": True,
        "language": "en"
    },
    "accessibility": {
        "high_contrast": False,
        "large_text": False,
        "dyslexic_font": False,
        "text_to_speech": False,
        "break_reminders": True,
        "keyboard_shortcuts": True
    },
    "api": {
        "rate_limit": 3,
        "timeout": 10
    }
}

# Create default config file if it doesn't exist
if not CONFIG_FILE.exists():
    import json
    with open(CONFIG_FILE, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)

# Create API keys file if it doesn't exist
if not API_KEYS_FILE.exists():
    import json
    with open(API_KEYS_FILE, 'w') as f:
        json.dump({
            "openai": "",
            "anthropic": ""
        }, f, indent=4)

__all__ = [
    'ConfigManager',
    'APP_NAME',
    'APP_VERSION',
    'APP_AUTHOR',
    'APP_WEBSITE',
    'THEMES',
    'ACCESSIBILITY',
    'ERROR_MESSAGES',
    'API_CONFIG',
    'FEATURES',
    'APP_DIR',
    'CONFIG_DIR',
    'CACHE_DIR',
    'LOG_DIR',
    'DATA_DIR',
    'CONFIG_FILE',
    'API_KEYS_FILE',
    'CACHE_FILE',
    'LOG_FILE',
    'ERROR_LOG_FILE',
    'USER_DATA_FILE',
    'DEFAULT_CONFIG'
]
