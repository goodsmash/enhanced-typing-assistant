"""Visualization module for typing performance and learning curves"""

from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class PerformanceCanvas(FigureCanvasQTAgg):
    """Canvas for displaying performance metrics"""
    
    def __init__(self, width: int = 8, height: int = 6, dpi: int = 100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)
        
    def clear(self):
        """Clear the figure and close it properly"""
        self.fig.clear()
        plt.close(self.fig)
        
class LearningCurveWidget(QWidget):
    """Widget for displaying learning curves and performance trends"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.canvas = PerformanceCanvas()
        self.layout.addWidget(self.canvas)
        
    def closeEvent(self, event):
        """Handle widget closure"""
        self.canvas.clear()
        super().closeEvent(event)
        
    def plot_learning_curve(self, 
                          data: List[Dict[str, float]], 
                          metric: str = 'wpm',
                          window_size: int = 5) -> None:
        """Plot learning curve for a specific metric
        
        Args:
            data: List of performance data points
            metric: Metric to plot ('wpm', 'accuracy', 'streak')
            window_size: Size of moving average window
        """
        try:
            if not data:
                self._show_no_data_message()
                return
                
            # Extract data and ensure timezone consistency
            dates = []
            values = []
            for d in data:
                try:
                    date = datetime.fromisoformat(d['timestamp']).replace(tzinfo=None)
                    value = float(d[metric])
                    dates.append(date)
                    values.append(value)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid data point: {e}")
                    continue
            
            if not dates:
                self._show_no_data_message()
                return
                
            # Calculate moving average
            if len(values) >= window_size:
                ma = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
                ma_dates = dates[window_size-1:]
            else:
                ma = values
                ma_dates = dates
            
            # Clear previous plot
            self.canvas.axes.clear()
            
            # Plot raw data and moving average
            self.canvas.axes.plot(dates, values, 'o-', alpha=0.5, label='Raw data')
            self.canvas.axes.plot(ma_dates, ma, 'r-', linewidth=2, label=f'{window_size}-point moving average')
            
            # Add trend line
            z = np.polyfit(range(len(values)), values, 1)
            p = np.poly1d(z)
            self.canvas.axes.plot(dates, p(range(len(values))), 'g--', 
                                label=f'Trend: {z[0]:.2f} {metric}/session')
            
            # Customize plot
            self.canvas.axes.set_title(f'{metric.upper()} Learning Curve')
            self.canvas.axes.set_xlabel('Session Date')
            self.canvas.axes.set_ylabel(metric.upper())
            self.canvas.axes.legend()
            self.canvas.axes.grid(True, alpha=0.3)
            
            # Set reasonable y-axis limits
            min_val = min(values)
            max_val = max(values)
            range_val = max_val - min_val
            self.canvas.axes.set_ylim(
                min_val - range_val * 0.1,
                max_val + range_val * 0.1
            )
            
            # Rotate x-axis labels for better readability
            plt.setp(self.canvas.axes.get_xticklabels(), rotation=45)
            
            # Adjust layout to prevent label cutoff
            self.canvas.fig.tight_layout()
            
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error plotting learning curve: {e}")
            self._show_error_message()
    
    def plot_performance_heatmap(self, 
                               data: List[Dict[str, float]], 
                               metric: str = 'wpm') -> None:
        """Plot performance heatmap showing daily/hourly patterns
        
        Args:
            data: List of performance data points
            metric: Metric to plot ('wpm', 'accuracy', 'streak')
        """
        try:
            if not data:
                self._show_no_data_message()
                return
                
            # Extract hour and day information
            hours = []
            days = []
            values = []
            for d in data:
                try:
                    date = datetime.fromisoformat(d['timestamp']).replace(tzinfo=None)
                    hour = date.hour
                    day = date.strftime('%A')
                    value = float(d[metric])
                    hours.append(hour)
                    days.append(day)
                    values.append(value)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid data point: {e}")
                    continue
            
            if not hours:
                self._show_no_data_message()
                return
            
            # Create 24x7 matrix for heatmap
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap = np.zeros((24, 7))
            counts = np.zeros((24, 7))
            
            for hour, day, value in zip(hours, days, values):
                day_idx = day_order.index(day)
                heatmap[hour, day_idx] += value
                counts[hour, day_idx] += 1
            
            # Calculate averages, avoiding division by zero
            with np.errstate(divide='ignore', invalid='ignore'):
                heatmap = np.divide(heatmap, counts)
                heatmap[np.isnan(heatmap)] = 0
            
            # Clear previous plot
            self.canvas.axes.clear()
            
            # Plot heatmap
            im = self.canvas.axes.imshow(heatmap, aspect='auto', cmap='YlOrRd')
            
            # Customize plot
            self.canvas.axes.set_title(f'{metric.upper()} Performance by Time')
            self.canvas.axes.set_xlabel('Day of Week')
            self.canvas.axes.set_ylabel('Hour of Day')
            
            # Set tick labels
            self.canvas.axes.set_xticks(range(7))
            self.canvas.axes.set_xticklabels(day_order, rotation=45)
            self.canvas.axes.set_yticks(range(0, 24, 2))
            self.canvas.axes.set_yticklabels(range(0, 24, 2))
            
            # Add colorbar
            self.canvas.figure.colorbar(im, ax=self.canvas.axes, 
                                      label=f'Average {metric.upper()}')
            
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error plotting performance heatmap: {e}")
            self._show_error_message()
    
    def plot_achievement_progress(self, achievements: List[Dict]) -> None:
        """Plot achievement progress
        
        Args:
            achievements: List of achievement data
        """
        try:
            if not achievements:
                self._show_no_data_message()
                return
            
            # Extract data
            names = [a['name'] for a in achievements if not a['unlocked']]
            progress = [a['progress'] for a in achievements if not a['unlocked']]
            
            if not names:  # All achievements unlocked
                self.canvas.axes.clear()
                self.canvas.axes.text(0.5, 0.5, 'All Achievements Unlocked! 🎉',
                                    ha='center', va='center', fontsize=14)
                self.canvas.draw()
                return
            
            # Clear previous plot
            self.canvas.axes.clear()
            
            # Create horizontal bar chart
            y_pos = np.arange(len(names))
            self.canvas.axes.barh(y_pos, progress, align='center')
            
            # Customize plot
            self.canvas.axes.set_title('Achievement Progress')
            self.canvas.axes.set_xlabel('Progress (%)')
            self.canvas.axes.set_yticks(y_pos)
            self.canvas.axes.set_yticklabels(names)
            
            # Add progress labels
            for i, v in enumerate(progress):
                self.canvas.axes.text(v + 1, i, f'{v:.1f}%', va='center')
            
            # Set limits
            self.canvas.axes.set_xlim(0, 100)
            
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error plotting achievement progress: {e}")
            self._show_error_message()
    
    def plot_improvement_radar(self, 
                             current_stats: Dict[str, float],
                             baseline_stats: Dict[str, float]) -> None:
        """Plot radar chart showing improvement across multiple metrics
        
        Args:
            current_stats: Current performance statistics
            baseline_stats: Baseline performance statistics
        """
        try:
            # Define metrics to plot
            metrics = ['wpm', 'accuracy', 'streak', 'session_length']
            
            # Get values, handling missing metrics
            current_values = [current_stats.get(m, 0) for m in metrics]
            baseline_values = [baseline_stats.get(m, 0) for m in metrics]
            
            # Calculate angles for radar chart
            angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
            
            # Close the plot by appending first values
            current_values += [current_values[0]]
            baseline_values += [baseline_values[0]]
            angles = np.concatenate((angles, [angles[0]]))
            
            # Clear previous plot
            self.canvas.axes.clear()
            
            # Create radar plot
            self.canvas.axes.plot(angles, current_values, 'o-', linewidth=2, label='Current')
            self.canvas.axes.plot(angles, baseline_values, 'o-', linewidth=2, label='Baseline')
            self.canvas.axes.fill(angles, current_values, alpha=0.25)
            
            # Set labels
            self.canvas.axes.set_xticks(angles[:-1])
            self.canvas.axes.set_xticklabels(metrics)
            
            # Add legend and title
            self.canvas.axes.legend(loc='upper right')
            self.canvas.axes.set_title('Performance Improvement Radar')
            
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error plotting improvement radar: {e}")
            self._show_error_message()
    
    def _show_no_data_message(self):
        """Display message when no data is available"""
        self.canvas.axes.clear()
        self.canvas.axes.text(0.5, 0.5, 'No data available yet.\nKeep practicing!',
                            ha='center', va='center', fontsize=12)
        self.canvas.draw()
        
    def _show_error_message(self):
        """Display error message when plotting fails"""
        self.canvas.axes.clear()
        self.canvas.axes.text(0.5, 0.5, 'Error displaying data.\nPlease try again.',
                            ha='center', va='center', fontsize=12, color='red')
        self.canvas.draw()
