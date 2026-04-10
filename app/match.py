
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


def is_word_boundary(sentence: str, start: int, end: int) -> bool:
    # Check left boundary
    if start > 0 and sentence[start - 1].isalnum():
        return False
    # Check right boundary
    if end + 1 < len(sentence) and sentence[end + 1].isalnum():
        return False
    return True

def match_endpoint(request: UDMatchRequest) -> UDMatchResponse:
    results = []
    tic = time.perf_counter()
    with indices_lock:
        for idx in request.indices:
            print(f"Matching against index: {idx}")
            entry = indices.get(idx)
            if not entry:
                print(f"Index not found: {idx}")
                continue
            if entry.get("size", 0) == 0:
                continue
            automaton = entry["automaton"]
            try:
                iterator = automaton.iter(request.sentence)
            except AttributeError:
                # Backward compatibility for pickles saved as trie (not finalized automaton).
                if len(automaton) == 0:
                    continue
                automaton.make_automaton()
                iterator = automaton.iter(request.sentence)

            print(f"Request sentence: '{request.sentence}'")
            for end_pos, (source, target) in iterator:
                print(f"Found match: source='{source}', target='{target}', end_pos={end_pos}")
                start_pos = end_pos - len(source) + 1
                if not is_word_boundary(request.sentence, start_pos, end_pos):
                    continue

                targets = target if isinstance(target, (set, list, tuple)) else [target]
                for tgt in targets:
                    print(f"Appending match: index='{idx}', source='{source}', target='{tgt}', start={start_pos}, end={end_pos}")
                    results.append(UDMatchResult(
                        index=idx,
                        source=source,
                        target=str(tgt),
                        start=start_pos,
                        end=end_pos
                    ))
    # Remove matches whose span is fully contained within a larger match's span
    # from the same index.
    filtered = [
        r for r in results
        if not any(
            other.index == r.index
            and (other.start <= r.start and other.end >= r.end)
            and (other.start < r.start or other.end > r.end)
            for other in results
        )
    ]

    runtime_s = time.perf_counter() - tic
    return UDMatchResponse(matches=filtered, runtime_ms=runtime_s * 1000)
