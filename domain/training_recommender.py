from typing import List, Tuple

from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner


class TrainingRecommender:
    def __init__(self, player: Player, top_n: int = 3):
        self.player = player
        self.top_n = top_n
        self.target_skills = set(player.weakest_white_skills(top_n))

    def build_balanced_plan(self, total_sessions: int = 10):
        """
        Builds a balanced training plan for the player.

        Args:
            total_sessions: Number of training sessions to plan

        Returns:
            A list of training recommendations
        """
        planner = TrainingPlanner(self.player)
        return planner.plan(max_trainings=total_sessions)
