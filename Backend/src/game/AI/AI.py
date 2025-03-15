import os
from app.settings import DEBUG

# Common constants used by all AI classes
DIFFICULTY_CONFIGS = {
    0: {"randomness": 0, "error_margin": 0}, # hard
    1: {"randomness": 0.1, "error_margin": 0.4}, # medium
    2: {"randomness": 0.2, "error_margin": 0.5}, # easy
}

DEBUG_FILE_PATH = os.path.join(os.path.dirname(__file__), "ai_debug.txt")

def debug_write(msg: str):
    """
    Appends a line of debug info to ai_debug.txt.
    This is for debugging only, to see what's happening inside the AI code.
    """
    if not DEBUG:
        return

    # You may want to handle exceptions or concurrency more robustly in production.
    with open(DEBUG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Import the components - these come after our definitions to avoid circular imports
from .AiLearner import Learner
from .AiThinker import Thinker
from .AiPlayer import AIPlayer
