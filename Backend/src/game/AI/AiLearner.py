from typing import Dict, Any, Tuple, Optional, List, Deque
from collections import deque
import random
import math
from game.constants import GAME_FPS
from app.settings import DEBUG

from .AI import debug_write, DIFFICULTY_CONFIGS


class Learner:
    """
    The AI's 'intelligence' component. Analyzes game data and opponent behavior
    to make strategic decisions about powerup usage and other gameplay elements.
    """

    def __init__(self, difficulty: int = 1):
        """
        Initialize the Learner with the specified difficulty level
        """
        self.difficulty = difficulty
        self.config = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[1])

        # Performance stats
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

        # Game state tracking
        self.last_game_state = {}

        # Powerup state tracking
        self.has_big_powerup = False
        self.has_speed_powerup = False

        # Opponent behavior tracking (last N positions)
        self.max_history = 50  # Store last 50 positions
        self.opponent_positions = deque(maxlen=self.max_history)
        self.opponent_movements = deque(maxlen=self.max_history-1)  # +1/-1/0 for movement direction
        self.opponent_ball_responses = deque(maxlen=10)  # How opponent responds to ball approaches

        # Strategic variables
        self.big_powerup_value = 0.5  # Base value of using big powerup
        self.speed_powerup_value = 0.5  # Base value of using speed powerup
        self.last_metrics = None  # Store last computed metrics

    def update_with_game_state(self, game_state: Dict[str, Any]) -> None:
        """
        Update internal state and tracking based on new game state
        """
        # Track opponent behavior
        self.track_opponent_behavior(game_state)

        # Update performance stats
        if self.last_game_state:
            self.check_for_scored_points(game_state)
            self.detect_ball_interception(game_state)
            self.update_ball_tracking(game_state)

        # Update success rate
        self.update_success_rate()

        # Update powerup state tracking
        self.update_powerup_states(game_state)

        # Store current game state for next comparison
        self.last_game_state = game_state

    def track_opponent_behavior(self, game_state: Dict[str, Any]) -> None:
        """
        Track opponent's position and movement patterns
        """
        # Get current opponent position
        opponent = game_state.get("playerLeft", {})
        current_pos = opponent.get("paddlePos", 50.0)

        # Add to position history
        self.opponent_positions.append(current_pos)

        # Calculate movement direction if we have previous positions
        if len(self.opponent_positions) >= 2:
            prev_pos = self.opponent_positions[-2]
            # Determine movement direction: +1 (down), -1 (up), 0 (static)
            movement = 0
            if current_pos > prev_pos + 0.5:  # Moving down
                movement = 1
            elif current_pos < prev_pos - 0.5:  # Moving up
                movement = -1
            self.opponent_movements.append(movement)

        # Track how opponent responds to ball approaches
        ball = game_state.get("ball", {})
        ball_dir_x = ball.get("directionX", 0)

        if (ball_dir_x < 0 and ball.get("posX", 50) < 50 and
            len(self.opponent_positions) >= 2):
            # Ball is moving toward opponent
            ball_y = ball.get("posY", 50)
            paddle_y = current_pos
            prev_paddle_y = self.opponent_positions[-2]

            # Record if opponent is moving toward ball
            if (ball_y > paddle_y and movement > 0) or (ball_y < paddle_y and movement < 0):
                # Opponent is tracking ball
                self.opponent_ball_responses.append(1)
            else:
                # Opponent not tracking ball well
                self.opponent_ball_responses.append(0)

    def check_for_scored_points(self, game_state: Dict[str, Any]) -> None:
        """
        Check if points were scored since the last update
        """
        last_score_left = self.last_game_state.get("playerLeft", {}).get("points", 0)
        last_score_right = self.last_game_state.get("playerRight", {}).get("points", 0)

        curr_score_left = game_state.get("playerLeft", {}).get("points", 0)
        curr_score_right = game_state.get("playerRight", {}).get("points", 0)

        # Point scored against AI
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

    def detect_ball_interception(self, game_state: Dict[str, Any]) -> None:
        """
        Detect if the AI successfully intercepted the ball
        """
        curr_ball_x = game_state.get("ball", {}).get("posX", 50)
        curr_ball_dir_x = game_state.get("ball", {}).get("directionX", 0)

        # If ball direction reversed near AI paddle, count as intercept
        if (self.ai_stats["last_direction_x"] > 0 and curr_ball_dir_x < 0 and
            self.ai_stats["last_ball_x"] > 90 and curr_ball_x > 90):
            self.ai_stats["successful_intercepts"] += 1
            debug_write(f"AI intercepted the ball! Total intercepts: {self.ai_stats['successful_intercepts']}")

    def update_ball_tracking(self, game_state: Dict[str, Any]) -> None:
        """
        Update tracking of ball position and direction
        """
        self.ai_stats["last_ball_x"] = game_state.get("ball", {}).get("posX", 50)
        self.ai_stats["last_ball_y"] = game_state.get("ball", {}).get("posY", 50)
        self.ai_stats["last_direction_x"] = game_state.get("ball", {}).get("directionX", 0)

    def update_success_rate(self) -> None:
        """
        Update total balls faced and success rate statistics
        """
        # Update total number of balls faced for success rate calculation
        self.ai_stats["total_balls_faced"] = (
            self.ai_stats["successful_intercepts"] + self.ai_stats["missed_balls"]
        )

        if self.ai_stats["total_balls_faced"] > 0:
            self.ai_stats["success_rate"] = (
                self.ai_stats["successful_intercepts"] / self.ai_stats["total_balls_faced"]
            )

    def update_powerup_states(self, game_state: Dict[str, Any]) -> None:
        """
        Update tracking of powerup availability and state
        """
        player_right = game_state.get("playerRight", {})

        # Track which powerups are available - FIXED REFERENCES
        self.has_big_powerup = player_right.get("powerupBig") == "available"
        self.has_speed_powerup = player_right.get("powerupSpeed") == "available"

        # Count usage if a powerup was used
        if player_right.get("powerupBig") == "used" or player_right.get("powerupSpeed") == "used":
            self.ai_stats["power_ups_used"] += 1

    def get_metrics(self, game_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate metrics and strategic decisions based on game state and opponent behavior
        """
        if game_state is None:
            game_state = self.last_game_state

        # Calculate recommended powerup usage
        use_big, use_speed = self.calculate_powerup_strategy(game_state)

        # Calculate opponent powerup probability (chance they'll use a powerup soon)
        opponent_powerup_probability = self.predict_opponent_powerup_usage(game_state)

        # Determine recommended difficulty
        recommended_difficulty = self.calculate_recommended_difficulty()

        # Store metrics for future reference
        metrics = {
            "useBig": use_big,
            "useSpeed": use_speed,
            "opponentPowerupProbability": opponent_powerup_probability,
            "recommendedDifficulty": recommended_difficulty,
        }

        self.last_metrics = metrics
        return metrics

    def calculate_powerup_strategy(self, game_state: Dict[str, Any]) -> Tuple[bool, bool]:
        """
        Determine strategic powerup usage based on game state and opponent behavior
        """
        # Start with base values
        big_value = self.big_powerup_value
        speed_value = self.speed_powerup_value

        # Check if powerups are even available
        player_right = game_state.get("playerRight", {})
        has_big = player_right.get("powerupBig") == "available"
        has_speed = player_right.get("powerupSpeed") == "available"

        if not has_big and not has_speed:
            return False, False

        # Factor 1: Game score context
        left_score = game_state.get("playerLeft", {}).get("points", 0)
        right_score = game_state.get("playerRight", {}).get("points", 0)

        # If we're ahead by a lot, save powerups
        if right_score > left_score + 3:
            big_value -= 0.3
            speed_value -= 0.3
            debug_write("Score advantage: reducing powerup value")

        # If we're behind, be more aggressive with powerups
        elif left_score > right_score:
            big_value += 0.2
            speed_value += 0.2
            debug_write("Score disadvantage: increasing powerup value")

            # If significantly behind, be even more aggressive
            if left_score > right_score + 2:
                big_value += 0.2
                speed_value += 0.2
                debug_write("Significant score disadvantage: further increasing powerup value")

        # Factor 2: End game scenario (close to match point)
        if left_score >= 9 or right_score >= 9:
            # End game - use powerups more aggressively
            big_value += 0.3
            speed_value += 0.3
            debug_write("End game scenario: increasing powerup value")

            # Extra boost if score is close
            if abs(left_score - right_score) <= 1:
                big_value += 0.2
                speed_value += 0.2
                debug_write("Close end game: further increasing powerup value")

        # Factor 3: Ball position and direction context
        ball = game_state.get("ball", {})
        ball_x = ball.get("posX", 50)
        ball_dir_x = ball.get("directionX", 0)

        # Ball coming toward AI - want to use SLOW (same speed powerup)
        if ball_dir_x > 0 and 40 < ball_x < 80:
            # Middle of court, ball coming toward AI - slow effect is helpful
            speed_value += 0.2
            debug_write("Ball approaching AI: increasing speed powerup value (slow effect)")

        # Ball moving away - want to use FAST (same speed powerup)
        elif ball_dir_x < 0 and ball_x < 40:
            # Ball moving toward opponent side - fast effect is helpful
            speed_value += 0.15
            debug_write("Ball moving to opponent: increasing speed powerup value (fast effect)")

        # Factor 4: Opponent behavior analysis
        if len(self.opponent_ball_responses) >= 3:
            # Calculate how well opponent tracks the ball
            response_rate = sum(self.opponent_ball_responses) / len(self.opponent_ball_responses)

            # If opponent is good at tracking, use speed powerup more (fast effect)
            if response_rate > 0.7:
                speed_value += 0.25
                debug_write(f"Opponent tracks well ({response_rate:.2f}): increasing speed powerup value")

            # If opponent is bad at tracking, use big paddle more
            elif response_rate < 0.4:
                big_value += 0.2
                debug_write(f"Opponent tracks poorly ({response_rate:.2f}): increasing big powerup value")

        # Factor 5: AI performance
        if self.ai_stats["consecutive_goals_against"] >= 2:
            # We're on a losing streak, use powerups more aggressively
            big_value += 0.2
            speed_value += 0.2
            debug_write("AI losing streak: increasing powerup values")

        # Make final decision (threshold-based)
        use_big = has_big and big_value > 0.7
        use_speed = has_speed and speed_value > 0.7

        debug_write(f"Powerup decision: big_value={big_value:.2f}, speed_value={speed_value:.2f}")
        debug_write(f"Final decision: use_big={use_big}, use_speed={use_speed}")

        return use_big, use_speed

    def predict_opponent_powerup_usage(self, game_state: Dict[str, Any]) -> float:
        """
        Predict the probability that the opponent will use a powerup soon
        """
        # Check if opponent has powerups available
        opponent = game_state.get("playerLeft", {})
        has_big = opponent.get("powerupBig") == "available"
        has_speed = opponent.get("powerupSpeed") == "available"

        if not has_big and not has_speed:
            return 0.0

        # Base probability
        probability = 0.2

        # Adjust based on game context
        left_score = game_state.get("playerLeft", {}).get("points", 0)
        right_score = game_state.get("playerRight", {}).get("points", 0)

        # More likely if behind
        if left_score < right_score:
            probability += 0.2

        # More likely in end game
        if left_score >= 9 or right_score >= 9:
            probability += 0.3

        # More likely if ball moving toward them
        ball = game_state.get("ball", {})
        ball_dir_x = ball.get("directionX", 0)
        if ball_dir_x < 0:
            probability += 0.1

        # Cap probability
        probability = min(0.9, probability)

        debug_write(f"Opponent powerup usage probability: {probability:.2f}")
        return probability

    def calculate_recommended_difficulty(self) -> int:
        """
        Calculate recommended difficulty based on AI performance
        """
        recommended_difficulty = self.difficulty

        # If AI is doing too well, increase difficulty
        if self.ai_stats["success_rate"] > 0.8 and self.difficulty < 2:
            recommended_difficulty = self.difficulty + 1
            debug_write(f"AI too successful ({self.ai_stats['success_rate']:.2f}): recommend difficulty {recommended_difficulty}")

        # If AI is struggling, decrease difficulty
        elif self.ai_stats["success_rate"] < 0.3 and self.difficulty > 0:
            recommended_difficulty = self.difficulty - 1
            debug_write(f"AI struggling ({self.ai_stats['success_rate']:.2f}): recommend difficulty {recommended_difficulty}")

        return recommended_difficulty

    def analyze_opponent_patterns(self) -> Dict[str, Any]:
        """
        Analyze opponent's movement patterns to detect strategy
        """
        if len(self.opponent_movements) < 10:
            return {"pattern": "unknown", "confidence": 0.0}

        # Count different movement types
        up_movements = self.opponent_movements.count(-1)
        down_movements = self.opponent_movements.count(1)
        static_movements = self.opponent_movements.count(0)
        total_movements = len(self.opponent_movements)

        # Calculate percentages
        up_percent = up_movements / total_movements
        down_percent = down_movements / total_movements
        static_percent = static_movements / total_movements

        # Determine dominant pattern
        pattern = "balanced"
        confidence = 0.5

        if static_percent > 0.6:
            pattern = "camper"  # Opponent doesn't move much
            confidence = static_percent
        elif up_percent > 0.4 and down_percent > 0.4:
            pattern = "sweeper"  # Opponent moves a lot both directions
            confidence = (up_percent + down_percent) / 2

        # Check if opponent prefers a court position
        positions = list(self.opponent_positions)
        avg_position = sum(positions) / len(positions)

        position_bias = "middle"
        if avg_position < 40:
            position_bias = "top"
        elif avg_position > 60:
            position_bias = "bottom"

        return {
            "pattern": pattern,
            "confidence": confidence,
            "position_bias": position_bias,
            "avg_position": avg_position
        }