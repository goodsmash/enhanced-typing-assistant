import os
import sys
import threading
import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, List
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTextEdit, QPushButton, 
    QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QMessageBox, QStatusBar, QMenuBar, QAction, QMenu, 
    QGridLayout, QSpinBox, QCheckBox, QProgressBar, QTabWidget,
    QDialog, QDialogButtonBox, QLineEdit, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor
from datetime import timedelta

# Optional imports with fallbacks
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import enchant
except ImportError:
    enchant = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

from api_providers import ProviderFactory
from text_correction import TextCorrector
from typing_assistant.gamification.achievements import AchievementTracker
from typing_assistant.gamification.visualization import LearningCurveWidget
from typing_assistant.gamification.word_counter import WordCounter


class CorrectionThread(QThread):
    """Worker thread for text correction"""
    correction_complete = pyqtSignal(str)
    correction_error = pyqtSignal(str)
    
    def __init__(self, text: str, ai_provider, mode: str, severity: str, language: str):
        super().__init__()
        self.text = text
        self.ai_provider = ai_provider
        self.mode = mode
        self.severity = severity
        self.language = language
        self.corrector = TextCorrector()
    
    def run(self):
        """Run the correction process"""
        try:
            # Prepare the prompt based on mode and severity
            prompt = self.get_correction_prompt()
            
            if self.ai_provider:
                # Get correction from AI provider
                corrected_text = self.ai_provider.correct_text(self.text, prompt)
            else:
                # Fallback to basic correction
                corrected_text = self.corrector.basic_correction(self.text)
            
            self.correction_complete.emit(corrected_text)
            
        except Exception as e:
            self.correction_error.emit(str(e))
    
    def get_correction_prompt(self) -> str:
        """Get the appropriate correction prompt based on mode and severity"""
        prompts = {
            "standard": {
                "low": "Correct only major spelling and grammar errors, maintaining the original style.",
                "medium": "Correct spelling, grammar, and minor style issues.",
                "high": "Correct all errors and improve clarity and style.",
                "maximum": "Completely polish the text for professional quality."
            },
            "cognitive_assistance": {
                "low": "Simplify complex sentences while maintaining meaning.",
                "medium": "Break down complex ideas into simpler components.",
                "high": "Restructure for maximum clarity and comprehension.",
                "maximum": "Provide detailed explanations and context."
            },
            "motor_difficulty": {
                "low": "Fix basic typing errors.",
                "medium": "Correct common motor-related typing mistakes.",
                "high": "Extensive correction of motor-related errors.",
                "maximum": "Complete reconstruction of poorly typed text."
            },
            "dyslexia-friendly": {
                "low": "Focus on phonetic corrections.",
                "medium": "Address common dyslexic spelling patterns.",
                "high": "Comprehensive correction with simplified vocabulary.",
                "maximum": "Full correction with dyslexia-friendly alternatives."
            },
            "learning_support": {
                "low": "Basic corrections with learning hints.",
                "medium": "Corrections with explanations of common mistakes.",
                "high": "Detailed corrections with learning resources.",
                "maximum": "Comprehensive corrections with educational content."
            }
        }
        
        base_prompt = prompts.get(self.mode, prompts["standard"])
        severity_prompt = base_prompt.get(self.severity, base_prompt["medium"])
        
        return f"You are a specialized text correction assistant. {severity_prompt} Target language: {self.language}"


