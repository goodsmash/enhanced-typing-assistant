"""
Cognitive Support Module for Enhanced Typing Assistant
Specifically designed for users with cognitive challenges, post-concussion syndrome,
and other neurological conditions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
import logging
from PyQt5.QtWidgets import QWidget, QTextEdit, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt5.QtGui import QColor, QPalette
import time
import re

logger = logging.getLogger(__name__)

@dataclass
class CognitiveProfile:
    """Represents user's cognitive needs and preferences."""
    light_sensitivity: bool = False
    reading_speed: str = "normal"  # slow, normal, fast
    focus_assist: bool = False
    memory_assist: bool = False
    fatigue_management: bool = False
    sensory_preferences: Dict[str, bool] = None
    reading_guide: bool = False
    break_reminders: bool = True
    color_overlay: Optional[str] = None
    font_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.sensory_preferences is None:
            self.sensory_preferences = {
                "reduce_motion": True,
                "reduce_transparency": True,
                "high_contrast": False,
                "muted_colors": True
            }
        if self.font_preferences is None:
            self.font_preferences = {
                "family": "OpenDyslexic",
                "size": 14,
                "line_spacing": 1.5,
                "letter_spacing": 0.5
            }

class CognitiveSupportManager:
    """Manages cognitive accessibility features with improved performance."""
    
    def __init__(self, parent: QWidget):
        self.parent = parent
        self.profile = CognitiveProfile()
        
        # Break management
        self.break_timer = QTimer()
        self.break_timer.timeout.connect(self.suggest_break)
        self.active_time = 0
        self.last_break_time = time.time()
        self.setup_break_monitoring()
        
        # Performance monitoring
        self.performance_metrics = {
            'breaks_taken': 0,
            'focus_duration': 0,
            'fatigue_indicators': 0,
            'ui_adjustments': 0
        }
        
        # Color overlays with alpha channel for different conditions
        self.color_overlays = {
            "post_concussion": QColor(255, 253, 208, 40),  # Soft yellow
            "migraine": QColor(203, 225, 255, 40),         # Soft blue
            "visual_stress": QColor(198, 255, 198, 40),    # Soft green
            "night_mode": QColor(40, 44, 52, 40),          # Dark mode
            "none": None
        }
        
        # Reading guide settings
        self.reading_guide_active = False
        self.reading_guide_position = 0
        self.guide_color = QColor(255, 255, 0, 30)  # Semi-transparent yellow
        
        # Initialize focus assistance
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self.check_focus)
        self.focus_timer.start(30000)  # Check every 30 seconds
        self.focus_metrics = []
        
        # Load user preferences
        self.load_user_preferences()
        
    def setup_break_monitoring(self):
        """Configure break monitoring system with adaptive timing."""
        self.activity_timer = QTimer()
        self.activity_timer.setInterval(60000)  # Check every minute
        self.activity_timer.timeout.connect(self.monitor_activity)
        self.activity_timer.start()
        
        # Adaptive break scheduling based on user patterns
        self.break_intervals = []
        self.fatigue_indicators = []
        
    def monitor_activity(self):
        """Monitor user activity with improved fatigue detection."""
        current_time = time.time()
        self.active_time += 1
        
        # Check for fatigue indicators
        fatigue_score = self.calculate_fatigue_score()
        self.fatigue_indicators.append(fatigue_score)
        
        # Adaptive break suggestion
        if self.should_suggest_break(fatigue_score):
            self.suggest_break()
            
    def calculate_fatigue_score(self) -> float:
        """Calculate user fatigue score based on multiple indicators."""
        indicators = {
            'time_since_break': min(1.0, (time.time() - self.last_break_time) / 3600),
            'typing_speed_change': self.get_typing_speed_change(),
            'error_rate': self.get_error_rate(),
            'focus_level': self.get_focus_level()
        }
        
        weights = {'time_since_break': 0.3, 'typing_speed_change': 0.3,
                  'error_rate': 0.2, 'focus_level': 0.2}
                  
        return sum(score * weights[indicator] for indicator, score in indicators.items())
        
    def should_suggest_break(self, fatigue_score: float) -> bool:
        """Determine if a break should be suggested based on fatigue score."""
        threshold = 0.7  # Adjustable threshold
        return (fatigue_score > threshold or 
                self.active_time >= 20 or  # 20 minutes maximum
                self.get_error_rate() > 0.2)  # Error rate threshold
                
    def suggest_break(self):
        """Suggest a break with personalized recommendations."""
        if not self.profile.break_reminders:
            return
            
        # Calculate optimal break duration
        break_duration = self.calculate_optimal_break_duration()
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Time for a Break")
        msg.setInformativeText(
            f"You've been working for {self.active_time} minutes. "
            f"Consider taking a {break_duration} minute break:\n\n"
            "• Look away from the screen (20-20-20 rule)\n"
            "• Gentle stretching exercises\n"
            "• Deep breathing\n"
            "• Stay hydrated"
        )
        msg.setWindowTitle("Break Reminder")
        
        # Add break timer
        self.start_break_timer(break_duration)
        
        msg.exec_()
        self.record_break_taken()
        
    def record_break_taken(self):
        """Record break statistics for adaptive scheduling."""
        self.performance_metrics['breaks_taken'] += 1
        self.last_break_time = time.time()
        self.active_time = 0
        self.fatigue_indicators = []
        
    def calculate_optimal_break_duration(self) -> int:
        """Calculate optimal break duration based on work session."""
        base_duration = 5  # Base 5-minute break
        
        # Adjust for fatigue
        fatigue_score = self.calculate_fatigue_score()
        fatigue_adjustment = int(fatigue_score * 5)  # Up to 5 additional minutes
        
        # Adjust for session length
        time_adjustment = int(self.active_time / 60)  # 1 minute per hour worked
        
        return min(20, base_duration + fatigue_adjustment + time_adjustment)
        
    def apply_color_overlay(self, text_edit: QTextEdit):
        """Apply color overlay with smooth transition."""
        if self.profile.color_overlay:
            try:
                color = self.color_overlays.get(self.profile.color_overlay)
                if color:
                    palette = text_edit.palette()
                    current_color = palette.color(QPalette.Base)
                    
                    # Smooth color transition
                    animation = QPropertyAnimation(text_edit, b"palette")
                    animation.setDuration(500)  # 500ms transition
                    animation.setStartValue(current_color)
                    animation.setEndValue(color)
                    animation.start()
                    
            except Exception as e:
                logger.error(f"Error applying color overlay: {e}")
                
    def check_focus(self):
        """Monitor user focus and provide assistance."""
        if not self.profile.focus_assist:
            return
            
        focus_level = self.get_focus_level()
        if focus_level < 0.6:  # Focus threshold
            self.provide_focus_assistance()
            
    def provide_focus_assistance(self):
        """Provide adaptive focus assistance."""
        # Implement focus assistance strategies
        strategies = [
            self.minimize_distractions,
            self.highlight_current_section,
            self.adjust_content_presentation
        ]
        
        for strategy in strategies:
            try:
                strategy()
            except Exception as e:
                logger.error(f"Error in focus assistance: {e}")
                
    def get_focus_level(self) -> float:
        """Calculate current focus level based on user interaction patterns."""
        # Implement focus level calculation
        return 0.8  # Placeholder
        
    def get_typing_speed_change(self) -> float:
        """Calculate recent change in typing speed."""
        # Implement typing speed change calculation
        return 0.0  # Placeholder
        
    def get_error_rate(self) -> float:
        """Calculate current error rate in typing."""
        # Implement error rate calculation
        return 0.0  # Placeholder
        
    def load_user_preferences(self):
        """Load and apply user cognitive support preferences."""
        try:
            # Load preferences from storage
            pass
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
            # Use defaults from CognitiveProfile
            
    def start_break_timer(self, duration: int):
        """Start break timer with specified duration."""
        self.break_timer.setInterval(duration * 60 * 1000)  # Convert minutes to milliseconds
        self.break_timer.start()
        
    def minimize_distractions(self):
        """Minimize distractions to improve focus."""
        # Implement distraction minimization strategies
        pass
        
    def highlight_current_section(self):
        """Highlight current section to improve focus."""
        # Implement section highlighting strategies
        pass
        
    def adjust_content_presentation(self):
        """Adjust content presentation to improve focus."""
        # Implement content presentation adjustments
        pass
