
import os
import pickle
from .shared import indices, indices_lock, RESOURCES_DIR

def load_index(name: str):
    # Ensure resources directory exists
    os.makedirs(RESOURCES_DIR, exist_ok=True)

    pkl_path = os.path.join(RESOURCES_DIR, f"{name}.pkl")
    if not os.path.exists(pkl_path):
        return False
    with open(pkl_path, "rb") as f:
        automaton = pickle.load(f)

    # Backward compatibility: finalize trie objects saved before make_automaton().
    if len(automaton) > 0:
        try:
            automaton.iter("")
        except AttributeError:
            automaton.make_automaton()

    with indices_lock:
        indices[name] = {"automaton": automaton, "size": len(automaton)}
    return True

def load_all_indices():
    for fname in os.listdir(RESOURCES_DIR):
        if fname.endswith(".pkl"):
            name = fname[:-4]
            load_index(name)
