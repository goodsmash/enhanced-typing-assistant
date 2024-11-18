import time
import psutil
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    cpu_percent: float
    memory_percent: float
    response_time_ms: float
    timestamp: datetime

class PerformanceMonitor:
    """Monitors application performance metrics."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.metrics_history: List[PerformanceMetrics] = []
        self.process = psutil.Process()
        self._start_time: Optional[float] = None

    def start_operation(self) -> None:
        """Start timing an operation."""
        self._start_time = time.time()

    def end_operation(self) -> float:
        """End timing an operation and return duration in milliseconds."""
        if self._start_time is None:
            return 0.0
        duration = (time.time() - self._start_time) * 1000
        self._start_time = None
        return duration

    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        try:
            cpu_percent = self.process.cpu_percent()
            memory_percent = self.process.memory_percent()
            response_time = self.end_operation() if self._start_time else 0.0
            
            metrics = PerformanceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                response_time_ms=response_time,
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history.pop(0)
                
            return metrics
        except Exception as e:
            logging.error(f"Error collecting performance metrics: {e}")
            raise

    def get_average_metrics(self, last_n: int = None) -> Dict[str, float]:
        """Calculate average metrics over the specified number of samples."""
        if not self.metrics_history:
            return {
                "avg_cpu_percent": 0.0,
                "avg_memory_percent": 0.0,
                "avg_response_time_ms": 0.0
            }

        samples = self.metrics_history[-last_n:] if last_n else self.metrics_history
        
        return {
            "avg_cpu_percent": sum(m.cpu_percent for m in samples) / len(samples),
            "avg_memory_percent": sum(m.memory_percent for m in samples) / len(samples),
            "avg_response_time_ms": sum(m.response_time_ms for m in samples) / len(samples)
        }

    def get_peak_metrics(self) -> Dict[str, float]:
        """Get peak performance metrics."""
        if not self.metrics_history:
            return {
                "peak_cpu_percent": 0.0,
                "peak_memory_percent": 0.0,
                "peak_response_time_ms": 0.0
            }

        return {
            "peak_cpu_percent": max(m.cpu_percent for m in self.metrics_history),
            "peak_memory_percent": max(m.memory_percent for m in self.metrics_history),
            "peak_response_time_ms": max(m.response_time_ms for m in self.metrics_history)
        }

    def clear_history(self) -> None:
        """Clear metrics history."""
        self.metrics_history.clear()

    def get_performance_report(self) -> Dict[str, Dict[str, float]]:
        """Generate a comprehensive performance report."""
        return {
            "current": self.collect_metrics().__dict__,
            "average": self.get_average_metrics(),
            "peak": self.get_peak_metrics()
        }

    def is_performance_critical(self, thresholds: Dict[str, float]) -> bool:
        """Check if current performance metrics exceed critical thresholds."""
        current = self.collect_metrics()
        return (
            current.cpu_percent > thresholds.get("cpu_percent", 80) or
            current.memory_percent > thresholds.get("memory_percent", 80) or
            current.response_time_ms > thresholds.get("response_time_ms", 1000)
        )
