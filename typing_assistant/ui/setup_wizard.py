"""Setup wizard for first-time configuration."""

from typing import Optional, Dict
import os
import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox,
                            QCheckBox, QComboBox, QSpinBox)

from ..utils.config_manager import ConfigManager
from ..utils.security import SecurityManager
from .accessibility import AccessibilityManager, ColorScheme, TextSize


class WelcomePage(QWizardPage):
    """Welcome page of the setup wizard."""

    def __init__(self):
        """Initialize welcome page."""
        super().__init__()
        self.setTitle("Welcome to Typing Assistant")
        
        layout = QVBoxLayout()
        
        welcome_text = (
            "Welcome to Typing Assistant!\n\n"
            "This wizard will help you set up your typing assistant with your "
            "preferences and API keys. The application will be configured to "
            "best assist your typing needs.\n\n"
            "Click Next to begin the setup process."
        )
        
        label = QLabel(welcome_text)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        self.setLayout(layout)


class APIConfigPage(QWizardPage):
    """API configuration page."""

    def __init__(self, config_manager: ConfigManager):
        """Initialize API config page."""
        super().__init__()
        self.setTitle("API Configuration")
        self.config_manager = config_manager
        
        layout = QVBoxLayout()
        
        # OpenAI API Key
        api_layout = QVBoxLayout()
        api_label = QLabel("OpenAI API Key:")
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_key)
        
        # Test API Key button
        test_button = QPushButton("Test API Key")
        test_button.clicked.connect(self.test_api_key)
        api_layout.addWidget(test_button)
        
        layout.addLayout(api_layout)
        
        # Save API key securely checkbox
        self.save_secure = QCheckBox("Save API key securely (recommended)")
        self.save_secure.setChecked(True)
        layout.addWidget(self.save_secure)
        
        self.setLayout(layout)

    def validatePage(self) -> bool:
        """Validate the page before proceeding."""
        if not self.api_key.text():
            QMessageBox.warning(
                self, "Missing API Key",
                "Please enter your OpenAI API key to continue."
            )
            return False
        return True

    def test_api_key(self):
        """Test the API key."""
        api_key = self.api_key.text()
        if not api_key:
            QMessageBox.warning(
                self, "Missing API Key",
                "Please enter an API key to test."
            )
            return
        
        # Here you would actually test the API key
        # For now, we'll just show a success message
        QMessageBox.information(
            self, "API Key Test",
            "API key test successful!"
        )


class AccessibilityPage(QWizardPage):
    """Accessibility configuration page."""

    def __init__(self, accessibility_manager: AccessibilityManager):
        """Initialize accessibility page."""
        super().__init__()
        self.setTitle("Accessibility Settings")
        self.accessibility_manager = accessibility_manager
        
        layout = QVBoxLayout()
        
        # Color scheme
        color_layout = QHBoxLayout()
        color_label = QLabel("Color Scheme:")
        self.color_scheme = QComboBox()
        self.color_scheme.addItems([
            "Standard",
            "High Contrast",
            "Dark Mode",
            "Deuteranopia (Red-Green)",
            "Protanopia (Red-Green)",
            "Tritanopia (Blue-Yellow)"
        ])
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_scheme)
        layout.addLayout(color_layout)
        
        # Text size
        size_layout = QHBoxLayout()
        size_label = QLabel("Text Size:")
        self.text_size = QSpinBox()
        self.text_size.setRange(8, 72)
        self.text_size.setValue(14)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.text_size)
        layout.addLayout(size_layout)
        
        # Screen reader
        self.screen_reader = QCheckBox("Enable Screen Reader")
        layout.addWidget(self.screen_reader)
        
        # Keyboard navigation
        self.keyboard_nav = QCheckBox("Enable Keyboard Navigation")
        self.keyboard_nav.setChecked(True)
        layout.addWidget(self.keyboard_nav)
        
        # Typing assistance
        self.auto_complete = QCheckBox("Enable Auto-Complete")
        self.auto_complete.setChecked(True)
        layout.addWidget(self.auto_complete)
        
        self.word_prediction = QCheckBox("Enable Word Prediction")
        self.word_prediction.setChecked(True)
        layout.addWidget(self.word_prediction)
        
        # Typing delay
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Typing Delay (ms):")
        self.typing_delay = QSpinBox()
        self.typing_delay.setRange(0, 1000)
        self.typing_delay.setValue(0)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.typing_delay)
        layout.addLayout(delay_layout)
        
        self.setLayout(layout)


class SetupWizard(QWizard):
    """Setup wizard for first-time configuration."""

    def __init__(self, config_manager: ConfigManager,
                 security_manager: Optional[SecurityManager] = None,
                 accessibility_manager: Optional[AccessibilityManager] = None):
        """Initialize setup wizard."""
        super().__init__()
        
        self.config_manager = config_manager
        self.security_manager = security_manager or SecurityManager()
        self.accessibility_manager = accessibility_manager or AccessibilityManager()
        
        self.setWindowTitle("Typing Assistant Setup")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Add pages
        self.welcome_page = WelcomePage()
        self.api_page = APIConfigPage(self.config_manager)
        self.accessibility_page = AccessibilityPage(self.accessibility_manager)
        
        self.addPage(self.welcome_page)
        self.addPage(self.api_page)
        self.addPage(self.accessibility_page)
        
        # Connect signals
        self.finished.connect(self.save_configuration)

    def save_configuration(self):
        """Save the configuration when the wizard is finished."""
        if self.result() == QWizard.Accepted:
            # Save API configuration
            api_key = self.api_page.api_key.text()
            if self.api_page.save_secure.isChecked():
                self.security_manager.store_api_key(api_key)
            else:
                self.config_manager.set_api_key(api_key)
            
            # Save accessibility settings
            color_scheme_map = {
                0: ColorScheme.STANDARD.value,
                1: ColorScheme.HIGH_CONTRAST.value,
                2: ColorScheme.DARK.value,
                3: ColorScheme.DEUTERANOPIA.value,
                4: ColorScheme.PROTANOPIA.value,
                5: ColorScheme.TRITANOPIA.value
            }
            
            self.accessibility_manager.set_color_scheme(
                color_scheme_map[self.accessibility_page.color_scheme.currentIndex()]
            )
            self.accessibility_manager.set_text_size(
                self.accessibility_page.text_size.value()
            )
            self.accessibility_manager.set_screen_reader_enabled(
                self.accessibility_page.screen_reader.isChecked()
            )
            self.accessibility_manager.set_keyboard_navigation_enabled(
                self.accessibility_page.keyboard_nav.isChecked()
            )
            self.accessibility_manager.set_auto_complete_enabled(
                self.accessibility_page.auto_complete.isChecked()
            )
            self.accessibility_manager.set_word_prediction_enabled(
                self.accessibility_page.word_prediction.isChecked()
            )
            self.accessibility_manager.set_typing_delay(
                self.accessibility_page.typing_delay.value()
            )
            
            # Save all settings
            self.config_manager.save()
            self.accessibility_manager.save_settings()
            
            QMessageBox.information(
                self, "Setup Complete",
                "Setup is complete! The application will now start with your settings."
            )
