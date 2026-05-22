

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from pydantic import BaseModel
from typing import List

from .index_store import load_all_indices
from .upload import upload_endpoint, UDUploadResponse
from .match import match_endpoint, UDMatchRequest, UDMatchResponse
from .health import health_endpoint, UDHealthResponse
from .remove import remove_endpoint, UDRemoveRequest, UDRemoveResponse
from .cache import get_cache_manager
from .statistics import get_statistics_manager

# Application lifespan: startup and shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize cache backend and load indices
    cache_manager = get_cache_manager()
    stats_manager = get_statistics_manager()
    print(f"Cache backend initialized: {cache_manager.cache_type.value} (enabled: {cache_manager.enabled})")
    print(f"Statistics tracking initialized")
    
    load_all_indices()
    print(f"Indices loaded at startup")
    
    yield  # Application serving
    
    # Cleanup on shutdown (if needed)
    print(f"Shutting down application")

# FastAPI application with async lifespan management
app = FastAPI(
    title="UDMatcher - Aho-Corasick Glossary Matcher",
    description="High-speed exact glossary term matching with caching and statistics",
    lifespan=lifespan
)


# ============================================================================
# ENDPOINTS
# ============================================================================

# GET /health - Health check with indices, cache status, and statistics
@app.get("/health", response_model=UDHealthResponse)
def health():
    """Get service health status, loaded indices, cache status, and statistics."""
    return health_endpoint()

# POST /upload - Upload glossary and create/update index
@app.post("/upload", response_model=UDUploadResponse)
def upload(file: UploadFile = File(...), name: str = Form(...)):
    """Upload a TSV glossary file (source<TAB>target) and create a searchable index."""
    return upload_endpoint(file, name)


# POST /match - Query indices for glossary term matches
@app.post("/match", response_model=UDMatchResponse)
def match(request: UDMatchRequest):
    """Query one or more indices for exact glossary term matches in a sentence."""
    return match_endpoint(request)

# POST /remove - Remove an index
@app.post("/remove", response_model=UDRemoveResponse)
def remove(request: UDRemoveRequest):
    """Delete an index from memory and disk."""
    return remove_endpoint(request)


# ============================================================================
# MIDDLEWARE & CONFIGURATION
# ============================================================================

# CORS middleware - allow all origins for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
