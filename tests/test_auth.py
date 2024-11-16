import pytest
import sqlite3
from typing_assistant.ui.login_dialog import AuthManager
from cryptography.fernet import Fernet
import jwt
import time
from datetime import datetime, timedelta
from typing_assistant.utils.security import SecurityManager
from typing_assistant.config import (
    PASSWORD_MIN_LENGTH, MAX_LOGIN_ATTEMPTS,
    SESSION_TIMEOUT_MINUTES, ENCRYPTION_KEY_LENGTH
)

@pytest.fixture
def auth_manager(temp_db_path):
    return AuthManager(str(temp_db_path))

@pytest.fixture
def security_manager():
    """Create a SecurityManager instance for testing."""
    return SecurityManager()

class TestAuth:
    def test_user_registration(self, auth_manager):
        """Test user registration functionality."""
        username = "testuser"
        password = "TestPass123!"
        
        # Test successful registration
        success = auth_manager.register_user(username, password)
        assert success
        
        # Test duplicate registration
        success = auth_manager.register_user(username, password)
        assert not success

    def test_user_login(self, auth_manager):
        """Test user login functionality."""
        username = "testuser2"
        password = "TestPass123!"
        
        # Register user first
        auth_manager.register_user(username, password)
        
        # Test successful login
        success = auth_manager.login(username, password)
        assert success
        
        # Test wrong password
        success = auth_manager.login(username, "WrongPass123!")
        assert not success
        
        # Test non-existent user
        success = auth_manager.login("nonexistent", password)
        assert not success

    def test_password_hashing(self, auth_manager):
        """Test that passwords are properly hashed."""
        username = "testuser3"
        password = "TestPass123!"
        
        auth_manager.register_user(username, password)
        
        # Check that password is hashed in database
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        stored_password = cursor.fetchone()[0]
        conn.close()
        assert stored_password != password
        assert len(stored_password) == 64  # SHA-256 hash length

def test_password_validation(security_manager):
    """Test password validation rules."""
    # Test minimum length
    assert not security_manager.validate_password("short")
    assert security_manager.validate_password("validpassword123")
    
    # Test complexity requirements
    assert not security_manager.validate_password("onlylowercase")
    assert not security_manager.validate_password("ONLYUPPERCASE")
    assert not security_manager.validate_password("123456789")
    assert security_manager.validate_password("Valid123!")

def test_password_hashing(security_manager):
    """Test password hashing functionality."""
    password = "TestPassword123!"
    hashed = security_manager.hash_password(password)
    
    # Test hash properties
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert hashed != password
    
    # Test verification
    assert security_manager.verify_password(password, hashed)
    assert not security_manager.verify_password("WrongPassword123!", hashed)

def test_token_generation(security_manager):
    """Test JWT token generation and validation."""
    user_data = {"user_id": 1, "username": "testuser"}
    token = security_manager.generate_token(user_data)
    
    # Test token properties
    assert isinstance(token, str)
    decoded = jwt.decode(token, security_manager.secret_key, algorithms=["HS256"])
    assert decoded["user_id"] == user_data["user_id"]
    assert decoded["username"] == user_data["username"]
    assert "exp" in decoded

def test_token_expiration(security_manager):
    """Test token expiration handling."""
    user_data = {"user_id": 1, "username": "testuser"}
    
    # Test expired token
    token = security_manager.generate_token(user_data, expires_in=1)
    time.sleep(2)  # Wait for token to expire
    with pytest.raises(jwt.ExpiredSignatureError):
        security_manager.validate_token(token)
    
    # Test valid token
    token = security_manager.generate_token(user_data)
    decoded = security_manager.validate_token(token)
    assert decoded["user_id"] == user_data["user_id"]

def test_api_key_management(security_manager):
    """Test API key management."""
    api_key = security_manager.generate_api_key()
    encrypted = security_manager.encrypt_api_key(api_key)
    decrypted = security_manager.decrypt_api_key(encrypted)
    
    assert isinstance(api_key, str)
    assert len(api_key) >= 32
    assert encrypted != api_key
    assert decrypted == api_key

def test_login_attempts(security_manager):
    """Test login attempt tracking."""
    username = "testuser"
    
    # Test failed attempts tracking
    for _ in range(MAX_LOGIN_ATTEMPTS - 1):
        assert not security_manager.is_account_locked(username)
        security_manager.record_failed_attempt(username)
    
    # Test account lockout
    security_manager.record_failed_attempt(username)
    assert security_manager.is_account_locked(username)
    
    # Test lockout expiration
    security_manager.failed_attempts[username]["timestamp"] = (
        datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES + 1)
    )
    assert not security_manager.is_account_locked(username)

def test_encryption_key_generation(security_manager):
    """Test encryption key generation."""
    key = security_manager.generate_encryption_key()
    assert isinstance(key, bytes)
    assert len(key) == ENCRYPTION_KEY_LENGTH

def test_secure_string_operations(security_manager):
    """Test secure string operations."""
    test_string = "sensitive_data"
    encrypted = security_manager.encrypt_string(test_string)
    decrypted = security_manager.decrypt_string(encrypted)
    
    assert encrypted != test_string
    assert decrypted == test_string
    
    # Test with empty string
    assert security_manager.encrypt_string("") == ""
    assert security_manager.decrypt_string("") == ""

def test_session_management(security_manager):
    """Test session management."""
    session = security_manager.create_session("testuser")
    
    assert "token" in session
    assert "created_at" in session
    assert security_manager.validate_session(session["token"])
    
    # Test session timeout
    session["created_at"] = datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES + 1)
    assert not security_manager.validate_session(session["token"])

def test_password_reset(security_manager):
    """Test password reset functionality."""
    reset_token = security_manager.generate_password_reset_token("testuser")
    assert security_manager.validate_reset_token(reset_token)
    
    # Test token expiration
    time.sleep(2)
    expired_token = security_manager.generate_password_reset_token("testuser", expires_in=1)
    assert not security_manager.validate_reset_token(expired_token)
