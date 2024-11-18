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

def apply_theme(window, theme='default'):
    """Apply theme to the application window"""
    palette = QPalette()
    
    if theme.lower() == 'dark':
        # Dark theme colors
        bg_color = QColor("#2b2b2b")
        text_color = QColor("#ffffff")
        menu_color = QColor("#3b3b3b")
        highlight_color = QColor("#323232")
    elif theme.lower() == 'high_contrast':
        # High contrast theme
        bg_color = QColor("#000000")
        text_color = QColor("#ffffff")
        menu_color = QColor("#000000")
        highlight_color = QColor("#0066cc")
    else:
        # Default light theme
        bg_color = QColor("#f0f0f0")
        text_color = QColor("#000000")
        menu_color = QColor("#ffffff")
        highlight_color = QColor("#e0e0e0")

    # Set colors for various UI elements
    palette.setColor(QPalette.Window, bg_color)
    palette.setColor(QPalette.WindowText, text_color)
    palette.setColor(QPalette.Base, bg_color)
    palette.setColor(QPalette.AlternateBase, highlight_color)
    palette.setColor(QPalette.Text, text_color)
    palette.setColor(QPalette.Button, menu_color)
    palette.setColor(QPalette.ButtonText, text_color)
    palette.setColor(QPalette.Highlight, highlight_color)
    palette.setColor(QPalette.HighlightedText, text_color)

    # Apply palette to window
    window.setPalette(palette)

    # Style sheet for menus and other widgets
    window.setStyleSheet(f"""
        QMenuBar {{
            background-color: {menu_color.name()};
            color: {text_color.name()};
            border-bottom: 1px solid {highlight_color.name()};
        }}
        QMenuBar::item:selected {{
            background-color: {highlight_color.name()};
        }}
        QMenu {{
            background-color: {menu_color.name()};
            color: {text_color.name()};
            border: 1px solid {highlight_color.name()};
        }}
        QMenu::item:selected {{
            background-color: {highlight_color.name()};
        }}
        QComboBox {{
            background-color: {bg_color.name()};
            color: {text_color.name()};
            border: 1px solid {highlight_color.name()};
            padding: 5px;
        }}
        QTextEdit {{
            background-color: {bg_color.name()};
            color: {text_color.name()};
            border: 1px solid {highlight_color.name()};
            padding: 5px;
        }}
    """)
