import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

from config.trainings import TRAININGS
from domain.player import Player

MAX_SKILL_LEVEL = 400
BASE_TRAINING_GAIN = 10


def get_position_penalty_multiplier(positions: list[str]) -> float:
    """
    Returns a penalty multiplier based on player positions.
    For now, we're using a common penalty for all positions to ensure consistent behavior.
    """
    return 1.0  # Common penalty for all positions


def training_difficulty(
    skill_level: int,
    is_gray_skill: bool = False,
    position_penalty_multiplier: float = 1.0,
) -> float:
    """
    Calculate the difficulty factor for a skill based on its level.
    Higher skill levels have higher difficulty factors.
    For gray skills: up to 20 it's still manageable, but after 20 very high penalty
    """
    if is_gray_skill:
        # For gray skills, severely penalize even moderate levels to keep average under 20
        if skill_level <= 5:
            base_penalty = 10  # Much higher penalty for very low gray skills
        elif skill_level <= 10:
            base_penalty = 15  # Very high penalty after 10
        elif skill_level <= 15:
            base_penalty = 20  # Extremely high penalty after 15
        elif skill_level <= 20:
            base_penalty = 30  # Prohibitive penalty after 20
        elif skill_level <= 25:
            base_penalty = 40  # Prohibitive penalty
        elif skill_level <= 30:
            base_penalty = 50  # Prohibitive penalty
        elif skill_level <= 35:
            base_penalty = 60  # Prohibitive penalty
        elif skill_level <= 40:
            base_penalty = 70  # Prohibitive penalty
        else:
            base_penalty = 80  # Maximum penalty for high gray skills

        return base_penalty * position_penalty_multiplier
    else:
        # For white skills
        if skill_level <= 80:
            return 1.0
        elif skill_level <= 120:
            return 1.1
        elif skill_level <= 140:
            return 1.2
        elif skill_level <= 200:
            return 1.3
        elif skill_level <= 250:
            return 1.4
        else:
            return 1.5


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
        self.position_penalty_multiplier = get_position_penalty_multiplier(
            player.positions
        )

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
            best_training_id = self._find_best_training(
                simulated_skills, skill_training_counts
            )

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
                    skills=training_data["skills"],
                )

        return list(plan_items.values())

    def _find_best_training(
        self, skills: Dict[str, int], skill_training_counts: Dict[str, int]
    ) -> str | None:
        """
        Находит тренировку, которая лучше всего улучшит равномерность белых навыков.
        """
        # Получаем текущие значения белых навыков
        white_skill_values = {skill: skills[skill] for skill in self.white_skills}

        if not white_skill_values:
            return None

        # Вычисляем статистики для определения приоритетов
        sorted_white_skills = sorted(white_skill_values.items(), key=lambda x: x[1])
        min_skill_value = sorted_white_skills[0][1]
        max_skill_value = sorted_white_skills[-1][1]
        skill_gap = max_skill_value - min_skill_value

        # Вычисляем дисперсию и стандартное отклонение текущих белых навыков
        white_values_list = list(white_skill_values.values())
        mean_value = sum(white_values_list) / len(white_values_list)
        variance = sum((x - mean_value) ** 2 for x in white_values_list) / len(
            white_values_list
        )
        std_dev = variance**0.5  # стандартное отклонение

        # Определяем навыки, которые отстают, с учетом разницы между минимумом и текущим значением
        # Это позволяет лучше реагировать на отстающие навыки
        lowest_skills = []
        
        # Если разница между минимумом и другими навыками слишком велика (> 30), 
        # то включаем только самые отстающие навыки
        if skill_gap > 30:
            # Включаем только навыки, значение которых близко к минимальному (в пределах 20% от разницы)
            threshold = min_skill_value + max(10, skill_gap * 0.2)
            for skill, value in sorted_white_skills:
                if value <= threshold:
                    lowest_skills.append(skill)
        else:
            # Если разница не очень велика, выбираем навыки ниже среднего
            for skill, value in sorted_white_skills:
                if value <= mean_value:
                    lowest_skills.append(skill)
        
        # Всегда включаем самый слабый навык как приоритетный
        if sorted_white_skills and sorted_white_skills[0][0] not in lowest_skills:
            lowest_skills.insert(0, sorted_white_skills[0][0])

        best_training_id = None
        best_score = -float("inf")

        for tr_id, tr_data in TRAININGS.items():
            # Проверяем, есть ли белые навыки в этой тренировке
            training_white_skills = set(tr_data["skills"]) & self.white_skills
            if not training_white_skills:
                continue

            # Проверяем, есть ли серые навыки
            training_gray_skills = set(tr_data["skills"]) & self.gray_skills

            # Основная логика: штрафуем за серые навыки, премируем за покрытие отстающих навыков
            score = 0

            # Штраф за серые навыки - усиленный штраф, особенно для уже развитых серых навыков
            gray_penalty = 0
            for skill in training_gray_skills:
                # Чем выше значение серого навыка, тем больше штраф
                skill_level = skills[skill]
                # Используем функцию сложности для серых навыков с учетом позиционного множителя
                difficulty_factor = training_difficulty(
                    skill_level,
                    is_gray_skill=True,
                    position_penalty_multiplier=self.position_penalty_multiplier,
                )
                # Базовый штраф для серых навыков
                base_penalty = difficulty_factor * 5  # уменьшил базовый штраф, чтобы не перебарщивать
                gray_penalty += base_penalty

            # Премия за покрытие отстающих навыков - с учетом степени отставания
            low_skill_bonus = 0
            for skill in training_white_skills:
                if skill in lowest_skills:
                    # Чем больше отстает навык, тем выше премия
                    skill_value = skills[skill]
                    gap_to_max = max_skill_value - skill_value
                    # Увеличиваем премию для сильно отстающих навыков
                    # Используем квадратичную зависимость для более агрессивного преследования отстающих навыков
                    low_skill_bonus += max(0, gap_to_max) ** 1.5 * 1.5

            # Премия за покрытие разнообразных белых навыков, но с акцентом на баланс
            diversity_bonus = len(training_white_skills) * 3  # уменьшил немного

            # Премия за равномерность - тренировки, которые помогают уменьшить разрыв между навыками
            balance_bonus = 0
            if len(training_white_skills) > 1:
                # Если тренировка покрывает несколько белых навыков, особенно те, что отстают
                covered_low_skills = training_white_skills.intersection(lowest_skills)
                # Увеличиваем бонус за покрытие отстающих навыков
                balance_bonus = len(covered_low_skills) * 5.0

            # Штраф за повторное тренирование одного и того же навыка
            repetition_penalty = 0
            for skill in training_white_skills:
                if skill in skill_training_counts:
                    # Увеличиваем штраф для сильных навыков, чтобы не перекачивать их
                    skill_value = skills[skill]
                    # Штраф тем больше, чем выше уровень навыка
                    base_repetition_penalty = skill_training_counts[skill] * 3
                    # Дополнительный штраф для высоких навыков
                    if skill_value > mean_value + std_dev:  # если навык выше среднего + отклонение
                        base_repetition_penalty += (skill_value - mean_value) * 0.5
                    repetition_penalty += base_repetition_penalty

            # Более жесткий штраф за тренировки, которые усиливают уже сильные навыки
            strong_skill_penalty = 0
            for skill in training_white_skills:
                skill_value = skills[skill]
                # Если навык уже сильнее среднего, добавляем штраф
                if skill_value > mean_value + 10:  # если навык на 10+ выше среднего
                    # Чем выше навык, тем больше штраф
                    excess_amount = skill_value - mean_value
                    strong_skill_penalty += excess_amount * 0.3

            # Добавим премию за снижение ожидаемой дисперсии
            # Предскажем, как изменится дисперсия при применении этой тренировки
            temp_skills = skills.copy()
            for skill_id in tr_data["skills"]:
                if skill_id in temp_skills:
                    temp_skills[skill_id] = min(400, temp_skills[skill_id] + 10)

            new_white_values = [temp_skills[skill] for skill in self.white_skills]
            new_mean = sum(new_white_values) / len(new_white_values)
            new_variance = sum((x - new_mean) ** 2 for x in new_white_values) / len(
                new_white_values
            )

            # Проверим общий средний уровень навыков (все навыки)
            all_current_values = list(skills.values())
            current_global_avg = sum(all_current_values) / len(all_current_values)
            
            # Ограничим общий рост, особенно когда среднее превышает 180
            global_cap_penalty = 0
            if current_global_avg > 180:  # Начинаем ограничивать при среднем > 180
                excess_ratio = (current_global_avg - 180) / 20  # От 0 до 1 при достижении 200
                global_cap_penalty = gray_penalty * excess_ratio * 3.0  # Увеличенный штраф при высоком уровне

            # Если новая дисперсия будет меньше текущей, добавляем премию за уменьшение разброса
            if new_variance < variance:
                variance_reduction_bonus = (variance - new_variance) * 3.0  # увеличили множитель
                score = (
                    low_skill_bonus
                    + diversity_bonus
                    + balance_bonus
                    + variance_reduction_bonus
                    - gray_penalty
                    - repetition_penalty
                    - strong_skill_penalty
                    - global_cap_penalty
                )
            else:
                # Если дисперсия увеличивается, применяем штраф за увеличение разброса
                variance_increase_penalty = (new_variance - variance) * 2.0  # увеличили штраф
                score = (
                    low_skill_bonus
                    + diversity_bonus
                    + balance_bonus
                    - gray_penalty
                    - repetition_penalty
                    - strong_skill_penalty
                    - variance_increase_penalty
                    - global_cap_penalty
                )

            if score > best_score:
                best_score = score
                best_training_id = tr_id

        return best_training_id

    def _calculate_improvement(
        self,
        skills: Dict[str, int],
        training_data: Dict,
        current_min: int,
        current_max: int,
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
        original_variance = self._calculate_variance(
            list(original_white_values.values())
        )
        new_variance = self._calculate_variance(list(new_white_values.values()))

        # Улучшение - это уменьшение дисперсии (чем меньше дисперсия, тем равномернее навыки)
        variance_improvement = original_variance - new_variance

        # Также учитываем среднее значение белых навыков (чем выше, тем лучше)
        original_avg = sum(original_white_values.values()) / len(original_white_values)
        new_avg = sum(new_white_values.values()) / len(new_white_values)
        avg_improvement = new_avg - original_avg

        # Комбинируем улучшения
        total_improvement = (
            variance_improvement * (-10) + avg_improvement * 0.5
        )  # отрицательная дисперсия улучшает равномерность

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

    def _apply_training(
        self, skills: Dict[str, int], training_data_or_id: Dict | str
    ) -> None:
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
                skills[skill_id] = min(
                    MAX_SKILL_LEVEL, skills[skill_id] + BASE_TRAINING_GAIN
                )
