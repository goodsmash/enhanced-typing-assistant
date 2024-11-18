import pytest
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPalette
from modules.theme_manager import ThemeManager

def test_get_available_themes():
    """Test getting available themes."""
    themes = ThemeManager.get_available_themes()
    assert isinstance(themes, list)
    assert len(themes) > 0
    assert 'Light' in themes
    assert 'Dark' in themes
    assert 'High Contrast' in themes
    assert 'Colorblind Mode' in themes

def test_get_theme_colors():
    """Test getting theme colors."""
    colors = ThemeManager.get_theme_colors('Light')
    assert isinstance(colors, dict)
    assert 'window' in colors
    assert 'text' in colors
    assert 'button' in colors
    
    # Test invalid theme
    colors = ThemeManager.get_theme_colors('NonexistentTheme')
    assert colors == ThemeManager.THEMES['Light']

def test_apply_theme(qtbot):
    """Test applying theme to widget."""
    widget = QWidget()
    qtbot.addWidget(widget)
    
    # Test Light theme
    ThemeManager.apply_theme(widget, 'Light')
    palette = widget.palette()
    assert palette.color(QPalette.Window).name() == ThemeManager.THEMES['Light']['window']
    assert palette.color(QPalette.WindowText).name() == ThemeManager.THEMES['Light']['window_text']
    
    # Test Dark theme
    ThemeManager.apply_theme(widget, 'Dark')
    palette = widget.palette()
    assert palette.color(QPalette.Window).name() == ThemeManager.THEMES['Dark']['window']
    assert palette.color(QPalette.WindowText).name() == ThemeManager.THEMES['Dark']['window_text']
    
    # Test invalid theme (should default to Light)
    ThemeManager.apply_theme(widget, 'NonexistentTheme')
    palette = widget.palette()
    assert palette.color(QPalette.Window).name() == ThemeManager.THEMES['Light']['window']
