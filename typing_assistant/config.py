"""
Configuration settings for the Enhanced Typing Assistant application.
"""
import os
from pathlib import Path
from typing import Dict, Any
from appdirs import user_config_dir, user_cache_dir

# Application paths
APP_NAME = "TypingAssistant"
CONFIG_DIR = Path(user_config_dir(APP_NAME))
CACHE_DIR = Path(user_cache_dir(APP_NAME))
DATA_DIR = CONFIG_DIR / 'data'
LOGS_DIR = CONFIG_DIR / 'logs'
USER_DATA_DIR = CONFIG_DIR / 'user_data'

# Ensure directories exist
for directory in [CONFIG_DIR, CACHE_DIR, DATA_DIR, LOGS_DIR, USER_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File paths
LOG_FILE = LOGS_DIR / 'assistant.log'
USER_SETTINGS_FILE = USER_DATA_DIR / 'settings.json'
CONFIG_FILE = CONFIG_DIR / 'config.ini'
API_KEYS_FILE = CONFIG_DIR / '.env'

# Application settings
APP_VERSION = "2.0.0"
APP_AUTHOR = "Ryan McGinley"
APP_WEBSITE = "https://pepes.dev"
SUPPORT_EMAIL = "support@pepes.dev"
GITHUB_REPO = "https://github.com/goodsmash/typing_assistant"

# Security settings
ENCRYPTION_KEY_LENGTH = 32
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 3
SESSION_TIMEOUT_MINUTES = 30
API_KEY_ROTATION_DAYS = 90

# Performance settings
CACHE_SIZE = 1000
CACHE_EXPIRY_MINUTES = 60
MAX_TEXT_LENGTH = 10000
CORRECTION_DELAY_MS = 1500
BATCH_SIZE = 32

# UI settings
DEFAULT_WINDOW_SIZE = (1000, 800)
MIN_WINDOW_SIZE = (800, 600)
DEFAULT_FONT_SIZE = 14
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 48

# Theme configurations
THEMES = {
    'light': {
        'background': '#ffffff',
        'text': '#000000',
        'primary': '#007bff',
        'secondary': '#6c757d',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8'
    },
    'dark': {
        'background': '#1a1a1a',
        'text': '#ffffff',
        'primary': '#0d6efd',
        'secondary': '#6c757d',
        'success': '#198754',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#0dcaf0'
    },
    'high_contrast': {
        'background': '#000000',
        'text': '#ffffff',
        'primary': '#ffff00',
        'secondary': '#00ffff',
        'success': '#00ff00',
        'error': '#ff0000',
        'warning': '#ffaa00',
        'info': '#00ffff'
    },
    'colorblind': {
        'background': '#ffffff',
        'text': '#000000',
        'primary': '#0077bb',
        'secondary': '#ee7733',
        'success': '#009988',
        'error': '#cc3311',
        'warning': '#ee3377',
        'info': '#33bbee'
    }
}

# Accessibility settings
ACCESSIBILITY = {
    'screen_reader_support': True,
    'keyboard_navigation': True,
    'high_contrast_mode': False,
    'animation_reduced': False,
    'dyslexic_font': False,
    'font_scaling': 1.0,
    'cursor_size': 1.0,
    'auto_complete': True,
    'word_prediction': True,
    'text_to_speech': True,
    'speech_to_text': True
}

# Error messages
ERROR_MESSAGES = {
    'api_key_missing': 'OpenAI API key is required. Please enter your API key in Settings.',
    'api_key_invalid': 'Invalid API key. Please check your API key in Settings.',
    'network_error': 'Network error. Please check your internet connection.',
    'text_too_long': 'Text exceeds maximum length. Please reduce the text length.',
    'invalid_input': 'Invalid input. Please check your text.',
    'processing_error': 'Error processing text. Please try again.',
    'file_save_error': 'Error saving file. Please check permissions.',
    'file_load_error': 'Error loading file. Please check if file exists.',
    'invalid_password': 'Invalid password. Please try again.',
    'account_locked': 'Account locked due to too many failed attempts.',
    'session_expired': 'Session expired. Please log in again.',
    'update_failed': 'Failed to check for updates. Please try again later.'
}

# API configurations
API_CONFIG = {
    'openai': {
        'model': 'gpt-4',
        'temperature': 0.3,
        'max_tokens': 1000,
        'timeout': 30,
        'retry_attempts': 3,
        'retry_delay': 1
    },
    'speech_recognition': {
        'timeout': 5,
        'phrase_time_limit': 15,
        'language': 'en-US'
    }
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(LOG_FILE),
            'formatter': 'standard',
            'level': 'INFO',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Update checking
UPDATE_CONFIG = {
    'check_frequency_days': 7,
    'api_endpoint': f'{GITHUB_REPO}/releases/latest',
    'download_url': f'{GITHUB_REPO}/releases/download/',
    'changelog_url': f'{GITHUB_REPO}/blob/main/CHANGELOG.md'
}

# Feature flags
FEATURES = {
    'spell_check': True,
    'grammar_check': True,
    'style_check': True,
    'voice_input': True,
    'voice_output': True,
    'auto_save': True,
    'cloud_sync': False,
    'analytics': False,
    'beta_features': False
}

# Language support
SUPPORTED_LANGUAGES = {
    'en': {
        'name': 'English',
        'code': 'en-US',
        'spellcheck': True,
        'grammar': True,
        'voice': True
    },
    'es': {
        'name': 'Spanish',
        'code': 'es-ES',
        'spellcheck': True,
        'grammar': True,
        'voice': True
    },
    'fr': {
        'name': 'French',
        'code': 'fr-FR',
        'spellcheck': True,
        'grammar': True,
        'voice': True
    },
    # Add more languages as needed
}

# Privacy settings
PRIVACY_SETTINGS = {
    'data_collection': False,
    'crash_reports': True,
    'usage_statistics': False,
    'cloud_backup': False,
    'personalization': True,
    'third_party_integration': False
}

# Default user settings
DEFAULT_USER_SETTINGS = {
    'theme': 'light',
    'language': 'en',
    'font_size': DEFAULT_FONT_SIZE,
    'auto_correct': True,
    'spell_check': True,
    'voice_feedback': True,
    'accessibility': ACCESSIBILITY.copy(),
    'privacy': PRIVACY_SETTINGS.copy()
}

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
            raise RuntimeError("Failed to initialize configuration") from e

    def _init_encryption(self):
        """Initialize encryption for sensitive data."""
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    self.key = f.read()
            else:
                self.key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(self.key)
            
            self.cipher = Fernet(self.key)
            
        except Exception as e:
            raise

    def load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file)
            else:
                self._create_default_config()
                
        except Exception as e:
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration."""
        self.config['General'] = {
            'offline_mode': 'false',
            'correction_mode': 'standard',
            'correction_severity': '0.5',
            'language': 'en_US'
        }
        
        self.config['API'] = {
            'api_url': 'https://api.openai.com/v1',
            'model': 'gpt-3.5-turbo',
            'max_tokens': '150',
            'temperature': '0.3'
        }
        
        self.config['UI'] = {
            'theme': 'light',
            'font_size': '12',
            'high_contrast': 'false',
            'screen_reader': 'false'
        }
        
        self.save_config()

    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
                
        except Exception as e:
            raise

    def get_api_key(self) -> Optional[str]:
        """Get API key from secure storage."""
        try:
            return keyring.get_password(self.app_name, "api_key")
        except Exception as e:
            return None

    def set_api_key(self, api_key: str):
        """Securely store API key."""
        try:
            keyring.set_password(self.app_name, "api_key", api_key)
        except Exception as e:
            raise

    def clear_api_key(self):
        """Remove stored API key."""
        try:
            keyring.delete_password(self.app_name, "api_key")
        except Exception as e:
            raise

    def is_offline_mode(self) -> bool:
        """Check if offline mode is enabled."""
        return self.config.getboolean('General', 'offline_mode', fallback=False)

    def set_offline_mode(self, enabled: bool):
        """Set offline mode."""
        self.config['General']['offline_mode'] = str(enabled).lower()
        self.save_config()

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user and get access token."""
        try:
            # TODO: Implement proper authentication server
            # For now, using simple JWT for demo
            if not username or not password:
                return False
                
            payload = {
                'sub': username,
                'exp': datetime.utcnow() + timedelta(days=1)
            }
            
            self.auth_token = jwt.encode(payload, self.key, algorithm='HS256')
            self.token_expiry = datetime.utcnow() + timedelta(days=1)
            
            self.save_auth_state()
            return True
            
        except Exception as e:
            return False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated and token is valid."""
        try:
            if not self.auth_token or not self.token_expiry:
                return False
                
            if datetime.utcnow() > self.token_expiry:
                return False
                
            return True
            
        except Exception as e:
            return False

    def logout(self):
        """Clear authentication state."""
        try:
            self.auth_token = None
            self.token_expiry = None
            self.save_auth_state()
            
        except Exception as e:
            raise

    def save_auth_state(self):
        """Save authentication state securely."""
        try:
            if self.auth_token and self.token_expiry:
                state = {
                    'token': self.auth_token,
                    'expiry': self.token_expiry.isoformat()
                }
                encrypted = self.cipher.encrypt(json.dumps(state).encode())
                
                with open(self.config_dir / '.auth', 'wb') as f:
                    f.write(encrypted)
            else:
                # Remove auth file if exists
                auth_file = self.config_dir / '.auth'
                if auth_file.exists():
                    auth_file.unlink()
                    
        except Exception as e:
            raise

    def load_auth_state(self):
        """Load authentication state."""
        try:
            auth_file = self.config_dir / '.auth'
            if not auth_file.exists():
                return
                
            with open(auth_file, 'rb') as f:
                encrypted = f.read()
                
            decrypted = self.cipher.decrypt(encrypted)
            state = json.loads(decrypted)
            
            self.auth_token = state['token']
            self.token_expiry = datetime.fromisoformat(state['expiry'])
            
        except Exception as e:
            self.auth_token = None
            self.token_expiry = None

    def get_setting(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration setting."""
        try:
            return self.config.get(section, key, fallback=fallback)
        except Exception as e:
            return fallback

    def set_setting(self, section: str, key: str, value: Any):
        """Set configuration setting."""
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = str(value)
            self.save_config()
            
        except Exception as e:
            raise

    def get_api_settings(self) -> Dict[str, Any]:
        """Get all API-related settings."""
        return {
            'url': self.get_setting('API', 'api_url'),
            'model': self.get_setting('API', 'model'),
            'max_tokens': int(self.get_setting('API', 'max_tokens', 150)),
            'temperature': float(self.get_setting('API', 'temperature', 0.3))
        }

    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        try:
            self._create_default_config()
            
        except Exception as e:
            raise

def get_user_settings() -> Dict[str, Any]:
    """Load user settings from file or return defaults."""
    if USER_SETTINGS_FILE.exists():
        import json
        try:
            with open(USER_SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_USER_SETTINGS.copy()
    return DEFAULT_USER_SETTINGS.copy()

def save_user_settings(settings: Dict[str, Any]) -> None:
    """Save user settings to file."""
    import json
    try:
        USER_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USER_SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")
