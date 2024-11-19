"""Configuration manager for the Typing Assistant application."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from . import (
    APP_DIR, CONFIG_DIR, CONFIG_FILE, API_KEYS_FILE,
    DEFAULT_CONFIG, ERROR_MESSAGES
)

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration."""

    def __init__(self):
        """Initialize the configuration manager."""
        self._config: Dict[str, Any] = {}
        self._api_keys: Dict[str, str] = {}
        self.load_config()
        self.load_api_keys()

    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    self._config = json.load(f)
            else:
                self._config = DEFAULT_CONFIG.copy()
                self.save_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._config = DEFAULT_CONFIG.copy()

    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def load_api_keys(self) -> None:
        """Load API keys from file."""
        try:
            if API_KEYS_FILE.exists():
                with open(API_KEYS_FILE, 'r') as f:
                    self._api_keys = json.load(f)
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            self._api_keys = {"openai": "", "anthropic": ""}

    def save_api_keys(self) -> None:
        """Save API keys to file."""
        try:
            with open(API_KEYS_FILE, 'w') as f:
                json.dump(self._api_keys, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving API keys: {e}")

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        try:
            value = self._config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        try:
            keys = key.split('.')
            config = self._config
            for k in keys[:-1]:
                config = config.setdefault(k, {})
            config[keys[-1]] = value
            self.save_config()
        except Exception as e:
            logger.error(f"Error setting configuration {key}: {e}")

    def get_api_key(self, service: str) -> Optional[str]:
        """Get an API key."""
        return self._api_keys.get(service)

    def set_api_key(self, service: str, key: str) -> None:
        """Set an API key."""
        try:
            self._api_keys[service] = key
            self.save_api_keys()
        except Exception as e:
            logger.error(f"Error setting API key for {service}: {e}")

    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        self._config = DEFAULT_CONFIG.copy()
        self.save_config()

    def get_all_config(self) -> Dict[str, Any]:
        """Get entire configuration."""
        return self._config.copy()

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        try:
            self._config.update(new_config)
            self.save_config()
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")

    def validate_config(self) -> bool:
        """Validate configuration structure."""
        try:
            required_keys = set(DEFAULT_CONFIG.keys())
            current_keys = set(self._config.keys())
            return required_keys.issubset(current_keys)
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False

    def get_error_message(self, key: str) -> str:
        """Get an error message."""
        return ERROR_MESSAGES.get(key, ERROR_MESSAGES['unknown_error'])
