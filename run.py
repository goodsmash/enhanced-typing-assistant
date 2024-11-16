#!/usr/bin/env python3
"""Launcher script for the Typing Assistant application."""

import sys
import os
import logging
from pathlib import Path
from typing import List, Optional
import subprocess
import traceback
import shutil


def setup_logging() -> None:
    """Set up logging configuration."""
    log_dir = Path.home() / ".typing_assistant" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Rotate old log file if it exists
    log_file = log_dir / 'startup.log'
    if log_file.exists():
        backup = log_dir / 'startup.log.old'
        shutil.copy2(log_file, backup)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def ensure_dependencies() -> bool:
    """Ensure all required dependencies are installed."""
    required_packages = [
        'PyQt5',
        'cryptography',
        'openai',
        'nltk',
        'pyttsx3',
        'SpeechRecognition',
        'pyenchant',
        'keyring',
        'appdirs',
        'PyJWT',
        'configparser'
    ]
    
    try:
        import pkg_resources
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = [pkg for pkg in required_packages if pkg.lower() not in installed]
        
        if missing:
            logging.info(f"Installing missing dependencies: {', '.join(missing)}")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", *missing
            ])
            logging.info("Dependencies installed successfully")
            
        # Verify installation
        import PyQt5
        import cryptography
        import openai
        import nltk
        import pyttsx3
        import speech_recognition
        import enchant
        import keyring
        import appdirs
        import jwt
        import configparser
        
        logging.info("All dependencies verified successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error installing dependencies: {e}", exc_info=True)
        return False


def setup_nltk() -> bool:
    """Download required NLTK data."""
    try:
        import nltk
        
        required_packages = [
            'punkt',
            'averaged_perceptron_tagger',
            'maxent_ne_chunker',
            'words',
            'stopwords'
        ]
        
        for package in required_packages:
            try:
                nltk.data.find(f'tokenizers/{package}')
            except LookupError:
                logging.info(f"Downloading NLTK package: {package}")
                nltk.download(package, quiet=True)
        
        return True
        
    except Exception as e:
        logging.error(f"Error setting up NLTK: {e}", exc_info=True)
        return False


def setup_config_dirs() -> bool:
    """Set up configuration directories."""
    try:
        from typing_assistant.config import ConfigManager
        
        # Initialize config manager to create necessary directories
        config = ConfigManager()
        logging.info("Configuration directories set up successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error setting up configuration: {e}", exc_info=True)
        return False


def main() -> int:
    """Run the Typing Assistant application."""
    try:
        # Set up logging first
        setup_logging()
        logging.info("Starting Typing Assistant...")
        
        # Add the project directory to Python path
        project_dir = Path(__file__).resolve().parent
        sys.path.insert(0, str(project_dir))
        
        # Ensure dependencies are installed
        if not ensure_dependencies():
            logging.error("Failed to install required dependencies")
            return 1
        
        # Setup NLTK data
        if not setup_nltk():
            logging.error("Failed to set up NLTK data")
            return 1
            
        # Setup configuration directories
        if not setup_config_dirs():
            logging.error("Failed to set up configuration")
            return 1
        
        # Import and run the application
        try:
            from typing_assistant.app import TypingAssistant
            from PyQt5.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            window = TypingAssistant()
            window.show()
            return app.exec_()
            
        except ImportError as e:
            logging.error(f"Error importing application modules: {e}", exc_info=True)
            return 1
            
    except Exception as e:
        logging.error(f"Unhandled error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
