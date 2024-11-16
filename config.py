from typing import Dict, Final, Union, List, Any

# Version control
CONFIG_VERSION: Final[str] = '1.0.0'
CONFIG_TIMESTAMP: Final[str] = '2024-01-01'

# Language codes for text processing
TEXT_PROCESSING_LANGUAGE_CODES: Final[Dict[str, str]] = {
    'English': 'en_US',
    'Spanish': 'es_ES',
    'French': 'fr_FR',
    'German': 'de_DE',
    'Italian': 'it_IT',
    'Portuguese': 'pt_PT',
    'Russian': 'ru_RU',
    'Chinese': 'zh_CN',
    'Japanese': 'ja_JP',
    'Korean': 'ko_KR',
    'Arabic': 'ar_SA',
    'Hindi': 'hi_IN',
    'Dutch': 'nl_NL',
    'Swedish': 'sv_SE',
    'Polish': 'pl_PL',
    'Turkish': 'tr_TR',
    'Vietnamese': 'vi_VN',
    'Thai': 'th_TH'
}

# Language codes for spell checking
SPELL_CHECK_LANGUAGE_CODES: Final[Dict[str, str]] = {
    'English': 'en_US',
    'Spanish': 'es_ES',
    'French': 'fr_FR',
    # ...existing code...
}

# Language codes for speech recognition
SPEECH_LANGUAGE_CODES: Final[Dict[str, str]] = {
    'English': 'en-US',
    'Spanish': 'es-ES',
    'French': 'fr-FR',
    'German': 'de-DE',
    'Italian': 'it-IT',
    'Portuguese': 'pt-PT',
    'Russian': 'ru-RU',
    'Chinese': 'zh-CN',
    'Japanese': 'ja-JP',
    'Korean': 'ko-KR',
    'Arabic': 'ar-SA',
    'Hindi': 'hi-IN',
    'Dutch': 'nl-NL',
    'Swedish': 'sv-SE',
    'Polish': 'pl-PL',
    'Turkish': 'tr-TR',
    'Vietnamese': 'vi-VN',
    'Thai': 'th-TH'
}

# Input validation ranges
THRESHOLD_RANGES: Final[Dict[str, Dict[str, float]]] = {
    'min_confidence_threshold': {'min': 0.0, 'max': 1.0},
    'language_detection_threshold': {'min': 0.5, 'max': 1.0},
    'suggestion_similarity_threshold': {'min': 0.6, 'max': 1.0},
}

# Text processing configuration
TEXT_PROCESSING_CONFIG: Final[Dict[str, Any]] = {
    'min_confidence_threshold': 0.7,
    'language_detection_threshold': 0.8,
    'suggestion_similarity_threshold': 0.85,
    'max_corrections_per_word': 3,
    'pattern_recognition': {
        'enable_keyboard_pattern_detection': True,
        'enable_cognitive_pattern_detection': True,
        'enable_visual_pattern_detection': True,
        'pattern_confidence_threshold': 0.75
    },
    'accessibility': {
        'dyslexia_support': True,
        'motor_difficulty_support': True,
        'cognitive_assistance': True,
        'visual_feedback': True
    }
}

# Enhanced correction modes with more detailed instructions
CORRECTION_MODES: Final[Dict[str, str]] = {
    'Standard': "You are an expert in understanding and correcting mistyped text.",
    'Cognitive Assistance': "You are an expert in assisting users with cognitive challenges.",
    'Motor Difficulty': "You are an expert in correcting text from users with motor control difficulties.",
    'Dyslexia-Friendly': "You are an expert in assisting users with dyslexia and similar reading/writing challenges.",
    'Learning Support': "You are an expert in helping language learners improve their writing.",
    'ESL Support': "You are an expert in helping non-native English speakers improve their writing.",
    'Professional Writing': "You are an expert in formal and business writing enhancement.",
    'Technical Writing': "You are an expert in technical documentation and clarity."
}

# Correction modes for text correction
CORRECTION_MODES: Final[Dict[str, str]] = {
    'Standard': 'Standard text correction',
    'Grammar': 'Focus on grammar correction',
    'Spelling': 'Focus on spelling correction',
    # ...existing code...
}

SEVERITY_LEVELS: Final[Dict[str, str]] = {
    'Low': "Handle basic typing errors while preserving original text. Address: "
          "- Single character substitutions (e.g., 'teh' → 'the') "
          "- Adjacent key hits (e.g., 'nejxt' → 'next') "
          "- Simple doubled letters (e.g., 'thiss' → 'this') "
          "- Basic capitalization errors",
    
    'Medium': "Correct moderate typing difficulties and patterns. Handle: "
             "- Shifted hand position errors (e.g., 'vwery' → 'very', 'nrxt' → 'next') "
             "- Letter sequence scrambling (e.g., 'taht' → 'that') "
             "- Missing/extra spaces (e.g., 'thisand' → 'this and') "
             "- Common letter substitutions from nearby keys "
             "- Repeated letter patterns (e.g., 'helllo' → 'hello') "
             "- Basic accent mark errors",
    
    'High': "Apply advanced correction for significant typing challenges. Process: "
           "- Severe keyboard misalignment (e.g., 'vwstf' → 'best', 'rxamplr' → 'example') "
           "- Multiple concurrent errors (e.g., 'accicentg' → 'accident') "
           "- Shifted entire word patterns (e.g., 'ejhy' → 'what' from shifted hand position) "
           "- Stuck key repetitions (e.g., 'thhhhing' → 'thing') "
           "- Missing letters in clusters (e.g., 'coprhensive' → 'comprehensive') "
           "- Word boundary detection (e.g., 'andmore' → 'and more') "
           "- Phonetic approximations (e.g., 'compreshun' → 'compression')",
    
    'Maximum': "Implement extensive reconstruction for severe typing issues. Handle: "
              "- Complete keyboard misalignment recovery "
              "- Multi-language character confusion (e.g., mixed charset typing) "
              "- Severe pattern displacement (e.g., 'ecxamlek' → 'example') "
              "- Context-based word reconstruction "
              "- Stuck modifier keys (e.g., shifted/ctrl/alt key errors) "
              "- Rolling finger patterns (e.g., 'thigns' → 'things') "
              "- Adaptive learning from user's common error patterns "
              "- Cross-language phonetic matching "
              "- Gesture typing errors and swipe patterns "
              "- Time-based error detection (rapid vs. slow typing errors) "
              "- Multi-word context reconstruction "
              "- Keyboard layout switching errors"
}

