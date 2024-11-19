"""Default configuration settings for the Enhanced Typing Assistant."""

# Application paths and information
APP_NAME = "Enhanced Typing Assistant"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Codeium"
APP_WEBSITE = "https://codeium.com"
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
        'background': '#f0f0f0',
        'text': '#333333',
        'primary': '#2196F3',
        'secondary': '#FFC107',
        'success': '#4CAF50',
        'error': '#f44336',
        'warning': '#FF9800',
        'info': '#2196F3'
    },
    'dark': {
        'background': '#121212',
        'text': '#ffffff',
        'primary': '#BB86FC',
        'secondary': '#03DAC6',
        'success': '#00C853',
        'error': '#CF6679',
        'warning': '#FFB74D',
        'info': '#64B5F6'
    },
    'high_contrast': {
        'background': '#000000',
        'text': '#ffffff',
        'primary': '#ffff00',
        'secondary': '#00ffff',
        'success': '#00ff00',
        'error': '#ff0000',
        'warning': '#ffa500',
        'info': '#00ffff'
    }
}

# Accessibility settings
ACCESSIBILITY = {
    'font_families': {
        'default': 'Arial',
        'dyslexic': 'OpenDyslexic',
        'monospace': 'Consolas'
    },
    'font_sizes': {
        'small': 12,
        'medium': 14,
        'large': 16,
        'extra_large': 18
    },
    'line_heights': {
        'compact': 1.2,
        'normal': 1.5,
        'relaxed': 1.8
    },
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
    'offline_mode': 'Application is running in offline mode. Some features may be unavailable.',
    'api_error': 'Error communicating with the API. Please check your internet connection and try again.',
    'config_error': 'Error loading configuration. Using default settings.',
    'file_error': 'Error accessing file system. Please check permissions.',
    'memory_error': 'Insufficient memory. Please close other applications and try again.',
    'permission_error': 'Permission denied. Please check your access rights.',
    'timeout_error': 'Operation timed out. Please try again.',
    'unknown_error': 'An unknown error occurred. Please try again.'
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
    },
    'openai': {
        'model': 'gpt-4',
        'temperature': 0.3,
        'max_tokens': 100,
        'timeout': 10,
        'retry_attempts': 3,
        'retry_delay': 1
    },
    'anthropic': {
        'model': 'claude-2',
        'temperature': 0.3,
        'max_tokens': 100,
        'timeout': 10,
        'retry_attempts': 3,
        'retry_delay': 1
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
    'offline_mode': True,  # Enable offline mode by default
    'text_correction': {
        'enabled': True,
        'auto_correct': True,
        'spell_check': True,
        'grammar_check': True,
        'style_check': True,
        'delay': 200
    },
    'accessibility': {
        'high_contrast': False,
        'large_text': False,
        'text_to_speech': False,
        'keyboard_shortcuts': True,
        'break_reminders': True
    },
    'cognitive_support': {
        'enabled': True,
        'word_prediction': True,
        'context_aware': True,
        'learning_support': True
    },
    'translation': {
        'enabled': True,
        'auto_detect': True,
        'target_language': 'en',
        'preserve_formatting': True
    }
}
