from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import logging

class ThemeManager:
    """
    Manages application themes and color schemes.
    """
    
    THEMES = {
        'Light': {
            'window': '#FFFFFF',
            'window_text': '#000000',
            'base': '#F0F0F0',
            'alternate_base': '#E0E0E0',
            'text': '#000000',
            'button': '#E0E0E0',
            'button_text': '#000000',
            'bright_text': '#FFFFFF',
            'link': '#0000FF',
            'highlight': '#308CC6',
            'highlight_text': '#FFFFFF'
        },
        'Dark': {
            'window': '#2B2B2B',
            'window_text': '#FFFFFF',
            'base': '#323232',
            'alternate_base': '#3B3B3B',
            'text': '#FFFFFF',
            'button': '#454545',
            'button_text': '#FFFFFF',
            'bright_text': '#FFFFFF',
            'link': '#56A0DB',
            'highlight': '#2D5C88',
            'highlight_text': '#FFFFFF'
        },
        'High Contrast': {
            'window': '#000000',
            'window_text': '#FFFFFF',
            'base': '#000000',
            'alternate_base': '#1A1A1A',
            'text': '#FFFFFF',
            'button': '#FFFFFF',
            'button_text': '#000000',
            'bright_text': '#FFFFFF',
            'link': '#00FF00',
            'highlight': '#FFFFFF',
            'highlight_text': '#000000'
        },
        'Colorblind Mode': {
            'window': '#FFFFFF',
            'window_text': '#000000',
            'base': '#F5F5F5',
            'alternate_base': '#E6E6E6',
            'text': '#000000',
            'button': '#E6E6E6',
            'button_text': '#000000',
            'bright_text': '#FFFFFF',
            'link': '#0066FF',
            'highlight': '#FFB366',
            'highlight_text': '#000000'
        }
    }
    
    @staticmethod
    def apply_theme(widget, theme_name: str) -> None:
        """
        Apply a theme to a widget and all its children.
        
        :param widget: QWidget - The widget to apply the theme to.
        :param theme_name: str - Name of the theme to apply.
        """
        if theme_name not in ThemeManager.THEMES:
            logging.warning(f"Theme '{theme_name}' not found. Using Light theme.")
            theme_name = 'Light'
            
        theme = ThemeManager.THEMES[theme_name]
        palette = QPalette()
        
        # Set color roles
        palette.setColor(QPalette.Window, QColor(theme['window']))
        palette.setColor(QPalette.WindowText, QColor(theme['window_text']))
        palette.setColor(QPalette.Base, QColor(theme['base']))
        palette.setColor(QPalette.AlternateBase, QColor(theme['alternate_base']))
        palette.setColor(QPalette.Text, QColor(theme['text']))
        palette.setColor(QPalette.Button, QColor(theme['button']))
        palette.setColor(QPalette.ButtonText, QColor(theme['button_text']))
        palette.setColor(QPalette.BrightText, QColor(theme['bright_text']))
        palette.setColor(QPalette.Link, QColor(theme['link']))
        palette.setColor(QPalette.Highlight, QColor(theme['highlight']))
        palette.setColor(QPalette.HighlightedText, QColor(theme['highlight_text']))
        
        widget.setPalette(palette)
        
    @staticmethod
    def get_available_themes() -> list:
        """
        Get a list of available themes.
        
        :return: list - List of theme names.
        """
        return list(ThemeManager.THEMES.keys())
    
    @staticmethod
    def get_theme_colors(theme_name: str) -> dict:
        """
        Get the color scheme for a specific theme.
        
        :param theme_name: str - Name of the theme.
        :return: dict - Dictionary of color values.
        """
        if theme_name not in ThemeManager.THEMES:
            logging.warning(f"Theme '{theme_name}' not found. Using Light theme.")
            theme_name = 'Light'
            
        return ThemeManager.THEMES[theme_name].copy()
