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
        
        # Словарь для отслеживания количества тренировок для каждого белого навыка
        skill_training_counts = {skill: 0 for skill in self.white_skills}

        for _ in range(max_trainings):
            # Находим лучшую тренировку для следующего шага
            best_training_id = self._find_best_training(simulated_skills, skill_training_counts)
            
            if best_training_id is None:
                break
                
            # Применяем тренировку к симулируемым навыкам
            self._apply_training(simulated_skills, best_training_id)
            
            # Обновляем счетчики тренировок для белых навыков
            training_data = TRAININGS[best_training_id]
            for skill in training_data["skills"]:
                if skill in self.white_skills:
                    skill_training_counts[skill] += 1
            
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

    def _find_best_training(self, skills: Dict[str, int], skill_training_counts: Dict[str, int]) -> str | None:
        """
        Находит тренировку, которая лучше всего улучшит равномерность белых навыков.
        """
        # Получаем текущие значения белых навыков
        white_skill_values = {skill: skills[skill] for skill in self.white_skills}
        
        if not white_skill_values:
            return None
            
        # Сначала определим, какие навыки наиболее отстают
        sorted_white_skills = sorted(white_skill_values.items(), key=lambda x: x[1])
        
        # Выберем навыки с самыми низкими значениями как приоритетные для тренировки
        lowest_skills = [skill for skill, value in sorted_white_skills[:4]]  # 4 самых слабых навыка
        
        best_training_id = None
        best_score = -float('inf')
        
        for tr_id, tr_data in TRAININGS.items():
            # Проверяем, есть ли белые навыки в этой тренировке
            training_white_skills = set(tr_data["skills"]) & self.white_skills
            if not training_white_skills:
                continue
                
            # Проверяем, есть ли серые навыки (чем их больше, тем хуже)
            training_gray_skills = set(tr_data["skills"]) & self.gray_skills
            
            # Основная логика: штрафуем за серые навыки, премируем за покрытие отстающих навыков
            score = 0
            
            # Штраф за серые навыки
            gray_penalty = len(training_gray_skills) * 20  # усиленный штраф за серые навыки
            
            # Премия за покрытие отстающих навыков
            low_skill_bonus = 0
            for skill in training_white_skills:
                if skill in lowest_skills:
                    low_skill_bonus += 15  # высокая премия за тренировку отстающих навыков
            
            # Премия за покрытие разнообразных белых навыков
            diversity_bonus = len(training_white_skills) * 3
            
            # Штраф за повторное тренирование одного и того же навыка
            repetition_penalty = 0
            for skill in training_white_skills:
                if skill in skill_training_counts:
                    repetition_penalty += skill_training_counts[skill] * 2
            
            score = low_skill_bonus + diversity_bonus - gray_penalty - repetition_penalty
            
            if score > best_score:
                best_score = score
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
        
        # Вычисляем дисперсию (разброс) белых навыков до и после тренировки
        original_variance = self._calculate_variance(list(original_white_values.values()))
        new_variance = self._calculate_variance(list(new_white_values.values()))
        
        # Улучшение - это уменьшение дисперсии (чем меньше дисперсия, тем равномернее навыки)
        variance_improvement = original_variance - new_variance
        
        # Также учитываем среднее значение белых навыков (чем выше, тем лучше)
        original_avg = sum(original_white_values.values()) / len(original_white_values)
        new_avg = sum(new_white_values.values()) / len(new_white_values)
        avg_improvement = new_avg - original_avg
        
        # Комбинируем улучшения
        total_improvement = variance_improvement * (-10) + avg_improvement * 0.5  # отрицательная дисперсия улучшает равномерность
        
        return total_improvement
    
    def _calculate_variance(self, values: List[int]) -> float:
        """
        Вычисляет дисперсию списка значений.
        """
        if len(values) <= 1:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

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
