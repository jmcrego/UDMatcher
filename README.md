# FastAPI AhoCorasick Matcher

A FastAPI application for high-speed exact matching using multiple <b>AhoCorasick</b> indices. Supports concurrent requests, index upload, and health monitoring.

## Preprocessing Glossaries and Queries

- A glossary (TSV file) consists of two columns separated by tabs (\t): a <b>source-side term</b> (used for retrieval) and a <b>target-side term</b>.
```
my source term[\t]my target term
```

- Source-side terms are NOT preprocessed before indexing or matching. In particular:
  - Matching is case-sensitive
  - No normalization or tokenization is applied
  - Punctuation and whitespace are preserved as-is


- The query contains a sentence field with the input text in which glossary entries (source-side terms) are matched:
```
An example of sentence containing the source term to be matched.
```

- Matching is performed directly against the raw query string using exact or substring-based comparison.

## Features
- Load all `*.pkl` indices from the `resources` directory at startup
- `/health`: List available indices and their sizes
- `/upload`: Upload a TSV file and specify the index name to create and load
- `/match`: Query one or more indices for exact matches in a sentence, returning match positions

## Endpoints

### `GET /health`
Returns a list of loaded indices and their sizes (number of entries).

### `POST /upload`
Upload a TSV file (two columns: `<source term>\t<target term>`) and specify the index name. The server saves the file as `resources/NAME.tsv`, builds the index, saves it as `resources/NAME.pkl`, and loads it into memory.

**Request (multipart/form-data):**
- `file`: The TSV file
- `name`: The desired index name (used for .tsv and .pkl files)

### `POST /match`
Query one or more indices for matches in a sentence.


## Setup

## Installation

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

Start the FastAPI server (default port 8000, or use --port 8001 if needed):
```bash
uvicorn app.main:app --reload --port 8001
```


## Example Requests

### Health Check
```bash
curl http://localhost:8001/health
```

### Upload an Index
```bash
curl -X POST "http://localhost:8001/upload" \
  -F "file=@/Users/josepcrego/Desktop/UD.en-fr.tsv" \
  -F "name=UD_enfr"
```

### Match a Sentence
```bash
curl -X POST "http://localhost:8001/match" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "your sentence here", "indices": ["UD_enfr"]}'
```

### Remove an Index
```bash
curl -X POST "http://localhost:8001/remove" \
  -H "Content-Type: application/json" \
  -d '{"index": "UD_enfr"}'
```

## Directory Structure
- `app.py` — Main FastAPI application
- `resources/` — Directory for .tsv and .pkl index files

## License
MIT
