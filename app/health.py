from pydantic import BaseModel
from typing import List
from .shared import indices, indices_lock

class UDHealthIndex(BaseModel):
    name: str
    size: int

class UDHealthResponse(BaseModel):
    indices: List[UDHealthIndex]

def health_endpoint() -> UDHealthResponse:
    with indices_lock:
        return UDHealthResponse(indices=[UDHealthIndex(name=k, size=v["size"]) for k, v in indices.items()])
