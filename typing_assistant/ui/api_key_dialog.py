"""Dialog for entering OpenAI API key."""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class APIKeyDialog(QDialog):
    """Dialog for entering and validating OpenAI API key."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_key = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle('Enter API Key')
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            'Please enter your OpenAI API key.\n'
            'You can find this in your OpenAI account settings.'
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # API Key input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText('sk-...')
        self.key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.key_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.validate_and_accept)
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Offline mode option
        offline_label = QLabel(
            'Note: You can also use the app in offline mode\n'
            'with limited functionality.'
        )
        offline_label.setWordWrap(True)
        layout.addWidget(offline_label)
        
        self.offline_button = QPushButton('Use Offline Mode')
        self.offline_button.clicked.connect(self.use_offline_mode)
        layout.addWidget(self.offline_button)
        
        self.setLayout(layout)
        
    def validate_and_accept(self):
        """Validate the API key format and accept if valid."""
        key = self.key_input.text().strip()
        
        if not key:
            QMessageBox.warning(
                self,
                'Invalid API Key',
                'Please enter an API key.'
            )
            return
            
        if not key.startswith('sk-'):
            QMessageBox.warning(
                self,
                'Invalid API Key',
                'API key should start with "sk-".'
            )
            return
            
        self.api_key = key
        self.accept()
        
    def use_offline_mode(self):
        """Enable offline mode and close dialog."""
        reply = QMessageBox.question(
            self,
            'Enable Offline Mode',
            'Are you sure you want to use offline mode?\n'
            'Some features will be limited.',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.parent().toggle_offline_mode(True)
            self.reject()
