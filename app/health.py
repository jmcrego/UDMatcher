from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .shared import indices, indices_lock
from .cache import get_cache_manager
from .statistics import get_statistics_manager


class UDHealthIndex(BaseModel):
    name: str
    size: int


class CacheStatus(BaseModel):
    enabled: bool
    type: str
    size: int
    max_size: int


class UDHealthResponse(BaseModel):
    indices: List[UDHealthIndex]
    cache: Optional[CacheStatus] = None
    statistics: Optional[Dict[str, Any]] = None


def health_endpoint() -> UDHealthResponse:
    """Health endpoint returning indices, cache status, and statistics."""
    with indices_lock:
        indices_list = [UDHealthIndex(name=k, size=v["size"]) for k, v in indices.items()]
    
    # Get cache status
    cache_manager = get_cache_manager()
    cache_status = CacheStatus(**cache_manager.get_status())
    
    # Get statistics
    stats_manager = get_statistics_manager()
    statistics = stats_manager.get_stats()
    
    return UDHealthResponse(
        indices=indices_list,
        cache=cache_status,
        statistics=statistics
    )
