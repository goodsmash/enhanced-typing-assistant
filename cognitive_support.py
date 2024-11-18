"""
Cognitive Support Module for Enhanced Typing Assistant
Specifically designed for users with cognitive challenges, post-concussion syndrome,
and other neurological conditions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import logging
from PyQt5.QtWidgets import QWidget, QTextEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPalette

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
    
    def __post_init__(self):
        if self.sensory_preferences is None:
            self.sensory_preferences = {
                "reduce_motion": True,
                "reduce_transparency": True,
                "high_contrast": False,
                "muted_colors": True
            }

class CognitiveSupportManager:
    """Manages cognitive accessibility features."""
    
    def __init__(self, parent: QWidget):
        self.parent = parent
        self.profile = CognitiveProfile()
        self.break_timer = QTimer()
        self.break_timer.timeout.connect(self.suggest_break)
        self.active_time = 0
        self.setup_break_monitoring()
        
        # Color overlays for different conditions
        self.color_overlays = {
            "post_concussion": QColor(255, 253, 208, 40),  # Soft yellow
            "migraine": QColor(203, 225, 255, 40),         # Soft blue
            "visual_stress": QColor(198, 255, 198, 40),    # Soft green
            "none": None
        }
        
        # Reading guide settings
        self.reading_guide_active = False
        self.reading_guide_position = 0
        
    def setup_break_monitoring(self):
        """Configure break monitoring system."""
        self.activity_timer = QTimer()
        self.activity_timer.setInterval(60000)  # Check every minute
        self.activity_timer.timeout.connect(self.monitor_activity)
        self.activity_timer.start()
        
    def monitor_activity(self):
        """Monitor user activity and suggest breaks."""
        self.active_time += 1
        if self.active_time >= 20:  # Suggest break after 20 minutes
            self.suggest_break()
            
    def suggest_break(self):
        """Suggest a break to the user."""
        from PyQt5.QtWidgets import QMessageBox
        if self.profile.break_reminders:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Time for a Break")
            msg.setInformativeText(
                "You've been working for a while. Consider taking a short break:\n\n"
                "• Look away from the screen for 20 seconds\n"
                "• Stretch gently\n"
                "• Take a few deep breaths"
            )
            msg.setWindowTitle("Break Reminder")
            msg.exec_()
            self.active_time = 0
            
    def apply_color_overlay(self, text_edit: QTextEdit):
        """Apply color overlay based on user's needs."""
        if self.profile.color_overlay:
            palette = text_edit.palette()
            color = self.color_overlays.get(self.profile.color_overlay)
            if color:
                palette.setColor(QPalette.Base, color)
                text_edit.setPalette(palette)
                
    def toggle_reading_guide(self, text_edit: QTextEdit):
        """Toggle the reading guide feature."""
        self.reading_guide_active = not self.reading_guide_active
        if self.reading_guide_active:
            # Implement reading guide highlight
            cursor = text_edit.textCursor()
            format = cursor.blockFormat()
            format.setBackground(QColor(255, 255, 200))
            cursor.setBlockFormat(format)
        else:
            # Remove reading guide highlight
            cursor = text_edit.textCursor()
            format = cursor.blockFormat()
            format.clearBackground()
            cursor.setBlockFormat(format)
            
    def adjust_for_fatigue(self, text_edit: QTextEdit):
        """Adjust interface for fatigue management."""
        if self.profile.fatigue_management:
            # Increase contrast and text size
            font = text_edit.font()
            font.setPointSize(font.pointSize() + 2)
            text_edit.setFont(font)
            
            # Adjust colors for reduced eye strain
            palette = text_edit.palette()
            palette.setColor(QPalette.Text, Qt.darkGray)
            palette.setColor(QPalette.Base, QColor(253, 253, 247))
            text_edit.setPalette(palette)
            
    def enable_focus_mode(self, text_edit: QTextEdit):
        """Enable focus mode for better concentration."""
        if self.profile.focus_assist:
            # Highlight current line
            text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
            format = text_edit.currentCharFormat()
            format.setBackground(QColor(252, 252, 250))
            text_edit.setCurrentCharFormat(format)
            
            # Dim non-active text
            palette = text_edit.palette()
            palette.setColor(QPalette.Inactive, QPalette.Text, Qt.lightGray)
            text_edit.setPalette(palette)
            
    def apply_memory_assists(self, text_edit: QTextEdit):
        """Apply memory assistance features."""
        if self.profile.memory_assist:
            # Implement auto-save
            self.setup_auto_save(text_edit)
            
            # Add visual cues for important content
            self.highlight_important_content(text_edit)
            
    def setup_auto_save(self, text_edit: QTextEdit):
        """Set up automatic saving of content."""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setInterval(60000)  # Save every minute
        self.auto_save_timer.timeout.connect(lambda: self.save_content(text_edit))
        self.auto_save_timer.start()
        
    def save_content(self, text_edit: QTextEdit):
        """Save content to prevent loss."""
        try:
            content = text_edit.toPlainText()
            with open("backup.txt", "w", encoding="utf-8") as f:
                f.write(content)
            logger.info("Content auto-saved successfully")
        except Exception as e:
            logger.error(f"Failed to auto-save content: {e}")
            
    def highlight_important_content(self, text_edit: QTextEdit):
        """Add visual cues for important content."""
        cursor = text_edit.textCursor()
        format = cursor.charFormat()
        
        # Highlight important patterns (dates, numbers, etc.)
        import re
        content = text_edit.toPlainText()
        patterns = {
            r'\d{1,2}/\d{1,2}/\d{2,4}': QColor(255, 240, 240),  # Dates
            r'\d+': QColor(240, 255, 240),                       # Numbers
            r'[A-Z][A-Z]+': QColor(240, 240, 255)               # Acronyms
        }
        
        for pattern, color in patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), cursor.KeepAnchor)
                format = cursor.charFormat()
                format.setBackground(color)
                cursor.setCharFormat(format)
                
    def adjust_for_post_concussion(self):
        """Apply settings optimized for post-concussion syndrome."""
        self.profile.light_sensitivity = True
        self.profile.reading_speed = "slow"
        self.profile.focus_assist = True
        self.profile.fatigue_management = True
        self.profile.color_overlay = "post_concussion"
        self.profile.sensory_preferences.update({
            "reduce_motion": True,
            "reduce_transparency": True,
            "high_contrast": False,
            "muted_colors": True
        })
        self.profile.break_reminders = True
        self.apply_post_concussion_settings()
        
    def apply_post_concussion_settings(self):
        """Apply specific settings for post-concussion syndrome."""
        # Adjust text display
        text_edit = self.parent.findChild(QTextEdit)
        if text_edit:
            # Increase line spacing
            font = text_edit.font()
            font.setPointSize(14)  # Larger text
            text_edit.setFont(font)
            
            # Set optimal colors
            palette = text_edit.palette()
            palette.setColor(QPalette.Base, self.color_overlays["post_concussion"])
            palette.setColor(QPalette.Text, QColor(70, 70, 70))  # Soft dark gray
            text_edit.setPalette(palette)
            
            # Adjust line spacing
            format = text_edit.document().defaultTextOption()
            format.setLineHeight(150, format.ProportionalHeight)
            text_edit.document().setDefaultTextOption(format)
            
        # Enable frequent breaks
        self.break_timer.setInterval(1200000)  # 20 minutes
        self.break_timer.start()
