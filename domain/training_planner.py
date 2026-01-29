import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

from config.trainings import TRAININGS
from domain.player import Player

MAX_SKILL_LEVEL = 400
BASE_TRAINING_GAIN = 10


@dataclass
class TrainingPlanItem:
    training_id: str
    name: str
    repeats: int
    skills: List[str] = None


class TrainingPlanner:
    def __init__(self, player: Player):
        self.player = player
        self.white_skills = set(player.white_skills)
        self.gray_skills = set(player.gray_skills)

    def plan(self, max_trainings: int = 50) -> List[TrainingPlanItem]:
        """
        Формирует план тренировок для равномерной прокачки белых навыков.
        Возвращает список TrainingPlanItem.
        """
        plan_items: Dict[str, TrainingPlanItem] = {}

        # копия, чтобы симулировать рост
        simulated_skills = self.player.skills.copy()

        for _ in range(max_trainings):
            # Находим лучшую тренировку для следующего шага
            best_training_id = self._find_best_training(simulated_skills)
            
            if best_training_id is None:
                break
                
            # Применяем тренировку к симулируемым навыкам
            self._apply_training(simulated_skills, best_training_id)
            
            # Добавляем тренировку в план
            if best_training_id in plan_items:
                plan_items[best_training_id].repeats += 1
            else:
                training_data = TRAININGS[best_training_id]
                plan_items[best_training_id] = TrainingPlanItem(
                    training_id=best_training_id,
                    name=training_data["name"],
                    repeats=1,
                    skills=training_data["skills"]
                )

        return list(plan_items.values())

    def _find_best_training(self, skills: Dict[str, int]) -> str | None:
        """
        Находит тренировку, которая лучше всего улучшит равномерность белых навыков.
        """
        # Получаем текущие значения белых навыков
        white_skill_values = {skill: skills[skill] for skill in self.white_skills}
        
        if not white_skill_values:
            return None
            
        min_white = min(white_skill_values.values())
        max_white = max(white_skill_values.values())
        
        best_training_id = None
        best_improvement = -float('inf')
        
        for tr_id, tr_data in TRAININGS.items():
            # Проверяем, есть ли белые навыки в этой тренировке
            training_white_skills = set(tr_data["skills"]) & self.white_skills
            if not training_white_skills:
                continue
                
            # Проверяем, есть ли серые навыки (чем их больше, тем хуже)
            training_gray_skills = set(tr_data["skills"]) & self.gray_skills
            
            # Симулируем применение тренировки
            simulated_after = skills.copy()
            improvement_score = self._calculate_improvement(
                simulated_after, tr_data, min_white, max_white
            )
            
            # Учитываем штраф за серые навыки
            gray_penalty = math.log(len(training_gray_skills) + 1) * 5  # вес штрафа можно настроить
            final_score = improvement_score - gray_penalty
            
            if final_score > best_improvement:
                best_improvement = final_score
                best_training_id = tr_id
        
        return best_training_id

    def _calculate_improvement(
        self, 
        skills: Dict[str, int], 
        training_data: Dict, 
        current_min: int, 
        current_max: int
    ) -> float:
        """
        Вычисляет улучшение равномерности белых навыков при применении тренировки.
        Положительное значение означает улучшение.
        """
        # Сохраняем текущие значения белых навыков до тренировки
        original_white_values = {s: skills[s] for s in self.white_skills}
        
        # Применяем тренировку
        temp_skills = skills.copy()
        self._apply_training(temp_skills, training_data)
        
        # Получаем новые значения белых навыков
        new_white_values = {s: temp_skills[s] for s in self.white_skills}
        
        # Вычисляем новую разницу между min и max белыми навыками
        new_min = min(new_white_values.values())
        new_max = max(new_white_values.values())
        
        # Улучшение = разница между старой и новой разницами
        # Если разница уменьшилась, это улучшение
        original_gap = current_max - current_min
        new_gap = new_max - new_min
        
        gap_improvement = original_gap - new_gap  # положительное значение = улучшение
        
        # Также учитываем среднее значение белых навыков (чем выше, тем лучше)
        original_avg = sum(original_white_values.values()) / len(original_white_values)
        new_avg = sum(new_white_values.values()) / len(new_white_values)
        avg_improvement = new_avg - original_avg
        
        # Комбинируем улучшения
        total_improvement = gap_improvement * 2 + avg_improvement * 0.5  # веса можно настроить
        
        return total_improvement

    def _apply_training(self, skills: Dict[str, int], training_data_or_id: Dict | str) -> None:
        """
        Применяет тренировку к переданным навыкам (влияет напрямую на переданный словарь).
        """
        if isinstance(training_data_or_id, str):
            training_data = TRAININGS[training_data_or_id]
        else:
            training_data = training_data_or_id
            
        for skill_id in training_data["skills"]:
            if skill_id in skills:
                # Увеличиваем навык с учетом максимального порога
                skills[skill_id] = min(MAX_SKILL_LEVEL, skills[skill_id] + BASE_TRAINING_GAIN)
