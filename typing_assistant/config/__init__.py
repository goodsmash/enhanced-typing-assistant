"""Configuration package for the Enhanced Typing Assistant."""

from .config_manager import ConfigManager
from .default_config import (
    APP_NAME, APP_VERSION, APP_AUTHOR, APP_WEBSITE,
    THEMES, ACCESSIBILITY, ERROR_MESSAGES, API_CONFIG, FEATURES
)

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
    'FEATURES'
]
