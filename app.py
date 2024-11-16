#!/usr/bin/env python3

import sys
import os
import signal
import logging
import argparse
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from enhanced_typing_assistant import EnhancedTypingAssistant

VERSION = '1.0.0'

def signal_handler(signum, frame):
    logging.info('Received signal %d, shutting down...', signum)
    sys.exit(0)

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('typing_assistant.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Check for required dependencies before starting."""
    missing = []
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        missing.append("PyQt5")
    
    try:
        import openai
    except ImportError:
        missing.append("openai")
    
    if missing:
        print("Error: Missing required dependencies:", ", ".join(missing))
        print("Please install using: pip install " + " ".join(missing))
        sys.exit(1)

def setup_environment():
    """Setup environment variables and paths."""
    # Add application directory to Python path
    app_dir = Path(__file__).parent.absolute()
    sys.path.append(str(app_dir))
    
    # Ensure config directory exists
    config_dir = app_dir / 'config'
    config_dir.mkdir(exist_ok=True)
    
    # Set QT_AUTO_SCREEN_SCALE_FACTOR for better scaling
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

def show_welcome_dialog():
    """Show welcome dialog with instructions."""
    from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout
    from PyQt5.QtCore import Qt
    
    dialog = QDialog()
    dialog.setWindowTitle('Welcome to Enhanced Typing Assistant')
    dialog.setFixedSize(600, 400)
    
    layout = QVBoxLayout()
    
    # Welcome message
    welcome_label = QLabel('Welcome to Enhanced Typing Assistant!')
    welcome_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(welcome_label)
    
    # Instructions
    instructions = """
    <h3>Getting Started:</h3>
    <ol>
        <li>First, you'll need to log in or create an account</li>
        <li>Enter your OpenAI API key when prompted</li>
        <li>Start typing in the input area</li>
    </ol>
    
    <h3>Features:</h3>
    <ul>
        <li>Real-time text correction</li>
        <li>Speech-to-text input</li>
        <li>Text-to-speech output</li>
        <li>Multiple language support</li>
        <li>Accessibility options</li>
    </ul>
    
    <h3>Tips:</h3>
    <ul>
        <li>Use Ctrl+Enter to correct text</li>
        <li>Press F1 for help</li>
        <li>Adjust settings in the menu</li>
    </ul>
    """
    
    instructions_label = QLabel(instructions)
    instructions_label.setWordWrap(True)
    instructions_label.setOpenExternalLinks(True)
    layout.addWidget(instructions_label)
    
    # OK button
    ok_button = QPushButton('Get Started')
    ok_button.clicked.connect(dialog.accept)
    layout.addWidget(ok_button)
    
    dialog.setLayout(layout)
    return dialog

def main():
    """Main function to run the application."""
    # Initialize QApplication
    app = QApplication(sys.argv)
    
    try:
        # Show welcome dialog
        welcome = show_welcome_dialog()
        welcome.exec_()
        
        # Create and show the main window
        window = EnhancedTypingAssistant()
        window.show()
        
        # Start the application event loop
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical('Fatal error occurred', exc_info=True)
        QMessageBox.critical(None, 'Error', f'A fatal error occurred: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Setup logging
        setup_logging()
        
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Enhanced Typing Assistant')
        parser.add_argument('--version', action='store_true', help='Show version information')
        args = parser.parse_args()
        
        if args.version:
            print(f'Enhanced Typing Assistant v{VERSION}')
            sys.exit(0)
        
        # Check dependencies and setup environment
        check_dependencies()
        setup_environment()
        
        # Run the application
        main()
    except Exception as e:
        logging.critical('Fatal error occurred', exc_info=True)
        sys.exit(1)
