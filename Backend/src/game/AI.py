import numpy as np
from typing import List, Dict, Any
import threading
from queue import Queue
import logging
import time
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

    DIFFICULTY_EASY = 0
    DIFFICULTY_MEDIUM = 1
    DIFFICULTY_HARD = 2

    def __init__(self, difficulty=DIFFICULTY_MEDIUM):
        self.difficulty = difficulty
        # Last time we made a decision
        self.last_decision_time = 0
        # Track if we're using a powerup
        self.using_powerup = False
        # Store latest action
        self.current_action = None
        # Randomness factors based on difficulty
        if difficulty == self.DIFFICULTY_EASY:
            self.movement_change_probability = 0.1  # 10% chance to change direction each frame
            self.stationary_weight = 0.6           # 60% chance of no movement when changing
        elif difficulty == self.DIFFICULTY_MEDIUM:
            self.movement_change_probability = 0.2  # 20% chance to change direction each frame
            self.stationary_weight = 0.5           # 50% chance of no movement when changing
        else:  # HARD
            self.movement_change_probability = 0.3  # 30% chance to change direction each frame
            self.stationary_weight = 0.4           # 40% chance of no movement when changing

    async def action(self, game_state=None):
        """
        Main method that decides what action to take based on the game state.
        For now, just returns random paddle movements.
        """
        import random

        # If no game state is provided, return the current action
        if not game_state:
            return self.current_action

        # Decide whether to change movement direction
        if random.random() < self.movement_change_probability or self.current_action is None:
            # Choose a random movement
            movements = ["0", "+", "-"]  # No movement, down, up
            weights = [self.stationary_weight, (1 - self.stationary_weight) / 2, (1 - self.stationary_weight) / 2]

            # Select a movement based on weights
            movement = random.choices(movements, weights=weights, k=1)[0]

            # Convert to AI action format
            if movement == "0":
                computed_move = "none"
            elif movement == "+":
                computed_move = "down"
            else:  # "-"
                computed_move = "up"

            self.current_action = {
                "computed_move": computed_move,
                "movement": movement,
                "confidence": 1.0
            }

        # Return the current action
        return self.current_action

    def move_paddle(self, paddle_pos, ball_pos, ball_direction_x, ball_direction_y, paddle_size=10, is_left_side=True):
        """
        Simple random paddle movement.
        Returns:
            '+': Move paddle down
            '-': Move paddle up
            '0': Don't move paddle
        """
        import random

        # Get current movement from last action or generate a new one
        if self.current_action and "movement" in self.current_action:
            return self.current_action["movement"]

        # If we don't have a current action, generate a random one
        movements = ["0", "+", "-"]
        weights = [self.stationary_weight, (1 - self.stationary_weight) / 2, (1 - self.stationary_weight) / 2]
        return random.choices(movements, weights=weights, k=1)[0]

    def get_move(self, game_state):
        """
        Extract relevant game state and call move_paddle.
        """
        if not game_state or not isinstance(game_state, dict):
            return "0"

        # Extract game state parameters
        try:
            ball = game_state.get('ball', {})
            playerRight = game_state.get('playerRight', {})

            paddle_pos = playerRight.get('paddlePos', 50)
            ball_pos_x = ball.get('posX', 50)
            ball_pos_y = ball.get('posY', 50)
            ball_direction_x = ball.get('directionX', 0)
            ball_direction_y = ball.get('directionY', 0)
            paddle_size = playerRight.get('paddleSize', 10)

            # Call move_paddle with extracted parameters
            return self.move_paddle(
                paddle_pos,
                (ball_pos_x, ball_pos_y),
                ball_direction_x,
                ball_direction_y,
                paddle_size,
                False  # AI is right player
            )
        except Exception as e:
            import logging
            logging.error(f"Error in AI get_move: {e}")
            return "0"

    def cleanup(self):
        """
        Cleanup method to be called when the game ends
        """
        pass  # Nothing to clean up in this simplified version

