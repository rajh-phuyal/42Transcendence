import numpy as np
from typing import List, Dict, Any
import threading
from queue import Queue, Empty
import logging
from game.constants import GAME_FPS


DIFFICULTY_CONFIGS = {
    # easy
    0: {
        "randomness": 0.3,
        "error_margin": 0.6
    },
    # medium
    1: {
        "randomness": 0.2,
        "error_margin": 0.5
    },
    # hard
    2: {
        "randomness": 0.1,
        "error_margin": 0.4
    }
}

class Thinker:
    """
    This class computes game strategies in the background while the game is running.
    It uses a separate thread to avoid blocking the game loop.
    """
    def __init__(self, action_queue: Queue, difficulty: int = 0):
        self.action_queue = action_queue
        self.depth = difficulty * 10
        self.compute_queue = Queue(maxsize=1)  # Queue for new game states to process
        self.result_queue = action_queue   # Queue for computed results
        self.running = True
        self.thread = threading.Thread(target=self._compute_loop, daemon=True)
        self.thread.start()

    def _compute_loop(self):
        """
        Background thread that continuously processes game states
        """
        while self.running:
            try:
                # Get the latest game state to process
                game_state = self.compute_queue.get()
                # Compute the next move/strategy
                result = self.train(game_state)
                # Clear the result queue of old results and put new result
                while not self.result_queue.empty():
                    self.result_queue.get()
                self.result_queue.put(result)
            except Exception as e:
                logging.error(f"Error in AI compute loop: {e}")

    def think(self, game_state: Dict[str, Any]) -> None:
        """
        Submit a new game state for processing.
        Non-blocking - will drop the state if the trainer is busy.
        """
        if not self.compute_queue.full():
            self.compute_queue.put(game_state)

    def train(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        The actual training/computation logic.
        This runs in the background thread.
        """
        # For now, just generate a random movement (placeholder)
        import random
        movements = ["0", "+", "-"]  # No movement, down, up
        movement = random.choice(movements)

        # Return in the format expected by the game
        return {
            'movePaddle': movement,
            'activatePowerupBig': False,
            'activatePowerupSpeed': False
        }

    def cleanup(self):
        """
        Cleanup method to stop the background thread
        """
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)  # Wait up to 1 second for thread to end


class AIPlayer:
    """
    This class is used to play the game.
    It uses Thinker for background computation while maintaining responsive gameplay.
    """

    def __init__(self, difficulty=1):
        # Get difficulty configuration
        self.difficulty = difficulty

        # Create a queue for AI movements
        self.action_queue = Queue(maxsize=GAME_FPS)

        # Create a thinker for AI computation
        self.thinker = Thinker(self.action_queue, difficulty)

        # Pre-fill the queue with default actions for the first second
        self._fill_queue_with_defaults()

    def compute(self, game_state):
        """
        Save the game state to the AI's memory for processing
        """
        # Send the game state to the thinker for background processing
        self.thinker.think(game_state)

        # If queue is running low, add some fallback actions
        # (This ensures we always have actions even if thinker is slow)
        if self.action_queue.qsize() <= 2:
            self._add_fallback_actions()

    async def action(self):
        """
        Return the next action from the queue
        """
        try:
            # Try to get an action from the queue
            action = self.action_queue.get_nowait()
            return action
        except Empty:
            # If queue is empty, return a default "do nothing" action
            return {
                'movePaddle': "0",
                'activatePowerupBig': False,
                'activatePowerupSpeed': False
            }

    def cleanup(self):
        """
        Cleanup method to be called when the game ends
        """
        # Stop the thinker's background processing
        self.thinker.cleanup()

        # Clear the queue
        while not self.action_queue.empty():
            self.action_queue.get()

    # Helper methods
    def _fill_queue_with_defaults(self):
        """Fill the queue with default no-movement actions"""
        # Clear the queue first
        while not self.action_queue.empty():
            self.action_queue.get()

        # Add no-movement actions for the first second
        default_action = {
            'movePaddle': "0",
            'activatePowerupBig': False,
            'activatePowerupSpeed': False
        }

        for _ in range(GAME_FPS):
            self.action_queue.put(default_action)

    def _add_fallback_actions(self):
        """Add some fallback actions to ensure queue never empties"""
        import random

        # Get config values based on difficulty
        config = DIFFICULTY_CONFIGS[self.difficulty]
        randomness = config["randomness"]
        error_margin = config["error_margin"]

        # Generate a few random movements as fallbacks
        prev_movement = "0"
        for _ in range(3):  # Add 3 fallback actions
            if random.random() < randomness:
                # Choose a random movement
                movements = ["0", "+", "-"]
                weights = [error_margin, (1 - error_margin) / 2, (1 - error_margin) / 2]
                movement = random.choices(movements, weights=weights, k=1)[0]
            else:
                # Keep previous movement for continuity
                movement = prev_movement

            prev_movement = movement

            # Only add if queue isn't full
            if not self.action_queue.full():
                self.action_queue.put({
                    'movePaddle': movement,
                    'activatePowerupBig': False,
                    'activatePowerupSpeed': False
                })

