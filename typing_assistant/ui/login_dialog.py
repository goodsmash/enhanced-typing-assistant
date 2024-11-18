"""Dialog for user login."""

import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QHBoxLayout,
    QWidget
)
from PyQt5.QtCore import Qt
from datetime import datetime

from ..utils.config_manager import ConfigManager
from ..utils.security import SecurityManager

logger = logging.getLogger(__name__)

class CreateAccountDialog(QDialog):
    """Dialog for creating a new account."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.security_manager = SecurityManager()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle('Create Account')
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            'Create a new account to access all features.\n'
            'Your password must be at least 8 characters long.'
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Choose a username')
        form_layout.addRow('Username:', self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Choose a password')
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Password:', self.password_input)
        
        # Confirm password input
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('Confirm password')
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Confirm Password:', self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton('Create Account')
        self.create_button.clicked.connect(self.create_account)
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def create_account(self):
        """Create a new account."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate inputs
        if not username:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter a username.')
            return
            
        if not password:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter a password.')
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, 'Invalid Input', 'Passwords do not match.')
            return
            
        if len(password) < 8:
            QMessageBox.warning(
                self,
                'Invalid Input',
                'Password must be at least 8 characters long.'
            )
            return
            
        try:
            # Create users directory if it doesn't exist
            users_dir = self.config_manager.config_dir / "users"
            users_dir.mkdir(exist_ok=True)
            
            # Check if username already exists
            user_file = users_dir / f"{username}.json"
            if user_file.exists():
                QMessageBox.warning(
                    self,
                    'Username Taken',
                    'This username is already taken. Please choose another.'
                )
                return
                
            # Create password hash
            password_hash = self.security_manager.hash_password(password)
            
            # Create user data
            user_data = {
                'username': username,
                'password_hash': password_hash,
                'created_at': datetime.utcnow().isoformat(),
                'settings': {}
            }
            
            # Encrypt and save user data
            encrypted = self.config_manager.cipher.encrypt(
                json.dumps(user_data).encode()
            )
            with open(user_file, 'wb') as f:
                f.write(encrypted)
                
            QMessageBox.information(
                self,
                'Success',
                'Account created successfully! You can now log in.'
            )
            self.accept()
            
        except Exception as e:
            logger.error(f"Error creating account: {e}")
            QMessageBox.critical(
                self,
                'Error',
                'An error occurred while creating your account. Please try again.'
            )

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
        
        # Load user data
        users_dir = Path(self.config_manager.config_dir) / "users"
        user_file = users_dir / f"{username}.json"
        
        if not user_file.exists():
            QMessageBox.warning(
                self,
                'Invalid Username',
                'This username does not exist.'
            )
            return
            
        try:
            # Load and decrypt user data
            with open(user_file, 'rb') as f:
                encrypted = f.read()
            user_data = json.loads(self.config_manager.cipher.decrypt(encrypted).decode())
            
            # Check password
            if not self.security_manager.check_password(password, user_data['password_hash']):
                QMessageBox.warning(
                    self,
                    'Invalid Password',
                    'The password is incorrect.'
                )
                return
                
            self.accept()
            
        except Exception as e:
            logger.error(f"Error logging in: {e}")
            QMessageBox.critical(
                self,
                'Error',
                'An error occurred while logging in. Please try again.'
            )
        
    def create_account(self):
        """Open account creation dialog."""
        dialog = CreateAccountDialog(self)
        dialog.exec_()
        
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
