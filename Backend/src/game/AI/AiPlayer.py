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

        self.last_performance_check = 0
        self.action_count = 0
        self.adapt_interval = 1  # Check for adaptation every snapshot

        # Game state tracking
        self.last_state = None
        self.last_left_score = 0
        self.last_right_score = 0

        # Powerup usage tracking
        self.powerup_attempts = 0
        self.is_critical_moment = False

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
        self.check_critical_moment(game_state)
        self.handle_powerups(game_state)
        self.update_tracking(game_state)
        self.adapt_difficulty()

        # clear the queue on state change, this will fall back to do nothing or random
        while not self.action_queue.empty():
            self.action_queue.get()

        # Let the thinker plan ahead
        self.thinker.think(game_state)

        # we never run out of actions
        if self.action_queue.qsize() <= 2:
            self.add_fallback_actions()

    def check_critical_moment(self, game_state: Dict[str, Any]) -> None:
        """
        Determine if we're in a critical moment where powerup usage is urgent
        """
        left_score = game_state.get("playerLeft", {}).get("points", 0)
        right_score = game_state.get("playerRight", {}).get("points", 0)

        # Critical moment is when game is close and near the end
        self.is_critical_moment = ((left_score >= 9 or right_score >= 9) and
                                  abs(left_score - right_score) <= 2)

        if self.is_critical_moment:
            debug_write("CRITICAL GAME MOMENT DETECTED")

    def handle_powerups(self, game_state: Dict[str, Any]) -> None:
        """
        Determine when to use powerups based on game state
        """
        # Get powerup states
        player = game_state.get("playerRight", {})
        big_available = player.get("powerupBig") == "available"
        slow_available = player.get("powerupSlow") == "available"
        fast_available = player.get("powerupFast") == "available"

        # If no powerups available, reset counter and return
        speed_available = slow_available or fast_available
        if not (big_available or speed_available):
            self.powerup_attempts = 0
            return

        # Increment attempt counter
        self.powerup_attempts += 1

        # Determine when to use powerups
        max_attempts = 2 if not self.is_critical_moment else 1

        # If not time to use powerups yet, return
        if self.powerup_attempts < max_attempts:
            return

        # Time to use powerups!
        debug_write(f"Using powerups after {self.powerup_attempts} attempts")

        # Determine which powerups to use
        ball = game_state.get("ball", {})
        ball_coming_toward_ai = ball.get("directionX", 0) > 0

        use_big = big_available
        use_speed = speed_available

        # Add powerup activation actions
        for _ in range(3):  # Multiple frames to ensure activation
            self.action_queue.put({
                "movePaddle": "0",  # Neutral movement
                "activatePowerupBig": use_big,
                "activatePowerupSpeed": use_speed
            })

        # Reset counter
        self.powerup_attempts = 0

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
        self.thinker.learner.difficulty = new_difficulty
        self.thinker.learner.config = DIFFICULTY_CONFIGS.get(new_difficulty, DIFFICULTY_CONFIGS[1])
        debug_write(f"Difficulty adjusted to {new_difficulty}")

    def add_fallback_actions(self) -> None:
        """
        Add fallback actions to ensure we never run out
        """
        randomness = DIFFICULTY_CONFIGS[self.difficulty]["randomness"]

        for _ in range(GAME_FPS // 6):
            if not self.action_queue.full():
                move = '0' if random.random() < randomness else random.choice(["+", "-"])
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