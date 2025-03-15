import logging
from queue import Queue, Empty
from typing import Dict, Any
import random
from datetime import datetime, timezone
from game.constants import GAME_FPS

from .AI import debug_write, DIFFICULTY_CONFIGS
from .AiThinker import Thinker

class AIPlayer:
    """
    Main AI entrypoint used by the game loop. Owns the Thinker + action_queue.
    The game loop calls:
      ai.compute(game_state)  # about once per second for a new snapshot
      action = await ai.action()  # each frame to see what to do next
    """

    def __init__(self, difficulty=0):
        self.difficulty = difficulty
        self.action_queue = Queue()
        self.thinker = Thinker(self.action_queue, difficulty)
        self.last_performance_check = 0
        self.action_count = 0
        self.adapt_interval = 10  # Check for adaptation every 10 snapshots
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

        # Log when powerups become available - with very visible formatting
        if current_big_state == "available" and self.last_big_state != "available":
            debug_write("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            debug_write("!!! BIG POWERUP NOW AVAILABLE !!!")
            debug_write("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if current_speed_state == "available" and self.last_speed_state != "available":
            debug_write("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            debug_write("!!! SPEED POWERUP NOW AVAILABLE !!!")
            debug_write("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        # Check if we've used powerups
        if self.last_big_state == "available" and current_big_state != "available":
            self.powerup_big_used = True
            debug_write("!!! BIG POWERUP STATE CHANGE: " + self.last_big_state + " -> " + current_big_state)
            debug_write("!!! BIG POWERUP HAS BEEN USED OR CHANGED STATE !!!")
        if self.last_speed_state == "available" and current_speed_state != "available":
            self.powerup_speed_used = True
            debug_write("!!! SPEED POWERUP STATE CHANGE: " + self.last_speed_state + " -> " + current_speed_state)
            debug_write("!!! SPEED POWERUP HAS BEEN USED OR CHANGED STATE !!!")

        # Store current powerup states
        self.last_big_state = current_big_state
        self.last_speed_state = current_speed_state

        # Determine if this is a critical game moment (close scores near end of game)
        if (left_score >= 9 or right_score >= 9) and abs(left_score - right_score) <= 2:
            self.game_critical_moment = True
            debug_write(f"CRITICAL GAME MOMENT DETECTED! Score: {left_score}-{right_score}")
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

                debug_write(f"FORCED POWERUP ACTIVATION: Big={use_big}, Slow={use_slow}, Fast={use_fast}, Speed={use_speed}")
                debug_write(f"Ball direction: {dir_x}, Coming toward AI: {ball_coming_toward_ai}")

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

            # Track and log when we actually try to use powerups
            if action.get("activatePowerupBig", False):
                debug_write("⭐⭐⭐ EXECUTING BIG POWERUP ACTION NOW ⭐⭐⭐")
            if action.get("activatePowerupSpeed", False):
                debug_write("⭐⭐⭐ EXECUTING SPEED POWERUP ACTION NOW ⭐⭐⭐")

            return action

        except Empty:
            # Emergency fallback - if queue is empty, move toward center
            debug_write("Action queue empty! Using emergency fallback")
            paddle_pos = self.thinker.last_game_state.get("playerRight", {}).get("paddlePos", 50.0)

            # Move toward center if far from it
            if abs(paddle_pos - 50.0) > 10:
                move = "-" if paddle_pos > 50 else "+"
                debug_write(f"Emergency fallback - moving toward center: {move}")
            else:
                move = "0"

            # Check if any powerups are available that we should use in this emergency
            player_right = self.thinker.last_game_state.get("playerRight", {})
            big_available = player_right.get("powerupBig") == "available"
            slow_available = player_right.get("powerupSlow") == "available"
            fast_available = player_right.get("powerupFast") == "available"

            # Check ball direction for choosing between slow and fast
            ball = self.thinker.last_game_state.get("ball", {})
            dir_x = ball.get("directionX", 0)
            ball_coming_toward_ai = dir_x > 0

            # Choose appropriate speed powerup based on ball direction
            use_slow = slow_available and ball_coming_toward_ai
            use_fast = fast_available and not ball_coming_toward_ai

            # If neither matches direction but one is available, use what we have
            if not (use_slow or use_fast) and (slow_available or fast_available):
                use_slow = slow_available
                use_fast = fast_available

            speed_available = use_slow or use_fast

            # If in emergency and powerups available, use them!
            if big_available or speed_available:
                debug_write(f"⭐⭐⭐ EMERGENCY POWERUP USAGE! Big: {big_available}, Speed: {speed_available} ⭐⭐⭐")

            return {
                'movePaddle': move,
                'activatePowerupBig': big_available,
                'activatePowerupSpeed': speed_available
            }

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

    def _add_fallback_actions(self):
        """
        If we're running low, push some do-nothing or random ones
        so we never starve the game of actions.
        """
        randomness = DIFFICULTY_CONFIGS[self.difficulty]["randomness"]

        # Try to add some useful fallbacks - move toward center of board
        paddle_pos = self.thinker.last_game_state.get("playerRight", {}).get("paddlePos", 50.0)
        distance_to_center = 50.0 - paddle_pos

        debug_write(f"Generating fallback actions - paddle at {paddle_pos}, distance to center: {distance_to_center}")

        for _ in range(GAME_FPS // 3):  # 1/3 of the frames
            if random.random() < randomness:
                # Random movement with some bias toward center
                if distance_to_center > 5:
                    movement = "-"  # Move up toward center
                elif distance_to_center < -5:
                    movement = "+"  # Move down toward center
                else:
                    movement = random.choice(["+", "-", "0"])
            else:
                # Deliberate movement toward center
                if abs(distance_to_center) > 2:
                    movement = "-" if distance_to_center > 0 else "+"
                else:
                    movement = "0"

            if not self.action_queue.full():
                self.action_queue.put({
                    'movePaddle': movement,
                    'activatePowerupBig': False,
                    'activatePowerupSpeed': False
                })

            # Update our simulated position for next fallback
            if movement == "+":
                paddle_pos += 2
            elif movement == "-":
                paddle_pos -= 2

            # Recalculate distance to center
            distance_to_center = 50.0 - paddle_pos
