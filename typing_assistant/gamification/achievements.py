"""Achievement and milestone tracking for typing assistant"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class Achievement:
    """Data class for achievement information"""
    id: str
    name: str
    description: str
    category: str
    threshold: float
    icon: str
    unlocked: bool = False
    unlock_date: Optional[str] = None
    progress: float = 0.0

class AchievementTracker:
    """Tracks user achievements and milestones"""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self._load_achievements()
        
    def _load_achievements(self):
        """Initialize available achievements"""
        self.achievements = {
            # Speed achievements
            'speed_beginner': Achievement(
                'speed_beginner',
                'Speed Demon I',
                'Reach 30 WPM',
                'speed',
                30.0,
                '🏃'
            ),
            'speed_intermediate': Achievement(
                'speed_intermediate',
                'Speed Demon II',
                'Reach 45 WPM',
                'speed',
                45.0,
                '⚡'
            ),
            'speed_advanced': Achievement(
                'speed_advanced',
                'Speed Demon III',
                'Reach 60 WPM',
                'speed',
                60.0,
                '🚀'
            ),
            
            # Accuracy achievements
            'accuracy_bronze': Achievement(
                'accuracy_bronze',
                'Precision I',
                'Maintain 90% accuracy',
                'accuracy',
                90.0,
                '🎯'
            ),
            'accuracy_silver': Achievement(
                'accuracy_silver',
                'Precision II',
                'Maintain 95% accuracy',
                'accuracy',
                95.0,
                '✨'
            ),
            'accuracy_gold': Achievement(
                'accuracy_gold',
                'Precision III',
                'Maintain 98% accuracy',
                'accuracy',
                98.0,
                '🌟'
            ),
            
            # Streak achievements
            'streak_bronze': Achievement(
                'streak_bronze',
                'Streak I',
                'Achieve a 10-word streak',
                'streak',
                10.0,
                '🔥'
            ),
            'streak_silver': Achievement(
                'streak_silver',
                'Streak II',
                'Achieve a 25-word streak',
                'streak',
                25.0,
                '⚡'
            ),
            'streak_gold': Achievement(
                'streak_gold',
                'Streak III',
                'Achieve a 50-word streak',
                'streak',
                50.0,
                '🏆'
            ),
            
            # Session achievements
            'session_bronze': Achievement(
                'session_bronze',
                'Dedicated I',
                'Complete a 5-minute session',
                'session',
                5.0,
                '⏱️'
            ),
            'session_silver': Achievement(
                'session_silver',
                'Dedicated II',
                'Complete a 15-minute session',
                'session',
                15.0,
                '⌚'
            ),
            'session_gold': Achievement(
                'session_gold',
                'Dedicated III',
                'Complete a 30-minute session',
                'session',
                30.0,
                '🕒'
            ),
            
            # Improvement achievements
            'improvement_bronze': Achievement(
                'improvement_bronze',
                'Progress I',
                'Improve WPM by 10%',
                'improvement',
                10.0,
                '📈'
            ),
            'improvement_silver': Achievement(
                'improvement_silver',
                'Progress II',
                'Improve WPM by 25%',
                'improvement',
                25.0,
                '🎓'
            ),
            'improvement_gold': Achievement(
                'improvement_gold',
                'Progress III',
                'Improve WPM by 50%',
                'improvement',
                50.0,
                '🎯'
            ),
        }
    
    def update_achievements(self, stats: Dict[str, float]) -> List[Achievement]:
        """Update achievements based on current stats
        
        Args:
            stats: Current typing statistics
            
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        try:
            # Check speed achievements
            if 'wpm' in stats:
                newly_unlocked.extend(self._check_category('speed', stats['wpm']))
            
            # Check accuracy achievements
            if 'accuracy' in stats:
                newly_unlocked.extend(self._check_category('accuracy', stats['accuracy']))
            
            # Check streak achievements
            if 'streak' in stats:
                newly_unlocked.extend(self._check_category('streak', stats['streak']))
            
            # Check session achievements
            if 'time' in stats:
                minutes = stats['time'] / 60
                newly_unlocked.extend(self._check_category('session', minutes))
            
            # Check improvement achievements
            if 'improvement' in stats:
                newly_unlocked.extend(self._check_category('improvement', stats['improvement']))
            
            return newly_unlocked
            
        except Exception as e:
            logger.error(f"Error updating achievements: {e}")
            return []
    
    def _check_category(self, category: str, value: float) -> List[Achievement]:
        """Check achievements in a category against a value
        
        Args:
            category: Achievement category to check
            value: Value to check against thresholds
            
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        for achievement in self.achievements.values():
            if (achievement.category == category and 
                not achievement.unlocked and 
                value >= achievement.threshold):
                
                achievement.unlocked = True
                achievement.unlock_date = datetime.now().isoformat()
                achievement.progress = 100.0
                newly_unlocked.append(achievement)
            elif achievement.category == category:
                achievement.progress = min((value / achievement.threshold) * 100, 99.9)
        
        return newly_unlocked
    
    def save_achievements(self, filepath: str) -> None:
        """Save achievements to file
        
        Args:
            filepath: Path to save achievements
        """
        try:
            data = {
                id: {
                    'unlocked': achievement.unlocked,
                    'unlock_date': achievement.unlock_date,
                    'progress': achievement.progress
                }
                for id, achievement in self.achievements.items()
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving achievements to {filepath}: {e}")
    
    def load_achievements(self, filepath: str) -> None:
        """Load achievements from file
        
        Args:
            filepath: Path to load achievements from
        """
        try:
            if not os.path.exists(filepath):
                return
                
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            for id, achievement_data in data.items():
                if id in self.achievements:
                    achievement = self.achievements[id]
                    achievement.unlocked = achievement_data['unlocked']
                    achievement.unlock_date = achievement_data['unlock_date']
                    achievement.progress = achievement_data['progress']
                    
        except Exception as e:
            logger.error(f"Error loading achievements from {filepath}: {e}")
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements
        
        Returns:
            List of all achievements
        """
        return list(self.achievements.values())
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get unlocked achievements
        
        Returns:
            List of unlocked achievements
        """
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_next_achievements(self) -> List[Achievement]:
        """Get next achievements to unlock
        
        Returns:
            List of next achievements to target
        """
        return [
            a for a in self.achievements.values()
            if not a.unlocked and a.progress > 0
        ]
