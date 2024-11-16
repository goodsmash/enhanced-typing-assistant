from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

class StyleSheet:
    """Style sheets for the application"""
    
    MAIN_WINDOW = """
        QMainWindow {
            background-color: #f0f2f5;
        }
    """
    
    GROUP_BOX = """
        QGroupBox {
            background-color: white;
            border: 2px solid #e1e4e8;
            border-radius: 8px;
            margin-top: 1em;
            padding: 12px;
        }
        QGroupBox::title {
            color: #24292e;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            background-color: white;
        }
    """
    
    TEXT_EDIT = """
        QTextEdit {
            background-color: white;
            border: 2px solid #e1e4e8;
            border-radius: 6px;
            padding: 8px;
            selection-background-color: #0366d6;
            selection-color: white;
        }
        QTextEdit:focus {
            border: 2px solid #0366d6;
        }
    """
    
    BUTTON = """
        QPushButton {
            background-color: #2ea44f;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2c974b;
        }
        QPushButton:pressed {
            background-color: #288b43;
        }
        QPushButton:disabled {
            background-color: #94d3a2;
        }
    """
    
    SECONDARY_BUTTON = """
        QPushButton {
            background-color: #fafbfc;
            color: #24292e;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #f3f4f6;
            border-color: #c9ccd1;
        }
        QPushButton:pressed {
            background-color: #ebecf0;
        }
    """
    
    SPINBOX = """
        QSpinBox {
            background-color: white;
            border: 2px solid #e1e4e8;
            border-radius: 6px;
            padding: 4px;
        }
        QSpinBox:focus {
            border: 2px solid #0366d6;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            border: none;
            background-color: #f6f8fa;
            width: 20px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #e1e4e8;
        }
    """
    
    CHECKBOX = """
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #e1e4e8;
            border-radius: 4px;
        }
        QCheckBox::indicator:checked {
            background-color: #2ea44f;
            border-color: #2ea44f;
            image: url(check.png);
        }
        QCheckBox::indicator:hover {
            border-color: #0366d6;
        }
    """
    
    COMBOBOX = """
        QComboBox {
            background-color: white;
            border: 2px solid #e1e4e8;
            border-radius: 6px;
            padding: 4px 8px;
            min-width: 6em;
        }
        QComboBox:focus {
            border: 2px solid #0366d6;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: url(down-arrow.png);
        }
        QComboBox QAbstractItemView {
            border: 1px solid #e1e4e8;
            selection-background-color: #0366d6;
        }
    """
    
    SLIDER = """
        QSlider::groove:horizontal {
            border: 1px solid #e1e4e8;
            height: 4px;
            background: #f6f8fa;
            margin: 2px 0;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #2ea44f;
            border: none;
            width: 18px;
            height: 18px;
            margin: -8px 0;
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background: #2c974b;
        }
    """
    
    STATUS_BAR = """
        QStatusBar {
            background-color: #f6f8fa;
            color: #586069;
            border-top: 1px solid #e1e4e8;
        }
    """

class ColorSchemes:
    """Color schemes for the application"""
    
    DEFAULT = {
        'window': '#f0f2f5',
        'text': '#24292e',
        'primary': '#2ea44f',
        'secondary': '#0366d6',
        'border': '#e1e4e8',
        'hover': '#f3f4f6',
        'pressed': '#ebecf0',
        'disabled': '#959da5'
    }
    
    DARK = {
        'window': '#0d1117',
        'text': '#c9d1d9',
        'primary': '#238636',
        'secondary': '#1f6feb',
        'border': '#30363d',
        'hover': '#161b22',
        'pressed': '#1c2127',
        'disabled': '#484f58'
    }
    
    HIGH_CONTRAST = {
        'window': '#ffffff',
        'text': '#000000',
        'primary': '#006400',
        'secondary': '#0000ff',
        'border': '#000000',
        'hover': '#e6e6e6',
        'pressed': '#cccccc',
        'disabled': '#666666'
    }

def apply_theme(widget, theme='default'):
    """Apply a color theme to the widget and all its children"""
    if theme.lower() == 'dark':
        colors = ColorSchemes.DARK
    elif theme.lower() == 'high_contrast':
        colors = ColorSchemes.HIGH_CONTRAST
    else:
        colors = ColorSchemes.DEFAULT
        
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(colors['window']))
    palette.setColor(QPalette.WindowText, QColor(colors['text']))
    palette.setColor(QPalette.Base, QColor(colors['window']))
    palette.setColor(QPalette.AlternateBase, QColor(colors['hover']))
    palette.setColor(QPalette.Text, QColor(colors['text']))
    palette.setColor(QPalette.Button, QColor(colors['primary']))
    palette.setColor(QPalette.ButtonText, QColor('#ffffff'))
    palette.setColor(QPalette.Highlight, QColor(colors['secondary']))
    palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))
    
    widget.setPalette(palette)
