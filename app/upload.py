
import os
import ahocorasick
import pickle
from collections import defaultdict

from fastapi import UploadFile
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
    inflect2uds = defaultdict(set) # one inflection can map to multiple UD terms (so we use a set to store them), but repeated keys are overwritten in the automaton, so we will store the full set of UDs in the value of the automaton

    # Parse uploaded file line by line, build a dictionary of source -> set of targets
    for line in file.file:
        # Each line is expected to be "ud<TAB>inflects"
        # ud : source term ||| target term
        # inflects : source term inflection1;source term inflection2;...
        line = line.decode("utf-8").rstrip("\n")
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        ud, inflects = parts
        inflects = inflects.split(";")
        for inflect in inflects:
            if inflect:
                inflect2uds[inflect].add(ud)

    # Save the dictionary to disk (for record-keeping, not strictly necessary for the automaton)
    tsv_path = os.path.join(RESOURCES_DIR, f"{name}.tsv")
    with open(tsv_path, "w", encoding="utf-8") as out:
        for inflect, uds in inflect2uds.items():
            out.write(f"{inflect}\t{';'.join(uds)}\n")

    # Build Aho-Corasick automaton
    automaton = ahocorasick.Automaton()
    for inflect, uds in inflect2uds.items():
        automaton.add_word(inflect, (inflect, uds))
    automaton.make_automaton()

    # Save the automaton as a pickle file
    pkl_path = os.path.join(RESOURCES_DIR, f"{name}.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump(automaton, f)
    with indices_lock:
        indices[name] = {"automaton": automaton, "size": len(automaton)}
    return UDUploadResponse(status="ok", index=name, size=len(automaton))
