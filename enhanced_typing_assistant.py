"""Enhanced Typing Assistant with advanced text correction and accessibility features.

This module provides a comprehensive typing assistant with features including:
- Real-time spell checking and text correction
- Voice input and text-to-speech
- Multiple language support
- Dyslexia-friendly interface
- Performance analytics
- Secure user authentication
"""

import os
import sys
import threading
import asyncio
import hashlib
import base64
import logging
import cProfile
from datetime import datetime
from typing import Dict, Optional, Any, Tuple, List, Union
from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
import json
import csv
import requests
import sqlite3
import openai
import pyttsx3
from concurrent.futures import ThreadPoolExecutor

# GUI imports
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QTextEdit, QPushButton, QLabel, QSpinBox, QCheckBox,
    QComboBox, QSlider, QMessageBox, QInputDialog, QDialog, QFormLayout,
    QGridLayout, QStatusBar, QMenu, QMenuBar, QSystemTrayIcon, QProgressBar
)
from PyQt5.QtGui import (
    QFont, QTextCharFormat, QPalette, QColor, QIcon, 
    QTextCursor, QSyntaxHighlighter, QKeySequence
)
from PyQt5.QtCore import (
    Qt, QSettings, QTimer, pyqtSignal, QObject
)

# Try to import optional dependencies
try:
    import enchant
    ENCHANT_AVAILABLE = True
except ImportError:
    ENCHANT_AVAILABLE = False
    logging.warning("pyenchant not available. Spell checking will be disabled.")

try:
    import sqlite3worker
    SQLITE_WORKER_AVAILABLE = True
