import os
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path

class ConfigManager:
    """Manages application configuration with support for multiple environments."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config: Dict[str, Any] = {}
        self.default_config_path = os.path.join(config_dir, "default_config.json")
        self.user_config_path = os.path.join(config_dir, "user_config.json")
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from default and user config files."""
        try:
            # Load default config
            if os.path.exists(self.default_config_path):
                with open(self.default_config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                logging.warning(f"Default config file not found: {self.default_config_path}")
            
            # Override with user config if exists
            if os.path.exists(self.user_config_path):
                with open(self.user_config_path, 'r') as f:
                    user_config = json.load(f)
                    self._deep_update(self.config, user_config)
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            raise

    def save_user_config(self) -> None:
        """Save current configuration to user config file."""
        try:
            os.makedirs(os.path.dirname(self.user_config_path), exist_ok=True)
            with open(self.user_config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving user configuration: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value

    def reset_to_default(self) -> None:
        """Reset configuration to default values."""
        if os.path.exists(self.default_config_path):
            with open(self.default_config_path, 'r') as f:
                self.config = json.load(f)
            if os.path.exists(self.user_config_path):
                os.remove(self.user_config_path)

    def _deep_update(self, d: dict, u: dict) -> dict:
        """Recursively update nested dictionaries."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def export_config(self, filepath: str) -> None:
        """Export current configuration to a file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Error exporting configuration: {e}")
            raise

    def import_config(self, filepath: str) -> None:
        """Import configuration from a file."""
        try:
            with open(filepath, 'r') as f:
                imported_config = json.load(f)
                self.config = imported_config
                self.save_user_config()
        except Exception as e:
            logging.error(f"Error importing configuration: {e}")
            raise

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        return self.config.get(section, {})

    def validate_config(self) -> bool:
        """Validate the current configuration against schema."""
        # TODO: Implement configuration validation
        return True
