"""Configuration manager for the Enhanced Typing Assistant."""
import os
import json
import logging
import configparser
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from appdirs import user_config_dir, user_cache_dir
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration, API keys, and authentication."""
    
    def __init__(self):
        """Initialize configuration manager."""
        try:
            self.app_name = "TypingAssistant"
            self.config_dir = Path(user_config_dir(self.app_name))
            self.cache_dir = Path(user_cache_dir(self.app_name))
            self.config_file = self.config_dir / "config.ini"
            self.key_file = self.config_dir / ".keyfile"
            self.offline_file = self.config_dir / "offline_mode"
            
            # Ensure directories exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize configuration
            self.config = configparser.ConfigParser()
            self.load_config()
            
            # Initialize encryption
            self._init_encryption()
            
            # Load or initialize auth state
            self.auth_token = None
            self.token_expiry = None
            self.load_auth_state()
            
        except Exception as e:
            logger.error(f"Failed to initialize configuration: {e}")
            raise RuntimeError("Failed to initialize configuration") from e

    def _init_encryption(self):
        """Initialize encryption for sensitive data."""
        try:
            if not self.key_file.exists():
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
            with open(self.key_file, 'rb') as f:
                key = f.read()
            self.cipher = Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise

    def load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                self.config.read(self.config_file)
            except Exception as e:
                logger.error(f"Error reading config file: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration."""
        self.config['General'] = {
            'theme': 'light',
            'font_size': '12',
            'auto_correct': 'true',
            'language': 'en_US'
        }
        self.config['API'] = {
            'model': 'gpt-4',
            'temperature': '0.3',
            'max_tokens': '1000'
        }
        self.config['Performance'] = {
            'cache_size': '1000',
            'batch_size': '32',
            'correction_delay': '1500'
        }
        self.save_config()

    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            raise

    def get_api_key(self) -> Optional[str]:
        """Get API key from secure storage."""
        try:
            if not self.is_offline_mode():
                api_key_file = self.config_dir / ".api_key"
                if api_key_file.exists():
                    with open(api_key_file, 'rb') as f:
                        encrypted_key = f.read()
                    return self.cipher.decrypt(encrypted_key).decode()
            return None
        except Exception as e:
            logger.error(f"Error retrieving API key: {e}")
            return None

    def set_api_key(self, api_key: str):
        """Securely store API key."""
        try:
            api_key_file = self.config_dir / ".api_key"
            encrypted_key = self.cipher.encrypt(api_key.encode())
            with open(api_key_file, 'wb') as f:
                f.write(encrypted_key)
        except Exception as e:
            logger.error(f"Error storing API key: {e}")
            raise

    def clear_api_key(self):
        """Remove stored API key."""
        try:
            api_key_file = self.config_dir / ".api_key"
            if api_key_file.exists():
                api_key_file.unlink()
        except Exception as e:
            logger.error(f"Error clearing API key: {e}")
            raise

    def is_offline_mode(self) -> bool:
        """Check if offline mode is enabled."""
        return self.offline_file.exists()

    def set_offline_mode(self, enabled: bool):
        """Set offline mode."""
        try:
            if enabled:
                # Create offline mode marker file
                self.offline_file.touch()
                # Clear API key when going offline
                self.clear_api_key()
                logger.info("Offline mode enabled")
            else:
                # Remove offline mode marker file if it exists
                if self.offline_file.exists():
                    self.offline_file.unlink()
                logger.info("Offline mode disabled")
        except Exception as e:
            logger.error(f"Error setting offline mode: {e}")
            raise

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user and get access token."""
        try:
            # In offline mode, use simplified authentication
            if self.is_offline_mode():
                self.auth_token = "offline_token"
                self.token_expiry = datetime.now() + timedelta(days=30)
                self.save_auth_state()
                return True
                
            # TODO: Implement proper authentication with server
            # For now, use basic authentication
            if username and password:
                self.auth_token = "temp_token"
                self.token_expiry = datetime.now() + timedelta(hours=24)
                self.save_auth_state()
                return True
            return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated and token is valid."""
        if self.is_offline_mode():
            return True
        return (
            self.auth_token is not None and
            self.token_expiry is not None and
            datetime.now() < self.token_expiry
        )

    def logout(self):
        """Clear authentication state."""
        self.auth_token = None
        self.token_expiry = None
        self.save_auth_state()

    def save_auth_state(self):
        """Save authentication state securely."""
        try:
            auth_file = self.config_dir / ".auth"
            auth_data = {
                "token": self.auth_token,
                "expiry": self.token_expiry.isoformat() if self.token_expiry else None
            }
            encrypted_data = self.cipher.encrypt(json.dumps(auth_data).encode())
            with open(auth_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Error saving auth state: {e}")

    def load_auth_state(self):
        """Load authentication state."""
        try:
            auth_file = self.config_dir / ".auth"
            if auth_file.exists():
                with open(auth_file, 'rb') as f:
                    encrypted_data = f.read()
                auth_data = json.loads(self.cipher.decrypt(encrypted_data).decode())
                self.auth_token = auth_data.get("token")
                expiry_str = auth_data.get("expiry")
                self.token_expiry = datetime.fromisoformat(expiry_str) if expiry_str else None
        except Exception as e:
            logger.error(f"Error loading auth state: {e}")
            self.auth_token = None
            self.token_expiry = None

    def get_setting(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration setting."""
        try:
            return self.config.get(section, key, fallback=fallback)
        except Exception as e:
            logger.error(f"Error getting setting {section}.{key}: {e}")
            return fallback

    def set_setting(self, section: str, key: str, value: Any):
        """Set configuration setting."""
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = str(value)
            self.save_config()
        except Exception as e:
            logger.error(f"Error setting {section}.{key}: {e}")
            raise

    def get_api_settings(self) -> Dict[str, Any]:
        """Get all API-related settings."""
        return {
            'model': self.get_setting('API', 'model', 'gpt-4'),
            'temperature': float(self.get_setting('API', 'temperature', '0.3')),
            'max_tokens': int(self.get_setting('API', 'max_tokens', '1000'))
        }

    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self._create_default_config()
        if self.is_offline_mode():
            self.set_offline_mode(False)
        self.clear_api_key()
        self.logout()
