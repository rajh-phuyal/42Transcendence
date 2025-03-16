import threading
import logging
from queue import Queue, Empty
from typing import List, Dict, Any, Tuple, Optional
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
        self.last_paddle_pos = None

        # Start background thread to handle AI computations
        self.thread = threading.Thread(target=self.computeLoop, daemon=True)
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

    def computeLoop(self):
        """
        Main computation loop that runs in a background thread.
        Processes game states and generates actions.
        """
        while self.running:
            if self.waiting:
                continue

            try:
                game_state = self.game_state

                debug_write(f"--- NEW SNAPSHOT ---")
                debug_write(f"GameState: {game_state}")

                self.learner.update_with_game_state(game_state)
                metrics = self.learner.get_metrics(game_state)
                action_sequence = self.planActionsForNextSecond(game_state, metrics)

                self.queuePlannedActions(action_sequence)

                self.waiting = True

            except Exception as e:
                logging.error(f"Error in AI compute loop: {e}")

    def queuePlannedActions(self, action_sequence: List[Dict[str, Any]]) -> None:
        """
        Add the planned actions to the action queue.

        :param action_sequence: List of actions to queue
        """
        for action in action_sequence:
            if not self.action_queue.full():
                debug_write(f"Enqueued action: {action}")
                self.action_queue.put(action)
            else:
                break

        debug_write(f"Enqueued {len(action_sequence)} actions.")

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
        ) -> Optional[Tuple[int, float]]:
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

        # Normalize directions if needed
        dir_x, dir_y = self.normalizeDirections(dir_x, dir_y)

        dt = 1.0 / fps

        # Get wall boundaries
        top_wall, bottom_wall = self.getWallBoundaries()

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

        return self.simulateBallPath(x, y, vx, vy, dt_sub, substeps, collision_x, top_wall, bottom_wall, max_frames)

    def normalizeDirections(self, dir_x: float, dir_y: float) -> Tuple[float, float]:
        """
        Ensure direction values are not too small to avoid simulation issues.

        :param dir_x: X direction component
        :param dir_y: Y direction component
        :return: Normalized direction components
        """
        # VERY IMPORTANT: If direction is nearly zero, simulation will take too long
        # This happens in the game sometimes due to rounding errors - fix it
        norm_dir_x = 0.0001 if abs(dir_x) < 0.0001 else dir_x

        # CLAMP extremely small Y directions to prevent simulation errors
        norm_dir_y = 0.0001 if abs(dir_y) < 0.0001 else dir_y

        return norm_dir_x, norm_dir_y

    def getWallBoundaries(self) -> Tuple[float, float]:
        """
        Calculate the effective wall boundaries, taking ball size into account.

        :return: Tuple of (top_wall, bottom_wall) positions
        """
        ball_height = self.game_state.get("ball", {}).get("height", 1.0)
        # IMPROVED: Use a smaller wall buffer to avoid prediction errors
        top_wall = ball_height * 0.9  # Slightly smaller buffer
        bottom_wall = 100 - (ball_height * 0.9)  # Slightly smaller buffer

        return top_wall, bottom_wall

    def simulateBallPath(
            self,
            x: float,
            y: float,
            vx: float,
            vy: float,
            dt_sub: float,
            substeps: int,
            collision_x: float,
            top_wall: float,
            bottom_wall: float,
            max_frames: int
        ) -> Optional[Tuple[int, float]]:
        """
        Simulate the ball's path to predict collision with AI paddle.

        :param x: Starting x position
        :param y: Starting y position
        :param vx: X velocity
        :param vy: Y velocity
        :param dt_sub: Time step for simulation
        :param substeps: Number of substeps per frame
        :param collision_x: X coordinate where we want to detect collision
        :param top_wall: Y coordinate of top wall
        :param bottom_wall: Y coordinate of bottom wall
        :param max_frames: Maximum number of frames to simulate
        :return: Tuple of (frame_index, collision_y) or None if no collision
        """
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
                    collision_y = self.interpolateCollisionY(prev_x, prev_y, x, y, collision_x)
                    debug_write(f"Collision predicted at frame {frame_idx}, y={collision_y}")
                    return (frame_idx, collision_y)

            # Safety check - if x is way out of bounds, abort
            if x < -10 or x > 110:
                debug_write(f"Ball x position out of bounds: {x}, aborting prediction")
                return None

        # If we've gone through all frames, try estimating the collision
        return self.estimateCollision(x, y, vx, vy, collision_x, top_wall, bottom_wall, dt_sub * substeps, max_frames)

    def interpolateCollisionY(
            self,
            prev_x: float,
            prev_y: float,
            x: float,
            y: float,
            collision_x: float
        ) -> float:
        """
        Interpolate the exact y-position at the collision x-coordinate.

        :param prev_x: Previous x position
        :param prev_y: Previous y position
        :param x: Current x position
        :param y: Current y position
        :param collision_x: X coordinate where we want to calculate y
        :return: Interpolated y position at collision_x
        """
        # Interpolate exact y position at crossing
        if prev_x != x:  # Avoid division by zero
            t = (collision_x - prev_x) / (x - prev_x)
            collision_y = prev_y + t * (y - prev_y)
        else:
            collision_y = y

        # Get wall boundaries for clamping
        top_wall, bottom_wall = self.getWallBoundaries()

        # Clamp the collision y value to be in bounds
        collision_y = max(top_wall, min(bottom_wall, collision_y))

        return collision_y

    def estimateCollision(
            self,
            x: float,
            y: float,
            vx: float,
            vy: float,
            collision_x: float,
            top_wall: float,
            bottom_wall: float,
            dt: float,
            max_frames: int
        ) -> Optional[Tuple[int, float]]:
        """
        If simulation didn't result in a collision, estimate where it might happen.

        :param x: Last x position in simulation
        :param y: Last y position in simulation
        :param vx: X velocity
        :param vy: Y velocity
        :param collision_x: Target x position for collision
        :param top_wall: Y coordinate of top wall
        :param bottom_wall: Y coordinate of bottom wall
        :param dt: Time step used in simulation
        :param max_frames: Maximum frames simulated
        :return: Estimated collision data or None
        """
        # Check if we're even moving toward the collision plane
        if vx > 0 and x < collision_x:
            # We're moving toward collision but didn't reach it in max_frames
            debug_write(f"Ball moving toward collision_x but didn't reach in {max_frames} frames")
            # Estimate based on current trajectory
            time_to_collision = (collision_x - x) / vx if vx != 0 else float('inf')
            estimated_y = y + vy * time_to_collision
            # Clamp to screen bounds
            estimated_y = max(top_wall, min(bottom_wall, estimated_y))
            estimated_frame = int(time_to_collision / dt)
            debug_write(f"Estimated collision at frame {estimated_frame}, y={estimated_y}")
            return (estimated_frame, estimated_y)

        # No collision by max_frames
        debug_write(f"No collision predicted within {max_frames} frames")
        return None

    def planActionsForNextSecond(self, game_state: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan a sequence of actions for the next second based on game state and metrics.

        :param game_state: Current game state
        :param metrics: Metrics provided by the Learner
        :return: List of actions to execute
        """
        actions = []
        try:
            # Extract game state data
            ball, paddle, game_data = self.extractGameStateData(game_state)

            # Check for major paddle position changes
            self.checkForPaddlePositionChanges(paddle.get("paddlePos", 50.0))

            # Get powerup usage decisions
            powerup_decisions = self.determinePowerupUsage(paddle, metrics)

            # Get collision prediction
            collision_info = self.getCollisionPrediction(ball)

            # Calculate paddle movement plan
            movement_plan = self.calculateMovementPlan(ball, paddle, collision_info)

            # Generate actions based on our planning
            actions = self.generateActionSequence(paddle, movement_plan, powerup_decisions)

        except Exception as e:
            logging.error(f"Thinker plan error: {e}")
            debug_write(f"Error in planning: {str(e)}")
            # fallback actions
            actions = self.generateFallbackActions()

        return actions

    def extractGameStateData(self, game_state: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Extract relevant data from the game state.

        :param game_state: Current game state
        :return: Tuple of (ball, paddle, game_data) dictionaries
        """
        ball = game_state.get("ball", {})
        paddle = game_state.get("playerRight", {})
        game_data = game_state.get("gameData", {})

        return ball, paddle, game_data

    def checkForPaddlePositionChanges(self, paddle_pos: float) -> None:
        """
        Check if paddle position has changed dramatically, indicating a reset.

        :param paddle_pos: Current paddle position
        """
        if self.last_paddle_pos is not None and abs(self.last_paddle_pos - paddle_pos) > 20:
            debug_write(f"!!! MAJOR PADDLE POSITION CHANGE DETECTED: {self.last_paddle_pos} -> {paddle_pos}")
            # Reset prediction history since our context has completely changed
            self.last_predicted_y = None
            self.last_predicted_frame = None
            debug_write(f"Prediction history reset due to major position change")

        # Track the paddle position for next time
        self.last_paddle_pos = paddle_pos

    def determinePowerupUsage(self, paddle: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, bool]:
        """
        Determine which powerups to use based on game state and metrics.

        :param paddle: Paddle state data
        :param metrics: Metrics from Learner
        :return: Dictionary of powerup usage decisions
        """
        # Get powerup usage decisions from metrics
        use_big = metrics.get("useBig", False)
        use_speed = metrics.get("useSpeed", False)

        # Check for available powerups in the game state
        big_available = paddle.get("powerupBig") == "available"
        slow_available = paddle.get("powerupSlow") == "available"
        fast_available = paddle.get("powerupFast") == "available"

        debug_write(f"Powerup state check - Big: {paddle.get('powerupBig')}, Slow: {paddle.get('powerupSlow')}, Fast: {paddle.get('powerupFast')}")

        # Final determination of which powerups to actually use
        activate_big = use_big and big_available

        # For speed powerups, we need to determine which one to use based on ball direction
        ball = self.game_state.get("ball", {})
        dir_x = ball.get("directionX", 0)
        ball_coming_toward_ai = dir_x > 0

        use_slow = use_speed and slow_available and ball_coming_toward_ai
        use_fast = use_speed and fast_available and not ball_coming_toward_ai

        debug_write(f"Planning actions with powerups: useBig={use_big}(available:{big_available}), useSpeed={use_speed}(slow:{slow_available}, fast:{fast_available})")
        debug_write(f"ACTIVATING powerups: Big={activate_big}, Slow={use_slow}, Fast={use_fast}")

        return {
            "activate_big": activate_big,
            "use_slow": use_slow,
            "use_fast": use_fast,
            "ball_coming_toward_ai": ball_coming_toward_ai
        }

    def getCollisionPrediction(self, ball: Dict[str, Any]) -> Optional[Tuple[int, float]]:
        """
        Get prediction of when and where the ball will collide with the AI paddle.

        :param ball: Ball state data
        :return: Tuple of (collision_frame, collision_y) or None
        """
        ball_x = ball.get("posX", 50.0)
        ball_y = ball.get("posY", 50.0)
        dir_x = ball.get("directionX", 1.0)
        dir_y = ball.get("directionY", 0.0)
        speed = ball.get("speed", 1.0)

        # Check the situation - ball coming toward AI or moving away
        ball_coming_toward_ai = dir_x > 0

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

        # Use previous prediction as fallback if available and no new prediction
        if collision_info is None:
            if ball_coming_toward_ai:
                debug_write(f"No collision predicted but ball coming toward AI")

            if self.last_predicted_y is not None:
                collision_y = self.last_predicted_y
                if self.last_predicted_frame is not None:
                    collision_frame = max(1, self.last_predicted_frame - GAME_FPS)  # Decrement by 1 second
                else:
                    collision_frame = GAME_FPS
                debug_write(f"Using previous prediction: y={collision_y}, frame={collision_frame}")
                return (collision_frame, collision_y)
            else:
                # If no prediction at all, center the paddle
                collision_y = 50.0
                collision_frame = GAME_FPS
                debug_write(f"No prediction available - centering paddle")
                return (collision_frame, collision_y)
        else:
            collision_frame, collision_y = collision_info

            # Store for future reference
            self.last_predicted_y = collision_y
            self.last_predicted_frame = collision_frame

            # Apply smaller error based on difficulty
            collision_y = self.applyPredictionError(collision_y)

            return (collision_frame, collision_y)

    def applyPredictionError(self, collision_y: float) -> float:
        """
        Apply a difficulty-based error to the predicted collision y-position.

        :param collision_y: Predicted collision y-position
        :return: Adjusted collision y-position with error applied
        """
        # Apply a much smaller error based on difficulty
        randomness = DIFFICULTY_CONFIGS[self.difficulty]["randomness"] * 0.5  # Reduce by half
        error_margin = DIFFICULTY_CONFIGS[self.difficulty]["error_margin"] * 0.5  # Reduce by half

        # Add a smaller error to make AI challenging but not miss too much
        if random.random() < randomness:
            # Much smaller error range
            error_amount = random.uniform(-error_margin * 5, error_margin * 5)
            debug_write(f"Adding small error of {error_amount} to predicted y")
            collision_y += error_amount

            # Get paddle size for clamping
            paddle = self.game_state.get("playerRight", {})
            paddle_size = paddle.get("paddleSize", 10.0)

            # Clamp to keep in bounds
            collision_y = max(paddle_size/2, min(100 - paddle_size/2, collision_y))

        return collision_y

    def calculateMovementPlan(self, ball: Dict[str, Any], paddle: Dict[str, Any], collision_info: Optional[Tuple[int, float]]) -> Dict[str, Any]:
        """
        Calculate a plan for paddle movement based on collision prediction.

        :param ball: Ball state data
        :param paddle: Paddle state data
        :param collision_info: Collision prediction information
        :return: Movement plan with necessary parameters
        """
        # Default values when no collision predicted
        if collision_info is None:
            return {
                "total_needed": 0,
                "frames_to_reach": GAME_FPS,
                "collision_frame": GAME_FPS,
                "collision_y": 50.0,
                "current_pos": paddle.get("paddlePos", 50.0)
            }

        # Extract collision information
        collision_frame, collision_y = collision_info

        # Get paddle information
        paddle_pos = paddle.get("paddlePos", 50.0)
        paddle_size = paddle.get("paddleSize", 10.0)
        paddle_speed = paddle.get("paddleSpeed", 3.5)

        # Calculate how much to move to reach the predicted y position
        total_needed = collision_y - paddle_pos

        debug_write(f"Movement needed: {total_needed} (target y: {collision_y}, current y: {paddle_pos})")

        # Calculate frames needed to reach the target based on paddle speed and distance
        distance_to_travel = abs(total_needed)
        frames_to_travel = math.ceil(distance_to_travel / paddle_speed)
        frames_to_reach = min(frames_to_travel, collision_frame)

        # Make sure we have at least 1 frame
        frames_to_reach = max(1, frames_to_reach)

        debug_write(f"Movement plan: distance={distance_to_travel}, frames_needed={frames_to_travel}, frames_to_reach={frames_to_reach}")

        # In case the ball is moving away, center paddle more gradually
        dir_x = ball.get("directionX", 0)
        ball_x = ball.get("posX", 50.0)

        if dir_x < 0 and ball_x < 50:
            # Don't move to center if we're already close to center
            if abs(paddle_pos - 50.0) < 10:
                total_needed = 0
                debug_write(f"Ball away, already near center - staying still")
            else:
                total_needed = 50.0 - paddle_pos
                frames_to_reach = GAME_FPS // 2  # More gradual centering
                debug_write(f"Ball away from AI - centering paddle, movement needed: {total_needed}")

        return {
            "total_needed": total_needed,
            "frames_to_reach": frames_to_reach,
            "collision_frame": collision_frame,
            "collision_y": collision_y,
            "current_pos": paddle_pos,
            "paddle_size": paddle_size,
            "paddle_speed": paddle_speed
        }

    def generateActionSequence(
            self,
            paddle: Dict[str, Any],
            movement_plan: Dict[str, Any],
            powerup_decisions: Dict[str, bool]
        ) -> List[Dict[str, Any]]:
        """
        Generate a sequence of actions based on movement plan and powerup decisions.

        :param paddle: Paddle state data
        :param movement_plan: Calculated movement plan
        :param powerup_decisions: Powerup usage decisions
        :return: List of actions to execute
        """
        actions = []

        # Extract necessary values from movement plan
        total_needed = movement_plan["total_needed"]
        frames_to_reach = movement_plan["frames_to_reach"]
        collision_frame = movement_plan["collision_frame"]
        current_pos = movement_plan["current_pos"]
        paddle_size = movement_plan["paddle_size"]
        paddle_speed = movement_plan["paddle_speed"]

        # Extract powerup decisions
        activate_big = powerup_decisions["activate_big"]
        use_slow = powerup_decisions["use_slow"]
        use_fast = powerup_decisions["use_fast"]

        # IMPORTANT: Create a special first action with powerups
        # This ensures we explicitly try to use powerups right away
        if activate_big or use_slow or use_fast:
            first_action = self.createPowerupAction(
                total_needed,
                frames_to_reach,
                paddle_speed,
                current_pos,
                paddle_size,
                activate_big,
                use_slow,
                use_fast
            )
            actions.append(first_action["action"])
            current_pos = first_action["updated_pos"]

            # For remaining frames, we don't activate powerups again
            start_frame = 1
        else:
            start_frame = 0

        # Plan the rest of the actions (after the powerup action if used)
        for frame_i in range(start_frame, GAME_FPS):
            action = self.createMovementAction(
                frame_i,
                frames_to_reach,
                collision_frame,
                total_needed,
                paddle_speed,
                current_pos,
                paddle_size
            )
            actions.append(action["action"])
            current_pos = action["updated_pos"]

        return actions

    def createPowerupAction(
            self,
            total_needed: float,
            frames_to_reach: int,
            paddle_speed: float,
            current_pos: float,
            paddle_size: float,
            activate_big: bool,
            use_slow: bool,
            use_fast: bool
        ) -> Dict[str, Any]:
        """
        Create an action that activates powerups.

        :param total_needed: Total movement needed
        :param frames_to_reach: Frames available to reach target
        :param paddle_speed: Paddle movement speed
        :param current_pos: Current paddle position
        :param paddle_size: Size of the paddle
        :param activate_big: Whether to activate big paddle powerup
        :param use_slow: Whether to activate slow ball powerup
        :param use_fast: Whether to activate fast ball powerup
        :return: Dictionary with action and updated position
        """
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
        current_pos = self.clampPaddlePosition(current_pos, paddle_size)

        # Create the action with powerup usage
        action = {
            "movePaddle": move,
            "activatePowerupBig": activate_big,
            "activatePowerupSpeed": use_slow or use_fast
        }

        debug_write(f"SPECIAL POWERUP ACTION: Move={move}, PaddlePos={current_pos:.2f}, "
                    f"PowerUpBig={activate_big}, PowerUpSpeed={use_slow or use_fast}")

        return {
            "action": action,
            "updated_pos": current_pos
        }

    def createMovementAction(
            self,
            frame_i: int,
            frames_to_reach: int,
            collision_frame: int,
            total_needed: float,
            paddle_speed: float,
            current_pos: float,
            paddle_size: float
        ) -> Dict[str, Any]:
        """
        Create an action for paddle movement.

        :param frame_i: Current frame index
        :param frames_to_reach: Total frames to reach target
        :param collision_frame: Frame when collision is predicted
        :param total_needed: Total movement needed
        :param paddle_speed: Paddle movement speed
        :param current_pos: Current paddle position
        :param paddle_size: Size of the paddle
        :return: Dictionary with action and updated position
        """
        # Determine whether movement is needed
        if (frame_i >= frames_to_reach) or (frame_i >= collision_frame) or abs(total_needed) < 0.3:
            move = "0"
        else:
            # Calculate step for this frame
            step_per_frame = total_needed / frames_to_reach

            # Choose movement direction
            if step_per_frame > 0.2:  # Need to move DOWN
                move = "+"
                current_pos += min(paddle_speed, step_per_frame)
            elif step_per_frame < -0.2:  # Need to move UP
                move = "-"
                current_pos += max(-paddle_speed, step_per_frame)  # This will decrease y
            else:
                move = "0"  # No movement needed

        # Clamp paddle position
        current_pos = self.clampPaddlePosition(current_pos, paddle_size)

        # Create the action for this frame - no powerups for regular frames
        action = {
            "movePaddle": move,
            "activatePowerupBig": False,
            "activatePowerupSpeed": False
        }

        debug_write(f"Frame={frame_i}, Move={move}, PaddlePos={current_pos:.2f}, "
                    f"PowerUpBig=False, PowerUpSpeed=False")

        return {
            "action": action,
            "updated_pos": current_pos
        }

    def clampPaddlePosition(self, position: float, paddle_size: float) -> float:
        """
        Clamp paddle position to keep it within valid bounds.

        :param position: Current paddle position
        :param paddle_size: Size of the paddle
        :return: Clamped paddle position
        """
        if position < paddle_size/2:
            return paddle_size/2
        elif position > 100 - paddle_size/2:
            return 100 - paddle_size/2
        return position

    def generateFallbackActions(self) -> List[Dict[str, Any]]:
        """
        Generate fallback actions when there's an error in planning.

        :return: List of fallback actions
        """
        actions = []
        for _ in range(GAME_FPS):
            actions.append({
                "movePaddle": "0",
                "activatePowerupBig": False,
                "activatePowerupSpeed": False
            })
        return actions
