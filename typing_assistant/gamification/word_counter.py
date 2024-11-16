"""Word counting and performance tracking for typing assistant"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import deque
import json
import logging
from dataclasses import dataclass, asdict
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class TypingStats:
    """Data class for typing statistics"""
    words: int = 0
    chars: int = 0
    time: float = 0.0
    wpm: float = 0.0
    accuracy: float = 100.0
    corrections: int = 0
    streak: int = 0
    longest_streak: int = 0
    correct_words: int = 0
    incorrect_words: int = 0

class WordCounter:
    def __init__(self, history_size: int = 1000):
        """Initialize word counter with configurable history size.
        
        Args:
            history_size: Maximum number of historical entries to keep
        """
        # Compile regex patterns
        self.word_pattern = re.compile(r'\b\w+\b')
        self.number_pattern = re.compile(r'\d+')
        
        # Initialize timing
        self.session_start = datetime.now()
        self.last_update = self.session_start
        self.stats = TypingStats()
        
        # Initialize histories with fixed size
        self.word_history = deque(maxlen=history_size)
        self.correction_history = deque(maxlen=history_size)
        self.wpm_history = deque(maxlen=history_size)
        
        # Thread safety
        self._lock = Lock()
        
        # Performance tracking
        self._last_minute_words = deque(maxlen=60)  # Rolling window for WPM
        self._current_streak = 0
        self._last_word = None
    
    def count_words(self, text: str, update_stats: bool = True) -> Dict[str, float]:
        """Count words and characters in the given text with improved accuracy.
        
        Args:
            text: Text to analyze
            update_stats: Whether to update session statistics
            
        Returns:
            Dictionary containing word count statistics
        """
        try:
            with self._lock:
                # Split into words and filter out numbers
                words = [w for w in self.word_pattern.findall(text) 
                        if not self.number_pattern.match(w)]
                
                # Count valid characters (excluding whitespace)
                chars = sum(1 for c in text if not c.isspace())
                
                if update_stats:
                    self.stats.words = len(words)
                    self.stats.chars = chars
                    self._update_performance_metrics()
                
                return {
                    'words': len(words),
                    'chars': chars,
                    'wpm': self.stats.wpm,
                    'accuracy': self.stats.accuracy,
                    'streak': self.stats.streak
                }
                
        except Exception as e:
            logger.error(f"Error counting words: {e}")
            return {
                'words': 0,
                'chars': 0,
                'wpm': 0.0,
                'accuracy': 100.0,
                'streak': 0
            }
    
    def _update_performance_metrics(self):
        """Update WPM and other performance metrics using rolling window."""
        current_time = datetime.now()
        elapsed_time = (current_time - self.last_update).total_seconds()
        
        # Only update if sufficient time has passed
        if elapsed_time >= 1.0:  # Update every second
            with self._lock:
                # Calculate WPM using rolling window
                self._last_minute_words.append((current_time, self.stats.words))
                
                # Remove old entries
                while (self._last_minute_words and 
                       (current_time - self._last_minute_words[0][0]).total_seconds() > 60):
                    self._last_minute_words.popleft()
                
                # Calculate current WPM
                if len(self._last_minute_words) >= 2:
                    time_diff = (self._last_minute_words[-1][0] - 
                               self._last_minute_words[0][0]).total_seconds() / 60
                    word_diff = (self._last_minute_words[-1][1] - 
                               self._last_minute_words[0][1])
                    
                    if time_diff > 0:
                        self.stats.wpm = round(word_diff / time_diff, 1)
                
                # Update session time
                self.stats.time = round((current_time - self.session_start).total_seconds(), 2)
                self.last_update = current_time
                
                # Add to history
                self.wpm_history.append({
                    'wpm': self.stats.wpm,
                    'timestamp': current_time.isoformat(),
                    'accuracy': self.stats.accuracy
                })
    
    def track_correction(self, original: str, corrected: str) -> Dict[str, float]:
        """Track a correction event with improved streak handling.
        
        Args:
            original: Original incorrect text
            corrected: Corrected text
            
        Returns:
            Updated statistics dictionary
        """
        try:
            with self._lock:
                self.stats.corrections += 1
                self.stats.incorrect_words += 1
                
                # Reset streak on correction
                if self._current_streak > 0:
                    self.stats.longest_streak = max(
                        self.stats.longest_streak, 
                        self._current_streak
                    )
                self._current_streak = 0
                self.stats.streak = 0
                
                # Store correction
                self.correction_history.append({
                    'original': original,
                    'corrected': corrected,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Update accuracy
                total_words = self.stats.correct_words + self.stats.incorrect_words
                if total_words > 0:
                    self.stats.accuracy = round(
                        (self.stats.correct_words / total_words) * 100, 1
                    )
                
                return asdict(self.stats)
                
        except Exception as e:
            logger.error(f"Error tracking correction: {e}")
            return asdict(TypingStats())
    
    def track_correct_word(self, word: str) -> None:
        """Track a correctly typed word.
        
        Args:
            word: The correctly typed word
        """
        with self._lock:
            self.stats.correct_words += 1
            self._current_streak += 1
            self.stats.streak = self._current_streak
            self.stats.longest_streak = max(
                self.stats.longest_streak,
                self._current_streak
            )
            self._last_word = word
    
    def get_stats(self) -> Dict[str, float]:
        """Get current typing statistics.
        
        Returns:
            Dictionary containing all current statistics
        """
        with self._lock:
            return asdict(self.stats)
    
    def reset_stats(self) -> None:
        """Reset all statistics to initial values."""
        with self._lock:
            self.session_start = datetime.now()
            self.last_update = self.session_start
            self.stats = TypingStats()
            self.word_history.clear()
            self.correction_history.clear()
            self.wpm_history.clear()
            self._last_minute_words.clear()
            self._current_streak = 0
            self._last_word = None
    
    def save_stats(self, filepath: str) -> None:
        """Save current statistics to a file.
        
        Args:
            filepath: Path to save statistics
        """
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'stats': asdict(self.stats),
                    'word_history': list(self.word_history),
                    'correction_history': list(self.correction_history),
                    'wpm_history': list(self.wpm_history)
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats to {filepath}: {e}")
    
    def load_stats(self, filepath: str) -> None:
        """Load statistics from a file.
        
        Args:
            filepath: Path to load statistics from
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.stats = TypingStats(**data['stats'])
                self.word_history = deque(data['word_history'], maxlen=self.word_history.maxlen)
                self.correction_history = deque(data['correction_history'], maxlen=self.correction_history.maxlen)
                self.wpm_history = deque(data['wpm_history'], maxlen=self.wpm_history.maxlen)
        except Exception as e:
            logger.error(f"Error loading stats from {filepath}: {e}")
