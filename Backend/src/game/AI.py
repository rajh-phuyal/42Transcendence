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
        self.difficulty = difficulty
        self.compute_queue = Queue(maxsize=1)  # For new game states
        self.running = True
        self.last_game_state = None  # Store last game state for reference

        # Start background thread
        self.thread = threading.Thread(target=self._compute_loop, daemon=True)
        self.thread.start()

    def _compute_loop(self):
        """Background thread that continuously processes game states"""
        while self.running:
            try:
                # Get latest game state to process
                game_state = self.compute_queue.get()
                self.last_game_state = game_state

                # Generate a sequence of actions (about 1 second worth)
                action_sequence = self._generate_action_sequence(game_state)

                # Add actions to queue without clearing existing ones
                # (We want to build up a buffer of actions)
                for action in action_sequence:
                    if not self.action_queue.full():
                        self.action_queue.put(action)
                    else:
                        break  # Queue is full, stop adding

            except Exception as e:
                logging.error(f"Error in AI compute loop: {e}")

    def _generate_action_sequence(self, game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a sequence of related actions based on game state"""
        # For a basic implementation, create a simple ball-tracking strategy
        actions = []

        # Extract relevant data
        try:
            ball = game_state.get('ball', {})
            paddle = game_state.get('playerRight', {})
            ball_pos_y = ball.get('posY', 50)
            ball_dir_x = ball.get('directionX', 0)
            ball_dir_y = ball.get('directionY', 0)
            paddle_pos = paddle.get('paddlePos', 50)

            # Only actively track if ball is coming toward AI
            is_ball_approaching = ball_dir_x > 0

            # Calculate target position with some difficulty-based error
            target_y = ball_pos_y
            if is_ball_approaching:
                # Predict where ball will be
                field_width = 100
                paddle_x = 95  # Right side
                ball_pos_x = ball.get('posX', 50)
                distance = abs(paddle_x - ball_pos_x)
                time_to_impact = distance / abs(ball_dir_x) if ball_dir_x != 0 else 0
                predicted_y = ball_pos_y + (ball_dir_y * time_to_impact)

                # Add difficulty-based error
                config = DIFFICULTY_CONFIGS[self.difficulty]
                error_margin = config["error_margin"]
                import random
                target_y = predicted_y + random.uniform(-error_margin * 20, error_margin * 20)
            else:
                # Move toward center when ball is going away
                target_y = 50 + random.uniform(-10, 10)

            # Generate sequence of movements to reach target
            for _ in range(min(GAME_FPS, self.action_queue.maxsize - self.action_queue.qsize())):
                # Determine movement direction
                if paddle_pos < target_y - 3:  # Add small deadzone
                    movement = "+"  # Move down
                elif paddle_pos > target_y + 3:
                    movement = "-"  # Move up
                else:
                    movement = "0"  # Stay

                # Update simulated paddle position for next movement
                if movement == "+":
                    paddle_pos += 1  # Simplified movement speed
                elif movement == "-":
                    paddle_pos -= 1

                # Add action to sequence
                actions.append({
                    'movePaddle': movement,
                    'activatePowerupBig': False,
                    'activatePowerupSpeed': False
                })

        except Exception as e:
            logging.error(f"Error generating action sequence: {e}")
            # Fill with default actions on error
            for _ in range(5):
                actions.append({
                    'movePaddle': "0",
                    'activatePowerupBig': False,
                    'activatePowerupSpeed': False
                })

        return actions

    def think(self, game_state: Dict[str, Any]) -> None:
        """Submit a new game state for processing. Non-blocking."""
        # Put newest state in queue, replacing any existing one
        while not self.compute_queue.empty():
            self.compute_queue.get()
        self.compute_queue.put(game_state)

    def cleanup(self):
        """Stop the background thread"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)


class AIPlayer:
    """
    This class is used to play the game.
    It uses Thinker for background computation while maintaining responsive gameplay.
    """

    def __init__(self, difficulty=1):
        # Get difficulty configuration
        self.difficulty = difficulty

        # Create a queue for AI movements
        self.action_queue = Queue()

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
        for _ in range(3):
            if random.random() < randomness:
                # Choose a random movement
                movements = ["0", "+", "-"]
                weights = [error_margin, (1 - error_margin) / 2, (1 - error_margin) / 2]
                movement = random.choices(movements, weights=weights, k=1)[0]
            else:
                movement = prev_movement

            prev_movement = movement

            if not self.action_queue.full():
                self.action_queue.put({
                    'movePaddle': movement,
                    'activatePowerupBig': False,
                    'activatePowerupSpeed': False
                })

