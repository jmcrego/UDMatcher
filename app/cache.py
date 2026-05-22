"""
Caching system for UDMatcher with LRU in-memory cache or Redis backend support.
Inspired by TMMatcher caching architecture.

Supports:
- LocalMemoryCache: Fast in-memory LRU cache (default)
- RedisCache: Distributed cache backend for multi-server deployments
"""

import time
import threading
from typing import Any, Optional, Dict
from collections import OrderedDict
from enum import Enum


class CacheType(Enum):
    MEMORY = "memory"
    REDIS = "redis"


class LocalMemoryCache:
    """In-memory LRU (Least Recently Used) cache backend."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache and move to end (mark as recently used)."""
        with self.lock:
            if key not in self.cache:
                return None
            # Move to end (mark as recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def put(self, key: str, value: Any) -> None:
        """Put value in cache, removing oldest if at capacity."""
        with self.lock:
            if key in self.cache:
                # Move existing key to end
                self.cache.move_to_end(key)
            else:
                # Add new key
                if len(self.cache) >= self.max_size:
                    # Remove oldest (first) item
                    self.cache.popitem(last=False)
            self.cache[key] = value
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Get current number of entries in cache."""
        with self.lock:
            return len(self.cache)
    
    def get_all(self) -> Dict:
        """Get all cache entries (for debugging/stats)."""
        with self.lock:
            return dict(self.cache)


class RedisCache:
    """Distributed Redis cache backend (placeholder for future implementation)."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        # TODO: Implement Redis connection and methods
        print("WARNING: Redis cache not yet fully implemented. Using LocalMemoryCache fallback.")
        self.backend = LocalMemoryCache(max_size)
    
    def get(self, key: str) -> Optional[Any]:
        """Get from Redis cache."""
        return self.backend.get(key)
    
    def put(self, key: str, value: Any) -> None:
        """Put to Redis cache."""
        self.backend.put(key, value)
    
    def clear(self) -> None:
        """Clear Redis cache."""
        self.backend.clear()
    
    def size(self) -> int:
        """Get cache size."""
        return self.backend.size()


class CacheManager:
    """
    Manager for request result caching.
    Supports multiple backends (Memory/Redis) for different deployment scenarios.
    """
    
    def __init__(self, enabled: bool = True, cache_type: str = "memory", max_size: int = 1000):
        self.enabled = enabled
        self.cache_type = CacheType(cache_type.lower())
        self.max_size = max_size
        
        # Initialize appropriate cache backend
        if self.cache_type == CacheType.MEMORY:
            self.backend = LocalMemoryCache(max_size)
        elif self.cache_type == CacheType.REDIS:
            self.backend = RedisCache(max_size)
        else:
            self.backend = LocalMemoryCache(max_size)
    
    def get(self, key: str) -> Optional[Any]:
        """Get from cache if enabled."""
        if not self.enabled:
            return None
        return self.backend.get(key)
    
    def put(self, key: str, value: Any) -> None:
        """Put to cache if enabled."""
        if not self.enabled:
            return
        self.backend.put(key, value)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.backend.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return self.backend.size()
    
    def get_status(self) -> Dict[str, Any]:
        """Get cache status for health endpoint."""
        return {
            "enabled": self.enabled,
            "type": self.cache_type.value,
            "size": self.size(),
            "max_size": self.max_size
        }


def get_cache_manager() -> CacheManager:
    """Factory function to create cache manager from shared configuration."""
    from .shared import CACHE_ENABLED, CACHE_TYPE, CACHE_MAX_SIZE
    
    return CacheManager(enabled=CACHE_ENABLED, cache_type=CACHE_TYPE, max_size=CACHE_MAX_SIZE)
