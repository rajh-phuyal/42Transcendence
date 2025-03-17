from queue import Queue, Empty
from typing import Dict, Any
from game.constants import GAME_FPS

from .ai_utils import debugger_log, DIFFICULTY_CONFIGS
from .ai_thinker import Thinker

class AIPlayer:
    """
    Main AI used by the game loop. Owns the Thinker + action_queue.
    """

    def __init__(self, difficulty=0):
        self.difficulty = difficulty
        self.action_queue = Queue() # main queue where moments are stored
        self.thinker = Thinker(self.action_queue, difficulty) # my brain
        self.thinker.set_prediction_accuracy(8 - (difficulty * 3))

        self.last_performance_check = 0
        self.action_count = 0
        self.adapt_interval = 2  # Check for adaptation every 2 frames

        # Game state tracking
        self.last_state = None
        self.last_left_score = 0
        self.last_right_score = 0

        # Initialize with neutral movement
        self.action_queue.put({
            "movePaddle": "0",
            "activatePowerupBig": False,
            "activatePowerupSpeed": False
        })

    def update(self, game_state: Dict[str, Any]) -> None:
        """
        Called every ~1s. Tells the AI to do a new plan.
        """
        # Update tracking data
        self.update_tracking(game_state)
        self.adapt_difficulty()

        # Clear the action queue for a fresh plan,
        # this might fallback though to default actions
        while not self.action_queue.empty():
            self.action_queue.get()

        self.thinker.think(game_state)

        # Ensure we never run out of actions
        if self.action_queue.qsize() <= 2:
            self.add_fallback_actions()

    def update_tracking(self, game_state: Dict[str, Any]) -> None:
        """
        Update game states
        """
        self.last_state = game_state
        self.last_left_score = game_state.get("playerLeft", {}).get("points", 0)
        self.last_right_score = game_state.get("playerRight", {}).get("points", 0)
        self.action_count += 1

    def adapt_difficulty(self) -> None:
        """
        Adapt AI difficulty based on performance
        """
        if self.action_count - self.last_performance_check < self.adapt_interval:
            return
        self.last_performance_check = self.action_count

        try:
            # ai's performance metrics
            success_rate = self.thinker.learner.ai_stats.get("success_rate", 0.5)
            total_balls = self.thinker.learner.ai_stats.get("total_balls_faced", 0)
            intercepts = self.thinker.learner.ai_stats.get("successful_intercepts", 0)
            misses = self.thinker.learner.ai_stats.get("missed_balls", 0)

            debugger_log(f"Performance check: success_rate={success_rate:.2f}, "
                       f"total_balls={total_balls}, intercepts={intercepts}, misses={misses}")

            min_balls_required = 2 + self.difficulty
            if total_balls < min_balls_required: # not enough to go on
                debugger_log(f"Not enough data for difficulty adjustment yet. Need {min_balls_required} balls, have {total_balls}.")
                return

            # this is a bit arbitrary, but it works
            new_difficulty = self.difficulty
            if success_rate > 0.65 and self.difficulty == 0:
                new_difficulty = 1
            elif success_rate > 0.75 and self.difficulty == 1:
                new_difficulty = 2
            elif success_rate < 0.3 and self.difficulty > 0:
                new_difficulty = self.difficulty - 1

            # Apply change if needed
            if new_difficulty != self.difficulty:
                debugger_log(f"New difficulty: {new_difficulty} (success rate: {success_rate:.2f})")
                self.apply_difficulty_change(new_difficulty)

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