class EnhancedTypingAssistant(QMainWindow):
    """Main application window for the Enhanced Typing Assistant"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('TypingAssistant', 'Settings')
        self.dyslexia_font = self.settings.value('dyslexia_font', False, type=bool)
        self.correction_mode = self.settings.value('correction_mode', 'standard')
        self.correction_severity = self.settings.value('correction_severity', 'medium')
        self.selected_language = self.settings.value('language', 'en')
        self.selected_provider = self.settings.value('provider', 'Offline')
        self.api_key = self.load_api_key()
        self.ai_provider = None
        
        if self.api_key:
            try:
                self.ai_provider = ProviderFactory.create_provider(self.selected_provider, self.api_key)
                self.ai_provider.set_model(self.settings.value('model', 'GPT-3.5 Turbo'))
            except Exception as e:
                logging.error(f"Failed to initialize AI provider: {e}")
        
        # Initialize components
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Text editing components
        self.input_text = QTextEdit()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        # Control components
        self.correction_mode_combo = QComboBox()
        self.severity_combo = QComboBox()
        self.language_combo = QComboBox()
        self.wpm_label = QLabel("WPM: 0")
        self.correction_button = QPushButton("Correct Text")
        self.voice_input_button = QPushButton("Voice Input")
        self.tts_button = QPushButton("Text to Speech")
        
        # Status components
        self.status_bar = QStatusBar()
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status_bar)
        
        # Initialize workers
        self.correction_thread = None
        self.tts_engine = None
        if pyttsx3:
            self.tts_engine = pyttsx3.init()
        
        # Spell checker
        self.spell_checker = None
        if enchant:
            self.spell_checker = enchant.Dict(self.selected_language)
        
        # Speech recognition
        self.recognizer = None
        if sr:
            self.recognizer = sr.Recognizer()
        
        # Achievement tracking
        self.achievement_tracker = AchievementTracker()
        self.learning_curve = None  # Initialize later to prevent UI lag
        
        # Load saved achievements
        achievements_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data',
            'achievements.json'
        )
        self.achievement_tracker.load_achievements(achievements_path)
        
        # Initialize correction history database
        self.setup_database()

    def setup_ui(self):
        """Set up the main UI components"""
        self.setWindowTitle('Enhanced Typing Assistant')
        self.resize(1200, 800)
        
        # Create UI components
        self.create_menu_bar()
        self.create_text_area()
        self.create_control_panel()
        self.create_status_bar()
        
        # Initialize learning curve widget in a separate thread
        QTimer.singleShot(0, self.init_learning_curve)
        
        # Apply initial styles
        self.apply_styles()

    def create_text_area(self):
        """Create the text editing area"""
        text_layout = QHBoxLayout()
        
        # Input area
        input_group = QGroupBox("Input Text")
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)
        
        # Output area
        output_group = QGroupBox("Corrected Text")
        output_layout = QVBoxLayout()
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        
        text_layout.addWidget(input_group)
        text_layout.addWidget(output_group)
        self.layout.addLayout(text_layout)

    def create_control_panel(self):
        """Create the control panel with settings and buttons"""
        control_layout = QHBoxLayout()
        
        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QGridLayout()
        
        # Add settings controls
        settings_layout.addWidget(QLabel("Mode:"), 0, 0)
        settings_layout.addWidget(self.correction_mode_combo, 0, 1)
        settings_layout.addWidget(QLabel("Severity:"), 0, 2)
        settings_layout.addWidget(self.severity_combo, 0, 3)
        settings_layout.addWidget(QLabel("Language:"), 1, 0)
        settings_layout.addWidget(self.language_combo, 1, 1)
        settings_layout.addWidget(self.wpm_label, 1, 2)
        
        settings_group.setLayout(settings_layout)
        control_layout.addWidget(settings_group)
        
        # Buttons group
        button_group = QGroupBox("Actions")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.correction_button)
        button_layout.addWidget(self.voice_input_button)
        button_layout.addWidget(self.tts_button)
        button_group.setLayout(button_layout)
        control_layout.addWidget(button_group)
        
        self.layout.addLayout(control_layout)

    def setup_connections(self):
        """Set up signal connections for UI components"""
        self.correction_button.clicked.connect(self.correct_text)
        self.voice_input_button.clicked.connect(self.start_voice_input)
        self.tts_button.clicked.connect(self.speak_text)
        self.input_text.textChanged.connect(self.calculate_wpm)
        self.correction_mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.severity_combo.currentTextChanged.connect(self.on_severity_changed)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)

    def correct_text(self):
        """Process and correct the input text"""
        if not self.input_text.toPlainText():
            return
            
        if self.correction_thread and self.correction_thread.isRunning():
            return
            
        self.correction_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Correcting text...")
        
        # Create and start correction thread
        self.correction_thread = CorrectionThread(
            self.input_text.toPlainText(),
            self.ai_provider,
            self.correction_mode,
            self.correction_severity,
            self.selected_language
        )
        self.correction_thread.correction_complete.connect(self.handle_correction)
        self.correction_thread.correction_error.connect(self.handle_error)
        self.correction_thread.finished.connect(self.cleanup_correction)
        self.correction_thread.start()

    def handle_correction(self, corrected_text: str):
        """Handle the corrected text result with performance tracking"""
        original_text = self.input_text.toPlainText()
        self.output_text.setPlainText(corrected_text)
        
        # Track correction in word counter
        if hasattr(self, 'word_counter'):
            stats = self.word_counter.track_correction(original_text, corrected_text)
            self.update_performance_indicators(stats)
            
        self.status_bar.showMessage("Correction complete")
        
        # Save correction history
        self.save_correction_history(original_text, corrected_text)

    def handle_error(self, error_message: str):
        """Handle any errors during correction"""
        QMessageBox.warning(self, "Correction Error", f"An error occurred: {error_message}")
        self.status_bar.showMessage("Correction failed")

    def cleanup_correction(self):
        """Clean up after correction is complete"""
        self.correction_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.correction_thread = None

    def closeEvent(self, event):
        """Clean up resources before closing"""
        self.settings.sync()
        if self.tts_engine:
            self.tts_engine.stop()
        event.accept()

    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        save_action = QAction('Save Settings', self)
        save_action.triggered.connect(self.save_settings)
        file_menu.addAction(save_action)
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        
        # Appearance submenu
        appearance_menu = settings_menu.addMenu('Appearance')
        self.dyslexia_font_action = QAction('Dyslexia-Friendly Font', self)
        self.dyslexia_font_action.setCheckable(True)
        self.dyslexia_font_action.setChecked(self.dyslexia_font)
        self.dyslexia_font_action.triggered.connect(self.toggle_dyslexia_font)
        appearance_menu.addAction(self.dyslexia_font_action)
        
        # API settings
        api_action = QAction('API Settings', self)
        api_action.triggered.connect(self.show_api_settings)
        settings_menu.addAction(api_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        performance_action = QAction('Performance Statistics', self)
        performance_action.triggered.connect(self.show_performance_stats)
        help_menu.addAction(performance_action)

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar.showMessage('Ready')
        self.progress_bar.setVisible(False)

    def apply_styles(self):
        """Apply visual styles to the application"""
        if self.dyslexia_font:
            self.input_text.setFont(QFont('OpenDyslexic', 12))
            self.output_text.setFont(QFont('OpenDyslexic', 12))
        else:
            self.input_text.setFont(QFont('Arial', 12))
            self.output_text.setFont(QFont('Arial', 12))
        
        # Set a pleasant color scheme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        self.setPalette(palette)

    def load_settings(self):
        """Load application settings"""
        # Load correction modes
        modes = [
            ('standard', 'Standard Correction'),
            ('cognitive_assistance', 'Cognitive Assistance'),
            ('motor_difficulty', 'Motor Difficulty Support'),
            ('dyslexia-friendly', 'Dyslexia-Friendly'),
            ('learning_support', 'Learning Support')
        ]
        self.correction_mode_combo.clear()
        for mode, display in modes:
            self.correction_mode_combo.addItem(display, mode)
        
        # Set current mode
        index = self.correction_mode_combo.findData(self.correction_mode)
        if index >= 0:
            self.correction_mode_combo.setCurrentIndex(index)
        
        # Load severity levels
        severities = [
            ('low', 'Minimal Corrections'),
            ('medium', 'Balanced Corrections'),
            ('high', 'Comprehensive Corrections'),
            ('maximum', 'Maximum Support')
        ]
        self.severity_combo.clear()
        for severity, display in severities:
            self.severity_combo.addItem(display, severity)
        
        # Set current severity
        index = self.severity_combo.findData(self.correction_severity)
        if index >= 0:
            self.severity_combo.setCurrentIndex(index)
        
        # Load languages with proper names
        languages = [
            ('en', 'English'),
            ('es', 'Español'),
            ('fr', 'Français'),
            ('de', 'Deutsch'),
            ('it', 'Italiano'),
            ('pt', 'Português'),
            ('nl', 'Nederlands'),
            ('pl', 'Polski'),
            ('ru', 'Русский'),
            ('zh', '中文'),
            ('ja', '日本語'),
            ('ko', '한국어')
        ]
        self.language_combo.clear()
        for code, name in languages:
            self.language_combo.addItem(name, code)
        
        # Set current language
        index = self.language_combo.findData(self.selected_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

    def save_settings(self):
        """Save current settings"""
        self.settings.setValue('dyslexia_font', self.dyslexia_font)
        self.settings.setValue('correction_mode', self.correction_mode)
        self.settings.setValue('correction_severity', self.correction_severity)
        self.settings.setValue('language', self.selected_language)
        self.settings.setValue('provider', self.selected_provider)
        self.settings.sync()
        self.status_bar.showMessage('Settings saved', 3000)

    def load_api_key(self) -> Optional[str]:
        """Load API key from secure storage"""
        try:
            key_hash = self.settings.value('api_key_hash')
            if not key_hash:
                return None
            # In a production environment, use proper secure storage
            return key_hash
        except Exception as e:
            logging.error(f"Failed to load API key: {e}")
            return None

    def setup_database(self):
        """Initialize the correction history database and load previous stats"""
        self.word_counter = WordCounter()
        
        # Load previous stats if available
        history_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data',
            'correction_history.json'
        )
        if os.path.exists(history_file):
            self.word_counter.load_stats(history_file)
            
        # Initialize progress tracking UI
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")

    def calculate_wpm(self):
        """Calculate and update words per minute"""
        if not hasattr(self, 'word_counter'):
            self.word_counter = WordCounter()
            
        text = self.input_text.toPlainText()
        stats = self.word_counter.count_words(text)
        
        # Update WPM label and progress indicators
        self.wpm_label.setText(f"WPM: {stats['wpm']:.1f}")
        self.update_performance_indicators(stats)
        
    def update_performance_indicators(self, stats: Dict[str, float]):
        """Update UI with performance statistics"""
        # Update status bar with detailed stats
        status_text = (f"Words: {stats['words']} | "
                      f"Accuracy: {stats['accuracy']:.1f}% | "
                      f"Streak: {stats['streak']}")
        self.status_bar.showMessage(status_text)
        
        # Update progress bar to show relative performance
        if stats['wpm'] > 0:
            # Scale WPM to progress bar (0-100)
            # Assuming 60 WPM is a good target
            progress = min(int((stats['wpm'] / 60) * 100), 100)
            self.progress_bar.setValue(progress)
            self.progress_bar.setVisible(True)
            
            # Color code progress bar based on WPM
            if stats['wpm'] < 30:
                self.progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: #ff9999; }"
                )
            elif stats['wpm'] < 45:
                self.progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: #ffcc99; }"
                )
            else:
                self.progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: #99ff99; }"
                )
        else:
            self.progress_bar.setVisible(False)
            
        # Update achievements without blocking UI
        QTimer.singleShot(0, lambda: self.check_achievements(stats))
        
        # Update learning curve visualization
        self.update_learning_curve()
        
    def save_correction_history(self, original: str, corrected: str):
        """Save correction history for learning analytics"""
        if hasattr(self, 'word_counter'):
            history_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data',
                'correction_history.json'
            )
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            self.word_counter.save_stats(history_file)
            
    def start_voice_input(self):
        """Start voice input recording"""
        if not self.recognizer:
            QMessageBox.warning(self, "Feature Not Available", 
                              "Speech recognition is not available. Please install speech_recognition package.")
            return
            
        try:
            with sr.Microphone() as source:
                self.status_bar.showMessage("Listening...")
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                self.input_text.setPlainText(text)
                self.status_bar.showMessage("Voice input complete")
        except Exception as e:
            QMessageBox.warning(self, "Voice Input Error", str(e))
            self.status_bar.showMessage("Voice input failed")

    def speak_text(self):
        """Convert output text to speech"""
        if not self.tts_engine:
            QMessageBox.warning(self, "Feature Not Available", 
                              "Text-to-speech is not available. Please install pyttsx3 package.")
            return
            
        text = self.output_text.toPlainText()
        if text:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                QMessageBox.warning(self, "Text-to-Speech Error", str(e))

    def show_api_settings(self):
        """Show API settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("API Settings")
        dialog.setModal(True)
        layout = QVBoxLayout()
        
        # Provider selection
        provider_group = QGroupBox("AI Provider")
        provider_layout = QVBoxLayout()
        provider_combo = QComboBox()
        provider_combo.addItems(['OpenAI', 'Azure', 'Local'])
        provider_combo.setCurrentText(self.selected_provider)
        provider_layout.addWidget(provider_combo)
        provider_group.setLayout(provider_layout)
        
        # Model settings
        model_group = QGroupBox("Model Settings")
        model_layout = QGridLayout()
        
        # Model selection
        model_label = QLabel("Model:")
        model_combo = QComboBox()
        model_combo.addItems(['GPT-3.5 Turbo', 'GPT-4', 'Custom'])
        model_combo.setCurrentText(self.settings.value('model', 'GPT-3.5 Turbo'))
        
        # Temperature setting
        temp_label = QLabel("Temperature:")
        temp_spin = QDoubleSpinBox()
        temp_spin.setRange(0.0, 2.0)
        temp_spin.setSingleStep(0.1)
        temp_spin.setValue(float(self.settings.value('temperature', 0.7)))
        
        # Max tokens
        tokens_label = QLabel("Max Tokens:")
        tokens_spin = QSpinBox()
        tokens_spin.setRange(50, 4000)
        tokens_spin.setSingleStep(50)
        tokens_spin.setValue(int(self.settings.value('max_tokens', 1000)))
        
        # Add to grid
        model_layout.addWidget(model_label, 0, 0)
        model_layout.addWidget(model_combo, 0, 1)
        model_layout.addWidget(temp_label, 1, 0)
        model_layout.addWidget(temp_spin, 1, 1)
        model_layout.addWidget(tokens_label, 2, 0)
        model_layout.addWidget(tokens_spin, 2, 1)
        model_group.setLayout(model_layout)
        
        # API Key input
        key_group = QGroupBox("API Authentication")
        key_layout = QVBoxLayout()
        key_input = QLineEdit()
        key_input.setEchoMode(QLineEdit.Password)
        if self.api_key:
            key_input.setText(self.api_key)
        key_layout.addWidget(QLabel("API Key:"))
        key_layout.addWidget(key_input)
        key_group.setLayout(key_layout)
        
        # Test connection button
        test_button = QPushButton("Test Connection")
        test_button.clicked.connect(lambda: self.test_api_connection(
            provider_combo.currentText(),
            key_input.text(),
            model_combo.currentText()
        ))
        
        # Add all components
        layout.addWidget(provider_group)
        layout.addWidget(model_group)
        layout.addWidget(key_group)
        layout.addWidget(test_button)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(lambda: self.save_api_settings(
            provider_combo.currentText(),
            key_input.text(),
            model_combo.currentText(),
            temp_spin.value(),
            tokens_spin.value(),
            dialog
        ))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def test_api_connection(self, provider: str, api_key: str, model: str):
        """Test the API connection with provided settings"""
        try:
            provider_instance = ProviderFactory.create_provider(provider, api_key)
            provider_instance.set_model(model)
            
            # Test with a simple prompt
            result = provider_instance.correct_text(
                "Test connection.",
                "This is a test connection. Please respond with 'OK'."
            )
            
            if result:
                QMessageBox.information(
                    self,
                    "Connection Test",
                    "Successfully connected to API!"
                )
            else:
                raise Exception("No response from API")
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "Connection Test Failed",
                f"Could not connect to API: {str(e)}"
            )

    def save_api_settings(self, provider: str, api_key: str, model: str,
                         temperature: float, max_tokens: int, dialog: QDialog):
        """Save API settings and close dialog"""
        try:
            # Save settings
            self.settings.setValue('provider', provider)
            self.settings.setValue('model', model)
            self.settings.setValue('temperature', temperature)
            self.settings.setValue('max_tokens', max_tokens)
            
            # Hash and save API key
            if api_key:
                key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                self.settings.setValue('api_key_hash', key_hash)
                self.api_key = api_key
            
            # Update provider
            self.selected_provider = provider
            if self.api_key:
                self.ai_provider = ProviderFactory.create_provider(provider, self.api_key)
                self.ai_provider.set_model(model)
            
            self.settings.sync()
            dialog.accept()
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Save Failed",
                f"Failed to save settings: {str(e)}"
            )

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Enhanced Typing Assistant",
                         "Enhanced Typing Assistant v1.0\n\n"
                         "An AI-powered typing assistant designed to help users "
                         "with various cognitive and motor challenges.\n\n"
                         "Features:\n"
                         "- Multiple correction modes\n"
                         "- Voice input\n"
                         "- Text-to-speech\n"
                         "- Accessibility options")

    def toggle_dyslexia_font(self):
        """Toggle dyslexia-friendly font"""
        self.dyslexia_font = self.dyslexia_font_action.isChecked()
        self.apply_styles()

    def on_mode_changed(self, mode_display: str):
        """Handle correction mode change"""
        index = self.correction_mode_combo.currentIndex()
        mode = self.correction_mode_combo.itemData(index)
        if mode:
            self.correction_mode = mode
            self.settings.setValue('correction_mode', mode)

    def on_severity_changed(self, severity_display: str):
        """Handle severity level change"""
        index = self.severity_combo.currentIndex()
        severity = self.severity_combo.itemData(index)
        if severity:
            self.correction_severity = severity
            self.settings.setValue('correction_severity', severity)

    def on_language_changed(self, language_display: str):
        """Handle language change"""
        index = self.language_combo.currentIndex()
        language = self.language_combo.itemData(index)
        if language:
            self.selected_language = language
            self.settings.setValue('language', language)
            
            # Update spell checker
            if self.spell_checker and enchant:
                try:
                    self.spell_checker = enchant.Dict(language)
                except Exception as e:
                    logging.error(f"Failed to load dictionary for language {language}: {e}")
                    QMessageBox.warning(
                        self,
                        "Language Support",
                        f"Spell checking is not available for {language_display}.\n"
                        "Please install the appropriate dictionary."
                    )
    
    def show_performance_stats(self):
        """Show detailed performance statistics dialog"""
        if not hasattr(self, 'word_counter'):
            return
            
        stats = self.word_counter.get_stats()
        achievements = self.achievement_tracker.get_all_achievements()
        unlocked = self.achievement_tracker.get_unlocked_achievements()
        next_achievements = self.achievement_tracker.get_next_achievements()
        
        stats_text = (
            f"Typing Performance Statistics\n\n"
            f"Current Session:\n"
            f"- Words Typed: {stats['words']}\n"
            f"- Average WPM: {stats['wpm']:.1f}\n"
            f"- Accuracy: {stats['accuracy']:.1f}%\n"
            f"- Current Streak: {stats['streak']}\n"
            f"- Longest Streak: {stats['longest_streak']}\n"
            f"- Total Corrections: {stats['corrections']}\n\n"
            f"Session Duration: {timedelta(seconds=int(stats['time']))}\n\n"
            f"Achievements \u2705\n"
            f"Unlocked: {len(unlocked)}/{len(achievements)}\n\n"
        )
        
        if next_achievements:
            stats_text += "Next Achievements:\n"
            for achievement in next_achievements[:3]:
                stats_text += f"• {achievement.name}: {achievement.progress:.1f}% complete\n"
        
        QMessageBox.information(self, "Performance Statistics", stats_text)

    def init_learning_curve(self):
        """Initialize learning curve widget"""
        try:
            self.learning_curve = LearningCurveWidget()
            
            # Add learning curve widget to a new tab
            self.stats_tab = QWidget()
            stats_layout = QVBoxLayout(self.stats_tab)
            stats_layout.addWidget(self.learning_curve)
            
            # Add tab widget if it doesn't exist
            if not hasattr(self, 'tab_widget'):
                self.tab_widget = QTabWidget()
                self.layout.addWidget(self.tab_widget)
            
            self.tab_widget.addTab(self.stats_tab, "Learning Progress")
            
            # Update initial visualization
            self.update_learning_curve()
        except Exception as e:
            logger.error(f"Error initializing learning curve: {e}")

    def check_achievements(self, stats: Dict[str, float]):
        """Check and update achievements"""
        try:
            # Update achievements
            newly_unlocked = self.achievement_tracker.update_achievements(stats)
            
            # Show achievement notifications
            if newly_unlocked:
                self.show_achievement_notifications(newly_unlocked)
            
            # Save achievements
            achievements_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data',
                'achievements.json'
            )
            self.achievement_tracker.save_achievements(achievements_path)
            
            # Update learning curve visualization
            self.update_learning_curve()
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")

    def show_achievement_notifications(self, achievements: List[Achievement]):
        """Show achievement notifications without interrupting typing"""
        try:
            for achievement in achievements:
                notification = QMessageBox(self)
                notification.setIcon(QMessageBox.Information)
                notification.setWindowTitle("Achievement Unlocked! \u2705")
                notification.setText(
                    f"Congratulations! You've earned:\n\n"
                    f"{achievement.icon} {achievement.name}\n"
                    f"{achievement.description}"
                )
                notification.setStandardButtons(QMessageBox.Ok)
                
                # Use non-modal dialog to avoid interrupting typing
                notification.setWindowModality(Qt.NonModal)
                notification.show()
        except Exception as e:
            logger.error(f"Error showing achievement notification: {e}")

    def update_learning_curve(self):
        """Update learning curve visualization"""
        try:
            if self.learning_curve is None:
                return
                
            history = self.get_performance_history()
            if history:
                self.learning_curve.plot_learning_curve(history, 'wpm')
        except Exception as e:
            logger.error(f"Error updating learning curve: {e}")

    def get_performance_history(self) -> List[Dict[str, float]]:
        """Get performance history data"""
        try:
            if not hasattr(self, 'word_counter'):
                return []
                
            history = self.word_counter.get_history()
            if not history:
                return []
                
            # Ensure all required fields are present
            valid_history = []
            for entry in history:
                if all(key in entry for key in ['timestamp', 'wpm', 'accuracy', 'streak']):
                    valid_history.append(entry)
                
            return valid_history
            
        except Exception as e:
            logger.error(f"Error getting performance history: {e}")
            return []


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EnhancedTypingAssistant()
    window.show()
    sys.exit(app.exec_())
