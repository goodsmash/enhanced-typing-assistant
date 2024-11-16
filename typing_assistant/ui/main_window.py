"""Main application window."""

import sys
import os
import logging
from typing import Optional
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QKeySequence
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                          QHBoxLayout, QPushButton, QWidget, QComboBox,
                          QLabel, QSlider, QSpinBox, QCheckBox, QMessageBox,
                          QShortcut, QMenuBar, QMenu, QAction, QToolBar,
                          QDockWidget, QFrame, QSplitter)

from ..core.text_processor import TextProcessor
from ..core.speech_handler import SpeechHandler
from ..utils.config_manager import ConfigManager
from ..utils.theme_manager import ThemeManager
from .accessibility import AccessibilityManager
from .keyboard_shortcuts import KeyboardShortcutsManager
from .debug_panel import DebugPanel

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

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        try:
            # Initialize settings
            self.settings = QSettings('TypingAssistant', 'App')
            
            # Initialize components
            logger.info("Initializing main window components...")
            self.config = ConfigManager()
            self.theme_manager = ThemeManager()
            self.text_processor = TextProcessor(self.config.get_api_key())
            self.speech_handler = SpeechHandler()
            self.accessibility_manager = AccessibilityManager()
            
            # Create debug panel
            self.debug_panel = DebugPanel()
            self.debug_panel.hide()  # Hidden by default
            
            # Setup UI
            logger.info("Setting up user interface...")
            self.init_ui()
            self.setup_connections()
            self.apply_theme()
            
            # Initialize keyboard shortcuts
            logger.info("Setting up keyboard shortcuts...")
            self.keyboard_shortcuts = KeyboardShortcutsManager(self)
            self.setup_debug_shortcut()
            
            # Start with default settings
            self.correction_timer = QTimer(self)
            self.correction_timer.timeout.connect(self.check_text)
            self.correction_timer.start(2000)  # Check every 2 seconds
            
            # Update component status
            self.update_component_status()
            
            logger.info("Main window initialization complete")
            
        except Exception as e:
            logger.error(f"Error initializing main window: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Initialization Error",
                f"An error occurred while starting the application:\n{str(e)}\n\nPlease check the log file for details."
            )
            raise

    def setup_debug_shortcut(self):
        """Setup keyboard shortcut for debug panel."""
        debug_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        debug_shortcut.activated.connect(self.toggle_debug_panel)

    def toggle_debug_panel(self):
        """Toggle the debug panel visibility."""
        if self.debug_panel.isVisible():
            self.debug_panel.hide()
        else:
            self.debug_panel.show()
            self.update_component_status()

    def update_component_status(self):
        """Update status of all components in debug panel."""
        if not hasattr(self, 'debug_panel'):
            return
            
        # Text Processor
        self.debug_panel.update_component_status(
            "Text Processor",
            hasattr(self, 'text_processor'),
            f"Mode: {getattr(self.text_processor, 'correction_mode', 'N/A')}"
        )
        
        # Speech Handler
        self.debug_panel.update_component_status(
            "Speech Handler",
            hasattr(self, 'speech_handler'),
            "Ready for input/output"
        )
        
        # API Connection
        api_key = self.config.get_api_key()
        self.debug_panel.update_component_status(
            "API Connection",
            bool(api_key),
            "API key configured" if api_key else "No API key"
        )
        
        # Spell Check
        self.debug_panel.update_component_status(
            "Spell Check",
            True,
            "Active" if self.text_processor.dictionary else "Inactive"
        )
        
        # Grammar Check
        self.debug_panel.update_component_status(
            "Grammar Check",
            bool(api_key),
            "Available" if api_key else "Requires API key"
        )

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Accessible Typing Assistant")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Text editing area
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        
        # Text input area with styling
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Arial", 12))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                background-color: #fff;
            }
        """)
        text_layout.addWidget(self.text_edit)
        
        # Control panel
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # Correction mode group
        mode_group = QFrame()
        mode_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        mode_layout = QVBoxLayout(mode_group)
        
        mode_label = QLabel("Correction Mode:")
        mode_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Standard", "Strict", "Creative", "AI"])
        self.mode_combo.currentTextChanged.connect(
            lambda t: self.text_processor.set_correction_mode(t.lower())
        )
        mode_layout.addWidget(self.mode_combo)
        
        control_layout.addWidget(mode_group)
        
        # Severity slider group
        severity_group = QFrame()
        severity_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        severity_layout = QVBoxLayout(severity_group)
        
        severity_label = QLabel("Correction Severity:")
        severity_layout.addWidget(severity_label)
        
        self.severity_slider = QSlider(Qt.Horizontal)
        self.severity_slider.setMinimum(0)
        self.severity_slider.setMaximum(100)
        self.severity_slider.setValue(50)
        self.severity_slider.valueChanged.connect(
            lambda v: self.text_processor.set_correction_severity(v / 100)
        )
        severity_layout.addWidget(self.severity_slider)
        
        control_layout.addWidget(severity_group)
        
        # Speech controls group
        speech_group = QFrame()
        speech_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        speech_layout = QVBoxLayout(speech_group)
        
        speech_label = QLabel("Speech Controls:")
        speech_layout.addWidget(speech_label)
        
        speech_buttons = QHBoxLayout()
        
        self.speak_button = QPushButton("Speak Text")
        self.speak_button.clicked.connect(self.speak_text)
        speech_buttons.addWidget(self.speak_button)
        
        self.listen_button = QPushButton("Listen")
        self.listen_button.clicked.connect(self.start_listening)
        speech_buttons.addWidget(self.listen_button)
        
        speech_layout.addLayout(speech_buttons)
        control_layout.addWidget(speech_group)
        
        # Add stretch to push controls to top
        control_layout.addStretch()
        
        # Add widgets to splitter
        content_splitter.addWidget(text_widget)
        content_splitter.addWidget(control_widget)
        content_splitter.setStretchFactor(0, 2)  # Text area gets more space
        content_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        debug_action = QAction("Debug Panel", self)
        debug_action.setShortcut("Ctrl+D")
        debug_action.triggered.connect(self.toggle_debug_panel)
        view_menu.addAction(debug_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add buttons with icons (you'll need to add icons)
        new_btn = QPushButton("New")
        toolbar.addWidget(new_btn)
        
        open_btn = QPushButton("Open")
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("Save")
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        undo_btn = QPushButton("Undo")
        toolbar.addWidget(undo_btn)
        
        redo_btn = QPushButton("Redo")
        toolbar.addWidget(redo_btn)
        
        toolbar.addSeparator()
        
        speak_btn = QPushButton("Speak")
        toolbar.addWidget(speak_btn)
        
        listen_btn = QPushButton("Listen")
        toolbar.addWidget(listen_btn)

    def setup_connections(self):
        """Set up signal connections."""
        # Text correction
        self.text_edit.textChanged.connect(self.reset_correction_timer)

        # Speech
        self.speak_button.clicked.connect(self.speak_text)
        self.listen_button.clicked.connect(self.start_listening)

        # Other
        self.text_edit.textChanged.connect(self.reset_correction_timer)

    def apply_theme(self):
        """Apply the current theme to the window."""
        # Apply accessibility color scheme
        self.accessibility_manager.apply_palette(self)
        
        # Update font size based on accessibility settings
        self.update_font_size(self.accessibility_manager.get_text_size())

    def check_text(self):
        """Check and correct text if needed."""
        try:
            text = self.text_edit.toPlainText()
            if text:
                corrected_text = self.text_processor.enhance_text(text)
                if corrected_text != text:
                    cursor_position = self.text_edit.textCursor().position()
                    self.text_edit.setPlainText(corrected_text)
                    cursor = self.text_edit.textCursor()
                    cursor.setPosition(min(cursor_position, len(corrected_text)))
                    self.text_edit.setTextCursor(cursor)
                    
                    # Log correction in debug panel
                    logger.debug(f"Text corrected: '{text}' -> '{corrected_text}'")
                    
        except Exception as e:
            logger.error(f"Error during text correction: {e}", exc_info=True)
            self.correction_timer.stop()  # Stop timer to prevent repeated errors
            QMessageBox.warning(
                self,
                "Text Correction Error",
                "An error occurred during text correction. The auto-correction has been temporarily disabled."
            )

    def reset_correction_timer(self):
        """Reset the correction timer."""
        self.correction_timer.stop()
        self.correction_timer.start()

    def speak_text(self):
        """Speak the current text."""
        text = self.text_edit.textCursor().selectedText()
        if not text:
            text = self.text_edit.toPlainText()
        if text and self.accessibility_manager.is_screen_reader_enabled():
            self.speech_handler.speak(text)

    def start_listening(self):
        """Start listening for speech input."""
        self.speech_handler.start_listening()

    def show_about(self):
        """Show the about dialog."""
        QMessageBox.information(self, "About", "Accessible Typing Assistant")

    def closeEvent(self, event):
        """Handle application close event."""
        try:
            logger.info("Saving application state...")
            self.config.save()
            self.accessibility_manager.save_settings()
            self.settings.sync()
            
            logger.info("Cleaning up resources...")
            if hasattr(self, 'speech_handler'):
                self.speech_handler.stop_speaking()
                self.speech_handler.stop_recording()
                
            if hasattr(self, 'debug_panel'):
                self.debug_panel.close()
            
            logger.info("Application closing normally")
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}", exc_info=True)
            event.accept()  # Still close the app, but log the error
