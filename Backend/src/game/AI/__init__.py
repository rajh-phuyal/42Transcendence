"""
AI module for Pong with all the classes that the game loop needs.
"""
from .AI import DIFFICULTY_CONFIGS
from .AiPlayer import AIPlayer
from .AiThinker import Thinker
from .AiLearner import Learner

__all__ = ["AIPlayer", "Thinker", "Learner", "DIFFICULTY_CONFIGS"]