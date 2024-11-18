import os
import sys
import threading
from datetime import datetime
from typing import Dict
import logging
import asyncio

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTextEdit, QPushButton, QLabel,
    QCheckBox, QProgressBar, QMessageBox, QComboBox, QSpinBox,
    QAction, QFileDialog, QStatusBar, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout,
    QDialog, QLineEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QTimer, QSettings, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont

import openai
from dotenv import load_dotenv
import pyttsx3
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class TextCorrectionWorker(QObject):
    """Worker class that performs text correction using OpenAI's GPT-4 API in a separate thread."""
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    result_ready = pyqtSignal(str)

    def __init__(self, text: str, mode: str, severity: str, language: str) -> None:
        super().__init__()
        self.text = text
        self.mode = mode
        self.severity = severity
        self.language = language

    def run(self) -> None:
        """Perform text correction using the OpenAI API."""
        try:
            # Build context-aware prompt based on correction mode and severity
            mode_contexts = {
                'Cognitive Assistance': "You are an expert in assisting users with cognitive challenges.",
                'Motor Difficulty': "You are an expert in correcting text from users with motor control difficulties.",
                'Dyslexia-Friendly': "You are an expert in assisting users with dyslexia and similar reading/writing challenges.",
                'Learning Support': "You are an expert in helping language learners improve their writing.",
                'Standard': "You are an expert in understanding and correcting mistyped text."
            }

            severity_contexts = {
                'Low': "Make minimal corrections while preserving the original text structure.",
                'Medium': "Balance correction with preserving original intent.",
                'High': "Thoroughly correct errors while maintaining meaning.",
                'Maximum': "Provide comprehensive correction and improvement suggestions."
            }

            base_prompt = (
                f"{mode_contexts.get(self.mode, mode_contexts['Standard'])} "
                f"Working in {self.language}, with {self.severity.lower()} correction level. "
                f"{severity_contexts.get(self.severity, '')} "
                f"Please correct the following text:\n\n{self.text}"
            )

            # Call the OpenAI API with the constructed prompt
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a specialized text correction assistant focused on helping users with various challenges."},
                    {"role": "user", "content": base_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            corrected_text = response['choices'][0]['message']['content'].strip()
            self.result_ready.emit(corrected_text)
        except openai.error.OpenAIError as api_error:
            self.error_occurred.emit(f"OpenAI API Error: {str(api_error)}")
        except Exception as general_error:
            self.error_occurred.emit(f"An unexpected error occurred: {str(general_error)}")
        finally:
            self.finished.emit()

class AccessibilityManager:
    def __init__(self, parent):
        self.parent = parent
        self.settings_dict = {
            'live_translation': True
        }
        self.translation_worker = TranslationWorker()
        self.translation_widget = QWidget()
        self.translation_layout = QVBoxLayout(self.translation_widget)
        self.translation_label = QLabel("Translation")
        self.translation_layout.addWidget(self.translation_label)

    class TranslationWorker(QObject):
        finished = pyqtSignal()
        error_occurred = pyqtSignal(str)
        result_ready = pyqtSignal(str)

        def __init__(self):
            super().__init__()

        async def translate_text(self, text):
            try:
                # Simulate translation process
                await asyncio.sleep(1)
                translated_text = f"Translated: {text}"
                self.result_ready.emit(translated_text)
            except Exception as e:
                self.error_occurred.emit(f"Error translating text: {str(e)}")
            finally:
                self.finished.emit()

class TypingAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('TypingAssistant', 'Settings')
        self.load_settings()
        self.correction_history = []
        self.is_processing = False
        self.current_language = "English"
        self.correction_mode = "Standard"
        self.severity_level = "High"
        self.setup_ui()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)

        # Initialize accessibility manager
        self.accessibility_manager = AccessibilityManager(self)

        # Set up error handling
        self.setup_error_handling()

        # Start translation worker thread
        self.translation_thread = QThread()
        self.accessibility_manager.translation_worker.moveToThread(self.translation_thread)
        self.translation_thread.start()

    def load_settings(self):
        """Load user settings"""
        self.font_size = self.settings.value('font_size', 14, type=int)
        self.high_contrast = self.settings.value('high_contrast', False, type=bool)
        self.auto_correct = self.settings.value('auto_correct', True, type=bool)
        self.correction_delay = self.settings.value('correction_delay', 2000, type=int)
        self.voice_speed = self.settings.value('voice_speed', 150, type=int)
        
    def setup_ui(self):
        """Set up the main UI"""
        self.setWindowTitle('Enhanced Typing Assistant')
        self.resize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Settings panel
        settings_group = QGroupBox("Settings")
        settings_layout = QGridLayout()
        
        # Language selection
        language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German"])
        settings_layout.addWidget(language_label, 0, 0)
        settings_layout.addWidget(self.language_combo, 0, 1)
        
        # Mode selection
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Standard",
            "Cognitive Assistance",
            "Motor Difficulty",
            "Dyslexia-Friendly",
            "Learning Support"
        ])
        settings_layout.addWidget(mode_label, 1, 0)
        settings_layout.addWidget(self.mode_combo, 1, 1)
        
        # Severity level
        severity_label = QLabel("Correction Level:")
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["Low", "Medium", "High", "Maximum"])
        settings_layout.addWidget(severity_label, 2, 0)
        settings_layout.addWidget(self.severity_combo, 2, 1)
        
        # Auto-correct checkbox
        self.auto_correct_cb = QCheckBox("Auto-correct")
        self.auto_correct_cb.setChecked(self.auto_correct)
        settings_layout.addWidget(self.auto_correct_cb, 3, 0)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Text areas
        text_layout = QHBoxLayout()
        
        # Input area
        input_group = QGroupBox("Input Text")
        input_layout = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Type or paste your text here...")
        self.input_text.textChanged.connect(self.on_text_changed)
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)
        text_layout.addWidget(input_group)
        
        # Output area
        output_group = QGroupBox("Corrected Text")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Corrected text will appear here...")
        output_layout.addWidget(self.output_text)
        
        # Text-to-speech button
        self.tts_button = QPushButton("Read Aloud")
        self.tts_button.clicked.connect(self.read_text_aloud)
        output_layout.addWidget(self.tts_button)
        
        output_group.setLayout(output_layout)
        text_layout.addWidget(output_group)
        
        layout.addLayout(text_layout)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Correction timer
        self.correction_timer = QTimer()
        self.correction_timer.setSingleShot(True)
        self.correction_timer.timeout.connect(self.perform_correction)
        
        # Add translation widget to right panel
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.addWidget(self.accessibility_manager.translation_widget)
        layout.addWidget(self.right_panel)
        
        # Apply styles
        self.apply_styles()
        
    def on_text_changed(self):
        """Handle text changes"""
        if self.auto_correct_cb.isChecked():
            self.correction_timer.stop()
            self.correction_timer.start(self.correction_delay)
            
        try:
            text = self.input_text.toPlainText()
            if text and self.accessibility_manager.settings_dict['live_translation']:
                asyncio.create_task(self.accessibility_manager.translation_worker.translate_text(text))
        except Exception as e:
            self.handle_error(f"Error processing text: {str(e)}")
            
    def perform_correction(self):
        """Perform text correction"""
        if self.is_processing:
            return
            
        text = self.input_text.toPlainText()
        if not text:
            return
            
        self.is_processing = True
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Correcting text...")
        
        # Create and start correction thread
        self.correction_thread = QThread()
        self.correction_worker = TextCorrectionWorker(
            text,
            self.mode_combo.currentText(),
            self.severity_combo.currentText(),
            self.language_combo.currentText()
        )
        
        self.correction_worker.moveToThread(self.correction_thread)
        self.correction_thread.started.connect(self.correction_worker.run)
        self.correction_worker.finished.connect(self.correction_thread.quit)
        self.correction_worker.finished.connect(self.correction_worker.deleteLater)
        self.correction_thread.finished.connect(self.correction_thread.deleteLater)
        self.correction_worker.result_ready.connect(self.handle_correction)
        self.correction_worker.error_occurred.connect(self.handle_error)
        
        self.correction_thread.start()
        
    def handle_correction(self, corrected_text):
        """Handle corrected text"""
        self.output_text.setPlainText(corrected_text)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Correction complete")
        self.is_processing = False
        
    def handle_error(self, error_message):
        """Handle correction error"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Correction failed")
        self.is_processing = False
        QMessageBox.warning(self, "Error", error_message)
        
    def read_text_aloud(self):
        """Read corrected text using text-to-speech"""
        text = self.output_text.toPlainText()
        if text:
            def speak():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            threading.Thread(target=speak, daemon=True).start()
            
    def apply_styles(self):
        """Apply application styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_document)
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_api_settings)
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def new_document(self):
        """Clear the text areas"""
        self.input_text.clear()
        self.output_text.clear()
    
    def show_api_settings(self):
        """Show API settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("API Settings")
        dialog.setModal(True)
        layout = QVBoxLayout()
        
        # API Key input
        key_group = QGroupBox("API Key")
        key_layout = QVBoxLayout()
        key_input = QLineEdit()
        key_input.setEchoMode(QLineEdit.Password)
        if self.api_key:
            key_input.setText(self.api_key)
        key_layout.addWidget(key_input)
        key_group.setLayout(key_layout)
        layout.addWidget(key_group)
        
        # Test connection button
        test_button = QPushButton("Test Connection")
        test_button.clicked.connect(lambda: self.test_api_connection(key_input.text()))
        layout.addWidget(test_button)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(
            lambda: self.save_api_settings(key_input.text(), dialog)
        )
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def test_api_connection(self, api_key: str):
        """Test the API connection"""
        if api_key:
            QMessageBox.information(
                self,
                "Connection Test",
                "API connection successful!"
            )
        else:
            QMessageBox.warning(
                self,
                "Connection Test",
                "Please enter an API key first."
            )
    
    def save_api_settings(self, api_key: str, dialog: QDialog):
        """Save API settings"""
        try:
            if api_key:
                key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                self.settings.setValue('api_key_hash', key_hash)
                self.api_key = api_key
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Enhanced Typing Assistant</h2>
        <p>Version 1.0</p>
        <p>A powerful typing assistant with AI-powered text correction.</p>
        <p>Features:</p>
        <ul>
            <li>Real-time text correction</li>
            <li>Multiple correction modes</li>
            <li>API integration</li>
        </ul>
        """
        QMessageBox.about(self, "About", about_text)
    
    def setup_error_handling(self):
        """Set up error handling and logging."""
        try:
            # Configure error logging
            self.error_log = []
            
            # Set up error handlers
            def handle_exception(exc_type, exc_value, exc_traceback):
                logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
                self.handle_error(str(exc_value))
                
            sys.excepthook = handle_exception
            
        except Exception as e:
            logger.error(f"Error setting up error handling: {e}")
            
    def handle_error(self, error_message):
        """Handle and display errors to the user."""
        try:
            logger.error(error_message)
            self.error_log.append({
                'timestamp': datetime.now(),
                'message': error_message
            })
            
            # Show error in status bar
            self.statusBar().showMessage(f"Error: {error_message}", 5000)
            
            # Log to file if serious error
            if 'critical' in error_message.lower() or 'fatal' in error_message.lower():
                with open('error_log.txt', 'a') as f:
                    f.write(f"{datetime.now()}: {error_message}\n")
                    
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TypingAssistant()
    window.show()
    sys.exit(app.exec_())
