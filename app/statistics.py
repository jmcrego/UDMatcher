"""
Performance statistics tracking for UDMatcher.
Tracks request metrics, cache performance, and runtime analysis.
"""

import threading
import time
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class StatisticsData:
    """Statistics data structure."""
    total_requests: int = 0
    successful_requests: int = 0
    total_errors: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_runtime_ms: float = 0.0
    min_runtime_ms: float = float('inf')
    max_runtime_ms: float = 0.0
    
    @property
    def cache_hit_rate_percent(self) -> float:
        """Calculate cache hit rate percentage."""
        total_cache_ops = self.cache_hits + self.cache_misses
        if total_cache_ops == 0:
            return 0.0
        return (self.cache_hits / total_cache_ops) * 100
    
    @property
    def average_runtime_ms(self) -> float:
        """Calculate average runtime."""
        if self.total_requests == 0:
            return 0.0
        return self.total_runtime_ms / self.total_requests
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['cache_hit_rate_percent'] = round(self.cache_hit_rate_percent, 2)
        data['average_runtime_ms'] = round(self.average_runtime_ms, 2)
        data['min_runtime_ms'] = round(self.min_runtime_ms, 2) if self.min_runtime_ms != float('inf') else 0.0
        data['max_runtime_ms'] = round(self.max_runtime_ms, 2)
        return data


class StatisticsManager:
    """Manager for tracking service statistics."""
    
    def __init__(self):
        self.stats = StatisticsData()
        self.lock = threading.Lock()
    
    def record_request(self, runtime_ms: float, success: bool = True, 
                      cache_hit: bool = False) -> None:
        """Record a request with its metrics."""
        with self.lock:
            self.stats.total_requests += 1
            
            if success:
                self.stats.successful_requests += 1
            else:
                self.stats.total_errors += 1
            
            if cache_hit:
                self.stats.cache_hits += 1
            else:
                self.stats.cache_misses += 1
            
            self.stats.total_runtime_ms += runtime_ms
            self.stats.min_runtime_ms = min(self.stats.min_runtime_ms, runtime_ms)
            self.stats.max_runtime_ms = max(self.stats.max_runtime_ms, runtime_ms)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        with self.lock:
            return self.stats.to_dict()
    
    def reset(self) -> None:
        """Reset all statistics."""
        with self.lock:
            self.stats = StatisticsData()
    
    def get_cache_hits(self) -> int:
        """Get cache hit count."""
        with self.lock:
            return self.stats.cache_hits
    
    def get_cache_misses(self) -> int:
        """Get cache miss count."""
        with self.lock:
            return self.stats.cache_misses


# Global statistics manager instance
_statistics_manager: StatisticsManager = None


def get_statistics_manager() -> StatisticsManager:
    """Get or create global statistics manager."""
    global _statistics_manager
    if _statistics_manager is None:
        _statistics_manager = StatisticsManager()
    return _statistics_manager
