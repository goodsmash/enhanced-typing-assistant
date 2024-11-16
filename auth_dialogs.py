from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFormLayout
)
from PyQt5.QtCore import Qt

class LoginDialog(QDialog):
    """Dialog for user login."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login')
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        
        # Username field
        self.username = QLineEdit()
        self.username.setPlaceholderText('Enter username')
        layout.addRow('Username:', self.username)
        
        # Password field
        self.password = QLineEdit()
        self.password.setPlaceholderText('Enter password')
        self.password.setEchoMode(QLineEdit.Password)
        layout.addRow('Password:', self.password)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.accept)
        self.register_button = QPushButton('Register')
        self.register_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        layout.addRow(button_layout)
        
        self.setLayout(layout)

    def get_credentials(self):
        return self.username.text(), self.password.text()

class RegisterDialog(QDialog):
    """Dialog for user registration."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Register')
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        
        # Username field
        self.username = QLineEdit()
        self.username.setPlaceholderText('Choose a username')
        layout.addRow('Username:', self.username)
        
        # Password field
        self.password = QLineEdit()
        self.password.setPlaceholderText('Choose a password')
        self.password.setEchoMode(QLineEdit.Password)
        layout.addRow('Password:', self.password)
        
        # Confirm password field
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText('Confirm password')
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addRow('Confirm Password:', self.confirm_password)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.register_button = QPushButton('Register')
        self.register_button.clicked.connect(self.validate_and_accept)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow(button_layout)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet('color: red')
        layout.addRow(self.error_label)
        
        self.setLayout(layout)

    def validate_and_accept(self):
        if not self.username.text():
            self.error_label.setText('Username is required')
            return
        if not self.password.text():
            self.error_label.setText('Password is required')
            return
        if self.password.text() != self.confirm_password.text():
            self.error_label.setText('Passwords do not match')
            return
        if len(self.password.text()) < 6:
            self.error_label.setText('Password must be at least 6 characters')
            return
        self.accept()

    def get_credentials(self):
        return self.username.text(), self.password.text()
