from typing import Dict, Any, Tuple, Optional, List
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

        # Track which type of speed powerup is available
        self.has_slow_powerup = False
        self.has_fast_powerup = False

    def update_with_game_state(self, game_state: Dict[str, Any]) -> None:
        """
        Called with each new snapshot. We store it internally and update
        any usage stats like whether the AI is currently losing or winning.
        """
        if self.last_game_state:
            self.checkForScoredPoints(game_state)
            self.detectBallInterception(game_state)
            self.updateBallTracking(game_state)

        self.updateSuccessRate()

        # Store current game state for next comparison
        self.last_game_state = game_state

    def checkForScoredPoints(self, game_state: Dict[str, Any]) -> None:
        """
        Check if points were scored since the last update and update stats accordingly.

        :param game_state: Current game state
        """
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

    def detectBallInterception(self, game_state: Dict[str, Any]) -> None:
        """
        Detect if the AI successfully intercepted the ball based on direction changes.

        :param game_state: Current game state
        """
        curr_ball_x = game_state.get("ball", {}).get("posX", 50)
        curr_ball_dir_x = game_state.get("ball", {}).get("directionX", 0)

        # If ball direction reversed near AI paddle, count as intercept
        if (self.ai_stats["last_direction_x"] > 0 and curr_ball_dir_x < 0 and
            self.ai_stats["last_ball_x"] > 90 and curr_ball_x > 90):
            self.ai_stats["successful_intercepts"] += 1
            debug_write(f"AI intercepted the ball! Total intercepts: {self.ai_stats['successful_intercepts']}")

    def updateBallTracking(self, game_state: Dict[str, Any]) -> None:
        """
        Update tracking of ball position and direction.

        :param game_state: Current game state
        """
        self.ai_stats["last_ball_x"] = game_state.get("ball", {}).get("posX", 50)
        self.ai_stats["last_ball_y"] = game_state.get("ball", {}).get("posY", 50)
        self.ai_stats["last_direction_x"] = game_state.get("ball", {}).get("directionX", 0)

    def updateSuccessRate(self) -> None:
        """
        Update total balls faced and success rate statistics.
        """
        # Update total number of balls faced for success rate calculation
        self.ai_stats["total_balls_faced"] = (
            self.ai_stats["successful_intercepts"] + self.ai_stats["missed_balls"]
        )

        if self.ai_stats["total_balls_faced"] > 0:
            self.ai_stats["success_rate"] = (
                self.ai_stats["successful_intercepts"] / self.ai_stats["total_balls_faced"]
            )

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
        use_big_available, use_speed_available = self.checkPowerupAvailability(game_state)

        # 2) Create scenarios to evaluate
        scenarios = self.createScenarios(use_big_available, use_speed_available)

        # 3) Evaluate scenarios and select the best one
        best_scenario = self.evaluateScenarios(game_state, scenarios)

        # 4) Determine recommended difficulty based on performance
        recommended_difficulty = self.calculateRecommendedDifficulty()

        # Return the dictionary the Thinker will use to plan actual actions
        return {
            "useBig": best_scenario["useBig"],
            "useSpeed": best_scenario["useSpeed"],
            "opponentPowerupProbability": 0.2,  # Stub or real logic
            "recommendedDifficulty": recommended_difficulty,
        }

    def createScenarios(self, use_big_available: bool, use_speed_available: bool) -> List[Dict[str, Any]]:
        """
        Create scenarios to evaluate for powerup usage.

        :param use_big_available: Whether big powerup is available
        :param use_speed_available: Whether speed powerup is available
        :return: List of scenarios to evaluate
        """
        scenarios = [{"name": "none", "useBig": False, "useSpeed": False}]

        if use_big_available:
            scenarios.append({"name": "big", "useBig": True, "useSpeed": False})

        if use_speed_available:
            scenarios.append({"name": "speed", "useBig": False, "useSpeed": True})

        return scenarios

    def evaluateScenarios(self, game_state: Dict[str, Any], scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate all scenarios and select the best one.

        :param game_state: Current game state
        :param scenarios: List of scenarios to evaluate
        :return: The best scenario
        """
        best_scenario = scenarios[0]  # Default to first scenario (none)
        best_scenario_score = float("-inf")

        for scn in scenarios:
            scenario_score = self.simulateScenario(game_state, scn)
            if scenario_score > best_scenario_score:
                best_scenario_score = scenario_score
                best_scenario = scn

        # Log which scenario was selected
        debug_write(f"Selected scenario: {best_scenario['name']} - useBig: {best_scenario['useBig']}, useSpeed: {best_scenario['useSpeed']}")

        return best_scenario

    def calculateRecommendedDifficulty(self) -> int:
        """
        Calculate recommended difficulty based on AI performance.

        :return: Recommended difficulty level
        """
        recommended_difficulty = self.difficulty

        # If AI is doing too well (success rate > 0.8), increase difficulty
        if self.ai_stats["success_rate"] > 0.8 and self.difficulty < 2:
            recommended_difficulty = self.difficulty + 1
            debug_write(f"AI TOO GOOD! Increasing difficulty to {recommended_difficulty}")

        # If AI is doing poorly (success rate < 0.3), decrease difficulty
        elif self.ai_stats["success_rate"] < 0.3 and self.difficulty > 0:
            recommended_difficulty = self.difficulty - 1
            debug_write(f"AI STRUGGLING! Decreasing difficulty to {recommended_difficulty}")

        return recommended_difficulty

    def checkPowerupAvailability(self, game_state: Dict[str, Any]) -> Tuple[bool, bool]:
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

    def simulateScenario(self, game_state: Dict[str, Any], scenario: Dict[str, bool]) -> float:
        """
        Forward-simulate the ball + AI paddle for up to ~2 seconds, applying the scenario's
        powerup usage (big, speed) at the start. Return a numeric score indicating whether
        we can likely intercept or not. Higher = better.

        If the ball is inbound and we have slow, we might slow the ball. If it's outbound,
        we might speed it. This is simplified logic.
        """
        # Extract the initial state
        initial_state = self.extractSimulationState(game_state, scenario)

        # Apply powerup effects to the simulation
        sim_state = self.applyPowerupEffects(initial_state, scenario)

        # Run the simulation
        intercept_success, scenario_score = self.runSimulation(sim_state)

        # Adjust score based on game context
        scenario_score = self.adjustScoreBasedOnGameContext(game_state, scenario, scenario_score)

        # Log the final scenario score to help debugging
        debug_write(f"Scenario {scenario['name']} final score: {scenario_score}")

        return scenario_score

    def extractSimulationState(self, game_state: Dict[str, Any], scenario: Dict[str, bool]) -> Dict[str, Any]:
        """
        Extract the initial state for simulation from the game state.

        :param game_state: Current game state
        :param scenario: Scenario being evaluated
        :return: Initial simulation state
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

        return {
            "ball_x": ball_x,
            "ball_y": ball_y,
            "dir_x": dir_x,
            "dir_y": dir_y,
            "speed": speed,
            "paddle_pos": paddle_pos,
            "paddle_size": paddle_size,
            "use_big": use_big,
            "use_speed": use_speed,
            "scenario_score": 0.0  # Start with a base score
        }

    def applyPowerupEffects(self, state: Dict[str, Any], scenario: Dict[str, bool]) -> Dict[str, Any]:
        """
        Apply the effects of powerups to the simulation state.

        :param state: Initial simulation state
        :param scenario: Scenario being evaluated
        :return: Updated simulation state with powerup effects
        """
        # Make a copy to avoid modifying the original
        sim_state = state.copy()

        # Boost the score if this scenario uses powerups - make AI more eager to use them
        if sim_state["use_big"]:
            sim_state["scenario_score"] += 0.3  # Bias toward using powerups when available
        if sim_state["use_speed"]:
            sim_state["scenario_score"] += 0.3  # Bias toward using powerups when available

        # If we use big
        if sim_state["use_big"]:
            # Let's assume that "big" means we instantly get a bigger paddle for the next bounce
            # Example: from 10 to 22
            sim_state["paddle_size"] = 22.0
            debug_write(f"Scenario with BIG powerup: paddle size increased to {sim_state['paddle_size']}")

        # If we use speed (the ball is inbound => slow, outbound => fast)
        if sim_state["use_speed"]:
            if sim_state["dir_x"] > 0:
                # Ball moving right => inbound for the AI => slow it
                sim_state["speed"] = 1.0
                debug_write(f"Scenario with SLOW powerup: ball speed reduced to {sim_state['speed']}")
            else:
                # Ball moving left => outbound => speed it up
                sim_state["speed"] += 2.0
                debug_write(f"Scenario with FAST powerup: ball speed increased to {sim_state['speed']}")

        return sim_state

    def runSimulation(self, state: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Run the simulation for the scenario.

        :param state: Simulation state with powerup effects applied
        :return: Tuple of (intercept_success, scenario_score)
        """
        # Extract simulation state
        ball_x = state["ball_x"]
        ball_y = state["ball_y"]
        dir_x = state["dir_x"]
        dir_y = state["dir_y"]
        speed = state["speed"]
        paddle_pos = state["paddle_pos"]
        paddle_size = state["paddle_size"]
        scenario_score = state["scenario_score"]

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

            # Move paddle in the sim: try to track the ball_y
            paddle_pos = self.simulatePaddleMovement(paddle_pos, ball_y, paddle_size)

        return intercept_success, scenario_score

    def simulatePaddleMovement(self, paddle_pos: float, ball_y: float, paddle_size: float) -> float:
        """
        Simulate paddle movement during scenario evaluation.

        :param paddle_pos: Current paddle position
        :param ball_y: Ball Y position
        :param paddle_size: Size of the paddle
        :return: Updated paddle position
        """
        # Simple approach: if paddle is above ball, move down, etc.
        if paddle_pos < ball_y - 1:
            paddle_pos += 2.0
        elif paddle_pos > ball_y + 1:
            paddle_pos -= 2.0

        # clamp paddle
        if paddle_pos < (paddle_size / 2):
            paddle_pos = paddle_size / 2
        elif paddle_pos > 100 - (paddle_size / 2):
            paddle_pos = 100 - (paddle_size / 2)

        return paddle_pos

    def adjustScoreBasedOnGameContext(self, game_state: Dict[str, Any], scenario: Dict[str, bool], scenario_score: float) -> float:
        """
        Adjust scenario score based on game context (score, critical moments).

        :param game_state: Current game state
        :param scenario: Scenario being evaluated
        :param scenario_score: Current scenario score
        :return: Adjusted scenario score
        """
        use_big = scenario.get("useBig", False)
        use_speed = scenario.get("useSpeed", False)

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

        return scenario_score