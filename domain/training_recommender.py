from typing import List, Tuple
from domain.player import Player
from config.trainings import TRAININGS

class TrainingRecommender:
    def __init__(self, player: Player, top_n: int = 3):
        self.player = player
        self.top_n = top_n
        self.target_skills = set(player.weakest_white_skills(top_n))

    def recommend(self, max_results: int = 10) -> List[Tuple[str, str, List[str], List[str]]]:
        """
        Рекомендует тренировки для прокачки слабых белых навыков.
        
        Возвращает список кортежей:
        (id тренировки, название тренировки, белые навыки, остальные навыки которые тренировка затрагивает)
        """
        recs: List[Tuple[str, str, List[str], List[str], int, int]] = []

        # Находим максимальное значение среди белых навыков
        white_values = {s: self.player.skills[s] for s in self.player.white_skills}
        max_white = max(white_values.values())

        # Определяем отставание для каждого белого навыка
        deficit = {s: max_white - val for s, val in white_values.items()}

        for tr_id, data in TRAININGS.items():
            training_skills = set(data["skills"])
            # Белые навыки, которые тренировка качает
            white_hit = training_skills & self.player.white_skills
            # Желательные: топ N слабых
            desired_hit = training_skills & self.target_skills
            # Серые навыки
            gray_hit = training_skills & self.player.gray_skills

            # Игнорируем тренировки, которые не качают ни один белый навык
            if not white_hit:
                continue

            # Суммарное отставание, которое тренировка поможет компенсировать
            gain_score = sum(deficit[s] for s in white_hit)

            recs.append((
                tr_id,
                data["name"],
                list(desired_hit),  # желательные белые навыки
                list(training_skills),  # все навыки, которые качает
                len(gray_hit),  # кол-во серых
                gain_score      # суммарная польза для белых
            ))

        # Сортировка:
        # 1) меньше серых навыков
        # 2) больше суммарного прироста по белым
        recs.sort(key=lambda x: (x[4], -x[5]))

        # Ограничиваем количество результатов
        return [(tr_id, name, desired, all_skills) for tr_id, name, desired, all_skills, gray, gain in recs[:max_results]]
