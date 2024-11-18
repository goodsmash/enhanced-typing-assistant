"""Main entry point for the Enhanced Typing Assistant application."""

import os
import sys
import logging
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox,
    QLabel, QPushButton, QSystemTrayIcon, QMenu, QDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer

from typing_assistant.config import (
    ConfigManager, APP_NAME, APP_VERSION, ERROR_MESSAGES,
    THEMES, FEATURES
)
from typing_assistant.ui.main_window import MainWindow
from typing_assistant.ui.auth_dialog import AuthDialog
from typing_assistant.ui.settings_dialog import SettingsDialog
from typing_assistant.core.text_processor import TextProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Application(QApplication):
    """Main application class with enhanced error handling and offline mode support."""
    
    def __init__(self, argv):
        """Initialize the application."""
        super().__init__(argv)
        
        # Set application info
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)
        
        # Initialize configuration
        self.config_manager = ConfigManager()
        
        # Set up theme
        self.apply_theme()
        
        # Initialize main window
        self.main_window: Optional[MainWindow] = None
        
        # System tray icon
        self.tray_icon: Optional[QSystemTrayIcon] = None
        
        # Error dialog currently shown
        self.error_dialog: Optional[QDialog] = None
        
        # Set up error handling
        sys.excepthook = self.handle_exception
        
    def apply_theme(self):
        """Apply the current theme to the application."""
        theme_name = self.config_manager.get_setting('General', 'theme', 'light')
        theme = THEMES.get(theme_name, THEMES['light'])
        
        style_sheet = f"""
            QMainWindow, QDialog {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {theme['secondary']};
            }}
            QLabel {{
                color: {theme['text']};
            }}
        """
        self.setStyleSheet(style_sheet)
        
    def setup_tray_icon(self):
        """Set up the system tray icon."""
        if not self.tray_icon:
            self.tray_icon = QSystemTrayIcon(self)
            icon = QIcon(str(Path(__file__).parent / 'resources' / 'app_icon.ico'))
            self.tray_icon.setIcon(icon)
            
            # Create tray menu
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Show")
            show_action.triggered.connect(self.show_main_window)
            settings_action = tray_menu.addAction("Settings")
            settings_action.triggered.connect(self.show_settings)
            tray_menu.addSeparator()
            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(self.quit)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
    def show_main_window(self):
        """Show or create the main window."""
        if not self.main_window:
            self.main_window = MainWindow(self.config_manager)
            self.main_window.show()
        else:
            self.main_window.show()
            self.main_window.activateWindow()
            
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.config_manager, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            self.apply_theme()
            if self.main_window:
                self.main_window.apply_settings()
                
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle keyboard interrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Show error dialog if not already showing one
        if not self.error_dialog:
            self.error_dialog = QDialog()
            self.error_dialog.setWindowTitle("Error")
            layout = QVBoxLayout()
            
            error_label = QLabel(f"An error occurred: {str(exc_value)}")
            error_label.setWordWrap(True)
            layout.addWidget(error_label)
            
            if self.config_manager.is_offline_mode():
                offline_label = QLabel(ERROR_MESSAGES['offline_mode'])
                offline_label.setWordWrap(True)
                layout.addWidget(offline_label)
                
            retry_button = QPushButton("Retry")
            retry_button.clicked.connect(self.retry_operation)
            layout.addWidget(retry_button)
            
            offline_button = QPushButton("Work Offline")
            offline_button.clicked.connect(self.enable_offline_mode)
            layout.addWidget(offline_button)
            
            self.error_dialog.setLayout(layout)
            self.error_dialog.show()
            
    def retry_operation(self):
        """Retry the last failed operation."""
        if self.error_dialog:
            self.error_dialog.close()
            self.error_dialog = None
        if self.main_window:
            self.main_window.retry_last_operation()
            
    def enable_offline_mode(self):
        """Enable offline mode and restart the application."""
        try:
            self.config_manager.set_offline_mode(True)
            if self.error_dialog:
                self.error_dialog.close()
                self.error_dialog = None
                
            # Show confirmation dialog
            QMessageBox.information(
                None,
                "Offline Mode",
                "Offline mode enabled. The application will now restart."
            )
            
            # Restart the application
            self.quit()
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            logger.error(f"Failed to enable offline mode: {e}")
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to enable offline mode: {str(e)}"
            )

def main():
    """Main entry point for the application."""
    try:
        app = Application(sys.argv)
        
        # Set up system tray
        app.setup_tray_icon()
        
        # Show authentication dialog if needed
        config_manager = app.config_manager
        if not config_manager.is_authenticated() and not config_manager.is_offline_mode():
            auth_dialog = AuthDialog(config_manager)
            if auth_dialog.exec_() != QDialog.Accepted:
                sys.exit(1)
        
        # Show main window
        app.show_main_window()
        
        # Start the event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to start application: {str(e)}\n\n"
            "Try running in offline mode or check the logs for more information."
        )
        sys.exit(1)

if __name__ == '__main__':
    main()
