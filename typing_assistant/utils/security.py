"""
Security utilities for the Enhanced Typing Assistant.
Handles encryption, API key management, and secure storage.
"""
import base64
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

from ..config import (
    API_KEYS_FILE,
    ENCRYPTION_KEY_LENGTH,
    PASSWORD_MIN_LENGTH,
    MAX_LOGIN_ATTEMPTS,
    SESSION_TIMEOUT_MINUTES
)

class SecurityManager:
    """Manages security-related functionality."""
    
    def __init__(self):
        self._fernet = None
        self._session_start = None
        self._login_attempts = 0
        self._load_env()

    def _load_env(self) -> None:
        """Load environment variables."""
        if API_KEYS_FILE.exists():
            load_dotenv(API_KEYS_FILE)

    def initialize_encryption(self, password: str) -> bool:
        """Initialize encryption with a password."""
        try:
            if len(password) < PASSWORD_MIN_LENGTH:
                raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
            
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            self._fernet = Fernet(key)
            self._session_start = datetime.now()
            self._login_attempts = 0
            return True
        except Exception as e:
            print(f"Encryption initialization failed: {e}")
            return False

    def is_session_valid(self) -> bool:
        """Check if the current session is valid."""
        if not self._session_start:
            return False
        return (datetime.now() - self._session_start) < timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    def refresh_session(self) -> None:
        """Refresh the session timeout."""
        if self._session_start:
            self._session_start = datetime.now()

    def encrypt_api_key(self, api_key: str) -> Optional[str]:
        """Encrypt an API key."""
        if not self._fernet or not self.is_session_valid():
            return None
        try:
            return self._fernet.encrypt(api_key.encode()).decode()
        except Exception as e:
            print(f"API key encryption failed: {e}")
            return None

    def decrypt_api_key(self, encrypted_key: str) -> Optional[str]:
        """Decrypt an API key."""
        if not self._fernet or not self.is_session_valid():
            return None
        try:
            return self._fernet.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            print(f"API key decryption failed: {e}")
            return None

    def save_api_key(self, api_key: str) -> bool:
        """Securely save an API key."""
        try:
            encrypted_key = self.encrypt_api_key(api_key)
            if not encrypted_key:
                return False

            env_content = f"OPENAI_API_KEY='{encrypted_key}'\n"
            
            # Create directory if it doesn't exist
            API_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(API_KEYS_FILE, 'w') as f:
                f.write(env_content)
            
            return True
        except Exception as e:
            print(f"Failed to save API key: {e}")
            return False

    def load_api_key(self) -> Optional[str]:
        """Load and decrypt the API key."""
        try:
            if not API_KEYS_FILE.exists():
                return None

            load_dotenv(API_KEYS_FILE)
            encrypted_key = os.getenv('OPENAI_API_KEY')
            
            if not encrypted_key:
                return None

            return self.decrypt_api_key(encrypted_key)
        except Exception as e:
            print(f"Failed to load API key: {e}")
            return None

    def verify_password(self, password: str) -> bool:
        """Verify the user's password."""
        if self._login_attempts >= MAX_LOGIN_ATTEMPTS:
            raise ValueError("Account locked due to too many failed attempts")

        success = self.initialize_encryption(password)
        if not success:
            self._login_attempts += 1
        return success

    def logout(self) -> None:
        """Clear the current session."""
        self._fernet = None
        self._session_start = None

    @staticmethod
    def generate_secure_token() -> str:
        """Generate a secure random token."""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()

    @staticmethod
    def hash_password(password: str) -> str:
        """Create a secure hash of a password."""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        return base64.b64encode(salt + key).decode()

    @staticmethod
    def verify_password_hash(password: str, hash_str: str) -> bool:
        """Verify a password against its hash."""
        try:
            hash_bytes = base64.b64decode(hash_str)
            salt = hash_bytes[:32]
            key = hash_bytes[32:]
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt,
                100000
            )
            return key == new_key
        except Exception:
            return False
