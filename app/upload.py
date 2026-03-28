
import os
import ahocorasick
import pickle

from fastapi import UploadFile
from pydantic import BaseModel
from .shared import indices, indices_lock, RESOURCES_DIR

class UDUploadResponse(BaseModel):
    status: str
    index: str
    size: int

def upload_endpoint(file: UploadFile, name: str) -> UDUploadResponse:
    tsv_path = os.path.join(RESOURCES_DIR, f"{name}.tsv")
    with open(tsv_path, "wb") as out:
        out.write(file.file.read())
    automaton = ahocorasick.Automaton()
    with open(tsv_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 2:
                continue
            source, target = parts
            automaton.add_word(source, (source, target))
    automaton.make_automaton()
    pkl_path = os.path.join(RESOURCES_DIR, f"{name}.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump(automaton, f)
    with indices_lock:
        indices[name] = {"automaton": automaton, "size": len(automaton)}
    return UDUploadResponse(status="ok", index=name, size=len(automaton))
