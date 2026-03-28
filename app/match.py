
import time
from pydantic import BaseModel
from typing import List
from .shared import indices, indices_lock

class UDMatchRequest(BaseModel):
    sentence: str
    indices: List[str]

class UDMatchResult(BaseModel):
    index: str
    source: str
    target: str
    start: int
    end: int

class UDMatchResponse(BaseModel):
    matches: List[UDMatchResult]
    runtime_ms: float = 0

def match_endpoint(request: UDMatchRequest) -> UDMatchResponse:
    results = []
    tic = time.perf_counter()
    with indices_lock:
        for idx in request.indices:
            entry = indices.get(idx)
            if not entry:
                continue
            automaton = entry["automaton"]
            for end_pos, (source, target) in automaton.iter(request.sentence):
                start_pos = end_pos - len(source) + 1
                results.append(UDMatchResult(
                    index=idx,
                    source=source,
                    target=target,
                    start=start_pos,
                    end=end_pos
                ))
    runtime_s = time.perf_counter() - tic
    return UDMatchResponse(matches=results, runtime_ms=runtime_s * 1000)
