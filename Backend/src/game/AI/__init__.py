"""
AI module for Pong with all the classes that the game loop needs.
"""
from .ai_utils import DIFFICULTY_CONFIGS, calculate_ai_difficulty
from .ai_player import AIPlayer
from .ai_thinker import Thinker
from .ai_learner import Learner

__all__ = ["AIPlayer", "Thinker", "Learner", "DIFFICULTY_CONFIGS", "calculate_ai_difficulty"]