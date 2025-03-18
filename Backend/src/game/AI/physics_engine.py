"""
Ball physics simulation for the Pong AI.
Handles prediction of ball trajectories and collisions.
"""

import random
from typing import Dict, Any, Tuple, Optional
from game.constants import GAME_FPS
from .ai_utils import debugger_log

class PhysicsEngine:
    """
    Provides physics-based ball trajectory prediction with different accuracy levels.
    """

    @staticmethod
    def predict_collision_simple(
            ball_x: float, ball_y: float,
            dir_x: float, dir_y: float,
            speed: float,
            collision_x: float = 95.0,
            difficulty: int = 0) -> Optional[Tuple[int, float]]:
        """
        Ultra-fast prediction method - straight line calculation, no bounces
        """
        if abs(dir_x) < 0.0001:
            dir_x = 0.0001 if dir_x >= 0 else -0.0001
        if abs(dir_y) < 0.0001:
            dir_y = 0.0001 if dir_y >= 0 else -0.0001

        distance_x = collision_x - ball_x
        time_to_reach = distance_x / (dir_x * speed)

        if time_to_reach <= 0:
            return None

        # Calculate resulting y position (simple straight line)
        collision_y = ball_y + (dir_y * speed * time_to_reach)

        if difficulty == 0:
            # Add a consistent bias based on direction
            if dir_y > 0:
                collision_y += 10  # Consistently overshoot downward balls
            else:
                collision_y -= 10  # Consistently undershoot upward balls
            debugger_log(f"Added systematic error for easy difficulty")

        collision_y = max(5.0, min(95.0, collision_y))

        # Convert time to frame count
        frame_count = int(time_to_reach * GAME_FPS)

        return (frame_count, collision_y)

    @staticmethod
    def predict_collision_medium(
            ball_x: float, ball_y: float,
            dir_x: float, dir_y: float,
            speed: float,
            game_state: Dict[str, Any] = None,
            collision_x: float = 95.0) -> Optional[Tuple[int, float]]:
        """
        Medium prediction - handles up to 2 bounces
        """
        if abs(dir_x) < 0.0001:
            dir_x = 0.0001 if dir_x >= 0 else -0.0001
        if abs(dir_y) < 0.0001:
            dir_y = 0.0001 if dir_y >= 0 else -0.0001

        ball_height = 1.0
        if game_state and 'ball' in game_state:
            ball_height = game_state.get("ball", {}).get("height", 1.0)

        top_wall = ball_height * 0.9
        bottom_wall = 100 - (ball_height * 0.9)

        # Calculate time to reach paddle (if no bounces)
        distance_x = collision_x - ball_x
        time_to_reach = distance_x / (dir_x * speed)

        if time_to_reach <= 0:
            return None

        # Calculate resulting y position
        collision_y = ball_y + (dir_y * speed * time_to_reach)

        if collision_y < top_wall:
            bounce_overshoot = top_wall - collision_y
            collision_y = top_wall + bounce_overshoot
            debugger_log(f"Medium prediction: bounced off top wall")
        elif collision_y > bottom_wall:
            bounce_overshoot = collision_y - bottom_wall
            collision_y = bottom_wall - bounce_overshoot
            debugger_log(f"Medium prediction: bounced off bottom wall")

        if collision_y < top_wall:
            collision_y = 2 * top_wall - collision_y
            debugger_log(f"Medium prediction: second bounce (top)")
        elif collision_y > bottom_wall:
            collision_y = 2 * bottom_wall - collision_y
            debugger_log(f"Medium prediction: second bounce (bottom)")

        # Ensure y is within bounds
        collision_y = max(top_wall, min(bottom_wall, collision_y))

        frame_count = int(time_to_reach * GAME_FPS)

        return (frame_count, collision_y)

    @staticmethod
    def simulate_ball_path(
            start_x: float,
            start_y: float,
            dir_x: float,
            dir_y: float,
            speed: float,
            collision_x: float = 95.0,
            game_state: Dict[str, Any] = None,
            max_frames: int = 200) -> Optional[Tuple[int, float]]:
        """
        Simulate ball path to predict collision with paddle
        """
        if abs(dir_x) < 0.0001:
            dir_x = 0.0001 if dir_x >= 0 else -0.0001
        if abs(dir_y) < 0.0001:
            dir_y = 0.0001 if dir_y >= 0 else -0.0001

        ball_height = 1.0
        if game_state and 'ball' in game_state:
            ball_height = game_state.get("ball", {}).get("height", 1.0)

        top_wall = ball_height * 0.9
        bottom_wall = 100 - (ball_height * 0.9)

        # Calculate velocities of the ball in the current frame
        vx = dir_x * speed
        vy = dir_y * speed

        # Time step (can be adjusted based on accuracy)
        dt = 1.0 / GAME_FPS

        # Simulation variables
        x = start_x
        y = start_y

        debugger_log(f"Starting ball path simulation from x={x}, y={y}, vx={vx}, vy={vy}, max_frames={max_frames}")

        # Simulate frame by frame
        for frame_idx in range(max_frames):
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

            if prev_x <= collision_x and x >= collision_x:
                t = (collision_x - prev_x) / (x - prev_x) if x != prev_x else 0
                collision_y = prev_y + t * (y - prev_y)

                # Clamp to boundaries
                collision_y = max(top_wall, min(bottom_wall, collision_y))

                debugger_log(f"Collision predicted at frame {frame_idx}, y={collision_y}")
                return (frame_idx, collision_y)

        # Return a reasonable estimate if we're heading toward AI
        if dir_x > 0:
            estimated_frames = int((collision_x - start_x) / (vx * dt)) if vx > 0 else max_frames
            estimated_frames = max(1, min(estimated_frames, max_frames))

            # Extrapolate y position
            estimated_y = start_y + (vy * dt * estimated_frames)
            estimated_y = max(top_wall, min(bottom_wall, estimated_y))

            debugger_log(f"No direct collision, but estimated at frame {estimated_frames}, y={estimated_y}")
            return (estimated_frames, estimated_y)

        # No collision found
        debugger_log(f"No collision predicted within {max_frames} frames")
        return None

    @staticmethod
    def apply_prediction_error(collision_y: float, difficulty: int, config: Dict[str, Any]) -> float:
        """
        Apply difficulty-based error to the prediction
        """
        randomness = config.get("randomness", 0.2)
        error_margin = config.get("error_margin", 5.0)

        if random.random() < randomness:
            error_amount = random.uniform(-error_margin, error_margin)
            collision_y += error_amount
            debugger_log(f"Adding error of {error_amount:.2f} to prediction (difficulty {difficulty})")

            collision_y = max(5.0, min(95.0, collision_y))

        return collision_y