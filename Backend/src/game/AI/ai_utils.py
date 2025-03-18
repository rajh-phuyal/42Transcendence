import os
from app.settings import DEBUG
from game.game_cache import set_game_data, get_game_data
from datetime import datetime, timezone
from django.core.cache import cache

def difficulty_to_string(difficulty: int) -> str:
    return {
        0: "easy",
        1: "medium",
        2: "hard",
    }[difficulty]


# Common constants used by all AI classes
DIFFICULTY_CONFIGS = {
    0: {"randomness": 0.9, "error_margin": 20}, # easy (high randomness, large errors)
    1: {"randomness": 0.5, "error_margin": 10}, # medium
    2: {"randomness": 0.2, "error_margin": 3},  # hard (low randomness, small errors)
}

DEBUG_FILE_PATH = os.path.join(os.path.dirname(__file__), "ai_debug.txt")


def calculate_ai_difficulty(ai_score, player_score):
    """
    Calculate appropriate AI difficulty based on current game scores.

    Returns:
    - 0: Easy (early game)
    - 1: Medium (mid game)
    - 2: Hard (late game when opponent winning)
    """
    max_score = max(ai_score, player_score)
    game_progress = min(1.0, max_score / 10.0) # 11 points game is assumed

    # Early game (first few points)
    if game_progress < 0.3:
        return 0

    # Mid game
    if game_progress < 0.7:
        return 1

    # Late game
    if player_score > ai_score:
        return 2
    else:
        return 1

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


def save_ai_stats_to_cache(game_id: str, stats: dict) -> None:
    """
    Save AI stats to the game cache
    """
    cache.set(f"ai_stats_{game_id}", stats, timeout=3000)
    debugger_log(f"Saved AI stats to cache for game {game_id}")

def load_ai_stats_from_cache(game_id: str) -> dict:
    """
    Load AI stats from the game cache
    """
    stats = cache.get(f"ai_stats_{game_id}")
    if stats:
        debugger_log(f"Loaded AI stats from cache for game {game_id}")
        # Check if __game_id__ is in the stats
        if "__game_id__" not in stats:
            debugger_log(f"WARNING: __game_id__ not found in cached stats for game {game_id}")
    return stats

def clear_ai_stats_cache(game_id: str) -> None:
    """
    Clear AI stats from the game cache
    """
    cache.delete(f"ai_stats_{game_id}")

# Import the components, to avoid circular imports
from .ai_learner import Learner
from .ai_thinker import Thinker
from .ai_player import AIPlayer
