import numpy as np
from typing import List, Dict, Any
import threading
from queue import Queue
import logging

class Thinker:
    """
    This class computes game strategies in the background while the game is running.
    It uses a separate thread to avoid blocking the game loop.
    """
    def __init__(self, depth: int = 0):
        self.depth = depth
        self.compute_queue = Queue(maxsize=1)  # Queue for new game states to process
        self.result_queue = Queue(maxsize=1)   # Queue for computed results
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

    def get_latest_result(self) -> Dict[str, Any]:
        """
        Get the most recently computed result.
        Non-blocking - returns None if no result is available.
        """
        try:
            return self.result_queue.get_nowait()
        except:
            return None

    def train(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        The actual training/computation logic.
        This runs in the background thread.
        """
        # Your AI computation logic here
        # For example:
        # 1. Process the game state
        # 2. Update neural network
        # 3. Return computed strategy/moves
        return {"computed_move": "up", "confidence": 0.8}  # Example return

    def cleanup(self):
        """
        Cleanup method to stop the background thread
        """
        self.running = False
        if self.thread.is_alive():
            self.thread.join()


class AIPlayer:
    """
    This class is used to play the game.
    It uses AITrainer for background computation while maintaining responsive gameplay.
    """

    def __init__(self, depth: int = 0):
        self.depth = depth
        self.thinker = Thinker(depth)
        self.current_action = None

    def action(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main update method called by the game loop.
        - Submits current state to thinker for future computation
        - Returns best move based on previous computation and factors
        """
        # Submit current state for background processing
        self.thinker.think(game_state)

        # Get latest computed result if available
        result = self.thinker.get_latest_result()
        if result is not None:
            self.current_action = result

        return self.current_action or {"computed_move": "none", "confidence": 0.0}

    def move_paddle(self, paddle_pos: float, ball_pos: float, ball_speed: float) -> str:
        """
        Decides paddle movement based on latest computed strategy
        """
        return

    def get_move(self, paddle_pos: float, ball_pos: float, ball_speed: float) -> str:
        pass

    def get_powerup(self, game_state: Dict[str, Any]) -> str:
        pass

    def get_game_state(self) -> Dict[str, Any]:
        pass

    def cleanup(self):
        """
        Cleanup method to be called when the game ends
        """
        self.thinker.cleanup()

