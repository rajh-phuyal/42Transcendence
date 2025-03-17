import os
from app.settings import DEBUG

# Common constants used by all AI classes
DIFFICULTY_CONFIGS = {
    0: {"randomness": 0.9, "error_margin": 20}, # hard
    1: {"randomness": 0.5, "error_margin": 10}, # medium
    2: {"randomness": 0.2, "error_margin": 3}, # easy
}

DEBUG_FILE_PATH = os.path.join(os.path.dirname(__file__), "ai_debug.txt")


def calculate_ai_difficulty(ai_score, player_score):
    """
    Calculate appropriate AI difficulty based on current game scores.

    Returns:
    - 0: Easy
    - 1: Medium
    - 2: Hard
    """
    max_score = max(ai_score, player_score)
    progress = min(1.0, max_score / 10.0) # 11 points game is asumed
    diff = ai_score - player_score
    normalized_diff = max(-1.0, min(1.0, diff / 5.0))

    # Calculate base difficulty (ranges from 0.0 to 2.0)
    # Higher when:
    # - Game is further progressed
    # - AI is ahead (maintain lead)
    # - Player is significantly ahead (comeback mode)
    difficulty_float = (
        1.2 * progress
        + 0.5 * normalized_diff
        + (0.8 if player_score >= 8 and ai_score <= player_score - 2 else 0.0)
    )

    difficulty = max(0, min(2, round(difficulty_float)))

    return difficulty

def debugger_log(msg: str, file_path: str = DEBUG_FILE_PATH):
    """
    Appends a line of debug info to ai_debug.txt.
    This is for debugging only, to see what's happening inside the AI code.
    """
    if not DEBUG:
        return

    # You may want to handle exceptions or concurrency more robustly in production.
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Import the components, to avoid circular imports
from .ai_learner import Learner
from .ai_thinker import Thinker
from .ai_player import AIPlayer
