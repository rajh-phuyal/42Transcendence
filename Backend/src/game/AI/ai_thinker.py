import threading
import logging
from queue import Queue, Empty
from typing import List, Dict, Any, Tuple, Optional
import time
import math
from uuid import uuid4
from game.constants import GAME_FPS, GAME_STATE
from .ai_utils import debugger_log, DIFFICULTY_CONFIGS
from .ai_learner import Learner
from .physics_engine import PhysicsEngine

class Thinker:
    """
    A background 'Thinker' that generates actions for the AI player.
    """

    def __init__(self, action_queue: Queue, difficulty: int = 1, game_id: str = None):
        """Initialize the Thinker with action queue and difficulty level"""
        self.action_queue = action_queue
        self.difficulty = difficulty

        # Ensure game_id is not None
        if game_id is None:
            game_id = str(uuid4())
            debugger_log(f"Thinker generated new game_id: {game_id}")

        self.game_id = game_id
        self.running = True
        self.waiting = True
        self.game_state: Dict[str, Any] = {}

        #  prediction state
        self.last_predicted_y = None
        self.last_predicted_frame = None
        self.last_paddle_pos = None

        # Force clear queue to ensure we don't have lingering actions
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
            except Empty:
                break

        # difficulty controlles this
        # used for the prediction accuracy
        self.prediction_accuracy = 5

        # Create the learner with proper game_id
        self.learner = Learner(difficulty=difficulty, game_id=self.game_id)

        # Start background thread
        self.thread = threading.Thread(target=self.compute_loop, daemon=True)
        self.thread.start()


    def set_prediction_accuracy(self, value: int) -> None:
        """Set the prediction accuracy level (0-10)"""
        self.prediction_accuracy = max(0, min(10, value))
        debugger_log(f"Set prediction accuracy to {self.prediction_accuracy}")

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
                time.sleep(0.05)
                continue

            try:
                if not self.game_state:
                    self.waiting = True
                    continue

                debugger_log("--- NEW PLANNING CYCLE ---")

                # learn new stuff
                self.learner.learn(self.game_state)

                # see what the learner learned
                metrics = self.learner.get_metrics(self.game_state)

                # Validate recommended difficulty (ensure it's in a valid range)
                if "recommendedDifficulty" in metrics:
                    metrics["recommendedDifficulty"] = max(0, min(2, metrics["recommendedDifficulty"]))

                debugger_log(f"Metrics: {metrics}")

                # actions for the next second
                actions = self.action_plan(self.game_state, metrics)

                # Ensure we always have some actions to perform
                if not actions:
                    debugger_log("No actions returned from planning, adding fallback movement")
                    actions = self.create_fallback_actions()

                self.add_actions_to_queue(actions)

                self.waiting = True

            except Exception as e:
                logging.error(f"Error in AI compute loop: {e}")
                debugger_log(f"ERROR in compute loop: {str(e)}")

                # Add fallback actions on error to ensure AI always moves
                fallback_actions = self.create_fallback_actions()
                self.add_actions_to_queue(fallback_actions)
                debugger_log(f"Added {len(fallback_actions)} fallback actions after error")

    def create_fallback_actions(self) -> List[Dict[str, Any]]:
        """Create fallback actions that make the paddle move"""
        actions = []

        paddle_pos = self.game_state.get("playerRight", {}).get("paddlePos", 50.0)

        for i in range(GAME_FPS):
            if i < GAME_FPS // 3:
                move = "+" if paddle_pos < 45 else ("-" if paddle_pos > 55 else "0")
            else:
                move = "+" if i % 3 == 0 else ("-" if i % 3 == 1 else "0")

            action = {
                "movePaddle": move,
                "activatePowerupBig": False,
                "activatePowerupSpeed": False
            }
            actions.append(action)

        debugger_log(f"Created {len(actions)} fallback actions with varied movements")
        return actions

    def action_plan(self, game_state: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan a sequence of actions based on game state and metrics"""
        actions = []

        try:
            # Extract game elements
            ball = game_state.get("ball", {})
            paddle = game_state.get("playerRight", {})

            # Check for major paddle position changes
            # this is for when the ai is hallucinating its paddle position (sync stuff)
            self.check_paddle_position_changes(paddle.get("paddlePos", 50.0))

            powerup_decisions = self.determine_powerup_usage(paddle, metrics)

            # Predict where ball will collide with paddle
            collision_info = self.predict_collision(ball)

            # Plan paddle movement
            movement_plan = self.plan_movement(ball, paddle, collision_info)

            # Generate actions
            actions = self.generate_action_sequence(movement_plan, powerup_decisions)
            if not actions:
                debugger_log("generate_action_sequence returned empty actions list")
                return self.create_fallback_actions()

            return actions

        except Exception as e:
            logging.error(f"Error planning actions: {e}")
            debugger_log(f"ERROR planning actions: {str(e)}")
            # Return fallback actions instead of empty list
            return self.create_fallback_actions()

    def check_paddle_position_changes(self, paddle_pos: float) -> None:
        """Check if paddle position has changed significantly"""
        if self.last_paddle_pos is not None and abs(self.last_paddle_pos - paddle_pos) > 20:
            debugger_log(f"Major paddle position change: {self.last_paddle_pos} -> {paddle_pos}")
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

        debugger_log(f"Powerup decisions: Big={activate_big}, Speed={activate_speed}, Ball toward AI={ball_coming_toward_ai}")

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
            debugger_log(f"Ball moving away (x={ball_x}, y={ball_y}) - using fallback")
            return self.get_fallback_prediction(ball_y)

        # Choose prediction method based on accuracy parameter
        if self.prediction_accuracy <= 3:
            # Fast, simple prediction (no bounces)
            collision_info = PhysicsEngine.predict_collision_simple(
                ball_x, ball_y, dir_x, dir_y, speed,
                difficulty=self.difficulty
            )
            debugger_log(f"Using SIMPLE prediction (accuracy={self.prediction_accuracy})")
        elif self.prediction_accuracy <= 7:
            # Medium accuracy prediction (limited bounces)
            collision_info = PhysicsEngine.predict_collision_medium(
                ball_x, ball_y, dir_x, dir_y, speed,
                game_state=self.game_state
            )
            debugger_log(f"Using MEDIUM prediction (accuracy={self.prediction_accuracy})")
        else:
            # Full simulation (most accurate)
            max_frames = 50 + (self.prediction_accuracy * 15)
            collision_info = PhysicsEngine.simulate_ball_path(
                start_x=ball_x,
                start_y=ball_y,
                dir_x=dir_x,
                dir_y=dir_y,
                speed=speed,
                collision_x=95.0,
                game_state=self.game_state,
                max_frames=max_frames
            )
            debugger_log(f"Using FULL simulation (accuracy={self.prediction_accuracy})")

        # Store prediction for future reference
        if collision_info:
            self.last_predicted_frame, self.last_predicted_y = collision_info
            # Apply difficulty-based error
            collision_info = (
                collision_info[0],
                PhysicsEngine.apply_prediction_error(
                    collision_info[1],
                    self.difficulty,
                    DIFFICULTY_CONFIGS[self.difficulty]
                )
            )
            debugger_log(f"Using collision prediction: frame={collision_info[0]}, y={collision_info[1]}")
        else:
            collision_info = self.get_fallback_prediction(ball_y)

        return collision_info

    def get_fallback_prediction(self, ball_y: float) -> Tuple[int, float]:
        """Get fallback prediction when no collision is predicted"""
        if self.last_predicted_y is not None:
            collision_y = self.last_predicted_y
            collision_frame = max(1, self.last_predicted_frame - GAME_FPS) if self.last_predicted_frame else GAME_FPS
            debugger_log(f"Using previous prediction: y={collision_y}, frame={collision_frame}")
        else:
            # Default to follow the ball's y position instead of centering
            collision_y = ball_y
            collision_frame = GAME_FPS
            debugger_log(f"No prediction - tracking ball y={ball_y}")

            return (collision_frame, collision_y)

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

        # For easier difficulties, intentionally give less time to reach the target
        # This makes the AI "panic" and possibly not reach the target in time
        if self.difficulty == 0:
            frames_to_travel = int(frames_to_travel * 1.5)  # Give 50% more frames (slower reaction)
            debugger_log(f"Easy difficulty: slowing paddle movement reaction time")
        elif self.difficulty == 1:
            frames_to_travel = int(frames_to_travel * 1.2)  # Give 20% more frames (slightly slower)
            debugger_log(f"Medium difficulty: slightly slowing paddle movement")

        frames_to_reach = min(frames_to_travel, collision_frame)
        frames_to_reach = max(1, frames_to_reach)

        debugger_log(f"Movement plan: distance={distance}, frames_needed={frames_to_reach}, target_y={collision_y}")

        # If ball moving away, track ball's y position rather than just centering
        dir_x = ball.get("directionX", 0)
        ball_x = ball.get("posX", 50.0)
        ball_y = ball.get("posY", 50.0)

        # At lower difficulties, sometimes just follow the ball blindly even when inappropriate
        follow_ball_threshold = 50  # Default
        if self.difficulty == 0:
            follow_ball_threshold = 70  # Easy follows ball even when far from center
        elif self.difficulty == 1:
            follow_ball_threshold = 60  # Medium is slightly better at prediction

        if dir_x < 0 and ball_x < follow_ball_threshold:
            # Calculate distance to ball's y position
            follow_ball_needed = ball_y - paddle_pos

            # If significant movement needed, follow the ball
            if abs(follow_ball_needed) > 5:
                total_needed = follow_ball_needed
                frames_to_reach = GAME_FPS // 2
                debugger_log(f"Ball moving away - following ball y={ball_y}")

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
        debugger_log(f"Movement plan: total={total_needed}, frames={frames_to_reach}, collision={collision_frame}")

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
            # this is to prevent the ai from going out of the screen
            current_pos = max(paddle_size/2, min(100 - paddle_size/2, current_pos))

            # Create action
            action = {
                "movePaddle": move,
                "activatePowerupBig": use_big,
                "activatePowerupSpeed": use_speed
            }

            actions.append(action)
            start_frame = 1
            debugger_log(f"Action 0: move={move}, big={use_big}, speed={use_speed}")
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
                debugger_log(f"Action {frame_i}: move={move}, pos={current_pos:.1f}, remaining={total_needed:.1f}")

        return actions

    def add_actions_to_queue(self, actions: List[Dict[str, Any]]) -> None:
        """Add planned actions to the action queue"""
        for action in actions:
            if not self.action_queue.full():
                self.action_queue.put(action)

        debugger_log(f"Added {len(actions)} actions to queue")
