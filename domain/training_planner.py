from collections import defaultdict
from copy import deepcopy

from config.trainings import TRAININGS
from domain.training_simulator import simulate_training
from domain.balance_metric import white_balance_score


class TrainingPlanner:
    def __init__(
        self,
        player,
        max_steps: int = 50,
        gray_penalty: int = 3,
    ):
        self.player = player
        self.max_steps = max_steps
        self.gray_penalty = gray_penalty

    def build_plan(self) -> dict[str, int]:
        """
        Возвращает:
        {
            training_id: repeats_count
        }
        """

        current_skills = deepcopy(self.player.skills)
        white_skills = self.player.white_skills
        gray_skills = self.player.gray_skills

        plan: dict[str, int] = defaultdict(int)

        for _ in range(self.max_steps):
            current_balance = white_balance_score(
                current_skills, white_skills
            )

            best_training_id = None
            best_score = current_balance

            for tr_id, tr_data in TRAININGS.items():
                tr_skills = set(tr_data["skills"])

                # игнорируем тренировки, которые не качают белые навыки
                if not (tr_skills & white_skills):
                    continue

                simulated = simulate_training(current_skills, tr_id)

                new_balance = white_balance_score(
                    simulated, white_skills
                )

                # штраф за серые навыки
                gray_hits = len(tr_skills & gray_skills)
                total_score = new_balance + gray_hits * self.gray_penalty

                if total_score < best_score:
                    best_score = total_score
                    best_training_id = tr_id

            # если улучшить баланс больше нельзя — выходим
            if best_training_id is None:
                break

            # применяем лучшую тренировку
            current_skills = simulate_training(
                current_skills, best_training_id
            )
            plan[best_training_id] += 1

        return dict(plan)
