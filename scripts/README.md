# UDMatcher Scripts

Utility and test scripts for UDMatcher demonstration and management.

## Available Scripts

### 1. **health_check.py**
Quick health status check for the running server.

```bash
python scripts/health_check.py              # Full health report
python scripts/health_check.py --list       # List indices only
python scripts/health_check.py --stats      # Show statistics only
```

### 2. **cache_stats.py**
Detailed cache and performance statistics display.

```bash
python scripts/cache_stats.py stats         # Show cache statistics
python scripts/cache_stats.py health        # Full health endpoint response
python scripts/cache_stats.py clear         # Clear cache (note: clears on index change)
```

### 3. **test_basic_functionality.py**
Comprehensive test suite demonstrating all basic features:
- Health check endpoint
- Uploading a sample glossary
- Performing matches
- Viewing cache and statistics

```bash
python scripts/test_basic_functionality.py
```

Features demonstrated:
- ✓ Health check with indices, cache, and statistics
- ✓ Uploading TSV glossary files
- ✓ Matching queries against indices
- ✓ Cache hit/miss tracking
- ✓ Performance metrics collection

### 4. **test_cache_performance.py**
Demonstrates cache performance with repeated queries.

```bash
python scripts/test_cache_performance.py
```

Shows:
- Baseline statistics
- Query performance with cache hits (second identical query should be faster)
- Final statistics with cache hit rate

## Getting Started

1. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. **Run basic tests:**
   ```bash
   python scripts/test_basic_functionality.py
   ```

3. **Check health:**
   ```bash
   python scripts/health_check.py
   ```

4. **Demonstrate caching:**
   ```bash
   python scripts/test_cache_performance.py
   ```

## Key Features Demonstrated

### Caching System
- LRU in-memory cache (default)
- Configurable cache size via `TM_CACHE_MAX_SIZE` environment variable
- Cache automatically invalidated on index changes
- Configure via environment variables:
  ```bash
  export TM_CACHE_ENABLED=true
  export TM_CACHE_TYPE=memory
  export TM_CACHE_MAX_SIZE=1000
  ```

### Performance Statistics
- Total requests tracked
- Cache hit/miss rates
- Runtime metrics (min, max, average)
- All available in `/health` endpoint

### External Resources
- Indices stored in `~/.tm_resources/` (configurable via `TM_RESOURCES_PATH`)
- Separated from project repository
- Persistent across restarts

## Requirements

```bash
pip install requests
# Already in requirements.txt
```

## Example Output

```
$ python scripts/health_check.py

✓ Server is running

======================================================================
  UDMatcher Health Check
======================================================================

Loaded Indices: 2
  • en_fr_sample: 12 entries
  • sample_glossary: 25 entries

Cache Configuration:
  • Status: Enabled
  • Backend: memory
  • Size: 8/1000

Service Statistics:
  • Total Requests: 23
  • Successful: 23
  • Errors: 0
  • Cache Hits: 5
  • Cache Misses: 18
  • Hit Rate: 21.74%
  • Avg Runtime: 2.45ms

======================================================================
```
