#!/usr/bin/env python3

import sys
import os
import signal
import logging
import argparse
from pathlib import Path
import asyncio
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

from assistant_ui import TypingAssistant
from accessibility import AccessibilityManager
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

VERSION = '1.0.0'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.error_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.setup_error_handling()
        
    def setup_error_handling(self):
        """Set up global error handling."""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
                
            logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            self.error_queue.put((exc_type, exc_value, exc_traceback))
            
        sys.excepthook = handle_exception
        
    def process_errors(self):
        """Process errors from the error queue."""
        try:
            while not self.error_queue.empty():
                exc_type, exc_value, exc_traceback = self.error_queue.get_nowait()
                error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                
                # Log the error
                logger.error(f"Application error: {error_message}")
                
                # Show error dialog if critical
                if issubclass(exc_type, (RuntimeError, ImportError, AttributeError)):
                    QMessageBox.critical(
                        self.main_window,
                        "Critical Error",
                        f"A critical error occurred:\n{str(exc_value)}\n\nPlease check the log file for details."
                    )
                    
        except Exception as e:
            logger.error(f"Error in error processor: {e}")
            
    def initialize_application(self):
        """Initialize the main application components."""
        try:
            # Show splash screen
            splash_pixmap = QPixmap("assets/splash.png")
            splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
            splash.show()
            self.app.processEvents()
            
            # Initialize main window
            self.main_window = TypingAssistant()
            
            # Set up error processing timer
            self.error_timer = QTimer()
            self.error_timer.timeout.connect(self.process_errors)
            self.error_timer.start(1000)  # Check for errors every second
            
            # Initialize event loop for async operations
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Set up translation thread
            self.translation_thread = QThread()
            self.main_window.accessibility_manager.translation_worker.moveToThread(self.translation_thread)
            self.translation_thread.start()
            
            # Show main window and close splash
            self.main_window.show()
            splash.finish(self.main_window)
            
        except Exception as e:
            logger.error(f"Error initializing application: {e}")
            QMessageBox.critical(None, "Initialization Error", f"Failed to initialize application: {str(e)}")
            sys.exit(1)
            
    def run(self):
        """Run the application."""
        try:
            self.initialize_application()
            return self.app.exec_()
        except Exception as e:
            logger.error(f"Error running application: {e}")
            return 1
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources before exit."""
        try:
            if self.main_window:
                self.main_window.cleanup()
            if hasattr(self, 'translation_thread'):
                self.translation_thread.quit()
                self.translation_thread.wait()
            self.executor.shutdown(wait=True)
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    """Main entry point for the application."""
    try:
        app_manager = ApplicationManager()
        return app_manager.run()
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        return 1

if __name__ == '__main__':
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
        
        # Run the application
        sys.exit(main())
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
