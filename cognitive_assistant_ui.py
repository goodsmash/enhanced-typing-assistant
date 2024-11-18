import sys
import os
import asyncio
import threading
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTextEdit, QPushButton, QLabel,
    QComboBox, QVBoxLayout, QHBoxLayout, QGroupBox, QMessageBox,
    QStatusBar, QMenuBar, QAction, QMenu, QGridLayout, QSpinBox, QCheckBox, 
    QProgressBar, QDialog, QLineEdit, QFormLayout
)
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor

from api_providers import ProviderFactory, BaseAIProvider
from text_correction import TextCorrector
from cache import ExpiringCache

# Load environment variables
load_dotenv()

class APIKeyDialog(QDialog):
    """Dialog for entering API keys"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Configuration")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout()
        
        # OpenAI API Key
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.Password)
        layout.addRow("OpenAI API Key:", self.openai_key)
        
        # Anthropic API Key
        self.anthropic_key = QLineEdit()
        self.anthropic_key.setEchoMode(QLineEdit.Password)
        layout.addRow("Anthropic API Key:", self.anthropic_key)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        self.setLayout(layout)

class CorrectionThread(QThread):
    """Worker thread for text correction"""
    correction_complete = pyqtSignal(str)
    correction_error = pyqtSignal(str)
    
    def __init__(self, text: str, provider: BaseAIProvider, mode: str, severity: str, language: str):
        super().__init__()
        self.text = text
        self.provider = provider
        self.mode = mode
        self.severity = severity
        self.language = language
        self.corrector = TextCorrector()
        
    def run(self):
        """Run the correction process"""
        try:
            # Create event loop for async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run correction
            corrected = loop.run_until_complete(
                self.corrector.correct_text(
                    self.text,
                    mode=self.mode.lower(),
                    severity=self.severity.lower(),
                    language=self.language
                )
            )
            
            self.correction_complete.emit(corrected)
            
        except Exception as e:
            self.correction_error.emit(str(e))
        finally:
            loop.close()

class CognitiveTypingAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('TypingAssistant', 'Settings')
        
        # Load settings
        self.font_size = self.settings.value('font_size', 18, type=int)
        self.auto_correct = self.settings.value('auto_correct', True, type=bool)
        self.correction_delay = self.settings.value('correction_delay', 1500, type=int)
        self.voice_speed = self.settings.value('voice_speed', 150, type=int)
        self.severity_level = self.settings.value('severity_level', 'Medium', type=str)
        self.dyslexia_font = self.settings.value('dyslexia_font', False, type=bool)
        self.color_scheme = self.settings.value('color_scheme', 'High Contrast', type=str)
        self.current_language = self.settings.value('current_language', 'English', type=str)
        self.correction_mode = self.settings.value('correction_mode', 'Standard', type=str)
        self.wpm_target = self.settings.value('wpm_target', 40, type=int)
        self.show_wpm = self.settings.value('show_wpm', True, type=bool)
        
        # Initialize components
        self.setup_ui()
        self.init_text_correction()
        self.init_timers()
        self.init_providers()
        
        # Track typing metrics
        self.typing_start_time = None
        self.word_count = 0
        self.current_wpm = 0
        
    def setup_ui(self):
        """Initialize the user interface with cognitive accessibility features."""
        self.setWindowTitle('Cognitive Typing Assistant')
        self.resize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create settings panel
        settings_group = self.create_settings_group()
        main_layout.addWidget(settings_group)
        
        # Create AI provider panel
        ai_group = self.create_ai_settings_group()
        main_layout.addWidget(ai_group)
        
        # Create typing metrics panel
        metrics_group = self.create_metrics_group()
        main_layout.addWidget(metrics_group)
        
        # Create text areas
        text_layout = QHBoxLayout()
        
        # Input group with larger, clearer labels
        input_group = QGroupBox("Type or Paste Your Text Here")
        input_layout = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setFont(QFont('Arial', self.font_size))
        self.input_text.textChanged.connect(self.on_text_changed)
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)
        text_layout.addWidget(input_group)
        
        # Output group with clear formatting
        output_group = QGroupBox("Corrected Text")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont('Arial', self.font_size))
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        text_layout.addWidget(output_group)
        
        main_layout.addLayout(text_layout)
        
        # Create control buttons with high visibility
        controls_group = self.create_controls_group()
        main_layout.addWidget(controls_group)
        
        # Progress bar for visual feedback
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar for clear feedback
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Ready')
        
        # Create menu bar
        self.create_menu_bar()
        
        # Apply initial styles
        self.apply_cognitive_styles()
        
    def create_ai_settings_group(self):
        """Create the AI provider settings panel."""
        ai_group = QGroupBox("AI Settings")
        ai_layout = QGridLayout()
        
        # Provider selection
        provider_label = QLabel("AI Provider:")
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(self.provider_factory.get_available_providers())
        self.provider_combo.currentTextChanged.connect(self.update_provider)
        ai_layout.addWidget(provider_label, 0, 0)
        ai_layout.addWidget(self.provider_combo, 0, 1)
        
        # Model selection
        model_label = QLabel("AI Model:")
        self.model_combo = QComboBox()
        self.update_available_models()
        self.model_combo.currentTextChanged.connect(self.update_model)
        ai_layout.addWidget(model_label, 0, 2)
        ai_layout.addWidget(self.model_combo, 0, 3)
        
        # Correction mode
        mode_label = QLabel("Correction Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Standard", "Grammar", "Spelling", "Style", "Comprehensive"])
        self.mode_combo.setCurrentText(self.correction_mode)
        ai_layout.addWidget(mode_label, 1, 0)
        ai_layout.addWidget(self.mode_combo, 1, 1)
        
        # Correction severity
        severity_label = QLabel("Correction Level:")
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["Low", "Medium", "High"])
        self.severity_combo.setCurrentText(self.severity_level)
        ai_layout.addWidget(severity_label, 1, 2)
        ai_layout.addWidget(self.severity_combo, 1, 3)
        
        ai_group.setLayout(ai_layout)
        return ai_group

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        api_action = QAction('Configure APIs', self)
        api_action.triggered.connect(self.show_api_dialog)
        file_menu.addAction(api_action)
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        theme_menu = QMenu('Theme', self)
        themes = ['High Contrast', 'Dark Mode', 'Light Mode']
        for theme in themes:
            action = QAction(theme, self)
            action.triggered.connect(lambda checked, t=theme: self.change_theme(t))
            theme_menu.addAction(action)
        view_menu.addMenu(theme_menu)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_api_dialog(self):
        """Show the API configuration dialog."""
        dialog = APIKeyDialog(self)
        if dialog.exec_():
            # Save API keys
            openai_key = dialog.openai_key.text()
            anthropic_key = dialog.anthropic_key.text()
            
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
            if anthropic_key:
                os.environ['ANTHROPIC_API_KEY'] = anthropic_key
                
            # Reinitialize providers
            self.init_providers()
            self.status_bar.showMessage('API configuration updated')

    def init_providers(self):
        """Initialize AI providers."""
        self.provider_factory = ProviderFactory()
        self.current_provider = None
        
        # Try to initialize with existing API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                self.current_provider = self.provider_factory.create_provider('OpenAI', openai_key)
                self.provider_combo.setCurrentText('OpenAI')
            except Exception as e:
                self.show_error(f"Failed to initialize OpenAI provider: {str(e)}")

    def update_provider(self, provider_name: str):
        """Update the current AI provider."""
        try:
            api_key = os.getenv(f'{provider_name.upper()}_API_KEY')
            if not api_key:
                self.show_api_dialog()
                return
                
            self.current_provider = self.provider_factory.create_provider(provider_name, api_key)
            self.update_available_models()
            self.status_bar.showMessage(f'Switched to {provider_name} provider')
        except Exception as e:
            self.show_error(f"Failed to switch provider: {str(e)}")

    def update_available_models(self):
        """Update the available models for the current provider."""
        if self.current_provider:
            self.model_combo.clear()
            self.model_combo.addItems(self.current_provider.get_available_models())

    def update_model(self, model_name: str):
        """Update the current AI model."""
        if hasattr(self.current_provider, 'set_model'):
            self.current_provider.set_model(model_name)
            self.status_bar.showMessage(f'Switched to {model_name} model')

    def init_text_correction(self):
        """Initialize the text correction system."""
        self.correction_thread = None
        self.is_processing = False
        
    def init_timers(self):
        """Initialize timers for WPM calculation and auto-correction."""
        self.typing_timer = QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self.calculate_wpm)
        
        self.correction_timer = QTimer()
        self.correction_timer.setSingleShot(True)
        self.correction_timer.timeout.connect(self.perform_correction)
        
    def on_text_changed(self):
        """Handle text changes and update metrics."""
        if not self.typing_start_time:
            self.typing_start_time = datetime.now()
            
        # Start WPM calculation timer
        self.typing_timer.start(1000)  # Calculate WPM every second
        
        # Start correction timer if auto-correct is enabled
        if self.auto_correct and not self.is_processing:
            self.correction_timer.start(self.correction_delay)
            
    def calculate_wpm(self):
        """Calculate and update the current WPM."""
        if not self.typing_start_time:
            return
            
        current_time = datetime.now()
        elapsed_minutes = (current_time - self.typing_start_time).total_seconds() / 60
        
        if elapsed_minutes > 0:
            word_count = len(self.input_text.toPlainText().split())
            self.current_wpm = int(word_count / elapsed_minutes)
            
            if self.show_wpm:
                self.wpm_label.setText(f"Current WPM: {self.current_wpm}")
                
                # Visual feedback based on WPM target
                if self.current_wpm < self.wpm_target:
                    self.wpm_label.setStyleSheet("color: red;")
                else:
                    self.wpm_label.setStyleSheet("color: green;")
                    
    def perform_correction(self):
        """Perform text correction with cognitive support features."""
        text = self.input_text.toPlainText()
        if not text.strip() or self.is_processing:
            return
            
        self.is_processing = True
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage('Correcting text...')
        
        # Create and start correction thread
        self.correction_thread = CorrectionThread(
            text,
            self.current_provider,
            self.correction_mode,
            self.severity_level,
            self.current_language
        )
        self.correction_thread.correction_complete.connect(self.update_corrected_text)
        self.correction_thread.correction_error.connect(self.show_error)
        self.correction_thread.start()
        
    def update_corrected_text(self, corrected_text):
        """Update the output text with corrections."""
        self.output_text.setPlainText(corrected_text)
        self.is_processing = False
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage('Text corrected')
        
    def show_error(self, error_message):
        """Display error messages in a cognitive-friendly way."""
        self.is_processing = False
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage('Error occurred')
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Error")
        msg.setText(error_message)
        msg.setFont(QFont('Arial', self.font_size))
        msg.exec_()
        
    def clear_text(self):
        """Clear all text fields and reset metrics."""
        self.input_text.clear()
        self.output_text.clear()
        self.typing_start_time = None
        self.current_wpm = 0
        self.wpm_label.setText("Current WPM: 0")
        self.status_bar.showMessage('Ready')
        
    def update_text_size(self, size):
        """Update text size throughout the application."""
        sizes = {'Normal': 18, 'Large': 24, 'Very Large': 32}
        self.font_size = sizes[size]
        self.settings.setValue('font_size', self.font_size)
        self.apply_cognitive_styles()
        
    def update_word_spacing(self, spacing):
        """Update word spacing throughout the application."""
        spacings = {'Normal': 0, 'Wide': 2, 'Very Wide': 4}
        spacing_value = spacings[spacing]
        self.input_text.setStyleSheet(f"QTextEdit {{ letter-spacing: {spacing_value}px; }}")
        self.output_text.setStyleSheet(f"QTextEdit {{ letter-spacing: {spacing_value}px; }}")
        
    def update_wpm_target(self, target):
        """Update the WPM target."""
        self.wpm_target = target
        self.settings.setValue('wpm_target', target)
        
    def toggle_wpm_display(self, state):
        """Toggle WPM display visibility."""
        self.show_wpm = (state == Qt.Checked)
        self.settings.setValue('show_wpm', self.show_wpm)
        self.wpm_label.setVisible(self.show_wpm)
        
    def apply_cognitive_styles(self):
        """Apply cognitive-friendly styles throughout the application."""
        # Set fonts
        font = QFont('Arial', self.font_size)
        self.input_text.setFont(font)
        self.output_text.setFont(font)
        
        # Apply color scheme
        if self.color_scheme == 'High Contrast':
            self.setStyleSheet("""
                QMainWindow { background-color: white; }
                QTextEdit { background-color: white; color: black; border: 2px solid black; }
                QPushButton { 
                    background-color: black; 
                    color: white; 
                    border: none;
                    padding: 10px;
                    font-weight: bold;
                }
                QLabel { color: black; font-weight: bold; }
            """)
        
def main():
    app = QApplication(sys.argv)
    window = CognitiveTypingAssistant()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
