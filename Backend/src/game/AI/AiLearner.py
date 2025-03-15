from typing import Dict, Any, Tuple, Optional
from game.constants import GAME_FPS
from app.settings import DEBUG

from .AI import debug_write, DIFFICULTY_CONFIGS


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