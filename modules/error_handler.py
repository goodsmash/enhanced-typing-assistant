import sys
import traceback
import logging
from typing import Callable, Dict, Optional, Type
from datetime import datetime
from dataclasses import dataclass
from PyQt5.QtWidgets import QMessageBox

@dataclass
class ErrorInfo:
    """Container for error information."""
    error_type: Type[Exception]
    message: str
    timestamp: datetime
    traceback: str
    context: Dict[str, str]

class ErrorHandler:
    """Centralized error handling for the application."""
    
    def __init__(self):
        self.error_history: Dict[datetime, ErrorInfo] = {}
        self.error_callbacks: Dict[Type[Exception], Callable] = {}
        self.default_handler: Optional[Callable] = None
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configure logging settings."""
        logging.basicConfig(
            filename='typing_assistant_errors.log',
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def register_handler(self, error_type: Type[Exception], handler: Callable) -> None:
        """Register a handler for a specific error type."""
        self.error_callbacks[error_type] = handler

    def set_default_handler(self, handler: Callable) -> None:
        """Set the default error handler."""
        self.default_handler = handler

    def handle_error(self, error: Exception, context: Dict[str, str] = None) -> None:
        """Handle an error using registered handlers or default handler."""
        error_info = ErrorInfo(
            error_type=type(error),
            message=str(error),
            timestamp=datetime.now(),
            traceback=''.join(traceback.format_tb(error.__traceback__)),
            context=context or {}
        )
        
        # Log the error
        logging.error(
            f"Error: {error_info.message}\n"
            f"Type: {error_info.error_type.__name__}\n"
            f"Context: {error_info.context}\n"
            f"Traceback:\n{error_info.traceback}"
        )
        
        # Store in history
        self.error_history[error_info.timestamp] = error_info
        
        # Find and execute appropriate handler
        handler = self.error_callbacks.get(type(error))
        if handler:
            handler(error_info)
        elif self.default_handler:
            self.default_handler(error_info)
        else:
            self.show_error_dialog(error_info)

    def show_error_dialog(self, error_info: ErrorInfo) -> None:
        """Show error dialog to user."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(f"An error occurred: {error_info.message}")
        msg.setDetailedText(
            f"Error Type: {error_info.error_type.__name__}\n"
            f"Timestamp: {error_info.timestamp}\n"
            f"Context: {error_info.context}\n"
            f"Traceback:\n{error_info.traceback}"
        )
        msg.exec_()

    def get_error_history(self, error_type: Type[Exception] = None) -> Dict[datetime, ErrorInfo]:
        """Get error history, optionally filtered by error type."""
        if error_type is None:
            return self.error_history
        return {
            ts: info for ts, info in self.error_history.items()
            if info.error_type == error_type
        }

    def clear_error_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()

    def get_error_statistics(self) -> Dict[str, int]:
        """Get statistics about errors that have occurred."""
        stats = {}
        for error_info in self.error_history.values():
            error_type = error_info.error_type.__name__
            stats[error_type] = stats.get(error_type, 0) + 1
        return stats

    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback) -> None:
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_info = ErrorInfo(
            error_type=exc_type,
            message=str(exc_value),
            timestamp=datetime.now(),
            traceback=''.join(traceback.format_tb(exc_traceback)),
            context={"type": "uncaught_exception"}
        )
        
        logging.critical(
            f"Uncaught exception:\n"
            f"Type: {error_info.error_type.__name__}\n"
            f"Message: {error_info.message}\n"
            f"Traceback:\n{error_info.traceback}"
        )
        
        self.show_error_dialog(error_info)
