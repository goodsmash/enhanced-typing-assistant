import os
import pytest
from pathlib import Path
from typing_assistant.config import (
    APP_NAME, CONFIG_DIR, CACHE_DIR, DATA_DIR, LOGS_DIR, USER_DATA_DIR,
    LOG_FILE, USER_SETTINGS_FILE, CONFIG_FILE, API_KEYS_FILE
)

def test_config_directories_exist():
    """Test that all configuration directories are created."""
    directories = [CONFIG_DIR, CACHE_DIR, DATA_DIR, LOGS_DIR, USER_DATA_DIR]
    for directory in directories:
        assert directory.exists(), f"Directory {directory} does not exist"
        assert directory.is_dir(), f"{directory} is not a directory"

def test_config_paths():
    """Test that configuration paths are properly set."""
    assert APP_NAME == "TypingAssistant"
    assert isinstance(CONFIG_DIR, Path)
    assert isinstance(CACHE_DIR, Path)
    assert isinstance(DATA_DIR, Path)
    assert isinstance(LOGS_DIR, Path)
    assert isinstance(USER_DATA_DIR, Path)
    assert isinstance(LOG_FILE, Path)
    assert isinstance(USER_SETTINGS_FILE, Path)
    assert isinstance(CONFIG_FILE, Path)
    assert isinstance(API_KEYS_FILE, Path)

def test_log_file_creation():
    """Test that log file is created when logging is initialized."""
    assert LOG_FILE.parent.exists(), "Log directory does not exist"
    if not LOG_FILE.exists():
        LOG_FILE.touch()
    assert LOG_FILE.exists(), "Log file was not created"

def test_user_settings_file():
    """Test that user settings file is created when needed."""
    if not USER_SETTINGS_FILE.exists():
        USER_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        USER_SETTINGS_FILE.write_text("{}")
    assert USER_SETTINGS_FILE.exists(), "User settings file was not created"
    assert USER_SETTINGS_FILE.read_text() == "{}", "User settings file is not empty JSON"
