"""Configuration management functionality."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import jwt
import logging

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration and secrets."""

    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / ".typing_assistant"
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / "key.bin"
        self.auth_file = self.config_dir / ".auth"
        self.config: Dict[str, Any] = {}
        self.auth_token = None
        self.token_expiry = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load or create encryption key
        self._load_or_create_key()
        
        # Load existing config or create default
        self.load()
        
        # Load authentication state
        self.load_auth_state()

    def _load_or_create_key(self) -> None:
        """Load existing encryption key or create a new one."""
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self.key)
        self.cipher = Fernet(self.key)

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted_data = self.cipher.decrypt(encrypted_data.encode())
                        self.config = json.loads(decrypted_data)
                    else:
                        self._create_default_config()
            except Exception as e:
                print(f"Error loading config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def save(self) -> None:
        """Save configuration to file."""
        try:
            encrypted_data = self.cipher.encrypt(json.dumps(self.config).encode())
            with open(self.config_file, "w") as f:
                f.write(encrypted_data.decode())
        except Exception as e:
            print(f"Error saving config: {e}")

    def _create_default_config(self) -> None:
        """Create default configuration."""
        self.config = {
            "api_key": "",
            "theme": "default",
            "high_contrast": False,
            "font_size": 12,
            "speech_rate": 200,
            "correction_mode": "standard",
            "correction_severity": 0.5,
            "language": "en_US",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 150,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        self.save()

    def get_api_key(self) -> str:
        """Get OpenAI API key."""
        return self.config.get("api_key", "")

    def set_api_key(self, api_key: str) -> None:
        """Set OpenAI API key."""
        self.config["api_key"] = api_key
        self.save()

    def get_theme(self) -> str:
        """Get current theme."""
        return self.config.get("theme", "default")

    def set_theme(self, theme: str) -> None:
        """Set current theme."""
        self.config["theme"] = theme
        self.save()

    def get_high_contrast(self) -> bool:
        """Get high contrast mode setting."""
        return self.config.get("high_contrast", False)

    def set_high_contrast(self, enabled: bool) -> None:
        """Set high contrast mode."""
        self.config["high_contrast"] = enabled
        self.save()

    def get_font_size(self) -> int:
        """Get font size."""
        return self.config.get("font_size", 12)

    def set_font_size(self, size: int) -> None:
        """Set font size."""
        self.config["font_size"] = size
        self.save()

    def get_speech_rate(self) -> int:
        """Get speech rate."""
        return self.config.get("speech_rate", 200)

    def set_speech_rate(self, rate: int) -> None:
        """Set speech rate."""
        self.config["speech_rate"] = rate
        self.save()

    def get_correction_mode(self) -> str:
        """Get text correction mode."""
        return self.config.get("correction_mode", "standard")

    def set_correction_mode(self, mode: str) -> None:
        """Set text correction mode."""
        self.config["correction_mode"] = mode
        self.save()

    def get_correction_severity(self) -> float:
        """Get correction severity."""
        return self.config.get("correction_severity", 0.5)

    def set_correction_severity(self, severity: float) -> None:
        """Set correction severity."""
        self.config["correction_severity"] = severity
        self.save()

    def get_language(self) -> str:
        """Get interface language."""
        return self.config.get("language", "en_US")

    def set_language(self, language: str) -> None:
        """Set interface language."""
        self.config["language"] = language
        self.save()

    def get_api_settings(self) -> Dict[str, Any]:
        """Get API connection settings."""
        return {
            "model": self.config.get("model", "gpt-3.5-turbo"),
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 150),
            "frequency_penalty": self.config.get("frequency_penalty", 0.0),
            "presence_penalty": self.config.get("presence_penalty", 0.0)
        }

    def set_api_settings(self, settings: Dict[str, Any]) -> None:
        """Set API connection settings."""
        valid_keys = ["model", "temperature", "max_tokens", "frequency_penalty", "presence_penalty"]
        for key, value in settings.items():
            if key in valid_keys:
                self.config[key] = value
        self.save()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated and token is valid."""
        try:
            if not self.auth_token or not self.token_expiry:
                return False
                
            if datetime.utcnow() > self.token_expiry:
                self.auth_token = None
                self.token_expiry = None
                self.save_auth_state()
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking authentication: {e}")
            return False

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user and get access token."""
        try:
            if not username or not password:
                return False
                
            # Verify password against stored hash
            if not self.verify_password(username, password):
                return False
                
            # Generate new token
            payload = {
                'sub': username,
                'exp': datetime.utcnow() + timedelta(days=1)
            }
            
            self.auth_token = jwt.encode(payload, self.key, algorithm='HS256')
            self.token_expiry = datetime.utcnow() + timedelta(days=1)
            
            self.save_auth_state()
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def save_auth_state(self) -> None:
        """Save authentication state securely."""
        try:
            if not self.auth_token:
                if self.auth_file.exists():
                    self.auth_file.unlink()
                return
                
            state = {
                'token': self.auth_token,
                'expiry': self.token_expiry.isoformat()
            }
            
            encrypted = self.cipher.encrypt(json.dumps(state).encode())
            with open(self.auth_file, 'wb') as f:
                f.write(encrypted)
                
        except Exception as e:
            logger.error(f"Error saving auth state: {e}")

    def load_auth_state(self) -> None:
        """Load authentication state."""
        try:
            if not self.auth_file.exists():
                return
                
            with open(self.auth_file, 'rb') as f:
                encrypted = f.read()
                
            decrypted = self.cipher.decrypt(encrypted)
            state = json.loads(decrypted)
            
            self.auth_token = state['token']
            self.token_expiry = datetime.fromisoformat(state['expiry'])
            
        except Exception as e:
            logger.error(f"Error loading auth state: {e}")
            self.auth_token = None
            self.token_expiry = None

    def verify_password(self, username: str, password: str) -> bool:
        """Verify password against stored hash."""
        try:
            user_file = self.config_dir / f"users/{username}.json"
            if not user_file.exists():
                return False
                
            with open(user_file, 'rb') as f:
                encrypted = f.read()
                
            decrypted = self.cipher.decrypt(encrypted)
            user_data = json.loads(decrypted)
            
            # NOTE: This is a placeholder for the actual password verification logic
            # You should replace this with your actual password verification logic
            return password == user_data['password_hash']
            
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
