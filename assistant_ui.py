import sys
import os
import logging
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLabel, QPushButton, QStatusBar,
    QComboBox, QSpinBox, QCheckBox, QMessageBox,
    QTabWidget, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor
import openai
from openai import OpenAI
from text_correction import TextCorrectionWorker
from accessibility import AccessibilityManager
from typing_assistant.services.ai_service import AIServiceManager
from typing_assistant.ui.usage_widget import UsageWidget

logger = logging.getLogger(__name__)

class TypingAssistant(QMainWindow):
    """Main window for the Enhanced Typing Assistant."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the typing assistant."""
        super().__init__(parent)
        self.ai_service = AIServiceManager(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.offline_mode = not (bool(os.getenv('OPENAI_API_KEY')) or bool(os.getenv('ANTHROPIC_API_KEY')))
        self.correction_worker = None
        self.correction_timer = QTimer()
        self.correction_timer.setInterval(200)  # 200ms delay
        self.correction_timer.timeout.connect(self.on_text_changed)
        self.accessibility_manager = AccessibilityManager()
        self.setup_ui()
        self.setup_connections()
        self.initialize_correction_worker()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Enhanced Typing Assistant")
        self.setMinimumSize(1000, 700)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        tab_widget = QTabWidget()
        
        # Main editing tab
        editing_widget = QWidget()
        editing_layout = QVBoxLayout(editing_widget)
        
        # Create text areas
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Type or paste your text here...")
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Corrected text will appear here...")
        self.output_text.setReadOnly(True)

        # Create controls
        controls_layout = QHBoxLayout()
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German"])
        
        # Task selection
        self.task_combo = QComboBox()
        self.task_combo.addItems([
            "Grammar", "Spelling", "Style",
            "Rewrite", "Analysis", "Summary"
        ])
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.ai_service.get_available_models())
        
        # Quality selection
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Standard", "High"])
        
        # Cost sensitivity
        self.cost_sensitive = QCheckBox("Cost Sensitive")
        
        # Auto-correct toggle
        self.auto_correct = QCheckBox("Auto-correct")
        self.auto_correct.setChecked(True)

        # Add controls to layout
        controls_layout.addWidget(QLabel("Language:"))
        controls_layout.addWidget(self.language_combo)
        controls_layout.addWidget(QLabel("Task:"))
        controls_layout.addWidget(self.task_combo)
        controls_layout.addWidget(QLabel("Model:"))
        controls_layout.addWidget(self.model_combo)
        controls_layout.addWidget(QLabel("Quality:"))
        controls_layout.addWidget(self.quality_combo)
        controls_layout.addWidget(self.cost_sensitive)
        controls_layout.addWidget(self.auto_correct)
        controls_layout.addStretch()

        # Create model info display
        self.model_info = QTextEdit()
        self.model_info.setReadOnly(True)
        self.model_info.setMaximumHeight(100)
        self.update_model_info()

        # Create accessibility controls
        accessibility_layout = QHBoxLayout()
        self.high_contrast = QCheckBox("High Contrast")
        self.large_text = QCheckBox("Large Text")
        self.dyslexic_font = QCheckBox("Dyslexic Font")
        
        accessibility_layout.addWidget(self.high_contrast)
        accessibility_layout.addWidget(self.large_text)
        accessibility_layout.addWidget(self.dyslexic_font)
        accessibility_layout.addStretch()

        # Add all elements to editing layout
        editing_layout.addLayout(controls_layout)
        editing_layout.addWidget(self.model_info)
        editing_layout.addWidget(self.input_text)
        editing_layout.addWidget(self.output_text)
        editing_layout.addLayout(accessibility_layout)
        
        # Create usage widget
        self.usage_widget = UsageWidget()
        
        # Add tabs
        tab_widget.addTab(editing_widget, "Editor")
        tab_widget.addTab(self.usage_widget, "Usage Statistics")
        
        # Add tab widget to main layout
        layout.addWidget(tab_widget)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()

    def setup_connections(self):
        """Set up signal connections."""
        self.input_text.textChanged.connect(self.on_text_changed)
        self.high_contrast.stateChanged.connect(self.update_accessibility)
        self.large_text.stateChanged.connect(self.update_accessibility)
        self.dyslexic_font.stateChanged.connect(self.update_accessibility)
        self.language_combo.currentTextChanged.connect(self.update_settings)
        self.task_combo.currentTextChanged.connect(self.update_task)
        self.model_combo.currentTextChanged.connect(self.update_model_info)
        self.quality_combo.currentTextChanged.connect(self.update_settings)
        self.cost_sensitive.stateChanged.connect(self.update_settings)
        self.auto_correct.stateChanged.connect(self.update_settings)

    def initialize_correction_worker(self):
        """Initialize the text correction worker."""
        if hasattr(self, 'correction_thread'):
            self.correction_thread.quit()
            self.correction_thread.wait()

        self.correction_thread = QThread()
        self.correction_worker = TextCorrectionWorker()
        self.correction_worker.moveToThread(self.correction_thread)
        
        # Connect signals
        self.correction_worker.result_ready.connect(self.on_correction_finished)
        self.correction_worker.error_occurred.connect(self.on_correction_error)
        self.correction_thread.start()

    def on_text_changed(self):
        """Handle text input changes."""
        if not self.auto_correct.isChecked():
            return

        if self.correction_timer.isActive():
            self.correction_timer.stop()
        
        self.correction_timer.start()

    async def process_text(self):
        """Process the input text."""
        if not self.auto_correct.isChecked():
            return

        text = self.input_text.toPlainText()
        if not text:
            return

        try:
            if self.offline_mode:
                await self.run_offline_correction(text)
            else:
                await self.run_ai_correction(text)
        except Exception as e:
            self.show_error(f"Error processing text: {str(e)}")

    async def run_ai_correction(self, text: str):
        """Run AI-powered text correction."""
        try:
            quality = self.quality_combo.currentText().lower()
            task = self.task_combo.currentText().lower()
            model = self.model_combo.currentText()
            result, usage_info = await self.ai_service.process_text(
                text,
                task=task,
                model=model,
                quality=quality
            )
            
            # Update usage statistics
            self.usage_widget.update_usage(self.ai_service.get_usage_statistics())
            
            # Update the output text
            self.output_text.setText(result)
            
        except Exception as e:
            logger.error(f"AI correction error: {str(e)}")
            self.show_error(f"AI correction failed: {str(e)}")
            if self.correction_worker:
                await self.run_offline_correction(text)

    async def run_offline_correction(self, text: str):
        """Run offline text correction."""
        try:
            # Basic spell checking and grammar correction
            self.correction_worker.correct_text(text)
        except Exception as e:
            logger.error(f"Offline correction error: {str(e)}")
            self.show_error(f"Offline correction failed: {str(e)}")

    def on_correction_finished(self, corrected_text: str):
        """Handle completed text correction."""
        self.output_text.setPlainText(corrected_text)
        self.update_status("Text correction complete")

    def on_correction_error(self, error_msg: str):
        """Handle text correction errors."""
        logger.error(f"Correction error: {error_msg}")
        self.show_error(f"Correction error: {error_msg}")

    def update_accessibility(self):
        """Update accessibility settings."""
        try:
            settings = {
                'high_contrast': self.high_contrast.isChecked(),
                'large_text': self.large_text.isChecked(),
                'dyslexic_font': self.dyslexic_font.isChecked()
            }
            self.accessibility_manager.apply_settings(self, settings)
            self.update_status("Accessibility settings updated")
        except Exception as e:
            logger.error(f"Error updating accessibility settings: {e}")
            self.show_error("Error updating accessibility settings")

    def update_settings(self):
        """Update application settings."""
        try:
            # Update correction worker settings
            settings = {
                'language': self.language_combo.currentText().lower(),
                'quality': self.quality_combo.currentText().lower(),
                'auto_correct': self.auto_correct.isChecked(),
                'cost_sensitive': self.cost_sensitive.isChecked()
            }
            if self.correction_worker:
                self.correction_worker.update_settings(settings)
            self.update_status("Settings updated")
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            self.show_error("Error updating settings")

    def update_task(self):
        """Update recommended models for the selected task."""
        task = self.task_combo.currentText().lower()
        recommended_models = self.ai_service.get_recommended_models(task)
        
        # Update model combo box while preserving current selection if valid
        current_model = self.model_combo.currentText()
        self.model_combo.clear()
        self.model_combo.addItems(recommended_models)
        
        if current_model in recommended_models:
            self.model_combo.setCurrentText(current_model)
        
        self.update_model_info()
        self.update_status(f"Updated recommended models for {task}")

    def update_model_info(self):
        """Update the model information display."""
        try:
            model = self.model_combo.currentText()
            info = self.ai_service.get_model_info(model)
            
            # Format model information
            text = f"Model: {model}\n"
            text += "Strengths: " + ", ".join(info['characteristics']['strengths']) + "\n"
            text += f"Response Time: {info['characteristics']['avg_response_time']}s | "
            text += f"Max Tokens: {info['limits']['max_tokens']} | "
            text += f"Cost: ${info['pricing']['output_price_per_1k']:.4f}/1K tokens"
            
            self.model_info.setText(text)
            
        except Exception as e:
            logger.error(f"Error updating model info: {str(e)}")
            self.model_info.setText("Model information unavailable")

    def update_status(self, message: str = "Ready"):
        """Update the status bar message."""
        mode = "Offline" if self.offline_mode else "Online"
        self.status_bar.showMessage(f"{mode} Mode | {message}")

    def show_error(self, message: str):
        """Show error message to user."""
        self.status_bar.showMessage(f"Error: {message}")
        QMessageBox.warning(self, "Error", message)

    def closeEvent(self, event):
        """Handle application closure."""
        try:
            if hasattr(self, 'correction_thread'):
                self.correction_thread.quit()
                self.correction_thread.wait()
            event.accept()
        except Exception as e:
            logger.error(f"Error during closure: {e}")
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TypingAssistant()
    window.show()
    sys.exit(app.exec_())
