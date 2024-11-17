"""Typing Assistant Application with Real-time Correction and Accessibility Features"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                          QTextEdit, QLabel, QPushButton, QComboBox, QHBoxLayout,
                          QMessageBox, QShortcut, QMenuBar, QMenu, QAction, QToolBar,
                          QDockWidget, QFrame, QSplitter, QSlider, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QKeySequence

from .core.text_processor import TextProcessor
from .core.speech_handler import SpeechHandler
from .utils.config_manager import ConfigManager
from .utils.theme_manager import ThemeManager
from .ui.accessibility import AccessibilityManager
from .ui.keyboard_shortcuts import KeyboardShortcutsManager
from .ui.debug_panel import DebugPanel
from .ui.api_key_dialog import APIKeyDialog
from .ui.login_dialog import LoginDialog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / '.typing_assistant' / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TypingAssistantApp(QMainWindow):
    """Main application window with comprehensive accessibility features."""
    
    def __init__(self):
        """Initialize the application with all components."""
        super().__init__()
        try:
            # Initialize settings and components
            self.settings = QSettings('TypingAssistant', 'App')
            self.config_manager = ConfigManager()
            self.theme_manager = ThemeManager()
            self.text_processor = TextProcessor(self.config_manager.get_api_key())
            self.speech_handler = SpeechHandler()
            self.accessibility_manager = AccessibilityManager()
            
            # Create debug panel
            self.debug_panel = DebugPanel()
            self.debug_panel.hide()
            
            # Initialize timers
            self.correction_timer = QTimer()
            self.correction_timer.timeout.connect(self.correct_text)
            self.correction_timer.setInterval(1000)
            
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self.update_status)
            self.status_timer.start(5000)  # Update status every 5 seconds
            
            # Setup API connection and authentication
            self.setup_api_connection()
            self.check_auth_state()
            
            # Setup UI and connections
            self.init_ui()
            self.setup_connections()
            self.setup_shortcuts()
            self.apply_theme()
            
            # Initialize state
            self.is_processing = False
            self.is_listening = False
            self.last_correction = None
            
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing application: {e}", exc_info=True)
            self.show_error("Initialization Error", str(e))

    def setup_api_connection(self):
        """Setup API connection and handle offline mode."""
        try:
            # Check for API key
            self.api_key = self.config_manager.get_api_key()
            if not self.api_key:
                self.show_api_key_dialog()
            
            # Initialize API client with current settings
            self.api_settings = self.config_manager.get_api_settings()
            self.api_client = APIClient(
                api_key=self.api_key,
                **self.api_settings
            )
            
            # Update status
            self.update_connection_status()
            
        except Exception as e:
            logger.error(f"Error setting up API connection: {e}", exc_info=True)
            self.handle_connection_error()

    def show_api_key_dialog(self):
        """Show dialog to enter API key."""
        dialog = APIKeyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.api_key = dialog.api_key
            self.config_manager.set_api_key(self.api_key)
            self.setup_api_connection()

    def check_auth_state(self):
        """Check authentication state and show login if needed."""
        if not self.config_manager.is_authenticated():
            self.show_login_dialog()

    def show_login_dialog(self):
        """Show login dialog."""
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            success = self.config_manager.authenticate(
                dialog.username,
                dialog.password
            )
            if success:
                self.update_auth_status()
            else:
                QMessageBox.warning(
                    self,
                    "Login Failed",
                    "Invalid username or password. Please try again."
                )
                self.show_login_dialog()

    def update_auth_status(self):
        """Update UI based on authentication status."""
        is_auth = self.config_manager.is_authenticated()
        self.login_action.setVisible(not is_auth)
        self.logout_action.setVisible(is_auth)
        self.settings_action.setEnabled(is_auth)
        
        # Update status bar
        if is_auth:
            self.statusBar().showMessage("Logged in")
        else:
            self.statusBar().showMessage("Not logged in")

    def update_connection_status(self):
        """Update connection status in UI."""
        offline_mode = self.config_manager.is_offline_mode()
        has_api = bool(self.api_key)
        
        # Update status indicators
        self.connection_indicator.setPixmap(
            self.offline_icon if offline_mode else
            self.online_icon if has_api else
            self.error_icon
        )
        
        # Update status message
        if offline_mode:
            status = "Offline Mode"
        elif has_api:
            status = "Connected"
        else:
            status = "No API Key"
            
        self.connection_status.setText(status)
        
        # Update menu items
        self.offline_action.setChecked(offline_mode)
        self.api_settings_action.setEnabled(not offline_mode)

    def toggle_offline_mode(self, enabled: bool):
        """Toggle offline mode."""
        try:
            self.config_manager.set_offline_mode(enabled)
            self.update_connection_status()
            
            msg = "Offline mode enabled" if enabled else "Online mode enabled"
            self.statusBar().showMessage(msg, 3000)
            
        except Exception as e:
            logger.error(f"Error toggling offline mode: {e}", exc_info=True)
            QMessageBox.warning(
                self,
                "Error",
                "Failed to change connection mode. Please try again."
            )

    def handle_connection_error(self):
        """Handle API connection errors."""
        result = QMessageBox.warning(
            self,
            "Connection Error",
            "Failed to connect to the API. Would you like to enable offline mode?",
            QMessageBox.Yes | QMessageBox.No
        )
        if result == QMessageBox.Yes:
            self.toggle_offline_mode(True)

    def process_text(self, text: str) -> str:
        """Process text with appropriate mode."""
        try:
            if self.config_manager.is_offline_mode():
                # Use offline processing
                return self.text_processor.process_offline(text)
            else:
                # Use online API-based processing
                return self.text_processor.process_online(
                    text,
                    self.api_client
                )
                
        except Exception as e:
            logger.error(f"Error processing text: {e}", exc_info=True)
            self.handle_processing_error()
            return text

    def handle_processing_error(self):
        """Handle text processing errors."""
        result = QMessageBox.warning(
            self,
            "Processing Error",
            "Failed to process text. Would you like to switch to offline mode?",
            QMessageBox.Yes | QMessageBox.No
        )
        if result == QMessageBox.Yes:
            self.toggle_offline_mode(True)

    def init_ui(self):
        """Initialize the user interface with all features."""
        self.setWindowTitle('Typing Assistant')
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu and toolbar
        self.create_menu_bar()
        self.create_toolbar()
        
        # Create main content splitter
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Text editing
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        
        # Input area
        input_group = QFrame()
        input_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        input_layout = QVBoxLayout(input_group)
        
        input_label = QLabel('Type or speak your text:')
        input_layout.addWidget(input_label)
        
        self.input_text = QTextEdit()
        self.input_text.setAccessibleName('Main text input area')
        self.input_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: #4a9eff;
            }
        """)
        input_layout.addWidget(self.input_text)
        
        # Loading indicator
        self.loading_label = QLabel('')
        input_layout.addWidget(self.loading_label)
        
        text_layout.addWidget(input_group)
        
        # Output area
        output_group = QFrame()
        output_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        output_layout = QVBoxLayout(output_group)
        
        output_label = QLabel('Corrected text:')
        output_layout.addWidget(output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setAccessibleName('Corrected text output')
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #e9ecef;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        output_layout.addWidget(self.output_text)
        
        text_layout.addWidget(output_group)
        
        # Right side - Controls
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # Correction controls
        correction_group = QFrame()
        correction_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        correction_layout = QVBoxLayout(correction_group)
        
        # Mode selector
        mode_label = QLabel('Correction Mode:')
        correction_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Standard', 'Strict', 'Creative', 'AI'])
        correction_layout.addWidget(self.mode_combo)
        
        # Severity slider
        severity_label = QLabel('Correction Severity:')
        correction_layout.addWidget(severity_label)
        
        self.severity_slider = QSlider(Qt.Horizontal)
        self.severity_slider.setRange(0, 100)
        self.severity_slider.setValue(50)
        correction_layout.addWidget(self.severity_slider)
        
        control_layout.addWidget(correction_group)
        
        # Speech controls
        speech_group = QFrame()
        speech_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        speech_layout = QVBoxLayout(speech_group)
        
        speech_label = QLabel('Speech Controls:')
        speech_layout.addWidget(speech_label)
        
        speech_buttons = QHBoxLayout()
        
        self.speak_button = QPushButton('Speak Text')
        speech_buttons.addWidget(self.speak_button)
        
        self.listen_button = QPushButton('Start Listening')
        speech_buttons.addWidget(self.listen_button)
        
        speech_layout.addLayout(speech_buttons)
        
        # Voice settings
        voice_label = QLabel('Voice:')
        speech_layout.addWidget(voice_label)
        
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(self.speech_handler.get_available_voices())
        speech_layout.addWidget(self.voice_combo)
        
        # Speech rate
        rate_label = QLabel('Speech Rate:')
        speech_layout.addWidget(rate_label)
        
        self.rate_spin = QSpinBox()
        self.rate_spin.setRange(50, 400)
        self.rate_spin.setValue(200)
        speech_layout.addWidget(self.rate_spin)
        
        control_layout.addWidget(speech_group)
        
        # Accessibility controls
        accessibility_group = QFrame()
        accessibility_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        accessibility_layout = QVBoxLayout(accessibility_group)
        
        accessibility_label = QLabel('Accessibility:')
        accessibility_layout.addWidget(accessibility_label)
        
        self.high_contrast = QPushButton('Toggle High Contrast')
        accessibility_layout.addWidget(self.high_contrast)
        
        self.large_text = QPushButton('Toggle Large Text')
        accessibility_layout.addWidget(self.large_text)
        
        control_layout.addWidget(accessibility_group)
        
        # Add stretch to push controls to top
        control_layout.addStretch()
        
        # Add widgets to splitter
        content_splitter.addWidget(text_widget)
        content_splitter.addWidget(control_widget)
        content_splitter.setStretchFactor(0, 2)
        content_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.statusBar().showMessage('Ready')

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_document)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_document)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.input_text.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.input_text.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction('Cut', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.input_text.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction('Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.input_text.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.input_text.paste)
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        debug_action = QAction('Debug Panel', self)
        debug_action.setShortcut('Ctrl+D')
        debug_action.triggered.connect(self.toggle_debug_panel)
        view_menu.addAction(debug_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction('Help', self)
        help_action.setShortcut('F1')
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add quick access buttons
        new_btn = QPushButton('New')
        new_btn.clicked.connect(self.new_document)
        toolbar.addWidget(new_btn)
        
        open_btn = QPushButton('Open')
        open_btn.clicked.connect(self.open_document)
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_document)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        undo_btn = QPushButton('Undo')
        undo_btn.clicked.connect(self.input_text.undo)
        toolbar.addWidget(undo_btn)
        
        redo_btn = QPushButton('Redo')
        redo_btn.clicked.connect(self.input_text.redo)
        toolbar.addWidget(redo_btn)
        
        toolbar.addSeparator()
        
        speak_btn = QPushButton('Speak')
        speak_btn.clicked.connect(self.speak_text)
        toolbar.addWidget(speak_btn)
        
        listen_btn = QPushButton('Listen')
        listen_btn.clicked.connect(self.toggle_listening)
        toolbar.addWidget(listen_btn)

    def setup_connections(self):
        """Set up signal connections."""
        # Text correction
        self.input_text.textChanged.connect(self.start_correction_timer)
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        self.severity_slider.valueChanged.connect(
            lambda v: self.text_processor.set_correction_severity(v / 100)
        )
        
        # Speech
        self.speak_button.clicked.connect(self.speak_text)
        self.listen_button.clicked.connect(self.toggle_listening)
        self.voice_combo.currentTextChanged.connect(self.change_voice)
        self.rate_spin.valueChanged.connect(self.change_speech_rate)
        
        # Accessibility
        self.high_contrast.clicked.connect(self.toggle_high_contrast)
        self.large_text.clicked.connect(self.toggle_large_text)

    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # File shortcuts
        QShortcut(QKeySequence('Ctrl+N'), self, self.new_document)
        QShortcut(QKeySequence('Ctrl+O'), self, self.open_document)
        QShortcut(QKeySequence('Ctrl+S'), self, self.save_document)
        QShortcut(QKeySequence('Ctrl+Q'), self, self.close)
        
        # Edit shortcuts
        QShortcut(QKeySequence('Ctrl+Z'), self, self.input_text.undo)
        QShortcut(QKeySequence('Ctrl+Y'), self, self.input_text.redo)
        QShortcut(QKeySequence('Ctrl+X'), self, self.input_text.cut)
        QShortcut(QKeySequence('Ctrl+C'), self, self.input_text.copy)
        QShortcut(QKeySequence('Ctrl+V'), self, self.input_text.paste)
        
        # View shortcuts
        QShortcut(QKeySequence('Ctrl+D'), self, self.toggle_debug_panel)
        
        # Help shortcuts
        QShortcut(QKeySequence('F1'), self, self.show_help)
        
        # Accessibility shortcuts
        QShortcut(QKeySequence('Ctrl+H'), self, self.toggle_high_contrast)
        QShortcut(QKeySequence('Ctrl+L'), self, self.toggle_large_text)
        
        # Speech shortcuts
        QShortcut(QKeySequence('Ctrl+Space'), self, self.speak_text)
        QShortcut(QKeySequence('Ctrl+M'), self, self.toggle_listening)

    def start_correction_timer(self):
        """Start the correction timer and show loading indicator."""
        self.correction_timer.start()
        self.is_processing = True
        self.loading_label.setText('Processing...')
        self.loading_label.setAccessibleName('Text correction in progress')

    def correct_text(self):
        """Correct the input text and update the output with accessibility."""
        text = self.input_text.toPlainText()
        if text:
            corrected = self.process_text(text)
            self.output_text.setPlainText(corrected)
            
            # Update screen reader
            self.output_text.setAccessibleDescription(
                f'Corrected text: {corrected}'
            )
        
        self.correction_timer.stop()
        self.is_processing = False
        self.loading_label.setText('')
        self.loading_label.setAccessibleName('')

    def change_mode(self, mode):
        """Change the correction mode with accessibility announcement."""
        self.text_processor.correction_mode = mode.lower()
        self.mode_combo.setAccessibleDescription(f'Selected mode: {mode}')
        self.correct_text()

    def clear_text(self):
        """Clear both input and output text with accessibility."""
        self.input_text.clear()
        self.output_text.clear()
        self.loading_label.setText('')
        self.loading_label.setAccessibleName('')
        
        # Update screen reader
        self.input_text.setAccessibleDescription('Input text area cleared')
        self.output_text.setAccessibleDescription('Output text area cleared')

    def copy_corrected_text(self):
        """Copy corrected text to clipboard with accessibility."""
        text = self.output_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.loading_label.setText('Text copied to clipboard!')
            self.loading_label.setAccessibleName('Corrected text copied to clipboard')
            QTimer.singleShot(2000, lambda: self.loading_label.setText(''))

    def speak_text(self):
        """Speak the corrected text."""
        text = self.output_text.toPlainText()
        if text:
            self.speech_handler.speak_text(text)

    def toggle_listening(self):
        """Toggle listening mode."""
        if not self.is_listening:
            self.speech_handler.start_listening()
            self.is_listening = True
            self.listen_button.setText('Stop Listening')
        else:
            self.speech_handler.stop_listening()
            self.is_listening = False
            self.listen_button.setText('Start Listening')

    def change_voice(self, voice):
        """Change the speech voice."""
        self.speech_handler.set_voice(voice)

    def change_speech_rate(self, rate):
        """Change the speech rate."""
        self.speech_handler.set_speech_rate(rate)

    def toggle_high_contrast(self):
        """Toggle high contrast mode."""
        self.accessibility_manager.toggle_high_contrast()

    def toggle_large_text(self):
        """Toggle large text mode."""
        self.accessibility_manager.toggle_large_text()

    def new_document(self):
        """Create a new document."""
        self.input_text.clear()
        self.output_text.clear()

    def open_document(self):
        """Open an existing document."""
        # TODO: Implement file dialog to open document

    def save_document(self):
        """Save the current document."""
        # TODO: Implement file dialog to save document

    def show_settings(self):
        """Show the application settings."""
        # TODO: Implement settings dialog

    def show_about(self):
        """Show the about dialog."""
        # TODO: Implement about dialog

    def show_help(self):
        """Show the help dialog."""
        # TODO: Implement help dialog

    def toggle_debug_panel(self):
        """Toggle the debug panel."""
        if self.debug_panel.isVisible():
            self.debug_panel.hide()
        else:
            self.debug_panel.show()

    def apply_theme(self):
        """Apply the current theme to the application."""
        self.theme_manager.apply_theme()

    def update_status(self):
        """Update the application status."""
        # TODO: Implement status update logic

    def show_error(self, title, message):
        """Show an error message."""
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        """Handle application close event."""
        try:
            # Save application state
            self.settings.setValue('window/geometry', self.saveGeometry())
            self.settings.setValue('window/state', self.saveState())
            self.settings.setValue('correction/mode', self.mode_combo.currentText())
            self.settings.setValue('correction/severity', self.severity_slider.value())
            self.settings.setValue('speech/voice', self.voice_combo.currentText())
            self.settings.setValue('speech/rate', self.rate_spin.value())
            
            # Clean up resources
            self.speech_handler.cleanup()
            self.debug_panel.close()
            
            logger.info("Application closed successfully")
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}", exc_info=True)
            event.accept()

def main():
    """Main application entry point."""
    try:
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName('Typing Assistant')
        app.setApplicationVersion('1.0.0')
        app.setOrganizationName('TypingAssistant')
        app.setOrganizationDomain('typingassistant.com')
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show main window
        window = TypingAssistantApp()
        window.show()
        
        # Start application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
