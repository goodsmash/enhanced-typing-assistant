from datetime import datetime, timedelta
from typing import Any, Dict, Tuple, Optional, Iterator, List

class ExpiringCache:
    """Cache with size limit and expiration time.
    
    Attributes:
        max_size: Maximum number of items to store in cache
        expiration_minutes: Time in minutes before items expire
    """
    
    _cache: Dict[Tuple[str, str, str, str], Tuple[Any, datetime]]
    max_size: int
    expiration_minutes: int
    
    def __init__(self, max_size: int = 1000, expiration_minutes: int = 60) -> None:
        if max_size <= 0 or expiration_minutes <= 0:
            raise ValueError("max_size and expiration_minutes must be greater than 0")
        self._cache = {}
        self.max_size = max_size
        self.expiration_minutes = expiration_minutes

    def get(self, key: Tuple[str, str, str, str]) -> Optional[Any]:
        """Get item from cache if it exists and hasn't expired.
        
        Args:
            key: Tuple of strings identifying the cache item
            
        Returns:
            Cached value if exists and valid, None otherwise
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(minutes=self.expiration_minutes):
                return value
            del self._cache[key]
        return None

    def set(self, key: Tuple[str, str, str, str], value: Any) -> None:
        """Add item to cache, removing oldest if at size limit.
        
        Args:
            key: Tuple of strings identifying the cache item
            value: Value to store in cache
        """
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.items(), key=lambda x: x[1][1])[0]
            del self._cache[oldest_key]
        self._cache[key] = (value, datetime.now())

    def cleanup_expired(self) -> None:
        """Remove all expired entries from the cache."""
        now = datetime.now()
        self._cache = {
            key: (value, timestamp) for key, (value, timestamp) in self._cache.items()
            if now - timestamp < timedelta(minutes=self.expiration_minutes)
        }

    def clear(self) -> None:
        """Remove all items from the cache."""
        self._cache.clear()

    def size(self) -> int:
        """Return current number of active (non-expired) items in cache."""
        now = datetime.now()
        return sum(1 for _, (_, timestamp) in self._cache.items()
                   if now - timestamp < timedelta(minutes=self.expiration_minutes))

    def has_key(self, key: Tuple[str, str, str, str]) -> bool:
        """Check if key exists in cache and is not expired."""
        if key in self._cache:
            _, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(minutes=self.expiration_minutes):
                return True
            else:
                del self._cache[key]
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.now()
        active_items = sum(1 for _, (_, ts) in self._cache.items()
                          if now - ts < timedelta(minutes=self.expiration_minutes))
        return {
            "total_items": len(self._cache),
            "active_items": active_items,
            "expired_items": len(self._cache) - active_items,
            "max_size": self.max_size
        }

    def __iter__(self) -> Iterator[Tuple[str, str, str, str]]:
        """Iterate over non-expired keys in the cache."""
        now = datetime.now()
        return (key for key, (_, ts) in self._cache.items()
                if now - ts < timedelta(minutes=self.expiration_minutes))

    def __len__(self) -> int:
        """Return number of items in cache (including expired)."""
        return len(self._cache)

class PatternCache(ExpiringCache):
    """Cache specifically for typing patterns with statistical tracking."""
    
    def __init__(self, max_size: int = 1000, expiration_minutes: int = 60) -> None:
        super().__init__(max_size, expiration_minutes)
        self.pattern_stats = {}
    
    def add_pattern(self, pattern: str, correction: str) -> None:
        """Track pattern statistics."""
        if pattern not in self.pattern_stats:
            self.pattern_stats[pattern] = {
                'count': 0,
                'corrections': {}
            }
        self.pattern_stats[pattern]['count'] += 1
        if correction in self.pattern_stats[pattern]['corrections']:
            self.pattern_stats[pattern]['corrections'][correction] += 1
        else:
            self.pattern_stats[pattern]['corrections'][correction] = 1
    
    def get_pattern_stats(self) -> Dict[str, Dict]:
        """Get statistics about typing patterns."""
        return self.pattern_stats

    def get_common_corrections(self, pattern: str) -> List[Tuple[str, int]]:
        """Get most common corrections for a pattern."""
        if pattern in self.pattern_stats:
            corrections = self.pattern_stats[pattern]['corrections']
            return sorted(corrections.items(), key=lambda x: x[1], reverse=True)
        return []