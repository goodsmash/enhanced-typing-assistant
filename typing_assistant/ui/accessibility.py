"""Accessibility features and settings for the typing assistant."""

from enum import Enum
from typing import Dict, Optional

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QWidget


class ColorScheme(Enum):
    """Color schemes for accessibility."""
    STANDARD = "standard"
    HIGH_CONTRAST = "high_contrast"
    DARK = "dark"
    DEUTERANOPIA = "deuteranopia"
    PROTANOPIA = "protanopia"
    TRITANOPIA = "tritanopia"


class TextSize(Enum):
    """Text size presets."""
    SMALL = 12
    MEDIUM = 14
    LARGE = 18
    EXTRA_LARGE = 24


class AccessibilityManager:
    """Manages accessibility settings and features."""

    def __init__(self):
        """Initialize accessibility manager."""
        self.settings = QSettings("TypingAssistant", "Accessibility")
        self._color_scheme = self.settings.value("color_scheme", ColorScheme.STANDARD.value)
        self._text_size = self.settings.value("text_size", TextSize.MEDIUM.value)
        self._screen_reader_enabled = self.settings.value("screen_reader", False, type=bool)
        self._keyboard_navigation = self.settings.value("keyboard_navigation", True, type=bool)
        self._auto_complete = self.settings.value("auto_complete", True, type=bool)
        self._word_prediction = self.settings.value("word_prediction", True, type=bool)
        self._typing_delay = self.settings.value("typing_delay", 0, type=int)

        # Color schemes for different modes
        self._color_schemes = {
            ColorScheme.STANDARD.value: {
                "window": "#f8f9fa",
                "text": "#212529",
                "background": "#ffffff",
                "accent": "#007bff",
                "error": "#dc3545",
                "success": "#28a745",
            },
            ColorScheme.HIGH_CONTRAST.value: {
                "window": "#000000",
                "text": "#ffffff",
                "background": "#000000",
                "accent": "#ffff00",
                "error": "#ff0000",
                "success": "#00ff00",
            },
            ColorScheme.DARK.value: {
                "window": "#212529",
                "text": "#f8f9fa",
                "background": "#343a40",
                "accent": "#0d6efd",
                "error": "#dc3545",
                "success": "#28a745",
            },
            ColorScheme.DEUTERANOPIA.value: {
                "window": "#f8f9fa",
                "text": "#000000",
                "background": "#ffffff",
                "accent": "#0000ff",
                "error": "#ff0000",
                "success": "#ffff00",
            },
            ColorScheme.PROTANOPIA.value: {
                "window": "#f8f9fa",
                "text": "#000000",
                "background": "#ffffff",
                "accent": "#0000ff",
                "error": "#ffff00",
                "success": "#00ffff",
            },
            ColorScheme.TRITANOPIA.value: {
                "window": "#f8f9fa",
                "text": "#000000",
                "background": "#ffffff",
                "accent": "#ff0000",
                "error": "#00ff00",
                "success": "#0000ff",
            },
        }

    def get_color_scheme(self) -> str:
        """Get current color scheme."""
        return self._color_scheme

    def set_color_scheme(self, scheme: str) -> None:
        """Set color scheme."""
        if scheme in [s.value for s in ColorScheme]:
            self._color_scheme = scheme
            self.settings.setValue("color_scheme", scheme)

    def get_colors(self) -> Dict[str, str]:
        """Get current color scheme colors."""
        return self._color_schemes.get(self._color_scheme, self._color_schemes[ColorScheme.STANDARD.value])

    def get_text_size(self) -> int:
        """Get current text size."""
        return self._text_size

    def set_text_size(self, size: int) -> None:
        """Set text size."""
        self._text_size = size
        self.settings.setValue("text_size", size)

    def get_font(self) -> QFont:
        """Get accessibility-aware font."""
        font = QFont()
        font.setPointSize(self._text_size)
        font.setFamily("Segoe UI")  # Accessible default font
        return font

    def apply_palette(self, widget: QWidget) -> None:
        """Apply accessibility color palette to widget."""
        colors = self.get_colors()
        palette = QPalette()

        # Set colors for different widget states
        palette.setColor(QPalette.Window, QColor(colors["window"]))
        palette.setColor(QPalette.WindowText, QColor(colors["text"]))
        palette.setColor(QPalette.Base, QColor(colors["background"]))
        palette.setColor(QPalette.AlternateBase, QColor(colors["background"]).lighter(110))
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        palette.setColor(QPalette.Button, QColor(colors["accent"]))
        palette.setColor(QPalette.ButtonText, QColor(colors["background"]))
        palette.setColor(QPalette.Highlight, QColor(colors["accent"]))
        palette.setColor(QPalette.HighlightedText, QColor(colors["background"]))
        palette.setColor(QPalette.Link, QColor(colors["accent"]))
        palette.setColor(QPalette.LinkVisited, QColor(colors["accent"]).darker(120))

        widget.setPalette(palette)

    def is_screen_reader_enabled(self) -> bool:
        """Check if screen reader is enabled."""
        return self._screen_reader_enabled

    def set_screen_reader_enabled(self, enabled: bool) -> None:
        """Enable or disable screen reader."""
        self._screen_reader_enabled = enabled
        self.settings.setValue("screen_reader", enabled)

    def is_keyboard_navigation_enabled(self) -> bool:
        """Check if keyboard navigation is enabled."""
        return self._keyboard_navigation

    def set_keyboard_navigation_enabled(self, enabled: bool) -> None:
        """Enable or disable keyboard navigation."""
        self._keyboard_navigation = enabled
        self.settings.setValue("keyboard_navigation", enabled)

    def is_auto_complete_enabled(self) -> bool:
        """Check if auto-complete is enabled."""
        return self._auto_complete

    def set_auto_complete_enabled(self, enabled: bool) -> None:
        """Enable or disable auto-complete."""
        self._auto_complete = enabled
        self.settings.setValue("auto_complete", enabled)

    def is_word_prediction_enabled(self) -> bool:
        """Check if word prediction is enabled."""
        return self._word_prediction

    def set_word_prediction_enabled(self, enabled: bool) -> None:
        """Enable or disable word prediction."""
        self._word_prediction = enabled
        self.settings.setValue("word_prediction", enabled)

    def get_typing_delay(self) -> int:
        """Get typing delay in milliseconds."""
        return self._typing_delay

    def set_typing_delay(self, delay: int) -> None:
        """Set typing delay in milliseconds."""
        self._typing_delay = max(0, delay)
        self.settings.setValue("typing_delay", self._typing_delay)

    def save_settings(self) -> None:
        """Save all accessibility settings."""
        self.settings.sync()

    def get_keyboard_shortcuts(self) -> Dict[str, str]:
        """Get keyboard shortcuts for accessibility features."""
        return {
            "toggle_screen_reader": "Ctrl+Alt+S",
            "increase_text_size": "Ctrl++",
            "decrease_text_size": "Ctrl+-",
            "toggle_high_contrast": "Ctrl+Alt+H",
            "toggle_dark_mode": "Ctrl+Alt+D",
            "toggle_color_blind_mode": "Ctrl+Alt+C",
            "toggle_word_prediction": "Ctrl+Alt+W",
            "toggle_auto_complete": "Ctrl+Alt+A",
            "focus_text_area": "Alt+T",
            "focus_controls": "Alt+C",
            "speak_selected": "Ctrl+Space",
            "speak_all": "Ctrl+Shift+Space",
        }

    def get_aria_label(self, widget: QWidget) -> Optional[str]:
        """Get ARIA label for widget."""
        return widget.property("aria-label")

    def set_aria_label(self, widget: QWidget, label: str) -> None:
        """Set ARIA label for widget."""
        widget.setProperty("aria-label", label)
        widget.setToolTip(label)  # Also set tooltip for visual hint
