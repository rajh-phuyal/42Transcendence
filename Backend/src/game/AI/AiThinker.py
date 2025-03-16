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
    A background 'Thinker' that generates actions for the AI player.
    - Receives game states from the AIPlayer
    - Plans actions and adds them to the action queue
    - Uses Learner for decision making about powerups
    """

    def __init__(self, action_queue: Queue, difficulty: int = 1):
        """Initialize the Thinker with action queue and difficulty level"""
        self.action_queue = action_queue
        self.difficulty = difficulty
        self.running = True
        self.waiting = False
        self.game_state: Dict[str, Any] = {}

        # Track prediction state
        self.last_predicted_y = None
        self.last_predicted_frame = None
        self.last_paddle_pos = None

        # Single parameter to control prediction accuracy/speed
        # 0 = fastest/simplest, 10 = most accurate/complex
        self.prediction_accuracy = 5

        # Create the learner
        self.learner = Learner(difficulty=difficulty)

        # Start background thread
        self.thread = threading.Thread(target=self.compute_loop, daemon=True)
        self.thread.start()

    def set_prediction_accuracy(self, value: int) -> None:
        """Set the prediction accuracy level (0-10)"""
        self.prediction_accuracy = max(0, min(10, value))
        debug_write(f"Set prediction accuracy to {self.prediction_accuracy}")

    def think(self, game_state: Dict[str, Any]) -> None:
        """Process a new game state snapshot"""
        self.game_state = game_state
        self.waiting = False

    def cleanup(self):
        """Stop the background thread"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def compute_loop(self):
        """Main computation loop running in background thread"""
        while self.running:
            if self.waiting:
                continue

            try:
                game_state = self.game_state
                if not game_state:
                    self.waiting = True
                    continue

                debug_write("--- NEW PLANNING CYCLE ---")

                # Update learner with current state
                self.learner.update_with_game_state(game_state)

                # Get recommendations from learner
                metrics = self.learner.get_metrics(game_state)

                # Plan actions for the next second
                actions = self.plan_actions(game_state, metrics)

                # Add actions to the queue
                self.add_actions_to_queue(actions)

                self.waiting = True

            except Exception as e:
                logging.error(f"Error in AI compute loop: {e}")
                debug_write(f"ERROR in compute loop: {str(e)}")

    def plan_actions(self, game_state: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan a sequence of actions based on game state and metrics"""
        actions = []

        try:
            # Extract game elements
            ball = game_state.get("ball", {})
            paddle = game_state.get("playerRight", {})

            # Check for major paddle position changes
            self.check_paddle_position_changes(paddle.get("paddlePos", 50.0))

            # Get powerup decisions
            powerup_decisions = self.determine_powerup_usage(paddle, metrics)

            # Predict where ball will collide with paddle
            collision_info = self.predict_collision(ball)

            # Plan paddle movement
            movement_plan = self.plan_movement(ball, paddle, collision_info)

            # Generate actions
            actions = self.generate_action_sequence(paddle, movement_plan, powerup_decisions)

        except Exception as e:
            logging.error(f"Error planning actions: {e}")
            debug_write(f"ERROR planning actions: {str(e)}")
            actions = self.generate_fallback_actions()

        return actions

    def check_paddle_position_changes(self, paddle_pos: float) -> None:
        """Check if paddle position has changed significantly"""
        if self.last_paddle_pos is not None and abs(self.last_paddle_pos - paddle_pos) > 20:
            debug_write(f"Major paddle position change: {self.last_paddle_pos} -> {paddle_pos}")
            self.last_predicted_y = None
            self.last_predicted_frame = None

        self.last_paddle_pos = paddle_pos

    def determine_powerup_usage(self, paddle: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, bool]:
        """Determine which powerups to use based on metrics and game state"""
        # Get powerup recommendations from learner
        use_big = metrics.get("useBig", False)
        use_speed = metrics.get("useSpeed", False)

        # Check if powerups are available
        big_available = paddle.get("powerupBig") == "available"
        speed_available = paddle.get("powerupSpeed") == "available"

        # Ball direction affects the EFFECT of the speed powerup, not which powerup to use
        ball = self.game_state.get("ball", {})
        ball_coming_toward_ai = ball.get("directionX", 0) > 0

        # Final decision on powerup usage
        activate_big = use_big and big_available
        activate_speed = use_speed and speed_available

        debug_write(f"Powerup decisions: Big={activate_big}, Speed={activate_speed}, Ball toward AI={ball_coming_toward_ai}")

        return {
            "activate_big": activate_big,
            "activate_speed": activate_speed,
            "ball_coming_toward_ai": ball_coming_toward_ai
        }

    def predict_collision(self, ball: Dict[str, Any]) -> Optional[Tuple[int, float]]:
        """Predict when and where the ball will collide with the AI paddle"""
        ball_x = ball.get("posX", 50.0)
        ball_y = ball.get("posY", 50.0)
        dir_x = ball.get("directionX", 1.0)
        dir_y = ball.get("directionY", 0.0)
        speed = ball.get("speed", 1.0)

        # If ball moving away, use fallback
        if dir_x <= 0:
            debug_write(f"Ball moving away (x={ball_x}, y={ball_y}) - using fallback")
            return self.get_fallback_prediction(ball_y)

        # Choose prediction method based on accuracy parameter
        if self.prediction_accuracy <= 3:
            # Fast, simple prediction (no bounces)
            collision_info = self.predict_collision_simple(ball_x, ball_y, dir_x, dir_y, speed)
            debug_write(f"Using SIMPLE prediction (accuracy={self.prediction_accuracy})")
        elif self.prediction_accuracy <= 7:
            # Medium accuracy prediction (limited bounces)
            collision_info = self.predict_collision_medium(ball_x, ball_y, dir_x, dir_y, speed)
            debug_write(f"Using MEDIUM prediction (accuracy={self.prediction_accuracy})")
        else:
            # Full simulation (most accurate)
            collision_info = self.simulate_ball_path(
                start_x=ball_x,
                start_y=ball_y,
                dir_x=dir_x,
                dir_y=dir_y,
                speed=speed,
                collision_x=95.0
            )
            debug_write(f"Using FULL simulation (accuracy={self.prediction_accuracy})")

        # Store prediction for future reference
        if collision_info:
            self.last_predicted_frame, self.last_predicted_y = collision_info
            # Apply difficulty-based error
            collision_info = (collision_info[0], self.apply_prediction_error(collision_info[1]))
            debug_write(f"Using collision prediction: frame={collision_info[0]}, y={collision_info[1]}")
        else:
            collision_info = self.get_fallback_prediction(ball_y)

        return collision_info

    def predict_collision_simple(self, ball_x: float, ball_y: float, dir_x: float, dir_y: float, speed: float) -> Optional[Tuple[int, float]]:
        """
        Ultra-fast prediction method - straight line calculation, no bounces
        """
        # Normalize directions for stability
        if abs(dir_x) < 0.0001:
            dir_x = 0.0001 if dir_x >= 0 else -0.0001
        if abs(dir_y) < 0.0001:
            dir_y = 0.0001 if dir_y >= 0 else -0.0001

        # Target x position (AI paddle)
        collision_x = 95.0

        # Calculate time to reach paddle
        distance_x = collision_x - ball_x
        time_to_reach = distance_x / (dir_x * speed)

        if time_to_reach <= 0:
            return None

        # Calculate resulting y position (simple straight line)
        collision_y = ball_y + (dir_y * speed * time_to_reach)

        # Clamp y to game boundaries
        collision_y = max(5.0, min(95.0, collision_y))

        # Convert time to frame count
        frame_count = int(time_to_reach * GAME_FPS)

        return (frame_count, collision_y)

    def predict_collision_medium(self, ball_x: float, ball_y: float, dir_x: float, dir_y: float, speed: float) -> Optional[Tuple[int, float]]:
        """
        Medium prediction - handles up to 2 bounces
        """
        # Normalize directions for stability
        if abs(dir_x) < 0.0001:
            dir_x = 0.0001 if dir_x >= 0 else -0.0001
        if abs(dir_y) < 0.0001:
            dir_y = 0.0001 if dir_y >= 0 else -0.0001

        # Target x position (AI paddle)
        collision_x = 95.0

        # Game height boundaries
        ball_height = self.game_state.get("ball", {}).get("height", 1.0)
        top_wall = ball_height * 0.9
        bottom_wall = 100 - (ball_height * 0.9)

        # Calculate time to reach paddle (if no bounces)
        distance_x = collision_x - ball_x
        time_to_reach = distance_x / (dir_x * speed)

        if time_to_reach <= 0:
            return None

        # Calculate resulting y position
        collision_y = ball_y + (dir_y * speed * time_to_reach)

        # Check for bounces
        if collision_y < top_wall:
            # Bounced off top wall
            bounce_overshoot = top_wall - collision_y
            collision_y = top_wall + bounce_overshoot
            debug_write(f"Medium prediction: bounced off top wall")
        elif collision_y > bottom_wall:
            # Bounced off bottom wall
            bounce_overshoot = collision_y - bottom_wall
            collision_y = bottom_wall - bounce_overshoot
            debug_write(f"Medium prediction: bounced off bottom wall")

        # Check for second bounce
        if collision_y < top_wall:
            collision_y = 2 * top_wall - collision_y
            debug_write(f"Medium prediction: second bounce (top)")
        elif collision_y > bottom_wall:
            collision_y = 2 * bottom_wall - collision_y
            debug_write(f"Medium prediction: second bounce (bottom)")

        # Ensure y is within bounds
        collision_y = max(top_wall, min(bottom_wall, collision_y))

        # Convert time to frame count
        frame_count = int(time_to_reach * GAME_FPS)

        return (frame_count, collision_y)

    def get_fallback_prediction(self, ball_y: float) -> Tuple[int, float]:
        """Get fallback prediction when no collision is predicted"""
        if self.last_predicted_y is not None:
            collision_y = self.last_predicted_y
            collision_frame = max(1, self.last_predicted_frame - GAME_FPS) if self.last_predicted_frame else GAME_FPS
            debug_write(f"Using previous prediction: y={collision_y}, frame={collision_frame}")
        else:
            # Default to follow the ball's y position instead of centering
            collision_y = ball_y
            collision_frame = GAME_FPS
            debug_write(f"No prediction - tracking ball y={ball_y}")

        return (collision_frame, collision_y)

    def apply_prediction_error(self, collision_y: float) -> float:
        """Apply difficulty-based error to the prediction"""
        # Get difficulty parameters
        randomness = DIFFICULTY_CONFIGS[self.difficulty]["randomness"] * 0.5  # Reduced randomness
        error_margin = DIFFICULTY_CONFIGS[self.difficulty]["error_margin"] * 0.5  # Reduced error

        # Apply error based on difficulty
        if random.random() < randomness:
            error_amount = random.uniform(-error_margin * 5, error_margin * 5)
            collision_y += error_amount
            debug_write(f"Adding error of {error_amount} to prediction")

            # Clamp within bounds
            paddle = self.game_state.get("playerRight", {})
            paddle_size = paddle.get("paddleSize", 10.0)
            collision_y = max(paddle_size/2, min(100 - paddle_size/2, collision_y))

        return collision_y

    def simulate_ball_path(
            self,
            start_x: float,
            start_y: float,
            dir_x: float,
            dir_y: float,
            speed: float,
            collision_x: float,
            max_frames: int = None
        ) -> Optional[Tuple[int, float]]:
        """Simulate ball path to predict collision with paddle"""
        # Set max frames based on prediction accuracy
        if max_frames is None:
            # Scale frames based on accuracy: 50 frames at lowest, 200 at highest
            max_frames = 50 + (self.prediction_accuracy * 15)

        # Normalize directions for simulation stability
        if abs(dir_x) < 0.0001:
            dir_x = 0.0001 if dir_x >= 0 else -0.0001
        if abs(dir_y) < 0.0001:
            dir_y = 0.0001 if dir_y >= 0 else -0.0001

        # Get ball height for wall calculations
        ball_height = self.game_state.get("ball", {}).get("height", 1.0)
        top_wall = ball_height * 0.9
        bottom_wall = 100 - (ball_height * 0.9)

        # Calculate velocities
        vx = dir_x * speed
        vy = dir_y * speed

        # Time step (can be adjusted based on accuracy)
        dt = 1.0 / GAME_FPS

        # Simulation variables
        x = start_x
        y = start_y

        debug_write(f"Starting ball path simulation from x={x}, y={y}, vx={vx}, vy={vy}, max_frames={max_frames}")

        # Simulate frame by frame
        for frame_idx in range(max_frames):
            # Previous position
            prev_x = x
            prev_y = y

            # Move
            x += vx * dt
            y += vy * dt

            # Bounce off walls
            if y < top_wall:
                y = 2 * top_wall - y
                vy = -vy
            elif y > bottom_wall:
                y = 2 * bottom_wall - y
                vy = -vy

            # Check for collision with paddle
            if prev_x <= collision_x and x >= collision_x:
                # Interpolate y at collision
                t = (collision_x - prev_x) / (x - prev_x) if x != prev_x else 0
                collision_y = prev_y + t * (y - prev_y)

                # Clamp to boundaries
                collision_y = max(top_wall, min(bottom_wall, collision_y))

                debug_write(f"Collision predicted at frame {frame_idx}, y={collision_y}")
                return (frame_idx, collision_y)

        # Return a reasonable estimate if we're heading toward AI
        if dir_x > 0:
            estimated_frames = int((collision_x - start_x) / (vx * dt)) if vx > 0 else max_frames
            estimated_frames = max(1, min(estimated_frames, max_frames))

            # Extrapolate y position
            estimated_y = start_y + (vy * dt * estimated_frames)
            estimated_y = max(top_wall, min(bottom_wall, estimated_y))

            debug_write(f"No direct collision, but estimated at frame {estimated_frames}, y={estimated_y}")
            return (estimated_frames, estimated_y)

        # No collision found
        debug_write(f"No collision predicted within {max_frames} frames")
        return None

    def plan_movement(self, ball: Dict[str, Any], paddle: Dict[str, Any], collision_info: Optional[Tuple[int, float]]) -> Dict[str, Any]:
        """Plan paddle movement based on collision prediction"""
        if not collision_info:
            # If no collision info, follow the ball's y position
            return {
                "total_needed": ball.get("posY", 50.0) - paddle.get("paddlePos", 50.0),
                "frames_to_reach": GAME_FPS // 2,
                "collision_frame": GAME_FPS,
                "collision_y": ball.get("posY", 50.0),
                "current_pos": paddle.get("paddlePos", 50.0),
                "paddle_size": paddle.get("paddleSize", 10.0),
                "paddle_speed": paddle.get("paddleSpeed", 3.5)
            }

        # Extract collision info
        collision_frame, collision_y = collision_info

        # Get paddle info
        paddle_pos = paddle.get("paddlePos", 50.0)
        paddle_size = paddle.get("paddleSize", 10.0)
        paddle_speed = paddle.get("paddleSpeed", 3.5)

        # Calculate movement needed
        total_needed = collision_y - paddle_pos

        # Calculate frames needed to reach target
        distance = abs(total_needed)
        frames_to_travel = math.ceil(distance / paddle_speed)
        frames_to_reach = min(frames_to_travel, collision_frame)
        frames_to_reach = max(1, frames_to_reach)

        debug_write(f"Movement plan: distance={distance}, frames_needed={frames_to_reach}, target_y={collision_y}")

        # If ball moving away, track ball's y position rather than just centering
        dir_x = ball.get("directionX", 0)
        ball_x = ball.get("posX", 50.0)
        ball_y = ball.get("posY", 50.0)

        if dir_x < 0 and ball_x < 50:
            # Calculate distance to ball's y position
            follow_ball_needed = ball_y - paddle_pos

            # If significant movement needed, follow the ball
            if abs(follow_ball_needed) > 5:
                total_needed = follow_ball_needed
                frames_to_reach = GAME_FPS // 2
                debug_write(f"Ball moving away - following ball y={ball_y}")

        return {
            "total_needed": total_needed,
            "frames_to_reach": frames_to_reach,
            "collision_frame": collision_frame,
            "collision_y": collision_y,
            "current_pos": paddle_pos,
            "paddle_size": paddle_size,
            "paddle_speed": paddle_speed
        }

    def generate_action_sequence(
            self,
            paddle: Dict[str, Any],
            movement_plan: Dict[str, Any],
            powerup_decisions: Dict[str, bool]
        ) -> List[Dict[str, Any]]:
        """Generate a sequence of actions based on movement plan and powerup decisions"""
        actions = []

        # Extract movement plan
        total_needed = movement_plan["total_needed"]
        frames_to_reach = movement_plan["frames_to_reach"]
        collision_frame = movement_plan["collision_frame"]
        current_pos = movement_plan["current_pos"]
        paddle_size = movement_plan["paddle_size"]
        paddle_speed = movement_plan["paddle_speed"]

        # Extract powerup decisions
        use_big = powerup_decisions["activate_big"]
        use_speed = powerup_decisions["activate_speed"]

        # Debug movement plan
        debug_write(f"Movement plan: total={total_needed}, frames={frames_to_reach}, collision={collision_frame}")

        # Create special first action for powerups if needed
        if use_big or use_speed:
            # Determine movement for first action
            if total_needed > 0.5:
                move = "+"
                current_pos += min(paddle_speed, total_needed / frames_to_reach)
            elif total_needed < -0.5:
                move = "-"
                current_pos += max(-paddle_speed, total_needed / frames_to_reach)
            else:
                move = "0"

            # Clamp position
            current_pos = max(paddle_size/2, min(100 - paddle_size/2, current_pos))

            # Create action
            action = {
                "movePaddle": move,
                "activatePowerupBig": use_big,
                "activatePowerupSpeed": use_speed
            }

            actions.append(action)
            start_frame = 1
            debug_write(f"Action 0: move={move}, big={use_big}, speed={use_speed}")
        else:
            start_frame = 0

        # Generate remaining actions
        for frame_i in range(start_frame, GAME_FPS):
            # Determine movement - simplified to ensure clear movement
            if abs(total_needed) < 0.3 or frame_i >= frames_to_reach:
                move = "0"
            else:
                # More aggressive movement calculation
                move = "+" if total_needed > 0 else "-"

                # Calculate position change
                change = paddle_speed if move == "+" else -paddle_speed
                current_pos += change
                total_needed -= change  # Reduce remaining movement

                # Prevent overshooting
                if (move == "+" and total_needed < 0) or (move == "-" and total_needed > 0):
                    total_needed = 0

            # Clamp position
            current_pos = max(paddle_size/2, min(100 - paddle_size/2, current_pos))

            # Create action
            action = {
                "movePaddle": move,
                "activatePowerupBig": False,
                "activatePowerupSpeed": False
            }

            actions.append(action)

            # Log every few frames to avoid excessive logging
            if frame_i % 5 == 0:
                debug_write(f"Action {frame_i}: move={move}, pos={current_pos:.1f}, remaining={total_needed:.1f}")

        return actions

    def generate_fallback_actions(self) -> List[Dict[str, Any]]:
        """Generate fallback actions when planning fails"""
        actions = []

        # Get current paddle and ball positions
        paddle_pos = self.game_state.get("playerRight", {}).get("paddlePos", 50.0)
        ball_y = self.game_state.get("ball", {}).get("posY", 50.0)

        # Determine direction to move toward ball
        move_dir = "+" if ball_y > paddle_pos else "-" if ball_y < paddle_pos else "0"

        # Generate actions that track the ball
        for i in range(GAME_FPS):
            # Vary movement to avoid getting stuck
            if i % 3 == 0:
                move = move_dir
            else:
                move = "0"

            actions.append({
                "movePaddle": move,
                "activatePowerupBig": False,
                "activatePowerupSpeed": False
            })

        debug_write(f"Generated {len(actions)} fallback actions, following ball at y={ball_y}")
        return actions

    def add_actions_to_queue(self, actions: List[Dict[str, Any]]) -> None:
        """Add planned actions to the action queue"""
        for action in actions:
            if not self.action_queue.full():
                self.action_queue.put(action)

        debug_write(f"Added {len(actions)} actions to queue")
