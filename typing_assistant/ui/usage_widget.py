"""Widget for displaying AI usage statistics and costs."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QProgressBar, QPushButton, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Dict
import json

class UsageWidget(QWidget):
    """Widget to display token usage and cost information."""
    
    reset_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        
        # Token Usage Section
        token_frame = QFrame()
        token_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        token_layout = QVBoxLayout()
        
        self.total_tokens_label = QLabel("Total Tokens: 0")
        self.token_progress = QProgressBar()
        self.token_progress.setMaximum(100)
        self.token_progress.setValue(0)
        
        token_layout.addWidget(self.total_tokens_label)
        token_layout.addWidget(self.token_progress)
        token_frame.setLayout(token_layout)
        
        # Cost Section
        cost_frame = QFrame()
        cost_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        cost_layout = QVBoxLayout()
        
        self.total_cost_label = QLabel("Total Cost: $0.00")
        self.cost_breakdown = QLabel()
        self.cost_breakdown.setWordWrap(True)
        
        cost_layout.addWidget(self.total_cost_label)
        cost_layout.addWidget(self.cost_breakdown)
        cost_frame.setLayout(cost_layout)
        
        # Model Usage Section
        model_frame = QFrame()
        model_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        model_layout = QVBoxLayout()
        
        self.model_usage_label = QLabel("Model Usage:")
        self.model_breakdown = QLabel()
        self.model_breakdown.setWordWrap(True)
        
        model_layout.addWidget(self.model_usage_label)
        model_layout.addWidget(self.model_breakdown)
        model_frame.setLayout(model_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset Statistics")
        self.reset_button.clicked.connect(self.reset_requested.emit)
        self.export_button = QPushButton("Export Report")
        self.export_button.clicked.connect(self.export_usage_report)
        
        controls_layout.addWidget(self.reset_button)
        controls_layout.addWidget(self.export_button)
        
        # Add all sections to main layout
        layout.addWidget(token_frame)
        layout.addWidget(cost_frame)
        layout.addWidget(model_frame)
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)
        
    def update_usage(self, usage_data: Dict):
        """Update the display with new usage data."""
        # Update total tokens
        total_tokens = usage_data['total_tokens']
        self.total_tokens_label.setText(f"Total Tokens: {total_tokens:,}")
        
        # Update token progress (assuming a daily limit of 100,000 tokens)
        progress = min(100, (total_tokens / 100000) * 100)
        self.token_progress.setValue(int(progress))
        
        # Update cost information
        total_cost = usage_data['total_cost']
        self.total_cost_label.setText(f"Total Cost: ${total_cost:.4f}")
        
        # Update model breakdown
        model_text = []
        for model, stats in usage_data['models'].items():
            model_text.append(
                f"{model}:\n"
                f"  Input Tokens: {stats['input_tokens']:,}\n"
                f"  Output Tokens: {stats['output_tokens']:,}\n"
                f"  Cost: ${stats['total_cost']:.4f}"
            )
        
        self.model_breakdown.setText("\n\n".join(model_text))
        
    def export_usage_report(self):
        """Export usage statistics to a JSON file."""
        try:
            with open('usage_report.json', 'w') as f:
                json.dump(self.current_usage, f, indent=2)
        except Exception as e:
            print(f"Error exporting usage report: {e}")
            
    def reset_display(self):
        """Reset all display elements to their default state."""
        self.total_tokens_label.setText("Total Tokens: 0")
        self.token_progress.setValue(0)
        self.total_cost_label.setText("Total Cost: $0.00")
        self.model_breakdown.setText("")
        self.cost_breakdown.setText("")
