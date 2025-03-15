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
      ai.compute(game_state)  # about once per second for a new state snapshot
      action = await ai.action()  # get action for the frame
    """

    def __init__(self, difficulty=0):
        self.difficulty = difficulty
        self.action_queue = Queue()
        self.thinker = Thinker(self.action_queue, difficulty)
        self.last_performance_check = 0
        self.action_count = 0
        self.adapt_interval = 3  # Check for adaptation every 3 snapshots
        self.last_state = None  # Track game state to detect point resets
        self.last_left_score = 0
        self.last_right_score = 0

        # Track powerup usage and availability to ensure we use them during the game
        self.powerup_big_used = False
        self.powerup_speed_used = False
        self.last_big_state = "unavailable"
        self.last_speed_state = "unavailable"
        self.powerup_usage_attempts = 0

        # Track game state for better powerup usage decision making
        self.game_critical_moment = False  # Set to true in close games near the end
        self.next_powerup_usage_check = 10  # Check after this many compute calls

        # Initialize with neutral movement
        self.action_queue.put({
            "movePaddle": "0",
            "activatePowerupBig": False,
            "activatePowerupSpeed": False
        })

    def compute(self, game_state: Dict[str, Any]) -> None:
        """
        Called every ~1s. Tells the AI to do a fresh plan.
        """
        # Detect if a point was scored since last update - if so, clear the action queue
        left_score = game_state.get("playerLeft", {}).get("points", 0)
        right_score = game_state.get("playerRight", {}).get("points", 0)

        # Check for score change or serve change
        if self.last_state:
            score_changed = (left_score != self.last_left_score or right_score != self.last_right_score)
            serve_changed = (
                game_state.get("gameData", {}).get("playerServes") !=
                self.last_state.get("gameData", {}).get("playerServes")
            )

            if score_changed or serve_changed:
                debug_write(f"Game state change detected! Score change: {score_changed}, Serve change: {serve_changed}")
                debug_write(f"Clearing action queue to resynchronize with game state")
                # Clear the action queue to avoid stale actions
                while not self.action_queue.empty():
                    self.action_queue.get()

        # Track powerup availability changes
        player_right = game_state.get("playerRight", {})
        current_big_state = player_right.get("powerupBig", "unavailable")

        # Check both slow and fast for speed powerups
        slow_state = player_right.get("powerupSlow", "unavailable")
        fast_state = player_right.get("powerupFast", "unavailable")
        current_speed_state = "available" if slow_state == "available" or fast_state == "available" else "unavailable"

        # Check if we've used powerups
        if self.last_big_state == "available" and current_big_state != "available":
            self.powerup_big_used = True
        if self.last_speed_state == "available" and current_speed_state != "available":
            self.powerup_speed_used = True

        # Store current powerup states
        self.last_big_state = current_big_state
        self.last_speed_state = current_speed_state

        # Determine if this is a critical game moment (close scores near end of game)
        if (left_score >= 9 or right_score >= 9) and abs(left_score - right_score) <= 2:
            self.game_critical_moment = True
        else:
            self.game_critical_moment = False

        # Force powerup usage based on game state - more aggressively now
        # This is a critical path to ensure powerups get used
        if (current_big_state == "available" or slow_state == "available" or fast_state == "available"):
            self.powerup_usage_attempts += 1

            # If the ball direction has been determined, use it to make smarter decisions about slow/fast
            ball = game_state.get("ball", {})
            dir_x = ball.get("directionX", 0)
            ball_coming_toward_ai = dir_x > 0

            # Be more aggressive with usage in critical moments
            max_attempts = 2  # Even more aggressive now - try to use within 2 cycles

            # When in critical game moment, try to use immediately
            if self.game_critical_moment:
                max_attempts = 1

            if self.powerup_usage_attempts >= max_attempts:
                debug_write(f"FORCING POWERUP USAGE after {self.powerup_usage_attempts} attempts!!")
                # Clear queue to inject a forced powerup action
                while not self.action_queue.empty():
                    self.action_queue.get()

                # Determine which powerup to use based on game state
                use_big = current_big_state == "available"

                # Logic for speed powerups depends on ball direction
                use_slow = slow_state == "available" and ball_coming_toward_ai
                use_fast = fast_state == "available" and not ball_coming_toward_ai

                if not ball_coming_toward_ai and not use_fast and slow_state == "available":
                    # If ball going away and we don't have fast, still try to use slow
                    use_slow = True
                    debug_write("No FAST powerup, using SLOW even though ball moving away!")

                elif ball_coming_toward_ai and not use_slow and fast_state == "available":
                    # If ball coming toward us and we don't have slow, still try fast
                    use_fast = True
                    debug_write("No SLOW powerup, using FAST even though ball coming toward AI!")

                use_speed = use_slow or use_fast

                # Add several immediate actions that use available powerups
                # Adding multiple consecutive frames to increase chances of activation
                for i in range(3):  # Try for 3 consecutive frames
                    self.action_queue.put({
                        "movePaddle": "0",  # Neutral movement
                        "activatePowerupBig": use_big,
                        "activatePowerupSpeed": use_speed
                    })

                # Reset counter after forcing usage
                self.powerup_usage_attempts = 0
        else:
            # Reset counter if no powerups available
            self.powerup_usage_attempts = 0

        # Update state tracking
        self.last_state = game_state
        self.last_left_score = left_score
        self.last_right_score = right_score

        # Check if we should adapt difficulty based on performance
        self.action_count += 1
        if self.action_count - self.last_performance_check >= self.adapt_interval:
            self.last_performance_check = self.action_count
            self._check_for_difficulty_adaptation()

        self.thinker.think(game_state)

        # Ensure we never fully run out of actions
        if self.action_queue.qsize() <= 2:
            self._add_fallback_actions()

    async def action(self) -> Dict[str, Any]:
        """
        Called by the game loop each frame to get the next AI action.
        If the queue is empty, returns a do-nothing fallback.
        """
        try:
            action = self.action_queue.get_nowait()
            return action
        except Empty:
            self._add_fallback_actions()

    def cleanup(self):
        """
        Clean up the background thread when the game ends.
        """
        self.thinker.cleanup()
        while not self.action_queue.empty():
            self.action_queue.get()

    def _check_for_difficulty_adaptation(self):
        """
        Check if we need to adjust difficulty based on performance
        """
        try:
            # Get success rate from learner stats
            success_rate = self.thinker.learner.ai_stats.get("success_rate", 0.5)

            # Only adapt difficulty if we have enough data points
            min_balls_to_adapt = 3
            total_balls = self.thinker.learner.ai_stats.get("total_balls_faced", 0)

            if total_balls < min_balls_to_adapt:
                debug_write(f"Not enough data to adapt difficulty yet ({total_balls}/{min_balls_to_adapt} balls faced)")
                return

            # Decide if difficulty adjustment is needed
            recommended_difficulty = self.difficulty

            if success_rate > 0.8 and self.difficulty < 2:
                recommended_difficulty = self.difficulty + 1
                debug_write(f"AI too successful ({success_rate:.2f}), increasing difficulty to {recommended_difficulty}")
            elif success_rate < 0.3 and self.difficulty > 0:
                recommended_difficulty = self.difficulty - 1
                debug_write(f"AI struggling ({success_rate:.2f}), decreasing difficulty to {recommended_difficulty}")

            # Apply difficulty change if needed
            if recommended_difficulty != self.difficulty:
                self.difficulty = recommended_difficulty
                self.thinker.difficulty = recommended_difficulty
                self.thinker.learner.difficulty = recommended_difficulty
                self.thinker.learner.config = DIFFICULTY_CONFIGS.get(recommended_difficulty, DIFFICULTY_CONFIGS[1])
                debug_write(f"Difficulty adjusted to {recommended_difficulty}")
        except Exception as e:
            debug_write(f"Error in difficulty adaptation: {e}")


    # ----------- fallback actions -----------
    def _add_fallback_actions(self):
        """
        If we're running low, push some do-nothing or random ones
        so we never starve.
        """
        randomness = DIFFICULTY_CONFIGS[self.difficulty]["randomness"]

        for _ in range(GAME_FPS // 5):  # adding 1/5 of the frames
            if not self.action_queue.full():
                self.action_queue.put({
                    'movePaddle': '0' if random.random() < randomness else random.choice(["+", "-"]),
                    'activatePowerupBig': False,
                    'activatePowerupSpeed': False
                })
