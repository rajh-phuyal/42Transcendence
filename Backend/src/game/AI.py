import os
import threading
import logging
from queue import Queue, Empty
from typing import List, Dict, Any, Optional, Tuple
import random
from game.constants import GAME_FPS
import math


DIFFICULTY_CONFIGS = {
    0: {"randomness": 0.3, "error_margin": 0.6},
    1: {"randomness": 0.2, "error_margin": 0.5},
    2: {"randomness": 0.1, "error_margin": 0.4},
}


DEBUG_FILE_PATH = os.path.join(os.path.dirname(__file__), "ai_debug.txt")

def debug_write(msg: str):
    """
    Appends a line of debug info to ai_debug.txt.
    This is for debugging only, to see what's happening inside the AI code.
    """
    # You may want to handle exceptions or concurrency more robustly in production.
    with open(DEBUG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


class Learner:
    """
    The AI's 'intelligence' component. Gathers data from the game state,
    runs short-horizon simulations for potential strategies (like using
    powerups or not), and produces metrics/recommendations for the Thinker.
    """

    def __init__(self, difficulty: int = 1):
        """
        :param difficulty: AI difficulty (0=easy, 1=medium, 2=hard)
        """
        self.difficulty = difficulty
        self.config = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[1])
        self.ai_stats = {
            "consecutive_goals": 0,
            "consecutive_goals_against": 0,
            "missed_balls": 0,
            "successful_intercepts": 0,
            "total_balls_faced": 0,
            "last_ball_x": 50.0,
            "last_ball_y": 50.0,
            "last_direction_x": 0,
            "power_ups_used": 0,
            "success_rate": 0.5  # Start with neutral assumption
        }

        # We'll store the last known snapshot of the game state, so we can do
        # heavier analysis or simulation after update_with_game_state is called.
        self.last_game_state: Dict[str, Any] = {}

    def update_with_game_state(self, game_state: Dict[str, Any]) -> None:
        """
        Called with each new snapshot. We store it internally and update
        any usage stats like whether the AI is currently losing or winning.
        """
        if self.last_game_state:
            # Check if a point was scored since last update
            last_score_left = self.last_game_state.get("playerLeft", {}).get("points", 0)
            last_score_right = self.last_game_state.get("playerRight", {}).get("points", 0)

            curr_score_left = game_state.get("playerLeft", {}).get("points", 0)
            curr_score_right = game_state.get("playerRight", {}).get("points", 0)

            # Point was scored against AI (right player)
            if curr_score_left > last_score_left:
                self.ai_stats["consecutive_goals_against"] += 1
                self.ai_stats["consecutive_goals"] = 0
                self.ai_stats["missed_balls"] += 1
                debug_write(f"AI MISSED a ball! Total misses: {self.ai_stats['missed_balls']}")

            # AI scored a point
            elif curr_score_right > last_score_right:
                self.ai_stats["consecutive_goals"] += 1
                self.ai_stats["consecutive_goals_against"] = 0
                debug_write(f"AI scored! Consecutive goals: {self.ai_stats['consecutive_goals']}")

            # Track ball to detect successful intercepts
            curr_ball_x = game_state.get("ball", {}).get("posX", 50)
            curr_ball_dir_x = game_state.get("ball", {}).get("directionX", 0)

            # If ball direction reversed near AI paddle, count as intercept
            if (self.ai_stats["last_direction_x"] > 0 and curr_ball_dir_x < 0 and
                self.ai_stats["last_ball_x"] > 90 and curr_ball_x > 90):
                self.ai_stats["successful_intercepts"] += 1
                debug_write(f"AI intercepted the ball! Total intercepts: {self.ai_stats['successful_intercepts']}")

            self.ai_stats["last_ball_x"] = curr_ball_x
            self.ai_stats["last_ball_y"] = game_state.get("ball", {}).get("posY", 50)
            self.ai_stats["last_direction_x"] = curr_ball_dir_x

        # Update total number of balls faced for success rate calculation
        self.ai_stats["total_balls_faced"] = (
            self.ai_stats["successful_intercepts"] + self.ai_stats["missed_balls"]
        )

        if self.ai_stats["total_balls_faced"] > 0:
            self.ai_stats["success_rate"] = (
                self.ai_stats["successful_intercepts"] / self.ai_stats["total_balls_faced"]
            )

        # Store current game state for next comparison
        self.last_game_state = game_state

    def get_metrics(self, game_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entrypoint to get the AI's recommended usage of powerups and other metrics.

        :param game_state: Optionally pass a new state, else we'll use self.last_game_state.
        :return: A dict of metrics, e.g.:
           {
             "useBig": bool,
             "useSpeed": bool,
             "opponentPowerupProbability": float,
             "recommendedDifficulty": int
           }
        """
        if game_state is None:
            game_state = self.last_game_state

        # 1) Check powerup availability
        use_big_available, use_speed_available = self._check_powerup_availability(game_state)

        # 2) Evaluate scenarios:
        #    - "none" (use no powerup)
        #    - "big"  (if available)
        #    - "speed" (if available)
        scenarios = [{"name": "none", "useBig": False, "useSpeed": False}]
        if use_big_available:
            scenarios.append({"name": "big", "useBig": True, "useSpeed": False})
        if use_speed_available:
            scenarios.append({"name": "speed", "useBig": False, "useSpeed": True})

        # Debug log which powerups are available
        debug_write(f"Powerups available - Big: {use_big_available}, Speed: {use_speed_available}")

        # We'll run a short forward simulation for each scenario and pick the best.
        best_scenario_name = "none"
        best_scenario_score = float("-inf")

        for scn in scenarios:
            scenario_score = self._simulate_scenario(game_state, scn)
            if scenario_score > best_scenario_score:
                best_scenario_score = scenario_score
                best_scenario_name = scn["name"]

        use_big = (best_scenario_name == "big")
        use_speed = (best_scenario_name == "speed")

        # Log which scenario was selected
        debug_write(f"Selected scenario: {best_scenario_name} - useBig: {use_big}, useSpeed: {use_speed}")

        # Adaptive difficulty based on performance
        recommended_difficulty = self.difficulty

        # If AI is doing too well (success rate > 0.8), increase difficulty
        if self.ai_stats["success_rate"] > 0.8 and self.difficulty < 2:
            recommended_difficulty = self.difficulty + 1
            debug_write(f"AI TOO GOOD! Increasing difficulty to {recommended_difficulty}")

        # If AI is doing poorly (success rate < 0.3), decrease difficulty
        elif self.ai_stats["success_rate"] < 0.3 and self.difficulty > 0:
            recommended_difficulty = self.difficulty - 1
            debug_write(f"AI STRUGGLING! Decreasing difficulty to {recommended_difficulty}")

        # Return the dictionary the Thinker will use to plan actual actions.
        return {
            "useBig": use_big,
            "useSpeed": use_speed,
            "opponentPowerupProbability": 0.2,  # Stub or real logic
            "recommendedDifficulty": recommended_difficulty,
        }

    # --------------------------------------------------------------------------
    # Internal helper methods
    # --------------------------------------------------------------------------

    def _check_powerup_availability(self, game_state: Dict[str, Any]) -> Tuple[bool, bool]:
        """
        Check if powerups are still available for 'playerRight' (the AI).
        Return (big_available, speed_available).
        """
        player_right = game_state.get("playerRight", {})
        # Debug the current powerup state
        debug_write(f"Checking powerups: {player_right}")

        # Correctly identify available powerups
        has_big = (player_right.get("powerupBig") == "available")
        has_slow = (player_right.get("powerupSlow") == "available")
        has_fast = (player_right.get("powerupFast") == "available")

        # We can use either slow or fast as our "speed" powerup
        has_speed = has_slow or has_fast

        # Store which type of speed powerup is available for later reference
        self.has_slow_powerup = has_slow
        self.has_fast_powerup = has_fast

        debug_write(f"Powerup availability check: big={has_big}, speed={has_speed} (slow={has_slow}, fast={has_fast})")
        return has_big, has_speed

    def _simulate_scenario(self, game_state: Dict[str, Any], scenario: Dict[str, bool]) -> float:
        """
        Forward-simulate the ball + AI paddle for up to ~2 seconds, applying the scenario's
        powerup usage (big, speed) at the start. Return a numeric score indicating whether
        we can likely intercept or not. Higher = better.

        If the ball is inbound and we have slow, we might slow the ball. If it's outbound,
        we might speed it. This is simplified logic.
        """
        # Copy relevant fields
        ball = dict(game_state.get("ball", {}))
        paddle = dict(game_state.get("playerRight", {}))

        # Positions & directions
        ball_x = ball.get("posX", 50.0)
        ball_y = ball.get("posY", 50.0)
        dir_x = ball.get("directionX", 1.0)
        dir_y = ball.get("directionY", 0.0)
        speed = ball.get("speed", 1.0)

        paddle_pos = paddle.get("paddlePos", 50.0)
        paddle_size = paddle.get("paddleSize", 10.0)

        # Which powerups we're "using" in this scenario
        use_big = scenario.get("useBig", False)
        use_speed = scenario.get("useSpeed", False)

        # Start with a base score, which we'll adjust as we evaluate the scenario
        # This encourages powerup usage if they're available
        scenario_score = 0.0

        # Boost the score if this scenario uses powerups - make AI more eager to use them
        if use_big:
            scenario_score += 0.3  # Bias toward using powerups when available
        if use_speed:
            scenario_score += 0.3  # Bias toward using powerups when available

        # If we use big
        if use_big:
            # Let's assume that "big" means we instantly get a bigger paddle for the next bounce
            # Example: from 10 to 22
            paddle_size = 22.0
            debug_write(f"Scenario with BIG powerup: paddle size increased to {paddle_size}")

        # If we use speed (the ball is inbound => slow, outbound => fast)
        if use_speed:
            if dir_x > 0:
                # Ball moving right => inbound for the AI => slow it
                speed = 1.0
                debug_write(f"Scenario with SLOW powerup: ball speed reduced to {speed}")
            else:
                # Ball moving left => outbound => speed it up
                speed += 2.0
                debug_write(f"Scenario with FAST powerup: ball speed increased to {speed}")

        # We'll simulate up to ~2 seconds in small steps
        frames_to_simulate = min(2 * GAME_FPS, 200)  # 2 seconds or 200 frames, whichever is smaller
        dt = 1.0 / GAME_FPS

        # Track intercept success
        intercept_success = False

        # We'll track how well we do by checking if we can intercept the ball if it crosses x>=95
        for frame_idx in range(frames_to_simulate):
            # Move the ball
            ball_x += dir_x * speed * dt
            ball_y += dir_y * speed * dt

            # Basic top/bottom bounce
            if ball_y <= 0:
                ball_y = 0
                dir_y *= -1
            elif ball_y >= 100:
                ball_y = 100
                dir_y *= -1

            # Check if ball has reached AI's side
            if ball_x >= 95:
                # Attempt intercept
                top_paddle = paddle_pos - (paddle_size / 2)
                bot_paddle = paddle_pos + (paddle_size / 2)
                if top_paddle <= ball_y <= bot_paddle:
                    scenario_score += 1.0  # success
                    intercept_success = True
                else:
                    distance_to_paddle = min(abs(ball_y - top_paddle), abs(ball_y - bot_paddle))
                    # The closer we are to intercepting, the better
                    scenario_score -= distance_to_paddle / 10.0  # partial penalty based on distance
                break

            # If ball goes left of ~5 or 0, we might not worry for now, or keep simulating
            # For simplicity, let's just continue. The ball might bounce off the left paddle eventually,
            # but a real simulation would require the entire table logic if you want it robust.

            # Move paddle in the sim: try to track the ball_y
            # We'll do a simple approach: if paddle is above ball, move down, etc.
            # This matches how you would physically move in the actual game.
            if paddle_pos < ball_y - 1:
                paddle_pos += 2.0
            elif paddle_pos > ball_y + 1:
                paddle_pos -= 2.0

            # clamp paddle
            if paddle_pos < (paddle_size / 2):
                paddle_pos = paddle_size / 2
            elif paddle_pos > 100 - (paddle_size / 2):
                paddle_pos = 100 - (paddle_size / 2)

        # Adaptive powerup evaluation based on game situation
        # Check if we're losing - be more aggressive with powerups if behind
        ai_score = game_state.get("playerRight", {}).get("points", 0)
        opponent_score = game_state.get("playerLeft", {}).get("points", 0)

        # More likely to use powerups if we're behind in score
        if opponent_score > ai_score and (use_big or use_speed):
            scenario_score += 0.5
            debug_write(f"Boosting powerup scenario score because we're behind: {opponent_score}-{ai_score}")

        # If this is a close game (near 11-11), be more aggressive with powerups
        if ai_score >= 9 and opponent_score >= 9:
            if use_big or use_speed:
                scenario_score += 0.7
                debug_write(f"Boosting powerup scenario score in close game: {ai_score}-{opponent_score}")

        # Log the final scenario score to help debugging
        debug_write(f"Scenario {scenario['name']} final score: {scenario_score}")

        return scenario_score


class Thinker:
    """
    A background 'Thinker' that uses a Learner for heavier computations.
    - Receives game states via `think(game_state)`.
    - Runs in a separate thread so it never blocks the main loop.
    - Uses Learner to decide whether to use powerups, etc.
    - Generates ~1 second of actions and enqueues them to `action_queue`.
    """

    def __init__(self, action_queue: Queue, difficulty: int = 1):
        """
        :param action_queue: the queue where we push our planned actions
        :param difficulty: AI difficulty
        """
        self.action_queue = action_queue
        self.difficulty = difficulty
        self.compute_queue = Queue(maxsize=1)
        self.running = True
        self.last_game_state: Dict[str, Any] = {}

        # The 'brain' that does learning & simulation
        self.learner = Learner(difficulty=difficulty)

        # Track the last successful prediction for continuity
        self.last_predicted_y = None
        self.last_predicted_frame = None

        # Start background thread to handle AI computations
        self.thread = threading.Thread(target=self._compute_loop, daemon=True)
        self.thread.start()

    def think(self, game_state: Dict[str, Any]) -> None:
        """
        Called (e.g. once per second) with the latest snapshot.
        We store it in compute_queue, replacing any older snapshot.
        """
        while not self.compute_queue.empty():
            self.compute_queue.get()
        self.compute_queue.put(game_state)

    def cleanup(self):
        """
        Stop the background thread.
        """
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _compute_loop(self):
        while self.running:
            try:
                game_state = self.compute_queue.get()
                self.last_game_state = game_state

                # Dump the raw game state or just the key parts
                debug_write(f"--- NEW SNAPSHOT ---")
                debug_write(f"GameState: {game_state}")

                # 1) Update learner
                self.learner.update_with_game_state(game_state)

                # 2) Learner's metrics
                metrics = self.learner.get_metrics(game_state)
                debug_write(f"Metrics: {metrics}")

                # 3) Plan the next second
                action_sequence = self._plan_actions_for_next_second(game_state, metrics)

                # 4) Enqueue them
                for action in action_sequence:
                    if not self.action_queue.full():
                        debug_write(f"Enqueued action: {action}")
                        self.action_queue.put(action)
                    else:
                        break

                # Also dump how many actions we generated
                debug_write(f"Enqueued {len(action_sequence)} actions.")

            except Exception as e:
                logging.error(f"Error in AI compute loop: {e}")

    def predict_collision_frame_and_y(
            self,
            start_x: float,
            start_y: float,
            dir_x: float,
            dir_y: float,
            speed: float,
            fps: int = GAME_FPS,
            max_frames: int = 120,
            collision_x: float = 95.0
        ):
            """
            Predict at which frame (0..max_frames-1) and y-position the ball
            will be when it crosses 'collision_x'. This method:
            - Steps the ball in increments of 1/fps second
            - Bounces off top/bottom at y=0 or y=100
            - Returns (frame_index, collision_y) if x >= collision_x

            :param collision_x: The x coordinate we consider "AI's domain" (e.g., 95)
            :return: (frame_index, collisionY) or None if it never crosses in max_frames
            """
            # Sanity check - if ball is moving away from target, it won't hit
            if dir_x < 0 and start_x > collision_x:
                debug_write(f"Ball moving away from collision_x - no hit possible")
                return None

            if dir_x > 0 and start_x > collision_x:
                debug_write(f"Ball already past collision_x")
                return (0, start_y)  # Immediate collision

            # VERY IMPORTANT: If direction is nearly zero, simulation will take too long
            # This happens in the game sometimes due to rounding errors - fix it
            if abs(dir_x) < 0.0001:
                debug_write(f"X direction is nearly zero, adjusting to prevent infinite loop")
                dir_x = 0.0001 if dir_x >= 0 else -0.0001

            # CLAMP extremely small Y directions to prevent simulation errors
            if abs(dir_y) < 0.0001:
                dir_y = 0.0001 if dir_y >= 0 else -0.0001

            dt = 1.0 / fps

            # Constants for wall boundaries - taking ball size into account
            ball_height = self.last_game_state.get("ball", {}).get("height", 1.0)
            top_wall = ball_height  # Ball radius from top
            bottom_wall = 100 - ball_height  # Ball radius from bottom

            # Initialize for simulation
            x = start_x
            y = start_y
            vx = dir_x * speed  # Incorporate speed into velocity
            vy = dir_y * speed

            # Log initial prediction data
            debug_write(f"Starting prediction from: x={x}, y={y}, vx={vx}, vy={vy}, speed={speed}")
            debug_write(f"Target collision_x: {collision_x}")

            # Simplified physics simulation - step by step
            for frame_idx in range(max_frames):
                # Save previous position for interpolation
                prev_x = x
                prev_y = y

                # Move
                x += vx * dt
                y += vy * dt

                # Bounce off top/bottom walls with ball height considered
                if y < top_wall:
                    y = 2 * top_wall - y  # Reflect position
                    vy = -vy  # Reflect velocity
                    debug_write(f"Top wall bounce at frame {frame_idx}, x={x}")
                elif y > bottom_wall:
                    y = 2 * bottom_wall - y  # Reflect position
                    vy = -vy  # Reflect velocity
                    debug_write(f"Bottom wall bounce at frame {frame_idx}, x={x}")

                # Check if crossing collision_x on this step
                if prev_x <= collision_x and x >= collision_x:
                    # Interpolate exact y position at crossing
                    if prev_x != x:  # Avoid division by zero
                        t = (collision_x - prev_x) / (x - prev_x)
                        collision_y = prev_y + t * (y - prev_y)
                    else:
                        collision_y = y

                    # Clamp the collision y value to be in bounds
                    collision_y = max(top_wall, min(bottom_wall, collision_y))

                    debug_write(f"Collision predicted at frame {frame_idx}, y={collision_y}")
                    return (frame_idx, collision_y)

                # Safety check - if x is way out of bounds, abort
                if x < -10 or x > 110:
                    debug_write(f"Ball x position out of bounds: {x}, aborting prediction")
                    return None

            # If we've gone through all frames and haven't crossed,
            # check if we're even moving toward the collision plane
            if vx > 0 and start_x < collision_x:
                # We're moving toward collision but didn't reach it in max_frames
                debug_write(f"Ball moving toward collision_x but didn't reach in {max_frames} frames")
                # Estimate based on current trajectory
                time_to_collision = (collision_x - start_x) / vx if vx != 0 else float('inf')
                estimated_y = start_y + vy * time_to_collision
                # Clamp to screen bounds
                estimated_y = max(top_wall, min(bottom_wall, estimated_y))
                estimated_frame = int(time_to_collision / dt)
                debug_write(f"Estimated collision at frame {estimated_frame}, y={estimated_y}")
                return (estimated_frame, estimated_y)

            # No collision by max_frames
            debug_write(f"No collision predicted within {max_frames} frames")
            return None

    def _plan_actions_for_next_second(self, game_state: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = []
        try:
            # Pull out state
            ball = game_state.get("ball", {})
            paddle = game_state.get("playerRight", {})

            ball_x = ball.get("posX", 50.0)
            ball_y = ball.get("posY", 50.0)
            dir_x = ball.get("directionX", 1.0)
            dir_y = ball.get("directionY", 0.0)
            speed = ball.get("speed", 1.0)

            paddle_pos = paddle.get("paddlePos", 50.0)
            paddle_size = paddle.get("paddleSize", 10.0)
            paddle_speed = paddle.get("paddleSpeed", 3.5)

            # CRITICAL: Check if the paddle position has dramatically changed
            # This can happen due to game resets, points being scored, or other events
            if hasattr(self, 'last_paddle_pos') and abs(self.last_paddle_pos - paddle_pos) > 20:
                debug_write(f"!!! MAJOR PADDLE POSITION CHANGE DETECTED: {self.last_paddle_pos} -> {paddle_pos}")
                # Reset prediction history since our context has completely changed
                self.last_predicted_y = None
                self.last_predicted_frame = None
                debug_write(f"Prediction history reset due to major position change")

            # Track the paddle position for next time
            self.last_paddle_pos = paddle_pos

            use_big = metrics.get("useBig", False)
            use_speed = metrics.get("useSpeed", False)

            # Check which type of speed powerup is available (from _check_powerup_availability)
            has_slow = getattr(self, 'has_slow_powerup', False)
            has_fast = getattr(self, 'has_fast_powerup', False)

            # Determine which speed powerup to use based on ball direction
            # Use slow when ball coming toward AI, use fast when ball moving away
            ball_coming_toward_ai = dir_x > 0

            # Prepare the specific powerup actions
            activate_big = use_big
            activate_slow = use_speed and has_slow and ball_coming_toward_ai
            activate_fast = use_speed and has_fast and not ball_coming_toward_ai

            # Log our decision about powerups for this planning cycle
            debug_write(f"Planning actions with powerups: useBig={use_big}, useSpeed={use_speed}")
            debug_write(f"Specific powerups: activateBig={activate_big}, activateSlow={activate_slow}, activateFast={activate_fast}")

            # Check the situation - ball coming toward AI or moving away
            if ball_coming_toward_ai:
                collision_info = self.predict_collision_frame_and_y(
                    start_x=ball_x,
                    start_y=ball_y,
                    dir_x=dir_x,
                    dir_y=dir_y,
                    speed=speed,
                    fps=GAME_FPS,
                    max_frames=10 * GAME_FPS,  # Look further ahead
                    collision_x=95.0
                )
            else:
                collision_info = None
                debug_write(f"Ball moving away from AI - not predicting collision")

            # Default values when no collision predicted
            collision_frame = 2 * GAME_FPS  # Default to fairly far out
            collision_y = 50.0  # Default to middle

            # Use previous prediction as fallback if available and no new prediction
            if collision_info is None:
                if ball_coming_toward_ai:
                    debug_write(f"No collision predicted but ball coming toward AI")

                if self.last_predicted_y is not None:
                    collision_y = self.last_predicted_y
                    if self.last_predicted_frame is not None:
                        collision_frame = max(1, self.last_predicted_frame - GAME_FPS)  # Decrement by 1 second
                    debug_write(f"Using previous prediction: y={collision_y}, frame={collision_frame}")
                else:
                    # If no prediction at all, center the paddle
                    collision_y = 50.0
                    collision_frame = GAME_FPS
                    debug_write(f"No prediction available - centering paddle")
            else:
                collision_frame, collision_y = collision_info

                # Store for future reference
                self.last_predicted_y = collision_y
                self.last_predicted_frame = collision_frame

                # Apply some randomness based on difficulty
                randomness = DIFFICULTY_CONFIGS[self.difficulty]["randomness"]
                error_margin = DIFFICULTY_CONFIGS[self.difficulty]["error_margin"]

                # Add a bit of error to make AI less perfect
                if random.random() < randomness:
                    error_amount = random.uniform(-error_margin * 10, error_margin * 10)
                    debug_write(f"Adding error of {error_amount} to predicted y")
                    collision_y += error_amount
                    # Clamp to keep in bounds
                    collision_y = max(paddle_size/2, min(100 - paddle_size/2, collision_y))

            debug_write(f"Plan Next Second => BallX={ball_x}, BallY={ball_y}, "
                        f"DirX={dir_x}, DirY={dir_y}, speed={speed}, "
                        f"Predicted Collision: frame={collision_frame}, y={collision_y}, "
                        f"paddlePos={paddle_pos}, useBig={use_big}, useSpeed={use_speed}")

            # Calculate how much to move to reach the predicted y position
            total_needed = collision_y - paddle_pos

            debug_write(f"Movement needed: {total_needed} (target y: {collision_y}, current y: {paddle_pos})")

            # Calculate frames needed to reach the target based on paddle speed and distance
            # This helps ensure we don't try to move too fast
            distance_to_travel = abs(total_needed)
            frames_to_travel = math.ceil(distance_to_travel / paddle_speed)
            frames_to_reach = min(frames_to_travel, collision_frame)

            # Make sure we have at least 1 frame
            frames_to_reach = max(1, frames_to_reach)

            debug_write(f"Movement plan: distance={distance_to_travel}, frames_needed={frames_to_travel}, frames_to_reach={frames_to_reach}")

            # In case the ball is moving away, center paddle more gradually
            if dir_x < 0 and ball_x < 50:
                # Don't move to center if we're already close to center
                if abs(paddle_pos - 50.0) < 10:
                    total_needed = 0
                    debug_write(f"Ball away, already near center - staying still")
                else:
                    total_needed = 50.0 - paddle_pos
                    frames_to_reach = GAME_FPS // 2  # More gradual centering
                    debug_write(f"Ball away from AI - centering paddle, movement needed: {total_needed}")

            current_pos = paddle_pos
            for frame_i in range(GAME_FPS):
                # If we've reached our target position or passed collision frame, stop moving
                if (frame_i >= frames_to_reach) or (frame_i >= collision_frame) or abs(total_needed) < 1.0:
                    move = "0"
                else:
                    # Calculate step for this frame
                    step_per_frame = total_needed / frames_to_reach

                    # Choose movement direction - IMPORTANT: In the game:
                    # "+" means move DOWN (y increases)
                    # "-" means move UP (y decreases)
                    if step_per_frame > 0.5:  # Need to move DOWN
                        move = "+"
                        current_pos += min(paddle_speed, step_per_frame)
                    elif step_per_frame < -0.5:  # Need to move UP
                        move = "-"
                        current_pos += max(-paddle_speed, step_per_frame)  # This will decrease y
                    else:
                        move = "0"  # No movement needed

                # Clamp paddle position (important to update our tracked position)
                if current_pos < paddle_size/2:
                    current_pos = paddle_size/2
                elif current_pos > 100 - paddle_size/2:
                    current_pos = 100 - paddle_size/2

                # Create the action for this frame
                action = {
                    "movePaddle": move,
                    "activatePowerupBig": activate_big,
                    "activatePowerupSpeed": activate_slow or activate_fast  # Combine both speed types
                }
                actions.append(action)

                debug_write(f"Frame={frame_i}, Move={move}, PaddlePos={current_pos:.2f}, "
                            f"PowerUpBig={activate_big}, PowerUpSpeed={activate_slow or activate_fast}")

                # only trigger powerups once
                activate_big = False
                activate_slow = False
                activate_fast = False

        except Exception as e:
            logging.error(f"Thinker plan error: {e}")
            debug_write(f"Error in planning: {str(e)}")
            # fallback
            for _ in range(GAME_FPS):
                actions.append({
                    "movePaddle": "0",
                    "activatePowerupBig": False,
                    "activatePowerupSpeed": False
                })

        return actions


class AIPlayer:
    """
    Main AI entrypoint used by the game loop. Owns the Thinker + action_queue.
    The game loop calls:
      ai.compute(game_state)  # about once per second for a new snapshot
      action = await ai.action()  # each frame to see what to do next
    """

    def __init__(self, difficulty=1):
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

        # Log when powerups become available
        if current_big_state == "available" and self.last_big_state != "available":
            debug_write("!!! BIG POWERUP NOW AVAILABLE !!!")
        if current_speed_state == "available" and self.last_speed_state != "available":
            debug_write("!!! SPEED POWERUP NOW AVAILABLE !!!")

        # Check if we've used powerups
        if self.last_big_state == "available" and current_big_state == "unavailable":
            self.powerup_big_used = True
            debug_write("BIG POWERUP HAS BEEN USED!")
        if self.last_speed_state == "available" and current_speed_state == "unavailable":
            self.powerup_speed_used = True
            debug_write("SPEED POWERUP HAS BEEN USED!")

        # Store current powerup states
        self.last_big_state = current_big_state
        self.last_speed_state = current_speed_state

        # Determine if this is a critical game moment (close scores near end of game)
        if (left_score >= 9 or right_score >= 9) and abs(left_score - right_score) <= 2:
            self.game_critical_moment = True
            debug_write(f"CRITICAL GAME MOMENT DETECTED! Score: {left_score}-{right_score}")
        else:
            self.game_critical_moment = False

        # Force powerup usage based on game state
        if (current_big_state == "available" or current_speed_state == "available"):
            self.powerup_usage_attempts += 1

            # Be more aggressive with usage in critical moments
            max_attempts = 3 if self.game_critical_moment else 5

            if self.powerup_usage_attempts > max_attempts:
                debug_write(f"Forcing powerup usage after {self.powerup_usage_attempts} attempts")
                # Clear queue to inject a forced powerup action
                while not self.action_queue.empty():
                    self.action_queue.get()

                # Determine which speed powerup to use based on ball direction
                ball = game_state.get("ball", {})
                dir_x = ball.get("directionX", 0)
                ball_coming_toward_ai = dir_x > 0

                use_slow = slow_state == "available" and ball_coming_toward_ai
                use_fast = fast_state == "available" and not ball_coming_toward_ai
                use_speed = use_slow or use_fast

                # Add an immediate action that uses any available powerup
                self.action_queue.put({
                    "movePaddle": "0",  # Neutral movement
                    "activatePowerupBig": current_big_state == "available",
                    "activatePowerupSpeed": use_speed
                })

                debug_write(f"Forced powerup usage: Big={current_big_state=='available'}, Speed={use_speed}")

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

    async def action(self) -> Dict[str, Any]:
        """
        Called by the game loop each frame to get the next AI action.
        If the queue is empty, returns a do-nothing fallback.
        """
        try:
            action = self.action_queue.get_nowait()

            # Track when we actually try to use powerups
            if action.get("activatePowerupBig", False):
                debug_write("⭐ TRYING TO USE BIG POWERUP NOW ⭐")
            if action.get("activatePowerupSpeed", False):
                debug_write("⭐ TRYING TO USE SPEED POWERUP NOW ⭐")

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
            speed_available = (player_right.get("powerupSlow") == "available" or
                              player_right.get("powerupFast") == "available")

            # If in emergency and powerups available, use them!
            if big_available or speed_available:
                debug_write(f"Emergency powerup usage! Big: {big_available}, Speed: {speed_available}")

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
