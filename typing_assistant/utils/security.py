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

import logging
logger = logging.getLogger(__name__)

class SecurityManager:
    """Manages security-related functionality."""
    
    def __init__(self):
        self._fernet = None
        self._session_start = None
        self._login_attempts = 0
        self._load_env()
        
    def _load_env(self):
        """Load environment variables."""
        try:
            load_dotenv(API_KEYS_FILE)
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
            
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
            logger.error(f"Encryption initialization failed: {e}")
            return False
            
    def verify_password(self, password: str) -> bool:
        """Verify the user's password."""
        if self._login_attempts >= MAX_LOGIN_ATTEMPTS:
            raise ValueError("Account locked due to too many failed attempts")

        success = self.initialize_encryption(password)
        if not success:
            self._login_attempts += 1
        return success
        
    def hash_password(self, password: str) -> str:
        """Create a secure hash of a password."""
        try:
            if len(password) < PASSWORD_MIN_LENGTH:
                raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
                
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt,
                100000  # Number of iterations
            )
            
            # Combine salt and key
            return base64.b64encode(salt + key).decode()
            
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
            
    def check_password(self, password: str, hash_str: str) -> bool:
        """Check if a password matches its hash."""
        try:
            # Decode the stored hash
            hash_bytes = base64.b64decode(hash_str)
            salt = hash_bytes[:32]  # First 32 bytes are salt
            stored_key = hash_bytes[32:]  # Rest is the key
            
            # Hash the provided password with the same salt
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt,
                100000  # Same number of iterations as in hash_password
            )
            
            # Compare in constant time
            return stored_key == new_key
            
        except Exception as e:
            logger.error(f"Error checking password: {e}")
            return False
            
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt data."""
        if not self._fernet:
            raise ValueError("Encryption not initialized")
            
        try:
            return self._fernet.encrypt(data.encode())
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
            
    def decrypt_data(self, encrypted: bytes) -> str:
        """Decrypt data."""
        if not self._fernet:
            raise ValueError("Encryption not initialized")
            
        try:
            return self._fernet.decrypt(encrypted).decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
            
    def is_session_valid(self) -> bool:
        """Check if the current session is valid."""
        if not self._session_start:
            return False
            
        session_age = datetime.now() - self._session_start
        return session_age.total_seconds() < (SESSION_TIMEOUT_MINUTES * 60)
        
    def reset_session(self):
        """Reset the current session."""
        self._session_start = None
        self._fernet = None
        self._login_attempts = 0
        
    def store_api_key(self, api_key: str):
        """Securely store an API key."""
        try:
            if not api_key:
                return
                
            # Create a new encryption key for API storage
            encryption_key = Fernet.generate_key()
            cipher = Fernet(encryption_key)
            
            # Encrypt the API key
            encrypted_key = cipher.encrypt(api_key.encode())
            
            # Save both the encryption key and encrypted API key
            with open(API_KEYS_FILE, 'wb') as f:
                f.write(encryption_key + b'\n' + encrypted_key)
                
        except Exception as e:
            logger.error(f"Error storing API key: {e}")
            raise
            
    def get_api_key(self) -> Optional[str]:
        """Retrieve the stored API key."""
        try:
            if not os.path.exists(API_KEYS_FILE):
                return None
                
            with open(API_KEYS_FILE, 'rb') as f:
                encryption_key = f.readline().strip()
                encrypted_key = f.readline().strip()
                
            cipher = Fernet(encryption_key)
            return cipher.decrypt(encrypted_key).decode()
            
        except Exception as e:
            logger.error(f"Error retrieving API key: {e}")
            return None
