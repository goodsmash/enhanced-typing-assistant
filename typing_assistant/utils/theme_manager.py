"""Theme management functionality."""

from typing import Dict, Any


class ThemeManager:
    """Manages application themes and styles."""

    def __init__(self):
        """Initialize theme manager."""
        self.current_theme = "default"
        self.high_contrast = False
        self._load_themes()

    def _load_themes(self) -> None:
        """Load theme definitions."""
        self.themes = {
            "default": {
                "stylesheet": """
                    QMainWindow {
                        background-color: #f0f0f0;
                    }
                    QTextEdit {
                        background-color: white;
                        color: black;
                        border: 1px solid #c0c0c0;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                    QPushButton:pressed {
                        background-color: #005a9e;
                    }
                    QComboBox {
                        background-color: white;
                        border: 1px solid #c0c0c0;
                        border-radius: 4px;
                        padding: 4px;
                        min-width: 100px;
                    }
                    QSlider::groove:horizontal {
                        border: 1px solid #999999;
                        height: 8px;
                        background: #ffffff;
                        margin: 2px 0;
                        border-radius: 4px;
                    }
                    QSlider::handle:horizontal {
                        background: #0078d4;
                        border: 1px solid #5c5c5c;
                        width: 18px;
                        margin: -2px 0;
                        border-radius: 9px;
                    }
                    QLabel {
                        color: #333333;
                    }
                    QCheckBox {
                        color: #333333;
                    }
                    QSpinBox {
                        background-color: white;
                        border: 1px solid #c0c0c0;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """
            },
            "dark": {
                "stylesheet": """
                    QMainWindow {
                        background-color: #1e1e1e;
                    }
                    QTextEdit {
                        background-color: #252526;
                        color: #d4d4d4;
                        border: 1px solid #3c3c3c;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                    QPushButton:pressed {
                        background-color: #005a9e;
                    }
                    QComboBox {
                        background-color: #252526;
                        color: #d4d4d4;
                        border: 1px solid #3c3c3c;
                        border-radius: 4px;
                        padding: 4px;
                        min-width: 100px;
                    }
                    QSlider::groove:horizontal {
                        border: 1px solid #3c3c3c;
                        height: 8px;
                        background: #252526;
                        margin: 2px 0;
                        border-radius: 4px;
                    }
                    QSlider::handle:horizontal {
                        background: #0078d4;
                        border: 1px solid #3c3c3c;
                        width: 18px;
                        margin: -2px 0;
                        border-radius: 9px;
                    }
                    QLabel {
                        color: #d4d4d4;
                    }
                    QCheckBox {
                        color: #d4d4d4;
                    }
                    QSpinBox {
                        background-color: #252526;
                        color: #d4d4d4;
                        border: 1px solid #3c3c3c;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """
            },
            "high_contrast": {
                "stylesheet": """
                    QMainWindow {
                        background-color: black;
                    }
                    QTextEdit {
                        background-color: black;
                        color: white;
                        border: 2px solid white;
                        border-radius: 0px;
                        padding: 8px;
                    }
                    QPushButton {
                        background-color: black;
                        color: white;
                        border: 2px solid white;
                        border-radius: 0px;
                        padding: 6px 12px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: white;
                        color: black;
                    }
                    QPushButton:pressed {
                        background-color: yellow;
                        color: black;
                    }
                    QComboBox {
                        background-color: black;
                        color: white;
                        border: 2px solid white;
                        border-radius: 0px;
                        padding: 4px;
                        min-width: 100px;
                    }
                    QSlider::groove:horizontal {
                        border: 2px solid white;
                        height: 8px;
                        background: black;
                        margin: 2px 0;
                        border-radius: 0px;
                    }
                    QSlider::handle:horizontal {
                        background: white;
                        border: 2px solid white;
                        width: 18px;
                        margin: -2px 0;
                        border-radius: 0px;
                    }
                    QLabel {
                        color: white;
                    }
                    QCheckBox {
                        color: white;
                    }
                    QSpinBox {
                        background-color: black;
                        color: white;
                        border: 2px solid white;
                        border-radius: 0px;
                        padding: 4px;
                    }
                """
            }
        }

    def get_current_theme(self) -> Dict[str, Any]:
        """Get the current theme configuration."""
        if self.high_contrast:
            return self.themes["high_contrast"]
        return self.themes[self.current_theme]

    def set_theme(self, theme_name: str) -> None:
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
        else:
            raise ValueError(f"Theme '{theme_name}' not found")

    def set_high_contrast(self, enabled: bool) -> None:
        """Enable or disable high contrast mode."""
        self.high_contrast = enabled

    def get_available_themes(self) -> list:
        """Get list of available themes."""
        return list(self.themes.keys())
