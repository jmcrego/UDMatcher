"""
Index store management - loads and manages Aho-Corasick indices at startup.
"""

import os
import pickle
from .shared import indices, indices_lock, RESOURCES_DIR

def load_index(name: str) -> bool:
    """
    Load a single pickled Aho-Corasick index from disk.
    
    Args:
        name: Index name (corresponds to NAME.pkl file)
    
    Returns:
        True if loaded successfully, False otherwise
    """
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

def load_all_indices() -> None:
    """
    Load all pickled Aho-Corasick indices from the resources directory.
    Called at application startup to populate the indices cache.
    """
    for fname in os.listdir(RESOURCES_DIR):
        if fname.endswith(".pkl"):
            name = fname[:-4]
            success = load_index(name)
            if success:
                print(f"  - Loaded index: {name}")
            else:
                print(f"  - Failed to load index: {name}")
