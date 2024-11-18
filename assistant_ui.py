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
    QGridLayout, QSpinBox, QCheckBox, QProgressBar, QTabWidget
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
        self.learning_curve = LearningCurveWidget()
        
        # Load saved achievements
        self.achievement_tracker.load_achievements('achievements.json')
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        self.load_settings()
        
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
        
        # Add learning curve widget to a new tab
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout(self.stats_tab)
        stats_layout.addWidget(self.learning_curve)
        
        # Add tab widget if it doesn't exist
        if not hasattr(self, 'tab_widget'):
            self.tab_widget = QTabWidget()
            self.layout.addWidget(self.tab_widget)
        
        self.tab_widget.addTab(self.stats_tab, "Learning Progress")
        
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
        self.correction_mode_combo.addItems([
            'standard', 'cognitive_assistance', 'motor_difficulty',
            'dyslexia-friendly', 'learning_support'
        ])
        self.correction_mode_combo.setCurrentText(self.correction_mode)
        
        # Load severity levels
        self.severity_combo.addItems(['low', 'medium', 'high', 'maximum'])
        self.severity_combo.setCurrentText(self.correction_severity)
        
        # Load languages
        self.language_combo.addItems(['English', 'Spanish', 'French', 'German'])
        self.language_combo.setCurrentText(self.selected_language)

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
            
        # Update achievements
        newly_unlocked = self.achievement_tracker.update_achievements(stats)
        
        # Show achievement notifications
        for achievement in newly_unlocked:
            QMessageBox.information(
                self,
                "Achievement Unlocked! 🏆",
                f"Congratulations! You've earned: {achievement.name}\n{achievement.description}"
            )
        
        # Save achievements
        self.achievement_tracker.save_achievements('achievements.json')
        
        # Update learning curve visualization
        self.learning_curve.plot_learning_curve(self.get_performance_history(), 'wpm')
        
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
        # TODO: Implement API settings dialog
        pass

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

    def on_mode_changed(self, mode: str):
        """Handle correction mode change"""
        self.correction_mode = mode

    def on_severity_changed(self, severity: str):
        """Handle severity level change"""
        self.correction_severity = severity

    def on_language_changed(self, language: str):
        """Handle language change"""
        self.selected_language = language
        if self.spell_checker:
            try:
                self.spell_checker = enchant.Dict(language)
            except:
                logging.error(f"Failed to load dictionary for language: {language}")

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
            f"Achievements 🏆\n"
            f"Unlocked: {len(unlocked)}/{len(achievements)}\n\n"
        )
        
        if next_achievements:
            stats_text += "Next Achievements:\n"
            for achievement in next_achievements[:3]:
                stats_text += f"• {achievement.name}: {achievement.progress:.1f}% complete\n"
        
        QMessageBox.information(self, "Performance Statistics", stats_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EnhancedTypingAssistant()
    window.show()
    sys.exit(app.exec_())
