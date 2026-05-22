from fastapi import HTTPException
from pydantic import BaseModel
from .shared import indices, indices_lock, RESOURCES_DIR
from .cache import get_cache_manager
import os


class UDRemoveRequest(BaseModel):
    index: str

class UDRemoveResponse(BaseModel):
    status: str
    index: str


def remove_endpoint(request: UDRemoveRequest) -> UDRemoveResponse:
    name = request.index
    with indices_lock:
        if name not in indices:
            raise HTTPException(status_code=404, detail=f"Index '{name}' not found.")
        # Remove from memory
        del indices[name]
    # Remove .pkl file
    pkl_path = os.path.join(RESOURCES_DIR, f"{name}.pkl")
    if os.path.exists(pkl_path):
        os.remove(pkl_path)
    # Remove .tsv file
    tsv_path = os.path.join(RESOURCES_DIR, f"{name}.tsv")
    if os.path.exists(tsv_path):
        os.remove(tsv_path)
    
    # Invalidate cache when index is removed
    cache_manager = get_cache_manager()
    cache_manager.clear()
    
    return UDRemoveResponse(status="removed", index=name)

