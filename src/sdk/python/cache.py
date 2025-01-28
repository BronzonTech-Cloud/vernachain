"""Caching implementation for the Vernachain SDK."""

import time
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict
from dataclasses import dataclass

@dataclass
class CacheEntry:
    """Cache entry with value and expiration."""
    value: Any
    expires_at: float

class LRUCache:
    """LRU Cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of items to store
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self.cache:
            return None
            
        entry = self.cache[key]
        
        # Check if expired
        if time.time() > entry.expires_at:
            del self.cache[key]
            return None
            
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return entry.value
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default_ttl if None)
        """
        # Remove if key exists
        if key in self.cache:
            del self.cache[key]
            
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove first item (least recently used)
            
        expires_at = time.time() + (ttl if ttl is not None else self.default_ttl)
        self.cache[key] = CacheEntry(value, expires_at)
        
    def delete(self, key: str) -> None:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
        """
        if key in self.cache:
            del self.cache[key]
            
    def clear(self) -> None:
        """Clear all entries from cache."""
        self.cache.clear()
        
    def cleanup(self) -> None:
        """Remove expired entries."""
        now = time.time()
        expired = [
            key for key, entry in self.cache.items()
            if now > entry.expires_at
        ]
        for key in expired:
            del self.cache[key]


class CacheManager:
    """Cache manager with different TTLs for different types of data."""
    
    def __init__(self):
        # Different caches for different data types
        self.block_cache = LRUCache(max_size=1000, default_ttl=60)  # 1 minute for blocks
        self.tx_cache = LRUCache(max_size=10000, default_ttl=300)   # 5 minutes for transactions
        self.balance_cache = LRUCache(max_size=1000, default_ttl=30) # 30 seconds for balances
        self.stats_cache = LRUCache(max_size=100, default_ttl=60)    # 1 minute for stats
        
    def get_cache_for_endpoint(self, endpoint: str) -> Tuple[LRUCache, Optional[int]]:
        """
        Get appropriate cache and TTL for endpoint.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Tuple of (cache instance, ttl override or None)
        """
        if '/block/' in endpoint:
            return self.block_cache, None
        elif '/transaction/' in endpoint:
            return self.tx_cache, None
        elif '/address/' in endpoint:
            return self.balance_cache, None
        elif '/stats' in endpoint:
            return self.stats_cache, None
        else:
            return self.block_cache, 10  # Default cache with short TTL
            
    def cleanup_all(self) -> None:
        """Clean up all caches."""
        self.block_cache.cleanup()
        self.tx_cache.cleanup()
        self.balance_cache.cleanup()
        self.stats_cache.cleanup() 