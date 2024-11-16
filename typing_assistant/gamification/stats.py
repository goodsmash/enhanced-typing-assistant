"""User statistics and gamification tracking"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from threading import Lock
import os

logger = logging.getLogger(__name__)

@dataclass
class Achievement:
    """Achievement data class"""
    id: str
    name: str
    description: str
    xp_reward: int
    icon: str
    unlocked: bool = False
    unlock_date: Optional[str] = None

@dataclass
class DailyGoals:
    """Daily goals data class"""
    words: int = 0
    corrections: int = 0
    time_spent: float = 0.0
    completed: bool = False

@dataclass
class UserStatistics:
    """User statistics data class"""
    total_words: int = 0
    corrected_words: int = 0
    accuracy: float = 100.0
    streak_days: int = 0
    last_active: Optional[str] = None
    xp: int = 0
    level: int = 1
    daily_goals: DailyGoals = DailyGoals()
    achievements: List[Achievement] = None
    history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.achievements is None:
            self.achievements = []
        if self.history is None:
            self.history = []

class UserStats:
    def __init__(self, user_id: str, stats_dir: str = "user_stats"):
        """Initialize user statistics manager.
        
        Args:
            user_id: Unique user identifier
            stats_dir: Directory to store user statistics
        """
        self.user_id = user_id
        self.stats_dir = Path(stats_dir)
        self.stats_file = self.stats_dir / f"user_stats_{user_id}.json"
        self._lock = Lock()
        
        # Create stats directory if it doesn't exist
        os.makedirs(self.stats_dir, exist_ok=True)
        
        # Initialize stats
        self.stats = self._load_stats()
        
        # Define achievements
        self._init_achievements()
        
        # XP thresholds for levels
        self.level_thresholds = [
            1000,   # Level 2
            2500,   # Level 3
            5000,   # Level 4
            10000,  # Level 5
            20000,  # Level 6
            35000,  # Level 7
            50000,  # Level 8
            75000,  # Level 9
            100000  # Level 10
        ]
    
    def _init_achievements(self):
        """Initialize achievement definitions"""
        if not self.stats.achievements:
            self.stats.achievements = [
                Achievement(
                    id="first_session",
                    name="First Steps",
                    description="Complete your first typing session",
                    xp_reward=100,
                    icon="🎯"
                ),
                Achievement(
                    id="speed_demon",
                    name="Speed Demon",
                    description="Achieve 100 WPM",
                    xp_reward=500,
                    icon="⚡"
                ),
                Achievement(
                    id="accuracy_master",
                    name="Accuracy Master",
                    description="Maintain 98% accuracy for 1000 words",
                    xp_reward=300,
                    icon="🎯"
                ),
                Achievement(
                    id="streak_warrior",
                    name="Streak Warrior",
                    description="Maintain a 7-day streak",
                    xp_reward=400,
                    icon="🔥"
                ),
                Achievement(
                    id="word_master",
                    name="Word Master",
                    description="Type 10,000 words",
                    xp_reward=1000,
                    icon="📚"
                )
            ]
    
    def _load_stats(self) -> UserStatistics:
        """Load user statistics from file."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    return UserStatistics(**data)
            return UserStatistics()
        except Exception as e:
            logger.error(f"Error loading stats for user {self.user_id}: {e}")
            return UserStatistics()
    
    def _save_stats(self) -> None:
        """Save user statistics to file."""
        try:
            with self._lock:
                with open(self.stats_file, 'w') as f:
                    json.dump(asdict(self.stats), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats for user {self.user_id}: {e}")
    
    def update_word_count(self, words: int, corrected: int, wpm: float) -> Dict[str, Any]:
        """Update word count and related statistics.
        
        Args:
            words: Number of words typed
            corrected: Number of corrections made
            wpm: Words per minute
            
        Returns:
            Dictionary containing updated statistics and any unlocked achievements
        """
        try:
            with self._lock:
                self.stats.total_words += words
                self.stats.corrected_words += corrected
                
                # Update accuracy
                if self.stats.total_words > 0:
                    self.stats.accuracy = round(
                        (1 - (self.stats.corrected_words / self.stats.total_words)) * 100,
                        2
                    )
                
                # Update daily goals
                self.stats.daily_goals.words += words
                self.stats.daily_goals.corrections += corrected
                
                # Check achievements
                new_achievements = self._check_achievements(wpm)
                
                # Calculate XP
                xp_gained = self._calculate_xp(words, corrected, wpm)
                self.stats.xp += xp_gained
                
                # Check for level up
                old_level = self.stats.level
                self._update_level()
                leveled_up = self.stats.level > old_level
                
                # Update history
                self._update_history(words, corrected, wpm)
                
                # Save changes
                self._save_stats()
                
                return {
                    'stats': asdict(self.stats),
                    'new_achievements': new_achievements,
                    'xp_gained': xp_gained,
                    'leveled_up': leveled_up
                }
                
        except Exception as e:
            logger.error(f"Error updating word count: {e}")
            return {
                'stats': asdict(self.stats),
                'new_achievements': [],
                'xp_gained': 0,
                'leveled_up': False
            }
    
    def _calculate_xp(self, words: int, corrections: int, wpm: float) -> int:
        """Calculate XP gained from typing session.
        
        Args:
            words: Number of words typed
            corrections: Number of corrections made
            wpm: Words per minute
            
        Returns:
            XP points gained
        """
        # Base XP from words
        xp = words * 2
        
        # Speed bonus
        if wpm >= 60:
            xp += int(words * 0.5)  # 50% bonus for fast typing
        elif wpm >= 40:
            xp += int(words * 0.2)  # 20% bonus for moderate speed
        
        # Accuracy bonus
        accuracy = (words - corrections) / words if words > 0 else 0
        if accuracy >= 0.95:
            xp += int(words * 0.3)  # 30% bonus for high accuracy
        
        # Streak bonus
        if self.stats.streak_days > 0:
            xp = int(xp * (1 + min(self.stats.streak_days, 7) * 0.1))
        
        return xp
    
    def _update_level(self) -> None:
        """Update user level based on XP."""
        for level, threshold in enumerate(self.level_thresholds, 2):
            if self.stats.xp < threshold:
                self.stats.level = level
                break
        else:
            self.stats.level = len(self.level_thresholds) + 1
    
    def _check_achievements(self, wpm: float) -> List[Achievement]:
        """Check and update achievements.
        
        Args:
            wpm: Current words per minute
            
        Returns:
            List of newly unlocked achievements
        """
        new_achievements = []
        
        for achievement in self.stats.achievements:
            if not achievement.unlocked:
                unlocked = False
                
                if achievement.id == "first_session":
                    unlocked = self.stats.total_words > 0
                elif achievement.id == "speed_demon":
                    unlocked = wpm >= 100
                elif achievement.id == "accuracy_master":
                    unlocked = (self.stats.accuracy >= 98 and 
                              self.stats.total_words >= 1000)
                elif achievement.id == "streak_warrior":
                    unlocked = self.stats.streak_days >= 7
                elif achievement.id == "word_master":
                    unlocked = self.stats.total_words >= 10000
                
                if unlocked:
                    achievement.unlocked = True
                    achievement.unlock_date = datetime.now().isoformat()
                    self.stats.xp += achievement.xp_reward
                    new_achievements.append(achievement)
        
        return new_achievements
    
    def _update_history(self, words: int, corrections: int, wpm: float) -> None:
        """Update typing history.
        
        Args:
            words: Number of words typed
            corrections: Number of corrections made
            wpm: Words per minute
        """
        self.stats.history.append({
            'timestamp': datetime.now().isoformat(),
            'words': words,
            'corrections': corrections,
            'wpm': wpm,
            'accuracy': self.stats.accuracy,
            'xp': self.stats.xp,
            'level': self.stats.level
        })
        
        # Keep only last 30 days of history
        cutoff = datetime.now() - timedelta(days=30)
        self.stats.history = [
            h for h in self.stats.history 
            if datetime.fromisoformat(h['timestamp']) > cutoff
        ]
    
    def update_streak(self) -> None:
        """Update daily streak."""
        try:
            with self._lock:
                today = datetime.now().date()
                
                if self.stats.last_active:
                    last_active = datetime.fromisoformat(
                        self.stats.last_active
                    ).date()
                    
                    if today - last_active == timedelta(days=1):
                        self.stats.streak_days += 1
                    elif today != last_active:
                        self.stats.streak_days = 0
                
                self.stats.last_active = datetime.now().isoformat()
                self._save_stats()
                
        except Exception as e:
            logger.error(f"Error updating streak: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current user statistics.
        
        Returns:
            Dictionary containing all user statistics
        """
        with self._lock:
            return asdict(self.stats)
    
    def reset_daily_goals(self) -> None:
        """Reset daily goals."""
        with self._lock:
            self.stats.daily_goals = DailyGoals()
            self._save_stats()
