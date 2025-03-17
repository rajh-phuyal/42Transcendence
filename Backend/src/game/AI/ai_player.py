from queue import Queue, Empty
from typing import Dict, Any
from game.constants import GAME_FPS

from .ai_utils import debugger_log, DIFFICULTY_CONFIGS
from .ai_thinker import Thinker

class AIPlayer:
    """
    Main AI used by the game loop. Owns the Thinker + action_queue.
    """

    def __init__(self, difficulty=0, game_id=None):
        self.difficulty = difficulty
        self.game_id = game_id
        self.action_queue = Queue() # main queue where moments are stored
        self.thinker = Thinker(self.action_queue, difficulty, self.game_id) # my brain
        self.thinker.set_prediction_accuracy(8 - (difficulty * 3))

        self.last_performance_check = 0
        self.action_count = 0
        self.adapt_interval = 2  # Check for adaptation every 2 frames

        # Game state tracking
        self.last_state = None
        self.last_left_score = 0
        self.last_right_score = 0

        # Initialize with neutral movement
        self.add_fallback_actions()

    def update(self, game_state: Dict[str, Any]) -> None:
        """
        Called every ~1s. Tells the AI to do a new plan.
        """
        # Update tracking data
        self.keep_track(game_state)
        self.adapt_difficulty()

        # Clear the action queue for a fresh plan,
        # this might fallback though to default actions
        while not self.action_queue.empty():
            self.action_queue.get()

        self.thinker.think(game_state)

        # Ensure we never run out of actions
        if self.action_queue.qsize() <= 2:
            self.add_fallback_actions()

    def keep_track(self, game_state: Dict[str, Any]) -> None:
        """
        Update game states
        """
        self.last_state = game_state
        self.last_left_score = game_state.get("playerLeft", {}).get("points", 0)
        self.last_right_score = game_state.get("playerRight", {}).get("points", 0)
        self.action_count += 1

    def adapt_difficulty(self) -> None:
        """
        Adapt AI difficulty based on performance and game state
        """
        if self.action_count - self.last_performance_check < self.adapt_interval:
            return
        self.last_performance_check = self.action_count

        try:
            # Get current game state information
            current_ai_points = self.last_state.get("playerRight", {}).get("points", 0)
            current_opponent_points = self.last_state.get("playerLeft", {}).get("points", 0)
            score_diff = current_ai_points - current_opponent_points

            # ai's performance metrics
            success_rate = self.thinker.learner.ai_stats.get("success_rate", 0.5)
            total_balls = self.thinker.learner.ai_stats.get("total_balls_faced", 0)
            intercepts = self.thinker.learner.ai_stats.get("successful_intercepts", 0)
            misses = self.thinker.learner.ai_stats.get("missed_balls", 0)

            base_difficulty = self.difficulty
            difficulty_float = base_difficulty

            # Game progres
            max_score = max(current_ai_points, current_opponent_points)
            game_progress = min(1.0, max_score / 10.0)  # 0-1 range for game progression
            difficulty_float += game_progress * 0.3  # Slight increase as game progresses

            # Score difference
            normalized_diff = max(-1.0, min(1.0, score_diff / 3.0))
            difficulty_float -= normalized_diff * 0.4

            # Success rate impact
            if total_balls >= 2:  # Need minimum data
                # 50% success rate = no change, 100% = +1 difficulty, 0% = -1 difficulty
                success_modifier = (success_rate - 0.5) * 2.0
                difficulty_float += success_modifier * 0.5

            # End game comeback mechanics
            if current_opponent_points >= 8 and current_ai_points <= current_opponent_points - 2:
                difficulty_float -= 0.5
            elif current_ai_points >= 8 and current_opponent_points <= current_ai_points - 2:
                difficulty_float += 0.3

            # Clamp the float difficulty between 0 and 2
            difficulty_float = max(0.0, min(2.0, difficulty_float))

            # Round to get integer difficulty level
            if difficulty_float > self.difficulty + 0.3:
                new_difficulty = min(2, self.difficulty + 1)
                debugger_log(f"Increasing difficulty to {new_difficulty} (float value: {difficulty_float:.2f})")
                self.apply_difficulty_change(new_difficulty)
            elif difficulty_float < self.difficulty - 0.3:
                new_difficulty = max(0, self.difficulty - 1)
                debugger_log(f"Decreasing difficulty to {new_difficulty} (float value: {difficulty_float:.2f})")
                self.apply_difficulty_change(new_difficulty)
            else:
                debugger_log(f"Maintaining difficulty at {self.difficulty} (float value: {difficulty_float:.2f})")

            # Prediction accuracy
            prediction_accuracy = 8 - (self.difficulty * 3)
            accuracy_adjustment = int((difficulty_float - self.difficulty) * 2)
            new_accuracy = max(0, min(10, prediction_accuracy + accuracy_adjustment))
            if new_accuracy != self.thinker.prediction_accuracy:
                self.thinker.set_prediction_accuracy(new_accuracy)
                debugger_log(f"Adjusted prediction accuracy to {new_accuracy} (based on float difficulty)")

        except Exception as e:
            debugger_log(f"Error in difficulty adaptation: {e}")

    def apply_difficulty_change(self, new_difficulty: int) -> None:
        """
        Apply difficulty change to all AI components
        """
        self.difficulty = new_difficulty
        self.thinker.difficulty = new_difficulty
        self.thinker.set_prediction_accuracy(8 - (new_difficulty * 3))
        self.thinker.learner.difficulty = new_difficulty
        self.thinker.learner.config = DIFFICULTY_CONFIGS.get(new_difficulty, DIFFICULTY_CONFIGS[1])
        debugger_log(f"Difficulty adjusted to {new_difficulty}")

    def add_fallback_actions(self) -> None:
        """
        Add fallback actions to ensure we never run out
        """
        for _ in range(max(1, GAME_FPS // 8)):
            if not self.action_queue.full():
                self.action_queue.put({
                    'movePaddle': '0',
                    'activatePowerupBig': False,
                    'activatePowerupSpeed': False
                })

    async def action(self) -> Dict[str, Any]:
        """
        Return the next action from the queue.
        If the queue is empty, returns a do-nothing fallback.
        """
        try:
            return self.action_queue.get_nowait()
        except Empty:
            self.add_fallback_actions()
            try:
                return self.action_queue.get_nowait()
            except Empty:
                # Emergency fallback
                debugger_log("Emergency fallback: action queue still empty!")
                return {
                    "movePaddle": "0",
                    "activatePowerupBig": False,
                    "activatePowerupSpeed": False
                }

    def cleanup(self) -> None:
        """
        Clean up the background thread when the game ends.
        """
        self.thinker.cleanup()
        while not self.action_queue.empty():
            self.action_queue.get()