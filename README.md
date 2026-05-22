# FastAPI AhoCorasick Matcher

A FastAPI application for high-speed exact matching using multiple **AhoCorasick** indices. Supports concurrent requests, index upload, health monitoring, intelligent caching, and performance statistics.

## Features

### Core Matching
- Load all `*.pkl` indices from external `~/.tm_resources/` directory at startup
- `/health`: List available indices with cache and performance statistics
- `/upload`: Upload a TSV file and specify the index name to create and load
- `/match`: Query one or more indices for exact matches in a sentence, returning match positions

### New Features (v2.0)
- **Caching System**: In-memory LRU cache (or Redis) to speed up repeated queries
- **Performance Statistics**: Track requests, cache hits/misses, and runtime metrics
- **External Resources**: Indices stored in `~/.tm_resources/` (configurable)
- **Test Scripts**: Comprehensive examples in `/scripts/` directory

## Preprocessing Glossaries and Queries

- A glossary (TSV file) consists of two columns separated by [TAB] (`\t`): a **source-side term** (used for retrieval) and a **target-side term**.
```
my source term[TAB]my target term
```

- Source-side terms are **NOT** preprocessed before indexing or matching. In particular:
  - Matching is case-sensitive
  - No normalization, tokenization or punctuation removal is applied

- The query contains a sentence field with the input text in which glossary entries (source-side terms) are matched:
```
An example of sentence containing the source term to be matched.
```

- Matching is performed using the Aho–Corasick algorithm over the raw query string.
- A match is returned only if the span identified by the Aho–Corasick algorithm corresponds to a **full word match**, i.e. the matched substring is bounded by non-word characters (or string boundaries) and does not occur as part of a larger word.

## Caching

UDMatcher includes an intelligent caching system to improve performance for repeated searches.

### Cache Configuration

Configure cache behavior via environment variables:

```bash
# Enable cache (default: true)
export TM_CACHE_ENABLED=true

# Cache backend: 'memory' (default) or 'redis'
export TM_CACHE_TYPE=memory

# Maximum cache entries in memory (default: 1000)
export TM_CACHE_MAX_SIZE=1000
```

### Cache Backends

- **Memory (default)**: Fast in-memory LRU cache, perfect for single-server deployments
- **Redis**: Distributed cache backend for multi-server setups (requires Redis installation)

### Cache Management

View cache statistics:
```bash
python scripts/cache_stats.py stats
python scripts/health_check.py
```

## External Resources Directory

By default, UDMatcher stores all indices and uploads in `~/.tm_resources/`. To use a custom location, set the environment variable:

```bash
export TM_RESOURCES_PATH=/path/to/your/resources
```

The directory will be created automatically if it doesn't exist. This separation keeps your project repository clean and allows indices to persist independently.

## Endpoints

### `GET /health`
Returns a list of loaded indices with their sizes, cache status, and service statistics.

**Response Example:**
```json
{
  "indices": [
    {"name": "en_fr_sample", "size": 12}
  ],
  "cache": {
    "enabled": true,
    "type": "memory",
    "size": 5,
    "max_size": 1000
  },
  "statistics": {
    "total_requests": 42,
    "successful_requests": 42,
    "total_errors": 0,
    "cache_hits": 8,
    "cache_misses": 34,
    "cache_hit_rate_percent": 19.05,
    "average_runtime_ms": 3.2,
    "min_runtime_ms": 0.5,
    "max_runtime_ms": 25.3
  }
}
```

### `POST /upload`
Upload a TSV file (two columns: `<source term>\t<target term>`) and specify the index name. The server saves the file to `~/.tm_resources/NAME.tsv`, builds the index, saves it as `~/.tm_resources/NAME.pkl`, and loads it into memory. **Note:** Cache is automatically cleared when indices are uploaded.

**Request (multipart/form-data):**
- `file`: The TSV file
- `name`: The desired index name (used for .tsv and .pkl files)

### `POST /match`
Query one or more indices for exact matches in a sentence. Results are cached for identical queries.

**Request JSON:**
```json
{
  "sentence": "your sentence here",
  "indices": ["index_name_1", "index_name_2"]
}
```

**Response:**
```json
{
  "matches": [
    {
      "index": "index_name_1",
      "source": "matched source",
      "target": "matched target",
      "start": 0,
      "end": 14
    }
  ],
  "runtime_ms": 1.23,
  "cached": false
}
```

**Response fields:**
- `matches`: Array of exact matches found in the sentence
- `runtime_ms`: Time to perform the search (in milliseconds)
- `cached`: Boolean indicating if the result was served from cache (true = cache hit, false = new search)

### `POST /remove`
Delete an index and its associated files from disk and memory.

**Request JSON:**
```json
{
  "index": "index_name"
}
```

## Setup

### Installation

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install requirements:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Running the Server

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

## Testing & Examples

Comprehensive test scripts are provided in the `/scripts/` directory:

```bash
# Full test suite (upload, match, statistics)
python scripts/test_basic_functionality.py

# Quick health check
python scripts/health_check.py

# Demonstrate cache performance
python scripts/test_cache_performance.py

# View cache statistics
python scripts/cache_stats.py stats
```

See [scripts/README.md](scripts/README.md) for detailed documentation on each test script.

## Example Requests

### Health Check
```bash
curl http://localhost:8000/health | python -m json.tool
```

### Upload an Index
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/glossary.tsv" \
  -F "name=my_glossary"
```

### Match a Sentence
```bash
curl -X POST "http://localhost:8000/match" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "your sentence here", "indices": ["my_glossary"]}'
```

### Remove an Index
```bash
curl -X POST "http://localhost:8000/remove" \
  -H "Content-Type: application/json" \
  -d '{"index": "my_glossary"}'
```

## Directory Structure

- `app/` — Main application modules
  - `main.py` — FastAPI application
  - `cache.py` — Caching system (LRU, Redis support)
  - `statistics.py` — Performance statistics tracking
  - `health.py`, `match.py`, `upload.py`, `remove.py` — Endpoint implementations
  - `shared.py` — Shared resources (indices, resources directory)
- `scripts/` — Test scripts and utilities
  - `test_basic_functionality.py` — Full feature demonstration
  - `test_cache_performance.py` — Cache performance demo
  - `health_check.py` — Quick health status
  - `cache_stats.py` — Cache management
- `~/.tm_resources/` — External resources directory (indices, TSV files)

## License

MIT

## License
MIT
