import threading
import os
from pathlib import Path

# Shared resources for the app
indices = {}
indices_lock = threading.Lock()

# Resources directory - external location for indices and uploaded files
# Default: ~/.tm_resources, can be customized via TM_RESOURCES_PATH environment variable
_default_resources = Path.home() / ".tm_resources"
RESOURCES_DIR = Path(os.getenv("TM_RESOURCES_PATH", str(_default_resources)))

# Ensure resources directory exists
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

# Cache configuration - read from environment variables
# Enable cache (default: true)
CACHE_ENABLED = os.getenv("TM_CACHE_ENABLED", "true").lower() == "true"

# Cache backend: 'memory' (default) or 'redis'
CACHE_TYPE = os.getenv("TM_CACHE_TYPE", "memory")

# Maximum cache entries in memory (default: 1000)
# Older entries are evicted using LRU when limit is reached
CACHE_MAX_SIZE = int(os.getenv("TM_CACHE_MAX_SIZE", "1000"))
