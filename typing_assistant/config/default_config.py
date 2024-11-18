"""Default configuration settings for the Enhanced Typing Assistant."""

# Application paths and information
APP_NAME = "TypingAssistant"
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
    'update_failed': 'Failed to check for updates. Please try again later.',
    'offline_mode': 'Application is running in offline mode. Some features may be unavailable.'
}

# API configurations for both online and offline modes
API_CONFIG = {
    'online': {
        'model': 'gpt-4',
        'temperature': 0.3,
        'max_tokens': 1000,
        'timeout': 30,
        'retry_attempts': 3,
        'retry_delay': 1
    },
    'offline': {
        'use_local_model': True,
        'model_path': 'models/local_model',
        'cache_results': True,
        'max_cache_size_mb': 1000
    }
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
    'beta_features': False,
    'offline_mode': True  # Enable offline mode by default
}
