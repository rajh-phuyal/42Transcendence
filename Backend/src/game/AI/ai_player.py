from queue import Queue, Empty
from typing import Dict, Any
from game.constants import GAME_FPS
from uuid import uuid4

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

        # Pass game_id properly to the Thinker and ensure it's not None
        if self.game_id is None:
            self.game_id = str(uuid4())
            debugger_log(f"Generated new game_id: {self.game_id}")

        self.thinker = Thinker(self.action_queue, difficulty, self.game_id) # my brain
        self.thinker.set_prediction_accuracy(8 - (difficulty * 3))

        self.last_performance_check = 0
        self.action_count = 0
        self.adapt_interval = 10  # Check for adaptation every 10 frames

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
            # Check if a point was scored since last check
            point_scored = False
            if self.last_state:
                current_left_score = self.last_state.get("playerLeft", {}).get("points", 0)
                current_right_score = self.last_state.get("playerRight", {}).get("points", 0)

                # We'll track last checked scores to detect point scoring
                last_checked_scores = getattr(self, 'last_checked_scores', (0, 0))
                if (current_left_score, current_right_score) != last_checked_scores:
                    point_scored = True
                    self.last_checked_scores = (current_left_score, current_right_score)
                    debugger_log(f"Score changed to {current_left_score}-{current_right_score}")

            # Get Learner's recommended difficulty
            learner_recommendation = self.thinker.learner.get_metrics().get("recommendedDifficulty", self.difficulty)

            # Validate recommendation is in valid range (0-2)
            learner_recommendation = max(0, min(2, learner_recommendation))

            # Log the recommendation
            debugger_log(f"Learner recommended difficulty: {learner_recommendation} (current: {self.difficulty})")

            # Only apply difficulty changes when score changes and recommendation differs
            if point_scored and self.difficulty != learner_recommendation:
                self.apply_difficulty_change(learner_recommendation)
                debugger_log(f"Applied difficulty change from {self.difficulty} to {learner_recommendation}")

                # Prediction accuracy
                prediction_accuracy = 8 - (self.difficulty * 3)
                accuracy_adjustment = int((learner_recommendation - self.difficulty) * 2)
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