"""Dialog for user login."""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout
)
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    """Dialog for user login."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = None
        self.password = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle('Login')
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            'Please log in to access all features.\n'
            'You can create an account if you don\'t have one.'
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter username')
        form_layout.addRow('Username:', self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter password')
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Password:', self.password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.validate_and_accept)
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Create account option
        create_account_label = QLabel(
            'Don\'t have an account?\n'
            'You can create one to save your settings.'
        )
        create_account_label.setWordWrap(True)
        layout.addWidget(create_account_label)
        
        self.create_account_button = QPushButton('Create Account')
        self.create_account_button.clicked.connect(self.create_account)
        layout.addWidget(self.create_account_button)
        
        # Skip login option
        skip_label = QLabel(
            'Note: You can also use the app without logging in\n'
            'with limited functionality.'
        )
        skip_label.setWordWrap(True)
        layout.addWidget(skip_label)
        
        self.skip_button = QPushButton('Skip Login')
        self.skip_button.clicked.connect(self.skip_login)
        layout.addWidget(self.skip_button)
        
        self.setLayout(layout)
        
    def validate_and_accept(self):
        """Validate the login inputs and accept if valid."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username:
            QMessageBox.warning(
                self,
                'Invalid Input',
                'Please enter a username.'
            )
            return
            
        if not password:
            QMessageBox.warning(
                self,
                'Invalid Input',
                'Please enter a password.'
            )
            return
            
        self.username = username
        self.password = password
        self.accept()
        
    def create_account(self):
        """Open account creation dialog."""
        # TODO: Implement account creation
        QMessageBox.information(
            self,
            'Create Account',
            'Account creation will be available soon.'
        )
        
    def skip_login(self):
        """Skip login and use limited functionality."""
        reply = QMessageBox.question(
            self,
            'Skip Login',
            'Are you sure you want to skip login?\n'
            'Some features will be limited.',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.parent().toggle_offline_mode(True)
            self.reject()
