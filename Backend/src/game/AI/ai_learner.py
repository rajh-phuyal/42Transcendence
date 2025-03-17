from typing import Dict, Any, Tuple, Optional, List, Deque
from collections import deque
import random
from .ai_utils import debugger_log, DIFFICULTY_CONFIGS, save_ai_stats_to_cache, load_ai_stats_from_cache

GLOBAL_GAME_ID = None

class CachedStatsDict(dict):
    """A dictionary that automatically saves to cache when modified"""

    def __init__(self, initial_dict, *args, **kwargs):
        super().__init__(initial_dict or {}, *args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        save_ai_stats_to_cache(GLOBAL_GAME_ID, self)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        save_ai_stats_to_cache(GLOBAL_GAME_ID, self)

class Learner:
    """
    The AI's 'intelligence' component. Analyzes game data and opponent behavior.
    """

    def __init__(self, difficulty: int = 1, game_id: str = None):
        GLOBAL_GAME_ID = game_id
        self.difficulty = difficulty
        self.config = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[1])

        raw_stats = load_ai_stats_from_cache(GLOBAL_GAME_ID) or {}
        debugger_log(f"Raw stats: {raw_stats}")
        # Define default stats
        default_stats = {
            "consecutive_goals": 0,
            "consecutive_goals_against": 0,
            "missed_balls": 0,
            "successful_intercepts": 0,
            "total_balls_faced": 0,
            "last_ball_x": 50.0,
            "last_ball_y": 50.0,
            "last_direction_x": 0,
            "success_rate": 0.5
        }

        # this is for handling constant caching
        debugger_log(f"Starting stats: {default_stats | raw_stats} for game {GLOBAL_GAME_ID}")
        self._stats = CachedStatsDict(default_stats | raw_stats)

        self.last_game_state = {}
        self.has_big_powerup = False
        self.has_speed_powerup = False

        # Opponent behavior (last N positions)
        self.max_history = 50 * (difficulty + 1)  # Store last 50 * difficulty positions
        self.opponent_positions = deque(maxlen=self.max_history)
        self.opponent_movements = deque(maxlen=self.max_history-1)  # +1/-1/0 for movement direction
        self.opponent_ball_responses = deque(maxlen=10)

        # Strategic variables
        self.big_powerup_value = 0.5
        self.speed_powerup_value = 0.5
        self.last_metrics = None

    def learn(self, game_state: Dict[str, Any]) -> None:
        """
        Update internal state and tracking based on new game state
        """
        # Track opponent behavior
        self.learn_opponent_behavior(game_state)

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

    def learn_opponent_behavior(self, game_state: Dict[str, Any]) -> None:
        """
        Learn opponent's position and movement patterns
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

        if (ball_dir_x < 0 and ball.get("posX", 50) < 50 and len(self.opponent_positions) >= 2):
            # Ball is moving toward opponent
            ball_y = ball.get("posY", 50)
            paddle_y = current_pos

            # Record if opponent is moving toward ball
            if (ball_y > paddle_y and movement > 0) or (ball_y < paddle_y and movement < 0):
                # slow opponent
                self.opponent_ball_responses.append(1)
            else:
                # fast opponent
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
            self._stats["consecutive_goals_against"] += 1
            self._stats["consecutive_goals"] = 0
            self._stats["missed_balls"] += 1
            self._stats["total_balls_faced"] += 1  # Ensure this is incremented
            debugger_log(f"AI MISSED a ball! Total misses: {self._stats['missed_balls']}, "
                        f"Total faced: {self._stats['total_balls_faced']}")

        # AI scored a point
        elif curr_score_right > last_score_right:
            self._stats["consecutive_goals"] += 1
            self._stats["consecutive_goals_against"] = 0
            debugger_log(f"AI scored! Consecutive goals: {self._stats['consecutive_goals']}")

    def detect_ball_interception(self, game_state: Dict[str, Any]) -> None:
        """
        Detect if the AI successfully intercepted the ball
        """
        curr_ball_x = game_state.get("ball", {}).get("posX", 50)
        curr_ball_dir_x = game_state.get("ball", {}).get("directionX", 0)

        # If ball direction reversed near AI paddle, count as intercept
        if (self._stats["last_direction_x"] > 0 and curr_ball_dir_x < 0 and
            self._stats["last_ball_x"] > 80):  # Reduced from 90 to catch more bounces

            # Log the values for debugging
            debugger_log(f"Ball bounce detected: last_x={self._stats['last_ball_x']}, curr_x={curr_ball_x}, "
                        f"last_dir_x={self._stats['last_direction_x']}, curr_dir_x={curr_ball_dir_x}")

            self._stats["successful_intercepts"] += 1
            debugger_log(f"AI intercepted the ball! Total intercepts: {self._stats['successful_intercepts']}, "
                        f"Total faced: {self._stats['total_balls_faced'] + 1}")

    def update_ball_tracking(self, game_state: Dict[str, Any]) -> None:
        """
        Update tracking of ball position and direction
        """
        self._stats["last_ball_x"] = game_state.get("ball", {}).get("posX", 50)
        self._stats["last_ball_y"] = game_state.get("ball", {}).get("posY", 50)
        self._stats["last_direction_x"] = game_state.get("ball", {}).get("directionX", 0)

    def update_success_rate(self) -> None:
        """
        Update total balls faced and success rate statistics
        """
        # Update total number of balls faced for success rate calculation
        self._stats["total_balls_faced"] = (
            self._stats["successful_intercepts"] + self._stats["missed_balls"]
        )

        if self._stats["total_balls_faced"] > 0:
            self._stats["success_rate"] = (
                self._stats["successful_intercepts"] / self._stats["total_balls_faced"]
            )
            debugger_log(f"Success rate: {self._stats['success_rate']:.2f}")

    def update_powerup_states(self, game_state: Dict[str, Any]) -> None:
        """
        Update tracking of powerup availability and state
        """
        player_right = game_state.get("playerRight", {})

        # Track which powerups are available - FIXED REFERENCES
        self.has_big_powerup = player_right.get("powerupBig") == "available"
        self.has_speed_powerup = player_right.get("powerupSpeed") == "available"

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
        debugger_log(f"Opponent powerup probability: {opponent_powerup_probability}")

        recommended_difficulty = self.calculate_new_difficulty()

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

        left_score = game_state.get("playerLeft", {}).get("points", 0)
        right_score = game_state.get("playerRight", {}).get("points", 0)

        # For difficulty 0 (easy), use more random/less strategic powerup decisions (probabalistic)
        if self.difficulty == 0 and right_score > 5:
            if random.random() < 0.1: # 10% chance to use powerups
                use_big = has_big and random.random() < 0.5
                use_speed = has_speed and random.random() < 0.5
                debugger_log(f"Easy difficulty: random powerup decision - big={use_big}, speed={use_speed}")
                return use_big, use_speed

        # Factor 1: Game score context
        # If we're ahead by a lot, save powerups
        if right_score > left_score + 3:
            # At easier difficulties, don't strategically save powerups as much
            if self.difficulty == 0:
                big_value -= 0.1  # Small reduction at easy
            elif self.difficulty == 1:
                big_value -= 0.2  # Medium reduction at medium
            else:
                big_value -= 0.3  # Full strategic saving at hard

            speed_value -= (0.1 * (self.difficulty + 1))  # Scale by difficulty
            debugger_log(f"Score advantage: reducing powerup value (scaled by difficulty {self.difficulty})")

        # If we're behind, be more aggressive with powerups
        elif left_score > right_score:
            # At easier difficulties, don't be as strategic about powerup usage when behind
            if self.difficulty < 2:
                big_value += 0.1 * (self.difficulty + 1)  # Scale by difficulty
                speed_value += 0.1 * (self.difficulty + 1)  # Scale by difficulty
            else:
                big_value += 0.2
                speed_value += 0.2
            debugger_log(f"Score disadvantage: increasing powerup value (scaled by difficulty {self.difficulty})")

            # If significantly behind, be even more aggressive (scaled by difficulty)
            if left_score > right_score + 2:
                big_value += 0.1 * (self.difficulty + 1)
                speed_value += 0.1 * (self.difficulty + 1)
                debugger_log(f"Significant score disadvantage: further increasing powerup value")

        # Factor 2: End game scenario (close to match point)
        if left_score >= 9 or right_score >= 9:
            # End game - use powerups more aggressively, scaled by difficulty
            big_value += 0.1 * (self.difficulty + 1)
            speed_value += 0.1 * (self.difficulty + 1)
            debugger_log(f"End game scenario: increasing powerup value")

            # Extra boost if score is close
            if abs(left_score - right_score) <= 1:
                big_value += 0.1 * (self.difficulty + 1)
                speed_value += 0.1 * (self.difficulty + 1)
                debugger_log(f"Close end game: further increasing powerup value")

        # Factor 3: Ball position and direction context
        if self.difficulty > 0:  # Only medium and hard use ball position strategically
            ball = game_state.get("ball", {})
            ball_x = ball.get("posX", 50)
            ball_dir_x = ball.get("directionX", 0)

            # Ball coming toward AI - want to use SLOW (same speed powerup)
            if ball_dir_x > 0 and 40 < ball_x < 80:
                # Middle of court, ball coming toward AI - slow effect is helpful
                speed_value += 0.1 * (self.difficulty + 1)
                debugger_log(f"Ball approaching AI: increasing speed powerup value (slow effect)")

            # Ball moving away - want to use FAST (same speed powerup)
            elif ball_dir_x < 0 and ball_x < 40:
                # Ball moving toward opponent side - fast effect is helpful
                speed_value += 0.05 * (self.difficulty + 1)
                debugger_log(f"Ball moving to opponent: increasing speed powerup value (fast effect)")

        # Factor 4: Opponent behavior analysis
        if len(self.opponent_ball_responses) >= 3 and self.difficulty == 2:
            # Only at hard difficulty does the AI analyze opponent behavior
            # Calculate how well opponent tracks the ball
            response_rate = sum(self.opponent_ball_responses) / len(self.opponent_ball_responses)

            # If opponent is good at tracking, use speed powerup more (fast effect)
            if response_rate > 0.7:
                speed_value += 0.25
                debugger_log(f"Opponent tracks well ({response_rate:.2f}): increasing speed powerup value")

            # If opponent is bad at tracking, use big paddle more
            elif response_rate < 0.4:
                big_value += 0.2
                debugger_log(f"Opponent tracks poorly ({response_rate:.2f}): increasing big powerup value")

        # Factor 5: AI performance - reduced at lower difficulties
        losing_streak_boost = 0.1 * (self.difficulty + 1)  # Scale by difficulty
        if self._stats["consecutive_goals_against"] >= 2:
            # We're on a losing streak, use powerups more aggressively
            big_value += losing_streak_boost
            speed_value += losing_streak_boost
            debugger_log(f"AI losing streak: increasing powerup values (scaled by difficulty)")

        # Make final decision
        thresholds = {
            0: 0.5,  # Easy - more likely to use powerups
            1: 0.6,  # Medium
            2: 0.7   # Hard - more strategic
        }

        use_threshold = thresholds.get(self.difficulty, 0.6)
        use_big = has_big and big_value > use_threshold
        use_speed = has_speed and speed_value > use_threshold

        debugger_log(f"Powerup decision: big_value={big_value:.2f}, speed_value={speed_value:.2f}, threshold={use_threshold}")
        debugger_log(f"Final decision: use_big={use_big}, use_speed={use_speed}")

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

        debugger_log(f"Opponent powerup usage probability: {probability:.2f}")
        return probability

    def calculate_new_difficulty(self) -> int:
        """
        Calculate recommended difficulty based on AI performance
        """
        recommended_difficulty = self.difficulty

        # If AI is doing too well, increase difficulty
        if self._stats["success_rate"] > 0.8 and self.difficulty < 2:
            recommended_difficulty = self.difficulty + 1
            debugger_log(f"AI too successful ({self._stats['success_rate']:.2f}): recommend difficulty {recommended_difficulty}")

        # If AI is struggling, decrease difficulty
        elif self._stats["success_rate"] < 0.3 and self.difficulty > 0:
            recommended_difficulty = self.difficulty - 1
            debugger_log(f"AI struggling ({self._stats['success_rate']:.2f}): recommend difficulty {recommended_difficulty}")

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

    @property
    def ai_stats(self):
        """Can access the stats as ai_stats"""
        return self._stats