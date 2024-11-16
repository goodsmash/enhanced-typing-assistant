"""Debug panel for monitoring application state."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTextEdit, QPushButton, QTabWidget, QTreeWidget,
                           QTreeWidgetItem, QCheckBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

class DebugPanel(QWidget):
    """Debug panel for monitoring application state and components."""
    
    def __init__(self, parent=None):
        """Initialize debug panel."""
        super().__init__(parent)
        self.setWindowTitle("Debug Panel")
        self.setGeometry(100, 100, 800, 600)
        
        # Setup logging
        self.log_handler = QTextEditLogHandler(self)
        logging.getLogger().addHandler(self.log_handler)
        
        # Initialize UI
        self.init_ui()
        
        # Update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # Update every second
        
        # Component states
        self.components = {
            "Text Processor": False,
            "Speech Handler": False,
            "API Connection": False,
            "Spell Check": False,
            "Grammar Check": False
        }
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Components Tab
        components_widget = QWidget()
        components_layout = QVBoxLayout()
        
        # Component status tree
        self.component_tree = QTreeWidget()
        self.component_tree.setHeaderLabels(["Component", "Status", "Details"])
        self.component_tree.setColumnWidth(0, 200)
        components_layout.addWidget(self.component_tree)
        
        components_widget.setLayout(components_layout)
        tabs.addTab(components_widget, "Components")
        
        # Logs Tab
        logs_widget = QWidget()
        logs_layout = QVBoxLayout()
        
        # Log level selector
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Log Level:"))
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level.setCurrentText("INFO")
        self.log_level.currentTextChanged.connect(self.change_log_level)
        level_layout.addWidget(self.log_level)
        level_layout.addStretch()
        
        logs_layout.addLayout(level_layout)
        
        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(QFont("Courier", 10))
        logs_layout.addWidget(self.log_viewer)
        
        # Clear logs button
        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self.log_viewer.clear)
        logs_layout.addWidget(clear_button)
        
        logs_widget.setLayout(logs_layout)
        tabs.addTab(logs_widget, "Logs")
        
        # Statistics Tab
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        
        self.stats_tree = QTreeWidget()
        self.stats_tree.setHeaderLabels(["Metric", "Value"])
        self.stats_tree.setColumnWidth(0, 200)
        stats_layout.addWidget(self.stats_tree)
        
        stats_widget.setLayout(stats_layout)
        tabs.addTab(stats_widget, "Statistics")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
    def update_component_status(self, name: str, active: bool, details: str = ""):
        """Update the status of a component."""
        self.components[name] = active
        items = self.component_tree.findItems(name, Qt.MatchExactly, 0)
        
        if not items:
            item = QTreeWidgetItem(self.component_tree)
            item.setText(0, name)
        else:
            item = items[0]
            
        status = "Active" if active else "Inactive"
        item.setText(1, status)
        item.setText(2, details)
        
        # Set color based on status
        color = QColor("#2ecc71") if active else QColor("#e74c3c")
        item.setForeground(1, color)
        
    def update_stats(self):
        """Update statistics display."""
        self.stats_tree.clear()
        
        # Memory usage
        import psutil
        process = psutil.Process()
        memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_item = QTreeWidgetItem(self.stats_tree)
        memory_item.setText(0, "Memory Usage")
        memory_item.setText(1, f"{memory:.2f} MB")
        
        # CPU usage
        cpu_item = QTreeWidgetItem(self.stats_tree)
        cpu_item.setText(0, "CPU Usage")
        cpu_item.setText(1, f"{process.cpu_percent()}%")
        
        # Active threads
        import threading
        threads_item = QTreeWidgetItem(self.stats_tree)
        threads_item.setText(0, "Active Threads")
        threads_item.setText(1, str(threading.active_count()))
        
    def change_log_level(self, level: str):
        """Change the logging level."""
        numeric_level = getattr(logging, level.upper(), None)
        if numeric_level is not None:
            logging.getLogger().setLevel(numeric_level)
            
class QTextEditLogHandler(logging.Handler):
    """Custom logging handler that writes to a QTextEdit."""
    
    def __init__(self, debug_panel):
        """Initialize the handler."""
        super().__init__()
        self.debug_panel = debug_panel
        self.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        
    def emit(self, record):
        """Emit a log record."""
        msg = self.format(record)
        self.debug_panel.log_viewer.append(msg)
        
        # Color code based on level
        color = {
            logging.DEBUG: "#2d3436",    # Gray
            logging.INFO: "#2980b9",     # Blue
            logging.WARNING: "#f39c12",  # Orange
            logging.ERROR: "#c0392b",    # Red
            logging.CRITICAL: "#8e44ad"  # Purple
        }.get(record.levelno, "#2d3436")
        
        cursor = self.debug_panel.log_viewer.textCursor()
        format = cursor.charFormat()
        format.setForeground(QColor(color))
        cursor.movePosition(cursor.End)
        cursor.insertText("\n")
