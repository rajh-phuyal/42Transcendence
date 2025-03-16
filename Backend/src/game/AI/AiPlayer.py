from queue import Queue, Empty
from typing import Dict, Any
import random
from game.constants import GAME_FPS

from .AI import debug_write, DIFFICULTY_CONFIGS
from .AiThinker import Thinker

class AIPlayer:
    """
    Main AI used by the game loop. Owns the Thinker + action_queue.
    The game loop calls:
      ai.update(game_state)  # about once per second for a new state snapshot
      action = await ai.action()  # get action for the frame
    """

    def __init__(self, difficulty=0):
        self.difficulty = difficulty
        self.action_queue = Queue() # main queue where moments are stored
        self.thinker = Thinker(self.action_queue, difficulty) # my brain
        self.thinker.set_prediction_accuracy(4)

        self.last_performance_check = 0
        self.action_count = 0
        self.adapt_interval = 1  # Check for adaptation every snapshot

        # Game state tracking
        self.last_state = None
        self.last_left_score = 0
        self.last_right_score = 0

        # Initialize with neutral movement
        self.action_queue.put({
            "movePaddle": "0",
            "activatePowerupBig": False,
            "activatePowerupSpeed": False
        })

    def update(self, game_state: Dict[str, Any]) -> None:
        """
        Called every ~1s. Tells the AI to do a fresh plan.
        """
        # Update tracking data
        self.update_tracking(game_state)
        self.adapt_difficulty()

        # Clear the action queue for a fresh plan
        while not self.action_queue.empty():
            self.action_queue.get()

        # Let the thinker plan ahead - THIS HANDLES POWERUPS NOW
        self.thinker.think(game_state)

        # Ensure we never run out of actions
        if self.action_queue.qsize() <= 2:
            self.add_fallback_actions()

    def update_tracking(self, game_state: Dict[str, Any]) -> None:
        """
        Update game state tracking for next iteration
        """
        self.last_state = game_state
        self.last_left_score = game_state.get("playerLeft", {}).get("points", 0)
        self.last_right_score = game_state.get("playerRight", {}).get("points", 0)
        self.action_count += 1

    def adapt_difficulty(self) -> None:
        """
        Adapt AI difficulty based on performance
        """
        # Check periodically
        if self.action_count - self.last_performance_check < self.adapt_interval:
            return

        self.last_performance_check = self.action_count

        try:
            # Get performance metrics
            success_rate = self.thinker.learner.ai_stats.get("success_rate", 0.5)
            total_balls = self.thinker.learner.ai_stats.get("total_balls_faced", 0)

            # Need minimum data points
            if total_balls < 3:
                return

            # Determine if adjustment needed
            new_difficulty = self.difficulty

            if success_rate > 0.8 and self.difficulty < 2:
                new_difficulty = self.difficulty + 1
                debug_write(f"Increasing difficulty to {new_difficulty} (success rate: {success_rate:.2f})")
            elif success_rate < 0.3 and self.difficulty > 0:
                new_difficulty = self.difficulty - 1
                debug_write(f"Decreasing difficulty to {new_difficulty} (success rate: {success_rate:.2f})")

            # Apply change if needed
            if new_difficulty != self.difficulty:
                self.apply_difficulty_change(new_difficulty)

        except Exception as e:
            debug_write(f"Error in difficulty adaptation: {e}")

    def apply_difficulty_change(self, new_difficulty: int) -> None:
        """
        Apply difficulty change to all AI components
        """
        self.difficulty = new_difficulty
        self.thinker.difficulty = new_difficulty
        self.thinker.set_prediction_accuracy(8 - (new_difficulty * 2))
        self.thinker.learner.difficulty = new_difficulty
        self.thinker.learner.config = DIFFICULTY_CONFIGS.get(new_difficulty, DIFFICULTY_CONFIGS[1])
        debug_write(f"Difficulty adjusted to {new_difficulty}")

    def add_fallback_actions(self) -> None:
        """
        Add fallback actions to ensure we never run out
        """
        for _ in range(GAME_FPS // 6):
            if not self.action_queue.full():
                move = '0'
                self.action_queue.put({
                    'movePaddle': move,
                    'activatePowerupBig': False,
                    'activatePowerupSpeed': False
                })

    async def action(self) -> Dict[str, Any]:
        """
        Called by the game loop each frame to get the next AI action.
        If the queue is empty, returns a do-nothing fallback.
        """
        try:
            return self.action_queue.get_nowait()
        except Empty:
            self.add_fallback_actions()
            try:
                return self.action_queue.get_nowait()
            except Empty:
                # Emergency fallback
                debug_write("Emergency fallback: action queue still empty!")
                return {
                    "movePaddle": "0",
                    "activatePowerupBig": False,
                    "activatePowerupSpeed": False
                }

    def cleanup(self) -> None:
        """
        Clean up the background thread when the game ends.
        """
        self.thinker.cleanup()
        while not self.action_queue.empty():
            self.action_queue.get()