import threading
import logging
from queue import Queue, Empty
from typing import List, Dict, Any
import random
import math
from game.constants import GAME_FPS

from .AI import debug_write, DIFFICULTY_CONFIGS
from .AiLearner import Learner

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
        self.running = True
        self.waiting = False
        self.game_state: Dict[str, Any] = {}

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
        self.game_state = game_state
        self.waiting = False

    def cleanup(self):
        """
        Stop the background thread.
        """
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _compute_loop(self):
        while self.running:
            if self.waiting:
                continue

            try:
                game_state = self.game_state

                debug_write(f"--- NEW SNAPSHOT ---")
                debug_write(f"GameState: {game_state}")

                self.learner.update_with_game_state(game_state)
                metrics = self.learner.get_metrics(game_state)
                action_sequence = self._plan_actions_for_next_second(game_state, metrics)

                for action in action_sequence:
                    if not self.action_queue.full():
                        debug_write(f"Enqueued action: {action}")
                        self.action_queue.put(action)
                    else:
                        break

                debug_write(f"Enqueued {len(action_sequence)} actions.")

                self.waiting = True

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
            ball_height = self.game_state.get("ball", {}).get("height", 1.0)
            # IMPROVED: Use a smaller wall buffer to avoid prediction errors
            top_wall = ball_height * 0.9  # Slightly smaller buffer
            bottom_wall = 100 - (ball_height * 0.9)  # Slightly smaller buffer

            # Initialize for simulation
            x = start_x
            y = start_y
            vx = dir_x * speed  # Incorporate speed into velocity
            vy = dir_y * speed

            # Log initial prediction data
            debug_write(f"Starting prediction from: x={x}, y={y}, vx={vx}, vy={vy}, speed={speed}")
            debug_write(f"Target collision_x: {collision_x}")

            # Use a higher time resolution for more accurate predictions
            # Instead of 1 step per frame, use multiple substeps
            substeps = 4  # More substeps for better accuracy
            dt_sub = dt / substeps

            # Simplified physics simulation - step by step
            for frame_idx in range(max_frames):
                for substep in range(substeps):
                    # Save previous position for interpolation
                    prev_x = x
                    prev_y = y

                    # Move
                    x += vx * dt_sub
                    y += vy * dt_sub

                    # Bounce off top/bottom walls with ball height considered
                    if y < top_wall:
                        y = 2 * top_wall - y  # Reflect position
                        vy = -vy  # Reflect velocity
                        if substep == 0:  # Only log on the first substep to avoid excessive logs
                            debug_write(f"Top wall bounce at frame {frame_idx}, x={x}")
                    elif y > bottom_wall:
                        y = 2 * bottom_wall - y  # Reflect position
                        vy = -vy  # Reflect velocity
                        if substep == 0:  # Only log on the first substep to avoid excessive logs
                            debug_write(f"Bottom wall bounce at frame {frame_idx}, x={x}")

                    # Check if crossing collision_x on this substep
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

            # Get powerup usage decisions from metrics
            use_big = metrics.get("useBig", False)
            use_speed = metrics.get("useSpeed", False)

            # Check for available powerups in the game state
            big_available = paddle.get("powerupBig") == "available"
            slow_available = paddle.get("powerupSlow") == "available"
            fast_available = paddle.get("powerupFast") == "available"

            debug_write(f"Powerup state check - Big: {paddle.get('powerupBig')}, Slow: {paddle.get('powerupSlow')}, Fast: {paddle.get('powerupFast')}")

            # Final determination of which powerups to actually use (combining our decision with availability)
            activate_big = use_big and big_available

            # For speed powerups, we need to determine which one to use based on ball direction
            ball_coming_toward_ai = dir_x > 0
            use_slow = use_speed and slow_available and ball_coming_toward_ai
            use_fast = use_speed and fast_available and not ball_coming_toward_ai

            # Log our decision about powerups for this planning cycle
            debug_write(f"Planning actions with powerups: useBig={use_big}(available:{big_available}), useSpeed={use_speed}(slow:{slow_available}, fast:{fast_available})")
            debug_write(f"ACTIVATING powerups: Big={activate_big}, Slow={use_slow}, Fast={use_fast}")

            # Check the situation - ball coming toward AI or moving away
            if ball_coming_toward_ai:
                collision_info = self.predict_collision_frame_and_y(
                    start_x=ball_x,
                    start_y=ball_y,
                    dir_x=dir_x,
                    dir_y=dir_y,
                    speed=speed,
                    fps=GAME_FPS,
                    max_frames=4 * GAME_FPS,
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

                # Apply a much smaller error based on difficulty
                # REDUCED ERROR - This was causing the paddle to miss
                randomness = DIFFICULTY_CONFIGS[self.difficulty]["randomness"] * 0.5  # Reduce by half
                error_margin = DIFFICULTY_CONFIGS[self.difficulty]["error_margin"] * 0.5  # Reduce by half

                # Add a smaller error to make AI challenging but not miss too much
                if random.random() < randomness:
                    # Much smaller error range
                    error_amount = random.uniform(-error_margin * 5, error_margin * 5)
                    debug_write(f"Adding small error of {error_amount} to predicted y")
                    collision_y += error_amount
                    # Clamp to keep in bounds
                    collision_y = max(paddle_size/2, min(100 - paddle_size/2, collision_y))

            debug_write(f"Plan Next Second => BallX={ball_x}, BallY={ball_y}, "
                        f"DirX={dir_x}, DirY={dir_y}, speed={speed}, "
                        f"Predicted Collision: frame={collision_frame}, y={collision_y}, "
                        f"paddlePos={paddle_pos}, useBig={activate_big}, useSpeed={use_slow or use_fast}")

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

            # IMPORTANT: Create a special first action with powerups
            # This ensures we explicitly try to use powerups right away
            if activate_big or use_slow or use_fast:
                # Determine first movement
                if total_needed > 0.5:  # Need to move DOWN
                    move = "+"
                    current_pos += min(paddle_speed, total_needed / frames_to_reach)
                elif total_needed < -0.5:  # Need to move UP
                    move = "-"
                    current_pos += max(-paddle_speed, total_needed / frames_to_reach)  # This will decrease y
                else:
                    move = "0"  # No movement needed

                # Clamp paddle position
                if current_pos < paddle_size/2:
                    current_pos = paddle_size/2
                elif current_pos > 100 - paddle_size/2:
                    current_pos = 100 - paddle_size/2

                # Add the action with powerup usage
                first_action = {
                    "movePaddle": move,
                    "activatePowerupBig": activate_big,
                    "activatePowerupSpeed": use_slow or use_fast
                }
                actions.append(first_action)

                debug_write(f"SPECIAL POWERUP ACTION: Move={move}, PaddlePos={current_pos:.2f}, "
                            f"PowerUpBig={activate_big}, PowerUpSpeed={use_slow or use_fast}")

                # For remaining frames, we don't activate powerups again
                start_frame = 1
                powerups_used = True
            else:
                start_frame = 0
                powerups_used = False

            # Plan the rest of the actions (after the powerup action if used)
            for frame_i in range(start_frame, GAME_FPS):
                # CHANGED: Reduced movement threshold from 1.0 to 0.3
                # to make smaller, more precise movements
                if (frame_i >= frames_to_reach) or (frame_i >= collision_frame) or abs(total_needed) < 0.3:
                    move = "0"
                else:
                    # Calculate step for this frame
                    step_per_frame = total_needed / frames_to_reach

                    # CHANGED: Reduced the threshold from 0.5 to 0.2 for more responsive movement
                    # Choose movement direction - IMPORTANT: In the game:
                    # "+" means move DOWN (y increases)
                    # "-" means move UP (y decreases)
                    if step_per_frame > 0.2:  # Need to move DOWN - lower threshold
                        move = "+"
                        current_pos += min(paddle_speed, step_per_frame)
                    elif step_per_frame < -0.2:  # Need to move UP - lower threshold
                        move = "-"
                        current_pos += max(-paddle_speed, step_per_frame)  # This will decrease y
                    else:
                        move = "0"  # No movement needed

                # Clamp paddle position (important to update our tracked position)
                if current_pos < paddle_size/2:
                    current_pos = paddle_size/2
                elif current_pos > 100 - paddle_size/2:
                    current_pos = 100 - paddle_size/2

                # Create the action for this frame - no powerups for remaining frames
                action = {
                    "movePaddle": move,
                    "activatePowerupBig": False,
                    "activatePowerupSpeed": False
                }
                actions.append(action)

                debug_write(f"Frame={frame_i}, Move={move}, PaddlePos={current_pos:.2f}, "
                            f"PowerUpBig=False, PowerUpSpeed=False")

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
