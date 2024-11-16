import threading
import time
from typing import Any, Dict, Optional
from threading import Lock

class ExpiringCache:
    """Thread-safe cache with expiring entries."""
    
    def __init__(self, expiry_time: int = 3600):
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._lock = Lock()
        self._expiry_time = expiry_time
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if it exists and hasn't expired."""
        with self._lock:
            if key not in self._cache:
                return None
            
            value, timestamp = self._cache[key]
            if time.time() - timestamp > self._expiry_time:
                del self._cache[key]
                return None
                
            return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache with the current timestamp."""
        with self._lock:
            self._cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
    
    def _cleanup_loop(self) -> None:
        """Periodically clean up expired entries."""
        while True:
            time.sleep(300)  # Run cleanup every 5 minutes
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Remove expired entries from the cache."""
        current_time = time.time()
        with self._lock:
            keys_to_delete = [
                key for key, (_, timestamp) in self._cache.items()
                if current_time - timestamp > self._expiry_time
            ]
            for key in keys_to_delete:
                del self._cache[key]
