from typing import List, Tuple
from domain.player import Player
from config.trainings import TRAININGS

MAX_SKILL_LEVEL = 400
TRAINING_GAIN = 10  # фиксированный прирост за тренировку


class TrainingPlanner:
    def __init__(self, player: Player):
        self.player = player

    def plan(self, max_cycles: int = 10) -> List[Tuple[str, str, int]]:
        """
        Формирует план тренировок для балансировки всех белых навыков.

        Возвращает список кортежей:
        (id тренировки, name, количество повторений)
        """
        plan: List[Tuple[str, str, int]] = []

        player_skills = self.player.skills.copy()
        white_skills = self.player.white_skills
        gray_skills = self.player.gray_skills
        trainings = TRAININGS

        # Сколько нужно добрать до капа по каждому белому навыку
        deficit = {s: MAX_SKILL_LEVEL - player_skills[s] for s in white_skills}

        while (
            any(deficit[s] > 0 for s in white_skills)
            and len(plan) < max_cycles * len(trainings)
        ):
            best_training = None
            best_score = -1
            best_gray_hits = float("inf")

            for tr_id, data in trainings.items():
                tr_skills = set(data["skills"])

                white_hit = tr_skills & white_skills
                if not white_hit:
                    continue

                # Сколько реально нужных белых навыков качает
                effective_white_hits = sum(
                    1 for s in white_hit if deficit[s] > 0
                )
                if effective_white_hits == 0:
                    continue

                # Потолок тренировки — самый высокий белый навык в её списке
                training_ceiling = max(
                    player_skills[s] for s in white_hit
                )

                # Эффективность тренировки
                score = effective_white_hits / training_ceiling

                gray_hit = tr_skills & gray_skills

                if (
                    score > best_score
                    or (score == best_score and len(gray_hit) < best_gray_hits)
                ):
                    best_training = (tr_id, data)
                    best_score = score
                    best_gray_hits = len(gray_hit)

            if not best_training:
                break

            tr_id, data = best_training

            # Симулируем применение тренировки
            for s in data["skills"]:
                if s in deficit and deficit[s] > 0:
                    player_skills[s] = min(
                        MAX_SKILL_LEVEL,
                        player_skills[s] + TRAINING_GAIN,
                    )
                    deficit[s] = MAX_SKILL_LEVEL - player_skills[s]

            # Склеиваем одинаковые тренировки подряд
            if plan and plan[-1][0] == tr_id:
                plan[-1] = (plan[-1][0], plan[-1][1], plan[-1][2] + 1)
            else:
                plan.append((tr_id, data["name"], 1))

        return plan