# Severity levels for correction intensity
SEVERITY_LEVELS: Final[Dict[str, str]] = {
    'Low': 'Make minimal corrections',
    'Medium': 'Make moderate corrections',
    'High': 'Make thorough corrections',
    'Maximum': 'Make extensive corrections'
}

# Typing assistance configuration
TYPING_ASSISTANCE_CONFIG: Final[Dict[str, Any]] = {
    'auto_correction': {
        'enabled': True,
        'delay_ms': 500,
        'min_word_length': 3
    },
    'suggestion_display': {
        'max_suggestions': 5,
        'show_confidence': True,
        'highlight_changes': True
    },
    'accessibility': {
        'high_contrast': False,
        'large_text': False,
        'screen_reader_support': True
    },
    'cache': {
        'max_size': 1000,
        'expiration_minutes': 60
    }
}

# Logging configuration
LOGGING_CONFIG: Final[Dict[str, Any]] = {
    'log_level': 'INFO',
    'log_file_path': './logs/typing_assistant.log',
    'max_file_size_mb': 10,
    'backup_count': 5,
    'include_timestamps': True,
    'performance_tracking': True
}

# User feedback configuration
FEEDBACK_CONFIG: Final[Dict[str, Any]] = {
    'collect_analytics': True,
    'send_anonymous_stats': False,
    'improvement_suggestions': True,
    'correction_explanations': True,
    'learning_pattern_tracking': True
}

# Performance monitoring
PERFORMANCE_CONFIG: Final[Dict[str, Any]] = {
    'response_time_threshold_ms': 100,
    'batch_size': 50,
    'cache_size_mb': 256,
    'memory_limit_mb': 512,
    'threading_enabled': True
}

# Error handling
ERROR_HANDLING_CONFIG: Final[Dict[str, Dict[str, Any]]] = {
    'retry_attempts': {
        'max_attempts': 3,
        'delay_between_attempts_ms': 1000
    },
    'fallback_modes': {
        'enable_offline_mode': True,
        'enable_safe_mode': True
    }
}

# Add new keyboard layout patterns
KEYBOARD_LAYOUTS = {
    'QWERTY': {
        'rows': [
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm']
        ],
        'adjacent_keys': {
            'q': ['w', 'a', 's'],
            'w': ['q', 'e', 'a', 's', 'd'],
            # ... add all adjacent key mappings
        }
    },
    'AZERTY': {
        # Add AZERTY layout support
    },
    'DVORAK': {
        # Add DVORAK layout support
    }
}

# Enhanced cognitive assistance patterns
COGNITIVE_PATTERNS = {
    'dyslexic_swaps': [
        ('b', 'd'), ('p', 'q'), ('m', 'w'),
        ('n', 'u'), ('g', 'j'), ('ie', 'ei')
    ],
    'phonetic_confusions': {
        'f': ['ph'],
        'k': ['c', 'ch'],
        's': ['c', 'ss'],
        # Add more phonetic patterns
    },
    'visual_similarities': {
        'rn': 'm',
        'cl': 'd',
        'vv': 'w',
        # Add more visual similarity patterns
    }
}

# Update check configuration
UPDATE_CHECK_CONFIG: Final[Dict[str, Any]] = {
    'check_frequency_days': 7,
    'api_endpoint': 'https://api.github.com/repos/yourusername/typing_assistant/releases/latest'
}

# Export formats
EXPORT_FORMATS = {
    'CSV': '.csv',
    'JSON': '.json',
    'TXT': '.txt',
    'PDF': '.pdf'
}

# Common typing patterns
COMMON_TYPING_PATTERNS = {
    'key_repeats': r'(.)\1{2,}',  # e.g., 'helllo' instead of 'hello'
    # ...existing code...
}

# Gamification configuration
GAMIFICATION_CONFIG = {
    'wpm_refresh_rate': 1000,  # ms
    'achievement_levels': {
        'beginner': {'wpm': 0, 'color': '#A8E6CF'},
        'intermediate': {'wpm': 30, 'color': '#FFD3B6'},
        'advanced': {'wpm': 50, 'color': '#FF8B94'},
        'expert': {'wpm': 70, 'color': '#D4A5A5'}
    },
    # ...existing code...
}

# ...add other configurations as needed...