from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QSlider, QPushButton, QMessageBox, QCheckBox
from PyQt5.QtCore import Qt
import logging

class SettingsPanel(QWidget):
    """
    Provides a user interface for adjusting application settings.
    """
    
    def __init__(self, settings_manager, parent=None):
        """
        Initialize the SettingsPanel.
        
        :param settings_manager: SettingsManager - Instance of SettingsManager.
        :param parent: QWidget - The parent widget.
        """
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.init_ui()
    
    def init_ui(self):
        """
        Set up the user interface of the settings panel.
        """
        self.setWindowTitle("Settings")
        layout = QVBoxLayout()
        
        # Language Selection
        layout.addWidget(QLabel("Select Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(['English', 'Spanish', 'French', 'German', 'Chinese'])
        current_language = self.settings_manager.settings.get("current_language", "English")
        index = self.language_combo.findText(current_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        layout.addWidget(self.language_combo)
        
        # Speech Rate Slider
        layout.addWidget(QLabel("Speech Rate:"))
        self.speech_rate_slider = QSlider(Qt.Horizontal)
        self.speech_rate_slider.setMinimum(100)
        self.speech_rate_slider.setMaximum(200)
        self.speech_rate_slider.setValue(self.settings_manager.settings.get("speech_rate", 150))
        layout.addWidget(self.speech_rate_slider)
        
        # Theme Selection
        layout.addWidget(QLabel("Select Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Light', 'Dark', 'High Contrast', 'Colorblind Mode', 'Vibrant', 'Saturated Blue'])
        current_theme = self.settings_manager.settings.get("theme", "Light")
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        layout.addWidget(self.theme_combo)
        
        # Font Size SpinBox
        layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSlider(Qt.Horizontal)
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(self.settings_manager.settings.get("font_size", 12))
        layout.addWidget(self.font_size_spin)
        
        # Auto-Correct Checkbox
        layout.addWidget(QLabel("Enable Auto-Correct:"))
        self.auto_correct_checkbox = QCheckBox()
        self.auto_correct_checkbox.setChecked(self.settings_manager.settings.get("auto_correct", True))
        layout.addWidget(self.auto_correct_checkbox)
        
        # Correction Mode Selection
        layout.addWidget(QLabel("Correction Mode:"))
        self.correction_mode_combo = QComboBox()
        self.correction_mode_combo.addItems(['Standard', 'Cognitive', 'Motor', 'Dyslexia'])
        current_mode = self.settings_manager.settings.get("correction_mode", "Standard")
        index = self.correction_mode_combo.findText(current_mode)
        if index >= 0:
            self.correction_mode_combo.setCurrentIndex(index)
        layout.addWidget(self.correction_mode_combo)
        
        # Severity Level Selection
        layout.addWidget(QLabel("Severity Level:"))
        self.severity_level_combo = QComboBox()
        self.severity_level_combo.addItems(['Low', 'Medium', 'High', 'Maximum'])
        current_severity = self.settings_manager.settings.get("severity_level", "High")
        index = self.severity_level_combo.findText(current_severity)
        if index >= 0:
            self.severity_level_combo.setCurrentIndex(index)
        layout.addWidget(self.severity_level_combo)
        
        # Save Settings Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """
        Save the settings based on user input.
        """
        try:
            language = self.language_combo.currentText()
            speech_rate = self.speech_rate_slider.value()
            theme = self.theme_combo.currentText()
            font_size = self.font_size_spin.value()
            auto_correct = self.auto_correct_checkbox.isChecked()
            correction_mode = self.correction_mode_combo.currentText()
            severity_level = self.severity_level_combo.currentText()
            
            self.settings_manager.update_setting("current_language", language)
            self.settings_manager.update_setting("speech_rate", speech_rate)
            self.settings_manager.update_setting("theme", theme)
            self.settings_manager.update_setting("font_size", font_size)
            self.settings_manager.update_setting("auto_correct", auto_correct)
            self.settings_manager.update_setting("correction_mode", correction_mode)
            self.settings_manager.update_setting("severity_level", severity_level)
            
            QMessageBox.information(self, "Settings", "Settings have been saved successfully!")
            logging.info("Settings saved from SettingsPanel.")
            self.close()
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Error", "An error occurred while saving settings.")
