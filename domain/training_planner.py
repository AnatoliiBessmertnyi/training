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
        trainings = TRAININGS

        # Определяем сколько раз нужно качать каждый белый навык до 400
        deficit = {s: MAX_SKILL_LEVEL - player_skills[s] for s in white_skills}

        # Простой greedy-подход:
        # На каждом шаге выбираем тренировку, которая качает максимальное количество
        # белых навыков с текущим отставанием и минимально затрагивает серые
        while any(deficit[s] > 0 for s in white_skills) and len(plan) < max_cycles * len(trainings):
            best_training = None
            best_white_hits = 0
            best_gray_hits = float('inf')
            for tr_id, data in trainings.items():
                tr_skills = set(data["skills"])
                white_hit = tr_skills & white_skills
                gray_hit = tr_skills & self.player.gray_skills

                # считаем сколько навыков реально нужно качать (только те, что ниже MAX_SKILL_LEVEL)
                effective_white_hits = sum(1 for s in white_hit if deficit[s] > 0)

                if effective_white_hits == 0:
                    continue  # не качает нужных навыков

                # Выбираем тренировку с максимальным полезным эффектом, минимально трогая серые
                if (effective_white_hits > best_white_hits) or \
                   (effective_white_hits == best_white_hits and len(gray_hit) < best_gray_hits):
                    best_training = (tr_id, data)
                    best_white_hits = effective_white_hits
                    best_gray_hits = len(gray_hit)

            if not best_training:
                break  # нет подходящих тренировок

            tr_id, data = best_training

            # Применяем тренировку (симуляция)
            for s in data["skills"]:
                if s in deficit:
                    player_skills[s] = min(MAX_SKILL_LEVEL, player_skills[s] + TRAINING_GAIN)
                    deficit[s] = MAX_SKILL_LEVEL - player_skills[s]

            # Добавляем в план
            if plan and plan[-1][0] == tr_id:
                # увеличиваем счетчик повторений
                plan[-1] = (plan[-1][0], plan[-1][1], plan[-1][2] + 1)
            else:
                plan.append((tr_id, data["name"], 1))

        return plan
