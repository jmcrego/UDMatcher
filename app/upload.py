
import os
import ahocorasick
import pickle
from collections import defaultdict

from fastapi import UploadFile, HTTPException
from pydantic import BaseModel
from .shared import indices, indices_lock, RESOURCES_DIR

class UDUploadResponse(BaseModel):
    status: str
    index: str
    size: int

def upload_endpoint(file: UploadFile, name: str) -> UDUploadResponse:
    """
    Expects a TSV file with two columns: source and target.
    Creates an Aho-Corasick automaton from the source terms and saves it as a pickle file.
    """
    inflect_to_uds = defaultdict(set)

    # Parse uploaded file line by line and aggregate all targets for each source term.
    for line in file.file:
        line = line.decode("utf-8").rstrip("\n")
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        ud, inflects = parts[:2] 
        ud = ud.strip()
        inflects = inflects.strip().split(";")  # Assuming multiple inflects are semicolon-separated
        if ud and inflects:
            for inflect in inflects:
                inflect_to_uds[inflect].add(ud)

    if not inflect_to_uds:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file produced an empty index. Check TSV format and content."
        )

    # Save the dictionary to disk (for record-keeping, not strictly necessary for the automaton)
    # tsv_path = os.path.join(RESOURCES_DIR, f"{name}.tsv")
    # with open(tsv_path, "w", encoding="utf-8") as out:
    #     for inflect, uds in inflect_to_uds.items():
    #         out.write(f"{inflect}\t{';'.join(sorted(uds))}\n")

    # Build Aho-Corasick automaton
    automaton = ahocorasick.Automaton()
    for inflect, uds in inflect_to_uds.items():
        automaton.add_word(inflect, (inflect, uds))
    automaton.make_automaton()

    # Save the automaton as a pickle file
    pkl_path = os.path.join(RESOURCES_DIR, f"{name}.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump(automaton, f)
    with indices_lock:
        indices[name] = {"automaton": automaton, "size": len(automaton)}
    return UDUploadResponse(status="ok", index=name, size=len(automaton))
