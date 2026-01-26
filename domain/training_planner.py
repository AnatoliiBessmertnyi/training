from typing import List, Tuple
from domain.player import Player
from config.trainings import TRAININGS

MAX_SKILL_LEVEL = 400
BASE_TRAINING_GAIN = 10


class TrainingPlanner:
    def __init__(self, player: Player):
        self.player = player
        self.white_skills = set(player.white_skills)
        self.gray_skills = set(player.gray_skills)

    def plan(self, max_cycles: int = 10) -> List[Tuple[str, str, int]]:
        """
        Формирует план тренировок для равномерной прокачки белых навыков.
        Возвращает список:
        (training_id, name, repetitions)
        """
        plan: List[Tuple[str, str, int]] = []

        # копия, чтобы симулировать рост
        skills = self.player.skills.copy()

        deficit = {
            s: MAX_SKILL_LEVEL - skills[s]
            for s in self.white_skills
        }

        max_steps = max_cycles * len(TRAININGS)

        while any(v > 0 for v in deficit.values()) and len(plan) < max_steps:
            best = None
            best_score = -1

            for tr_id, tr in TRAININGS.items():
                trained = set(tr["skills"])

                white_hits = trained & self.white_skills
                gray_hits = trained & self.gray_skills

                # 1. минимум 2 белых навыка
                if len(white_hits) < 2:
                    continue

                # 2. реально нужные белые навыки
                effective_white = [
                    s for s in white_hits if deficit.get(s, 0) > 0
                ]
                if not effective_white:
                    continue

                # 3. нелинейный потолок
                ceiling = max(skills[s] for s in white_hits)
                ceiling_multiplier = self._ceiling_multiplier(ceiling)

                # 4. полезность
                raw_gain = len(effective_white) * BASE_TRAINING_GAIN

                # 5. штраф за серые
                gray_penalty = 1 + (len(gray_hits) * 0.6)

                # 6. финальный скор
                score = (raw_gain * len(white_hits)) / (ceiling_multiplier * gray_penalty)

                if score > best_score:
                    best_score = score
                    best = (tr_id, tr)

            if not best:
                break

            tr_id, tr = best

            # применяем тренировку
            for s in tr["skills"]:
                if s in deficit and deficit[s] > 0:
                    skills[s] = min(
                        MAX_SKILL_LEVEL,
                        skills[s] + BASE_TRAINING_GAIN
                    )
                    deficit[s] = MAX_SKILL_LEVEL - skills[s]

            # агрегируем план
            if plan and plan[-1][0] == tr_id:
                plan[-1] = (plan[-1][0], plan[-1][1], plan[-1][2] + 1)
            else:
                plan.append((tr_id, tr["name"], 1))

        return plan

    @staticmethod
    def _ceiling_multiplier(value: int) -> float:
        """
        Нелинейный потолок прокачки.
        Значения легко масштабируются в будущем.
        """
        if value < 60:
            return 0.8
        if value < 100:
            return 1.0
        if value < 140:
            return 1.2
        if value < 180:
            return 1.4
        if value < 220:
            return 1.6
        if value < 260:
            return 1.8
        if value < 300:
            return 2.0
        return 2.2
