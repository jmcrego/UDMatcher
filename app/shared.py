import threading
from pathlib import Path

# Shared resources for the app
indices = {}
indices_lock = threading.Lock()
RESOURCES_DIR = Path(__file__).parent.parent / "resources"
