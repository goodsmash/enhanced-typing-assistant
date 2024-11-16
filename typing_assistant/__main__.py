"""Main entry point for the typing assistant application."""

import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QSettings

from .ui.main_window import MainWindow
from .ui.setup_wizard import SetupWizard
from .utils.config_manager import ConfigManager
from .utils.security import SecurityManager
from .ui.accessibility import AccessibilityManager


def is_first_run() -> bool:
    """Check if this is the first time running the application."""
    settings = QSettings("TypingAssistant", "FirstRun")
    first_run = settings.value("FirstRun", True, type=bool)
    if first_run:
        settings.setValue("FirstRun", False)
    return first_run


def ensure_config_directory() -> None:
    """Ensure the configuration directory exists."""
    config_dir = Path.home() / ".typing_assistant"
    config_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (config_dir / "logs").mkdir(exist_ok=True)
    (config_dir / "cache").mkdir(exist_ok=True)
    (config_dir / "data").mkdir(exist_ok=True)


def run_setup_wizard(app: QApplication) -> bool:
    """Run the setup wizard.
    
    Returns:
        bool: True if setup was completed successfully, False otherwise
    """
    config_manager = ConfigManager()
    security_manager = SecurityManager()
    accessibility_manager = AccessibilityManager()
    
    wizard = SetupWizard(config_manager, security_manager, accessibility_manager)
    result = wizard.exec_()
    
    return result == wizard.Accepted


def main():
    """Run the typing assistant application."""
    # Enable High DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better accessibility
    
    # Ensure config directory exists
    ensure_config_directory()
    
    # Check for first run
    if is_first_run():
        if not run_setup_wizard(app):
            sys.exit(1)  # Exit if setup was cancelled
    
    # Initialize managers
    config_manager = ConfigManager()
    security_manager = SecurityManager()
    accessibility_manager = AccessibilityManager()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())