except ImportError:
    SQLITE_WORKER_AVAILABLE = False
    logging.warning("sqlite3worker not available. Using standard sqlite3.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default settings if config module not available
DEFAULT_SETTINGS = {
    'theme': 'light',
    'font_size': 12,
    'auto_correct': True,
    'voice_speed': 150,
    'language': 'en_US',
    'correction_mode': 'Standard',
    'correction_severity': 'Medium',
    'auto_save_interval': 300,
    'max_undo_steps': 50,
    'show_word_count': True,
    'show_char_count': True,
    'enable_analytics': True,
    'cache_size': 1000,
    'max_recent_files': 10
}

# Try to import local modules, use defaults if not available
try:
    from typing_assistant.config import (
        APP_NAME, CONFIG_DIR, CACHE_DIR, DATA_DIR, LOGS_DIR, USER_DATA_DIR,
        LOG_FILE, USER_SETTINGS_FILE, CONFIG_FILE, API_KEYS_FILE,
        APP_VERSION, APP_AUTHOR, APP_WEBSITE, THEMES
    )
    from typing_assistant.core.text_processor import TextProcessor
    from typing_assistant.utils.styles import StyleSheet, apply_theme
except ImportError as e:
    logger.warning(f"Could not import local modules: {e}. Using defaults.")
    APP_NAME = "Enhanced Typing Assistant"
    APP_VERSION = "2.0.0"
    APP_AUTHOR = "Typing Assistant Team"
    APP_WEBSITE = "https://typingassistant.com"
    CONFIG_DIR = Path.home() / ".typing_assistant"
    CACHE_DIR = CONFIG_DIR / "cache"
    DATA_DIR = CONFIG_DIR / "data"
    LOGS_DIR = CONFIG_DIR / "logs"
    USER_DATA_DIR = CONFIG_DIR / "user_data"
    LOG_FILE = LOGS_DIR / "app.log"
    USER_SETTINGS_FILE = CONFIG_DIR / "settings.json"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    API_KEYS_FILE = CONFIG_DIR / "api_keys.bin"
    THEMES = {
        'light': {'window': '#f8f9fa', 'text': '#212529'},
        'dark': {'window': '#212529', 'text': '#f8f9fa'}
    }

# Local imports
from styles import StyleSheet, apply_theme

# Define required dependencies with installation commands
DEPENDENCIES = [
    DependencyInfo("pyenchant", "enchant", "3.2.0", installation_command="pip install pyenchant"),
    DependencyInfo("SpeechRecognition", "speech_recognition", "3.8.1", installation_command="pip install SpeechRecognition"),
    DependencyInfo("cryptography", "cryptography", "36.0.0", installation_command="pip install cryptography"),
    DependencyInfo("pyttsx3", "pyttsx3", "2.90", installation_command="pip install pyttsx3"),
    DependencyInfo("matplotlib", "matplotlib", "3.4.3", installation_command="pip install matplotlib"),
    DependencyInfo("googletrans", "googletrans", "4.0.0-rc1", installation_command="pip install googletrans==4.0.0-rc1")
]

# Thread pool for parallel processing
thread_pool = ThreadPoolExecutor(max_workers=4)

# Import optional dependencies
try:
    import enchant
except ImportError:
    enchant = None
    logger.warning("enchant not installed - spell checking disabled")

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    logger.warning("speech_recognition not installed - voice input disabled")

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None
    logger.warning("cryptography not installed - secure storage disabled")

class SecurityUtils:
    """Security utility functions with enhanced encryption."""
    
    @staticmethod
    def generate_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Generate an encryption key from a password with salt."""
        try:
            if not password:
                raise ValueError("Password cannot be empty")
                
            # Generate or use provided salt
            if salt is None:
                salt = os.urandom(16)
            
            # Use stronger key derivation
            key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt,
                100000  # Increased iterations for security
            )
            
            return base64.urlsafe_b64encode(key), salt
        except Exception as e:
            logger.error(f"Error generating encryption key: {e}")
            raise

    @staticmethod
    @lru_cache(maxsize=100)
    def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, bytes]:
        """Hash password with salt using Argon2 if available, fallback to PBKDF2."""
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher()
            return ph.hash(password), salt or b''
        except ImportError:
            key, salt = SecurityUtils.generate_key(password, salt)
            return base64.b64encode(key).decode(), salt

class SpellCheckHighlighter(QSyntaxHighlighter):
    """Highlights misspelled words in text editor with performance optimizations."""
    
    def __init__(self, parent=None, language='en_US'):
        """Initialize spell check highlighter."""
        super().__init__(parent)
        
        # Set up spell checker if enchant is available
        self.spell_checker = None
        if ENCHANT_AVAILABLE:
            try:
                self.spell_checker = enchant.Dict(language)
                logger.info(f"Spell checker initialized with language: {language}")
            except enchant.Error as e:
                logger.error(f"Failed to initialize spell checker: {e}")
        
        # Initialize text formatting
        self.misspelled_format = QTextCharFormat()
        self.misspelled_format.setUnderlineColor(QColor(255, 0, 0))  # Red
        self.misspelled_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        
        # Performance optimizations
        self.word_cache = {}  # Cache for spell checking results
        self.max_cache_size = 10000
        self.last_text = ""
        self.last_results = []
        
        # Custom dictionary support
        self.custom_dictionary = set()
        self.load_custom_dictionary()
    
    def load_custom_dictionary(self) -> None:
        """Load custom dictionary from user settings."""
        try:
            settings = QSettings('TypingAssistant', 'SpellChecker')
            custom_words = settings.value('custom_dictionary', [], type=list)
            self.custom_dictionary = set(custom_words)
            logger.debug(f"Loaded {len(self.custom_dictionary)} custom words")
        except Exception as e:
            logger.error(f"Error loading custom dictionary: {e}")
            self.custom_dictionary = set()
    
    def save_custom_dictionary(self) -> None:
        """Save custom dictionary to user settings."""
        try:
            settings = QSettings('TypingAssistant', 'SpellChecker')
            settings.setValue('custom_dictionary', list(self.custom_dictionary))
            settings.sync()
            logger.debug(f"Saved {len(self.custom_dictionary)} custom words")
        except Exception as e:
            logger.error(f"Error saving custom dictionary: {e}")
    
    def add_to_dictionary(self, word: str) -> None:
        """Add a word to the custom dictionary."""
        if word and isinstance(word, str):
            self.custom_dictionary.add(word.lower())
            self.save_custom_dictionary()
            # Clear cache entry for this word
            self.word_cache.pop(word.lower(), None)
            logger.debug(f"Added word to custom dictionary: {word}")
    
    def clean_word(self, word: str) -> str:
        """Clean a word for spell checking with caching."""
        try:
            # Remove punctuation and whitespace
            import string
            cleaned = word.strip().strip(string.punctuation).lower()
            return cleaned
        except Exception as e:
            logger.error(f"Error cleaning word: {e}")
            return word
    
    def check_word(self, word: str) -> bool:
        """Check if a word is spelled correctly."""
        if not word or not isinstance(word, str):
            return True
            
        # Check cache first
        cleaned_word = self.clean_word(word)
        if cleaned_word in self.word_cache:
            return self.word_cache[cleaned_word]
            
        # Skip short words and numbers
        if len(cleaned_word) <= 1 or cleaned_word.isdigit():
            return True
            
        # Check custom dictionary
        if cleaned_word in self.custom_dictionary:
            return True
            
        # Check with enchant if available
        try:
            if self.spell_checker:
                is_correct = self.spell_checker.check(cleaned_word)
            else:
                is_correct = True  # Skip spell checking if enchant not available
                
            # Cache the result
            if len(self.word_cache) >= self.max_cache_size:
                self.word_cache.clear()  # Clear cache if too large
            self.word_cache[cleaned_word] = is_correct
            
            return is_correct
            
        except Exception as e:
            logger.error(f"Error checking word '{word}': {e}")
            return True
    
    def get_suggestions(self, word: str) -> List[str]:
        """Get spelling suggestions for a word."""
        if not self.spell_checker:
            return []
            
        try:
            cleaned_word = self.clean_word(word)
            if cleaned_word in self.custom_dictionary:
                return []
                
            suggestions = self.spell_checker.suggest(cleaned_word)
            return suggestions[:5]  # Limit to top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions for '{word}': {e}")
            return []
    
    def highlightBlock(self, text: str) -> None:
        """Highlight misspelled words in the text block."""
        if not text or not isinstance(text, str):
            return
            
        try:
            # Skip if spell checking is not available
            if not self.spell_checker:
                return
                
            # Performance optimization: skip if text hasn't changed
            if text == self.last_text:
                for start, length, is_correct in self.last_results:
                    if not is_correct:
                        self.setFormat(start, length, self.misspelled_format)
                return
                
            # Split text into words
            import re
            word_pattern = re.compile(r'\b\w+\b')
            matches = word_pattern.finditer(text)
            
            # Store results for caching
            results = []
            
            for match in matches:
                start = match.start()
                length = match.end() - start
                word = match.group()
                
                is_correct = self.check_word(word)
                results.append((start, length, is_correct))
                
                if not is_correct:
                    self.setFormat(start, length, self.misspelled_format)
            
            # Cache results
            self.last_text = text
            self.last_results = results
            
        except Exception as e:
            logger.error(f"Error highlighting text block: {e}")

class TextCorrectionWorker(QObject):
    """Worker class for text correction with advanced features and optimizations."""
    
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    result_ready = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, text: str, mode: str, severity: str, language: str, 
                 api_key: str, cache: dict, context: Optional[str] = None) -> None:
        """Initialize text correction worker."""
        super().__init__()
        
        # Input parameters
        self.text = text
        self.mode = mode
        self.severity = severity
        self.language = language
        self.api_key = api_key
        self.cache = cache or {}
        self.context = context
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        
        # Correction settings
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        self.chunk_size = 2000  # characters
        self.preserve_formatting = True
        self.is_cancelled = False
        
        # Performance tracking
        self._start_time = None
        self._chunks_processed = 0
        self._total_chunks = 0
        
        logger.info("TextCorrectionWorker initialized")
    
    def run(self) -> None:
        """Perform text correction using the OpenAI API."""
        try:
            if not self.text or not isinstance(self.text, str):
                raise ValueError("Invalid input text")
                
            if not self.api_key:
                raise ValueError("API key not provided")
                
            # Start performance tracking
            self._start_time = datetime.now()
            
            # Process text
            result = asyncio.run(self.async_run())
            
            if self.is_cancelled:
                logger.info("Text correction cancelled")
                return
                
            # Log performance metrics
            if self._start_time:
                elapsed = (datetime.now() - self._start_time).total_seconds()
                logger.info(f"Text correction completed in {elapsed:.2f} seconds")
            
            self.result_ready.emit(result)
            self.finished.emit()
            
        except Exception as e:
            logger.error(f"Error in text correction: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
            self.finished.emit()
    
    async def async_run(self) -> str:
        """Asynchronous method to perform text correction with chunking and progress tracking."""
        try:
            # Split text into chunks
            chunks = self._split_into_chunks(self.text)
            self._total_chunks = len(chunks)
            
            # Process chunks with progress tracking
            corrected_chunks = []
            for i, chunk in enumerate(chunks):
                if self.is_cancelled:
                    break
                    
                # Update progress
                progress = int((i / self._total_chunks) * 100)
                self.progress_updated.emit(progress)
                
                # Process chunk with retry logic
                corrected = await self._process_chunk_with_retry(chunk)
                if corrected:
                    corrected_chunks.append(corrected)
                    self._chunks_processed += 1
            
            # Combine chunks and preserve formatting
            final_text = self._combine_chunks(corrected_chunks)
            
            # Final progress update
            self.progress_updated.emit(100)
            
            return final_text
            
        except Exception as e:
            logger.error(f"Error in async text correction: {e}", exc_info=True)
            raise
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks while preserving sentence boundaries."""
        try:
            if len(text) <= self.chunk_size:
                return [text]
                
            chunks = []
            current_pos = 0
            
            while current_pos < len(text):
                # Find the end of the current chunk
                chunk_end = min(current_pos + self.chunk_size, len(text))
                
                # Adjust chunk end to preserve sentence boundaries
                if chunk_end < len(text):
                    # Look for sentence endings (.!?)
                    for i in range(chunk_end, max(current_pos, chunk_end - 100), -1):
                        if text[i-1] in '.!?' and (i == len(text) or text[i].isspace()):
                            chunk_end = i
                            break
                
                chunks.append(text[current_pos:chunk_end])
                current_pos = chunk_end
                
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting text into chunks: {e}")
            return [text]
    
    async def _process_chunk_with_retry(self, chunk: str, attempt: int = 0) -> Optional[str]:
        """Process a text chunk with retry logic."""
        try:
            # Check cache first
            cache_key = f"{chunk}:{self.mode}:{self.severity}"
            if cache_key in self.cache:
                logger.debug("Using cached correction")
                return self.cache[cache_key]
            
            corrected = await self._process_chunk(chunk)
            
            # Cache the result
            if len(self.cache) > 1000:  # Limit cache size
                self.cache.clear()
            self.cache[cache_key] = corrected
            
            return corrected
            
        except openai.error.RateLimitError:
            if attempt < self.max_retries:
                wait_time = (attempt + 1) * self.retry_delay
                logger.warning(f"Rate limit hit, retrying in {wait_time} seconds")
                await asyncio.sleep(wait_time)
                return await self._process_chunk_with_retry(chunk, attempt + 1)
            raise
            
        except openai.error.APIError as e:
            if attempt < self.max_retries and "server_error" in str(e).lower():
                wait_time = (attempt + 1) * self.retry_delay
                logger.warning(f"API error, retrying in {wait_time} seconds")
                await asyncio.sleep(wait_time)
                return await self._process_chunk_with_retry(chunk, attempt + 1)
            raise
            
        except Exception as e:
            logger.error(f"Error processing chunk: {e}", exc_info=True)
            if attempt < self.max_retries:
                wait_time = (attempt + 1) * self.retry_delay
                logger.warning(f"Retrying in {wait_time} seconds")
                await asyncio.sleep(wait_time)
                return await self._process_chunk_with_retry(chunk, attempt + 1)
            raise
    
    async def _process_chunk(self, chunk: str) -> str:
        """Process a single chunk of text."""
        try:
            # Prepare prompt based on correction mode and severity
            prompt = self._get_correction_prompt(chunk)
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                temperature=0.3,
                max_tokens=len(chunk) + 200,
                presence_penalty=0,
                frequency_penalty=0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in API call: {e}")
            raise
    
    def _get_correction_prompt(self, text: str) -> Dict[str, str]:
        """Get the appropriate prompt based on correction mode and severity."""
        prompts = {
            "Standard": {
                "system": "You are a professional text editor. Correct spelling and grammar while preserving the original meaning and style.",
                "user": f"Please correct this text, maintaining its original format and structure:\n\n{text}"
            },
            "Formal": {
                "system": "You are a formal writing expert. Make the text more professional and formal while correcting errors.",
                "user": f"Please make this text more formal and correct any errors:\n\n{text}"
            },
            "Creative": {
                "system": "You are a creative writing enhancer. Improve the text while maintaining its creative elements.",
                "user": f"Please enhance this text while preserving its creative style:\n\n{text}"
            }
        }
        
        return prompts.get(self.mode, prompts["Standard"])
    
    def _combine_chunks(self, chunks: List[str]) -> str:
        """Combine text chunks while preserving formatting."""
        try:
            if not chunks:
                return ""
                
            if len(chunks) == 1:
                return chunks[0]
                
            # Join chunks with proper spacing
            combined = []
            for i, chunk in enumerate(chunks):
                if i > 0 and not chunk.startswith(('.', '!', '?', ',', ';', ':', ')')):
                    combined.append(' ')
                combined.append(chunk.strip())
            
            return ''.join(combined)
            
        except Exception as e:
            logger.error(f"Error combining chunks: {e}")
            return ' '.join(chunks)
    
    def cancel(self) -> None:
        """Cancel the current correction process."""
        self.is_cancelled = True
        logger.info("Text correction cancelled")

class EnhancedTypingAssistant(QMainWindow):
    """Main window class for the Enhanced Typing Assistant application."""
    
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Enhanced Typing Assistant')
        self.resize(1000, 800)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize database with connection pooling
        self.db_pool = self.init_db_pool()
        self.conn = self.get_db_connection()
        self.cursor = self.conn.cursor()
        
        # User-related attributes
        self.user_id = None
        self.username = None
        self.user_settings = {}
        
        # Create status bar first
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Initializing...')
        
        # Progress bar in status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Settings with defaults
        self.settings = QSettings('TypingAssistant', 'Settings')
        self.default_settings = {
            'theme': 'light',
            'font_size': 12,
            'auto_correct': True,
            'voice_speed': 150,
            'language': 'en_US',
            'correction_mode': 'Standard',
            'correction_severity': 'Medium',
            'auto_save_interval': 300,  # 5 minutes
            'max_undo_steps': 50,
            'show_word_count': True,
            'show_char_count': True,
            'enable_analytics': True,
            'cache_size': 1000,
            'max_recent_files': 10
        }
        self.load_settings()
        
        # Initialize text processor
        self.text_processor = TextProcessor(self.api_key)
        
        # Correction history and cache with LRU
        self.correction_history = []
        self.cache = {}
        self.max_cache_entries = self.user_settings.get('cache_size', 1000)
        
        # Recent files
        self.recent_files = []
        self.load_recent_files()
        
        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = self.user_settings.get('max_undo_steps', 50)
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_interval = self.user_settings.get('auto_save_interval', 300)
        self.auto_save_timer.start(self.auto_save_interval * 1000)
        
        # Analytics data
        self.analytics = {
            'corrections_made': 0,
            'words_processed': 0,
            'characters_processed': 0,
            'session_start_time': datetime.now(),
            'total_processing_time': 0
        }
        
        # API key with secure storage
        self.api_key = None
        self.load_api_key()
        
        # Processing state
        self.is_processing = False
        
        # WPM tracking with improved accuracy
        self.wpm = 0
        self.word_count = 0
        self.char_count = 0
        self.start_time = None
        self.typing_intervals = []
        
        # UI Components
        self.input_text = None
        self.output_text = None
        self.correction_thread = None
        self.spell_checker = None
        self.dyslexia_font = False
        
        # Set up UI
        self.setup_ui()
        self.setup_shortcuts()
        
        # User Authentication
        if not self.login_user():
            logger.error("Login failed, exiting application")
            sys.exit(1)
        
        # Start performance monitoring if enabled
        if self.user_settings.get('enable_analytics', True):
            self.performance_monitor.start()
        
        self.status_bar.showMessage('Ready')
    
    def init_db_pool(self) -> sqlite3.Connection:
        """Initialize database connection pool."""
        try:
            import sqlite3worker
            db_path = DATA_DIR / 'typing_assistant.db'
            pool = sqlite3worker.SqliteWorker(str(db_path))
            
            # Create tables if they don't exist
            pool.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_count INTEGER DEFAULT 0,
                    settings_json TEXT
                )
            ''')
            
            pool.execute('''
                CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    original_text TEXT NOT NULL,
                    corrected_text TEXT NOT NULL,
                    correction_type TEXT NOT NULL,
                    processing_time REAL,
                    confidence_score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            pool.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id TEXT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            return pool
        except Exception as e:
            logger.error(f"Error initializing database pool: {e}")
            raise
    
    def get_db_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool."""
        return self.db_pool.get_connection()
    
    def login_user(self):
        """Handle user login or registration."""
        login = LoginDialog()
        if login.exec_() == QDialog.Accepted:
            username, password = login.get_credentials()
            if self.authenticate_user(username, password):
                self.username = username
                self.status_bar.showMessage(f'Logged in as {self.username}')
                return True
            else:
                QMessageBox.warning(self, 'Login Failed', 'Invalid credentials. Please try again.')
                return False
        else:
            register = RegisterDialog()
            if register.exec_() == QDialog.Accepted:
                username, password = register.get_credentials()
                if self.register_user(username, password):
                    self.username = username
                    self.status_bar.showMessage(f'Registered and logged in as {self.username}')
                    return True
                else:
                    QMessageBox.warning(self, 'Registration Failed', 'Username already exists. Please try again.')
                    return False
            else:
                sys.exit()

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials with hashed password."""
        hashed_password = self.hash_password(password)
        self.cursor.execute('SELECT id FROM users WHERE username=? AND password_hash=?', (username, hashed_password))
        result = self.cursor.fetchone()
        if result:
            self.user_id = result[0]
            return True
        return False

    def register_user(self, username: str, password: str) -> bool:
        """Register a new user with hashed password."""
        try:
            hashed_password = self.hash_password(password)
            self.cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
            self.conn.commit()
            self.user_id = self.cursor.lastrowid
            return True
        except sqlite3.IntegrityError:
            return False

    def hash_password(self, password: str) -> str:
        """Hash the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def load_settings(self) -> None:
        """Load user settings from QSettings."""
        self.font_size = self.settings.value('font_size', 12, type=int)
        self.auto_correct = self.settings.value('auto_correct', True, type=bool)
        self.voice_speed = self.settings.value('voice_speed', 150, type=int)
        self.color_scheme = self.settings.value('color_scheme', 'Default', type=str)
        self.current_language = self.settings.value('current_language', 'English', type=str)
        self.correction_mode = self.settings.value('correction_mode', 'Standard', type=str)
        self.severity_level = self.settings.value('severity_level', 'High', type=str)

    def load_api_key(self) -> None:
        """Load and decrypt the user's API key."""
        if Fernet is None:
            QMessageBox.critical(self, 'Missing Dependency', 'The cryptography library is required for API key encryption.')
            sys.exit()
        
        encrypted_key = self.settings.value('api_key', '', type=str)
        if encrypted_key:
            password = self.get_password()
            if password:
                try:
                    fernet = Fernet(SecurityUtils.generate_key(password))
                    self.api_key = fernet.decrypt(encrypted_key.encode()).decode()
                except Exception:
                    self.api_key = None
                    QMessageBox.warning(self, 'API Key Error', 'Failed to decrypt the API key. Please enter it again.')
                    self.enter_api_key()
            else:
                self.api_key = None
                self.enter_api_key()
        else:
            self.enter_api_key()

    def enter_api_key(self) -> None:
        """Prompt the user to enter their OpenAI API key."""
        api_key, ok = QInputDialog.getText(
            self,
            'Enter OpenAI API Key',
            'Please enter your OpenAI API Key:',
            echo=QLineEdit.Password
        )
        if ok and api_key.strip():
            password = self.get_password(confirm=True)
            if password:
                try:
                    fernet = Fernet(SecurityUtils.generate_key(password))
                    encrypted_key = fernet.encrypt(api_key.strip().encode()).decode()
                    self.settings.setValue('api_key', encrypted_key)
                    self.api_key = api_key.strip()
                except Exception as e:
                    QMessageBox.critical(self, 'Encryption Error', f'Failed to encrypt API key: {str(e)}')
                    self.enter_api_key()
            else:
                QMessageBox.critical(self, 'Password Required', 'A password is required to secure your API key.')
                sys.exit()
        else:
            QMessageBox.critical(self, 'API Key Required', 'An OpenAI API key is required to use this application.')
            sys.exit()

    def get_password(self, confirm=False) -> str:
        """Prompt the user to enter a password for encrypting the API key."""
        if confirm:
            password, ok = QInputDialog.getText(
                self,
                'Set Password',
                'Set a password to secure your API key:',
                echo=QLineEdit.Password
            )
            if ok and password:
                confirm_password, ok_confirm = QInputDialog.getText(
                    self,
                    'Confirm Password',
                    'Confirm your password:',
                    echo=QLineEdit.Password
                )
                if ok_confirm and password == confirm_password:
                    return password
                else:
                    QMessageBox.warning(self, 'Password Mismatch', 'Passwords do not match. Please try again.')
                    return self.get_password(confirm=True)
            else:
                return None
        else:
            password, ok = QInputDialog.getText(
                self,
                'Enter Password',
                'Enter your password to decrypt the API key:',
                echo=QLineEdit.Password
            )
            if ok and password:
                return password
            else:
                return None

    def setup_ui(self) -> None:
        """Initialize and set up the user interface."""
        self.setStyleSheet(StyleSheet.MAIN_WINDOW)
        self.setup_central_widget()
        self.create_menu_bar()
        self.apply_styles()
        self.init_timers()
        self.setup_spell_checker()

    def setup_spell_checker(self):
        """Initialize spell checker based on current language.""" 
        if enchant:
            language_code = self.get_language_code(self.current_language)
            try:
                self.spell_highlighter = SpellCheckHighlighter(self.input_text.document(), language_code)
            except enchant.errors.DictNotFoundError:
                self.spell_highlighter = None  # Dictionary not found for the language
        else:
            self.spell_highlighter = None  # Enchant is not available

    def setup_central_widget(self) -> None:
        """Set up the central widget and layout.""" 
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Correction Settings Group
        settings_group = self.create_settings_group()
        main_layout.addWidget(settings_group)

        # Input and Output Areas
        input_output_layout = QHBoxLayout()
        input_group = self.create_input_group()
        output_group = self.create_output_group()
        input_output_layout.addWidget(input_group)
        input_output_layout.addWidget(output_group)
        main_layout.addLayout(input_output_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Controls
        controls_group = self.create_controls_group()
        main_layout.addWidget(controls_group)

    def create_settings_group(self) -> QGroupBox:
        """Create the correction settings group box.""" 
        settings_group = QGroupBox("Correction Settings")
        settings_group.setStyleSheet(StyleSheet.GROUP_BOX)
        settings_layout = QGridLayout()

        # Language Selection with expanded languages
        language_label = QLabel('Language:')
        self.language_combo = QComboBox()
        languages = list(SPEECH_LANGUAGE_CODES.keys())  # Use languages from config
        self.language_combo.addItems(languages)
        self.language_combo.setCurrentText(self.current_language)
        self.language_combo.currentTextChanged.connect(self.update_correction_settings)
        self.language_combo.setStyleSheet(StyleSheet.COMBOBOX)
        settings_layout.addWidget(language_label, 0, 0)
        settings_layout.addWidget(self.language_combo, 0, 1)

        # Correction Mode with expanded modes
        mode_label = QLabel('Mode:')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Standard', 'Strict', 'Creative'])
        self.mode_combo.setCurrentText(self.correction_mode)
        self.mode_combo.currentTextChanged.connect(self.update_correction_settings)
        self.mode_combo.setStyleSheet(StyleSheet.COMBOBOX)
        settings_layout.addWidget(mode_label, 1, 0)
        settings_layout.addWidget(self.mode_combo, 1, 1)

        # Severity Level
        severity_label = QLabel('Severity:')
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(['High', 'Medium', 'Low'])
        self.severity_combo.setCurrentText(self.severity_level)
        self.severity_combo.currentTextChanged.connect(self.update_correction_settings)
        self.severity_combo.setStyleSheet(StyleSheet.COMBOBOX)
        settings_layout.addWidget(severity_label, 2, 0)
        settings_layout.addWidget(self.severity_combo, 2, 1)

        settings_group.setLayout(settings_layout)
        return settings_group

    def create_input_group(self) -> QGroupBox:
        """Create the input text group box.""" 
        input_group = QGroupBox("Input Text")
        input_group.setStyleSheet(StyleSheet.GROUP_BOX)
        input_layout = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setFont(QFont('Arial', self.font_size))
        self.input_text.textChanged.connect(self.on_text_changed)
        self.input_text.setPlaceholderText("Type or paste your text here.")
        self.input_text.setUndoRedoEnabled(True)
        self.input_text.setStyleSheet(StyleSheet.TEXT_EDIT)
        input_layout.addWidget(self.input_text)

        # Copy/Paste Buttons
        buttons_layout = QHBoxLayout()
        copy_button = QPushButton('Copy')
        copy_button.setStyleSheet(StyleSheet.SECONDARY_BUTTON)
        copy_button.clicked.connect(self.copy_input_text)
        copy_button.setToolTip('Copy the input text')
        paste_button = QPushButton('Paste')
        paste_button.setStyleSheet(StyleSheet.SECONDARY_BUTTON)
        paste_button.clicked.connect(self.paste_input_text)
        paste_button.setToolTip('Paste text from clipboard into the input area')
        voice_input_button = QPushButton('Voice Input')
        voice_input_button.setStyleSheet(StyleSheet.BUTTON)
        voice_input_button.clicked.connect(self.voice_input)
        voice_input_button.setToolTip('Click to input text using your voice.')
        buttons_layout.addWidget(copy_button)
        buttons_layout.addWidget(paste_button)
        buttons_layout.addWidget(voice_input_button)
        buttons_layout.setSpacing(10)
        input_layout.addLayout(buttons_layout)

        input_group.setLayout(input_layout)
        return input_group

    def copy_input_text(self):
        """Copy input text to clipboard.""" 
        clipboard = QApplication.clipboard()
        clipboard.setText(self.input_text.toPlainText())

    def paste_input_text(self):
        """Paste text from clipboard to input text area.""" 
        clipboard = QApplication.clipboard()
        self.input_text.insertPlainText(clipboard.text())

    def voice_input(self):
        """Capture voice input and insert it into the input text area.""" 
        if sr is None:
            QMessageBox.warning(self, 'Voice Input Error', 'SpeechRecognition library is not installed.')
            return
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            QMessageBox.information(self, 'Voice Input', 'Please speak now.')
            try:
                audio_data = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio_data, language=self.get_speech_language_code(self.current_language))
                self.input_text.insertPlainText(text + ' ')
            except sr.UnknownValueError:
                QMessageBox.warning(self, 'Voice Input Error', 'Could not understand the audio.')
            except sr.RequestError as e:
                QMessageBox.warning(self, 'Voice Input Error', f'Speech Recognition error: {str(e)}')
            except sr.WaitTimeoutError:
                QMessageBox.warning(self, 'Voice Input Error', 'Listening timed out while waiting for phrase to start.')

    def get_speech_language_code(self, language: str) -> str:
        """Get the language code for speech recognition.""" 
        return SPEECH_LANGUAGE_CODES.get(language, 'en-US')

    def create_output_group(self) -> QGroupBox:
        """Create the corrected text group box.""" 
        output_group = QGroupBox("Corrected Text")
        output_group.setStyleSheet(StyleSheet.GROUP_BOX)
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont('Arial', self.font_size))
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Corrected text will appear here.")
        self.output_text.setStyleSheet(StyleSheet.TEXT_EDIT)
        output_layout.addWidget(self.output_text)

        # Copy Button
        copy_button = QPushButton('Copy Corrected Text')
        copy_button.setStyleSheet(StyleSheet.BUTTON)
        copy_button.clicked.connect(self.copy_output_text)
        copy_button.setToolTip('Copy the corrected text')
        output_layout.addWidget(copy_button)

        output_group.setLayout(output_layout)
        return output_group

    def copy_output_text(self):
        """Copy output text to clipboard.""" 
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())

    def create_controls_group(self) -> QGroupBox:
        """Create the controls group box.""" 
        controls_group = QGroupBox("Controls")
        controls_group.setStyleSheet(StyleSheet.GROUP_BOX)
        controls_layout = QGridLayout()

        # Font Size Control
        font_label = QLabel('Font Size:')
        self.font_spinner = QSpinBox()
        self.font_spinner.setStyleSheet(StyleSheet.SPINBOX)
        self.font_spinner.setRange(8, 48)
        self.font_spinner.setValue(self.font_size)
        self.font_spinner.valueChanged.connect(self.change_font_size)
        self.font_spinner.setToolTip('Adjust the font size.')
        controls_layout.addWidget(font_label, 0, 0)
        controls_layout.addWidget(self.font_spinner, 0, 1)

        # Auto-Correct Toggle
        self.auto_correct_check = QCheckBox('Auto Correct')
        self.auto_correct_check.setStyleSheet(StyleSheet.CHECKBOX)
        self.auto_correct_check.setChecked(self.auto_correct)
        self.auto_correct_check.stateChanged.connect(self.toggle_auto_correct)
        self.auto_correct_check.setToolTip('Enable or disable automatic text correction.')
        controls_layout.addWidget(self.auto_correct_check, 1, 0, 1, 2)

        # Voice Speed Control
        speed_label = QLabel('Voice Speed:')
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setStyleSheet(StyleSheet.SLIDER)
        self.speed_slider.setRange(50, 300)
        self.speed_slider.setValue(self.voice_speed)
        self.speed_slider.valueChanged.connect(self.change_voice_speed)
        self.speed_slider.setToolTip('Adjust voice playback speed')
        controls_layout.addWidget(speed_label, 2, 0)
        controls_layout.addWidget(self.speed_slider, 2, 1)

        controls_group.setLayout(controls_layout)
        return controls_group

    def create_menu_bar(self) -> None:
        """Create the menu bar with File, Edit, and Help menus.""" 
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu('File')
        save_action = QAction('Save Corrected Text', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_corrected_text)
        file_menu.addAction(save_action)

        load_action = QAction('Load Text', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_text)
        file_menu.addAction(load_action)

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Add Export submenu to File menu
        export_menu = file_menu.addMenu('Export')
        for format_name in EXPORT_FORMATS:
            export_action = QAction(f'Export as {format_name}', self)
            export_action.triggered.connect(lambda checked, f=format_name: self.export_corrections(f))
            export_menu.addAction(export_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu('Edit')
        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.input_text.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.input_text.redo)
        edit_menu.addAction(redo_action)

        # Settings Menu
        settings_menu = menu_bar.addMenu('Settings')
        color_scheme_action = QAction('Color Scheme', self)
        color_scheme_action.triggered.connect(self.change_color_scheme_dialog)
        settings_menu.addAction(color_scheme_action)

        # Help Menu
        help_menu = menu_bar.addMenu('Help')
        tutorial_action = QAction('Tutorial', self)
        tutorial_action.triggered.connect(self.show_tutorial)
        help_menu.addAction(tutorial_action)

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # Add Update Check to Help menu
        check_updates_action = QAction('Check for Updates', self)
        check_updates_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(check_updates_action)

    def change_color_scheme_dialog(self):
        """Open a dialog to select the color scheme.""" 
        schemes = ['Default', 'High Contrast', 'Dark Mode', 'Colorblind Mode']
        scheme, ok = QInputDialog.getItem(self, 'Select Color Scheme', 'Color Scheme:', schemes, editable=False)
        if ok and scheme:
            self.change_color_scheme(scheme)

    def change_color_scheme(self, scheme: str) -> None:
        """Change the color scheme.""" 
        self.color_scheme = scheme
        self.settings.setValue('color_scheme', self.color_scheme)
        self.setProperty('colorScheme', scheme)
        self.style().unpolish(self)
        self.style().polish(self)

    def setup_status_bar(self) -> None:
        """Set up the status bar.""" 
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Ready')

    def apply_styles(self) -> None:
        """Apply styles to the application based on settings.""" 
        # Set dyslexia-friendly font if enabled
        font_family = 'OpenDyslexic' if self.dyslexia_font else 'Arial'
        self.input_text.setFont(QFont(font_family, self.font_size))
        self.output_text.setFont(QFont(font_family, self.font_size))

        # Apply initial color scheme
        self.change_color_scheme(self.color_scheme)

    def init_timers(self) -> None:
        """Initialize timers used in the application.""" 
        self.typing_timer = QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self.perform_correction)

    def on_text_changed(self) -> None:
        """Start the typing timer when text changes.""" 
        if not self.is_processing and self.auto_correct:
            self.typing_timer.start(self.correction_delay)

    def perform_correction(self) -> None:
        """Perform text correction.""" 
        text = self.input_text.toPlainText()
        if len(text.strip().split()) < self.min_word_length:
            return
        
        # Apply confidence thresholds from config
        min_confidence = TEXT_PROCESSING_CONFIG['min_confidence_threshold']
        language_confidence = TEXT_PROCESSING_CONFIG['language_detection_threshold']
        suggestion_threshold = TEXT_PROCESSING_CONFIG['suggestion_similarity_threshold']
        
        if text.strip() == '':
            return
        if not self.api_key:
            QMessageBox.warning(self, 'API Key Missing', 'Please enter your OpenAI API key in the settings.')
            return
        self.is_processing = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_bar.showMessage('Correcting text...')

        self.worker = TextCorrectionWorker(
            text,
            self.mode_combo.currentText(),
            self.severity_combo.currentText(),
            self.language_combo.currentText(),
            self.api_key,
            self.cache
        )

        # Set up the thread and move the worker to it
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.result_ready.connect(self.update_corrected_text)
        self.worker.error_occurred.connect(self.show_error_message)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def update_corrected_text(self, corrected_text: str) -> None:
        """Update the corrected text area with the corrected text.""" 
        self.output_text.setPlainText(corrected_text)
        self.correction_history.append({
            'input': self.input_text.toPlainText(),
            'corrected': corrected_text,
            'mode': self.mode_combo.currentText(),
            'severity': self.severity_combo.currentText(),
            'language': self.language_combo.currentText(),
            'timestamp': datetime.now().isoformat()
        })
        self.is_processing = False
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage('Ready')

    def change_font_size(self, size: int) -> None:
        """Change the font size in both text areas.""" 
        self.font_size = size
        self.input_text.setFont(QFont(self.input_text.font().family(), self.font_size))
        self.output_text.setFont(QFont(self.output_text.font().family(), self.font_size))
        self.settings.setValue('font_size', self.font_size)

    def toggle_auto_correct(self, state: int) -> None:
        """Toggle the auto-correct feature.""" 
        self.auto_correct = (state == Qt.Checked)
        self.settings.setValue('auto_correct', self.auto_correct)

    def change_voice_speed(self, speed: int) -> None:
        """Change the voice speed for text-to-speech.""" 
        self.voice_speed = speed
        self.settings.setValue('voice_speed', self.voice_speed)

    def read_corrected_text(self) -> None:
        """Read the corrected text aloud.""" 
        text = self.output_text.toPlainText()
        if text.strip() == '':
            return
        thread = threading.Thread(target=self.text_to_speech, args=(text,))
        thread.start()

    def text_to_speech(self, text: str) -> None:
        """Convert text to speech in a separate thread.""" 
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.voice_speed)
            # Set the language voice if available
            voices = engine.getProperty('voices')
            language_code = self.get_language_code(self.language_combo.currentText())
            for voice in voices:
                if language_code in voice.id:
                    engine.setProperty('voice', voice.id)
                    break
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            self.show_error_message(f"Text-to-speech error: {str(e)}")

    def get_language_code(self, language: str) -> str:
        """Get the language code for the given language.""" 
        return LANGUAGE_CODES.get(language, 'en_US')

    def save_corrected_text(self) -> None:
        """Save the corrected text to a file.""" 
        filename, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Text Files (*.txt)')
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(self.output_text.toPlainText())
                self.status_bar.showMessage(f'Saved to {filename}')
            except IOError as io_error:
                self.show_error_message(f"Failed to save file: {str(io_error)}")

    def load_text(self) -> None:
        """Load text from a file into the input text area.""" 
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text Files (*.txt)')
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    text = file.read()
                    self.input_text.setPlainText(text)
                self.status_bar.showMessage(f'Loaded from {filename}')
            except IOError as io_error:
                self.show_error_message(f"Failed to load file: {str(io_error)}")

    def show_tutorial(self) -> None:
        """Display a tutorial dialog.""" 
        QMessageBox.information(
            self,
            'Tutorial',
            'Welcome to the Enhanced Typing Assistant!\n\n'
            '1. Type or paste your text into the "Input Text" area.\n'
            '2. Use the "Voice Input" button to input text using your voice.\n'
            '3. The corrected text will appear in the "Corrected Text" area.\n'
            '4. Use the settings to adjust the correction mode, language, and severity.\n'
            '5. Enable dyslexia-friendly fonts and color schemes in the settings.\n'
            '6. Use the "Read Text" button to have the corrected text read aloud.\n'
            '7. Adjust font sizes and voice speed in the controls.\n'
            '8. Provide feedback to help us improve!'
        )

    def show_about_dialog(self) -> None:
        """Display the About dialog.""" 
        QMessageBox.information(
            self,
            'About Enhanced Typing Assistant',
            'Enhanced Typing Assistant\nVersion 2.0\n2023\n\n'
            'This application assists users with typing by providing real-time corrections '
            'and support for various accessibility needs.'
        )

    def show_error_message(self, message: str) -> None:
        """Display an error message to the user.""" 
        QMessageBox.critical(self, 'Error', message)
        self.is_processing = False
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage('Error occurred')

    def update_correction_settings(self) -> None:
        """Update correction settings when options change.""" 
        self.current_language = self.language_combo.currentText()
        self.correction_mode = self.mode_combo.currentText()
        self.severity_level = self.severity_combo.currentText()
        self.settings.setValue('current_language', self.current_language)
        self.settings.setValue('correction_mode', self.correction_mode)
        self.settings.setValue('severity_level', self.severity_level)
        self.setup_spell_checker()
        # Automatically trigger correction if there's text
        if self.input_text.toPlainText().strip() and self.auto_correct:
            self.typing_timer.start(self.correction_delay)

    def export_corrections(self, format_type: str) -> None:
        """Export correction history in the specified format.""" 
        if not self.correction_history:
            self.show_error_message("No corrections to export")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, 
            'Export Corrections',
            '',
            f'{format_type} Files (*{EXPORT_FORMATS[format_type]})'
        )

        if not filename:
            return

        try:
            if format_type == 'CSV':
                self.export_to_csv(filename)
            elif format_type == 'JSON':
                self.export_to_json(filename)
            elif format_type == 'TXT':
                self.export_to_txt(filename)
            elif format_type == 'PDF':
                self.export_to_pdf(filename)
                
            self.status_bar.showMessage(f'Successfully exported to {filename}')
        except Exception as e:
            self.show_error_message(f"Export failed: {str(e)}")

    def export_to_csv(self, filename: str) -> None:
        """Export correction history to CSV format.""" 
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.correction_history[0].keys())
            writer.writeheader()
            writer.writerows(self.correction_history)

    def export_to_json(self, filename: str) -> None:
        """Export correction history to JSON format.""" 
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.correction_history, file, indent=4)

    def export_to_txt(self, filename: str) -> None:
        """Export correction history to plain text format.""" 
        with open(filename, 'w', encoding='utf-8') as file:
            for entry in self.correction_history:
                file.write(f"Time: {entry['timestamp']}\n")
                file.write(f"Input: {entry['input']}\n")
                file.write(f"Corrected: {entry['corrected']}\n")
                file.write(f"Settings: {entry['mode']}, {entry['severity']}, {entry['language']}\n")
                file.write("-" * 80 + "\n")

    def export_to_pdf(self, filename: str) -> None:
        """Export correction history to PDF format.""" 
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet

            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Convert correction history to table data
            data = [['Time', 'Input', 'Corrected', 'Settings']]
            for entry in self.correction_history:
                data.append([
                    entry['timestamp'],
                    entry['input'],
                    entry['corrected'],
                    f"{entry['mode']}, {entry['severity']}, {entry['language']}"
                ])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            doc.build(elements)
        except ImportError:
            raise ImportError("reportlab is required for PDF export")

    def check_for_updates(self) -> None:
        """Check for application updates.""" 
        try:
            response = requests.get(UPDATE_CHECK_CONFIG['api_endpoint'])
            if response.status_code == 200:
                latest_version = response.json()['tag_name']
                current_version = '2.0'  # Should be stored in a constant
                
                if latest_version > current_version:
                    self.show_update_dialog(latest_version)
        except Exception as e:
            logger.error(f"Update check failed: {e}")

    def show_update_dialog(self, new_version: str) -> None:
        """Show update available dialog.""" 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Update Available")
        msg.setText(f"A new version ({new_version}) is available!")
        msg.setInformativeText("Would you like to visit the download page?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec_() == QMessageBox.Yes:
            import webbrowser
            webbrowser.open('https://github.com/yourusername/typing_assistant/releases/latest')

def main() -> None:
    """Main function to run the application.""" 
    app = QApplication(sys.argv)
    
    # Load the stylesheet
    try:
        stylesheet_path = os.path.join(os.path.dirname(__file__), 'styles.qss')
        with open(stylesheet_path, 'r') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        logger.error(f"Failed to load stylesheet: {e}")
    
    window = EnhancedTypingAssistant()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

class PerformanceMonitor:
    """Monitor and profile application performance."""
    
    def __init__(self):
        """Initialize performance monitor."""
        try:
            self.profiler = cProfile.Profile()
            self.stats = None
            self.monitoring = False
            self._start_time = None
            self._metrics = {
                'total_time': 0,
                'total_calls': 0,
                'function_stats': [],
                'memory_usage': 0
            }
            logger.info("Performance monitor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize performance monitor: {e}")
            raise
    
    def start(self) -> None:
        """Start performance monitoring."""
        try:
            if not self.monitoring:
                self.profiler.enable()
                self._start_time = datetime.now()
                self.monitoring = True
                logger.debug("Performance monitoring started")
        except Exception as e:
            logger.error(f"Failed to start performance monitoring: {e}")
            self.monitoring = False
    
    def stop(self) -> Dict[str, Any]:
        """Stop monitoring and return statistics."""
        if not self.monitoring:
            return self._metrics
            
        try:
            self.profiler.disable()
            self.monitoring = False
            
            # Calculate elapsed time
            if self._start_time:
                elapsed = (datetime.now() - self._start_time).total_seconds()
                self._metrics['total_time'] = elapsed
            
            # Process statistics
            import pstats
            from io import StringIO
            
            s = StringIO()
            ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
            ps.print_stats()
            
            # Update metrics
            self._metrics.update({
                'total_calls': getattr(ps, 'total_calls', 0),
                'function_stats': self._parse_function_stats(s.getvalue()),
                'memory_usage': self._get_memory_usage()
            })
            
            logger.debug("Performance monitoring stopped")
            return self._metrics
            
        except Exception as e:
            logger.error(f"Error stopping performance monitor: {e}")
            return self._metrics
    
    def _parse_function_stats(self, stats_str: str) -> List[Dict[str, Any]]:
        """Parse profiler output into structured data."""
        try:
            lines = stats_str.split('\n')[5:]  # Skip header
            parsed_stats = []
            
            for line in lines:
                if line.strip() and ('typing_assistant' in line or 'enhanced_typing_assistant' in line):
                    parts = line.strip().split()
                    if len(parts) >= 6:
                        parsed_stats.append({
                            'ncalls': parts[0],
                            'tottime': float(parts[1]),
                            'percall': float(parts[2]),
                            'cumtime': float(parts[3]),
                            'function': parts[5]
                        })
            return parsed_stats
        except Exception as e:
            logger.error(f"Error parsing function stats: {e}")
            return []
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            logger.warning("psutil not available, memory usage tracking disabled")
            return 0
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return 0
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self._metrics.copy()
