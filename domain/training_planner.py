import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

from config.trainings import TRAININGS
from domain.player import Player

MAX_SKILL_LEVEL = 400
BASE_TRAINING_GAIN = 10


def training_difficulty(
    skill_level: int,
    is_gray_skill: bool = False,
) -> float:
    """
    Calculate the difficulty factor for a skill based on its level.
    Higher skill levels have higher difficulty factors.
    For gray skills: up to 20 it's still manageable, but after 20 very high penalty
    """
    if is_gray_skill:
        # For gray skills, up to 20 it's still manageable, after 20 increasingly high penalty
        if skill_level <= 5:
            base_penalty = 3  # Low penalty for very low gray skills
        elif skill_level <= 10:
            base_penalty = 4  # High penalty after 20
        elif skill_level <= 15:
            base_penalty = 5  # High penalty after 20
        elif skill_level <= 20:
            base_penalty = 6  # Very high penalty
        elif skill_level <= 25:
            base_penalty = 7  # Very high penalty
        elif skill_level <= 30:
            base_penalty = 8  # Very high penalty
        elif skill_level <= 35:
            base_penalty = 9 # Very high penalty
        elif skill_level <= 40:
            base_penalty = 10  # Very high penalty
        else:
            base_penalty = 11  # Maximum penalty for high gray skills

        return base_penalty
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

        # Определяем навыки, которые отстают, на основе абсолютной разницы и процентного соотношения
        # Чем больше разница между минимумом и максимумом, тем больше приоритет у отстающих навыков
        threshold_for_low_skills = min_skill_value + (
            skill_gap * 0.4
        )  # увеличим порог для большего охвата отстающих навыков

        lowest_skills = []
        for skill, value in sorted_white_skills:
            if value <= threshold_for_low_skills:
                lowest_skills.append(skill)

        # Если разрыв маленький, то используем другой подход - фокус на уменьшении разницы
        if skill_gap < 25 and len(sorted_white_skills) > 1:
            # Когда навыки уже близки, нужно фокусироваться на самых отстающих
            target_range = min(
                3, len(sorted_white_skills)
            )  # количество отстающих навыков для фокуса
            lowest_skills = [
                skill for skill, value in sorted_white_skills[:target_range]
            ]

        best_training_id = None
        best_score = -float("inf")

        for tr_id, tr_data in TRAININGS.items():
            # Проверяем, есть ли белые навыки в этой тренировке
            training_white_skills = set(tr_data["skills"]) & self.white_skills
            if not training_white_skills:
                continue

            # Проверяем, есть ли серые навыки (для DC особенно важно избегать тренировок с серыми навыками)
            training_gray_skills = set(tr_data["skills"]) & self.gray_skills

            # Основная логика: штрафуем за серые навыки, премируем за покрытие отстающих навыков
            score = 0

            # Штраф за серые навыки - усиленный штраф, особенно для низкоуровневых серых навыков
            gray_penalty = 0
            for skill in training_gray_skills:
                # Чем выше значение серого навыка, тем больше штраф
                skill_level = skills[skill]
                # Используем функцию сложности для серых навыков с учетом позиционного множителя
                difficulty_factor = training_difficulty(
                    skill_level,
                    is_gray_skill=True,
                )
                # Увеличиваем штраф, особенно для низких серых навыков
                base_penalty = difficulty_factor * 10  # базовый штраф
                # Для DC (и других центральных позиций) увеличиваем штраф за серые навыки
                if "DC" in self.player.positions:
                    base_penalty *= 1.5  # дополнительный штраф для DC
                gray_penalty += base_penalty

            # Премия за покрытие отстающих навыков - с учетом степени отставания
            low_skill_bonus = 0
            for skill in training_white_skills:
                if skill in lowest_skills:
                    # Чем больше отстает навык, тем выше премия
                    skill_value = skills[skill]
                    gap_to_max = max_skill_value - skill_value
                    gap_to_min = skill_value - min_skill_value
                    # Используем комбинацию разницы с максимумом и разницы с минимумом для лучшей балансировки
                    improvement_potential = gap_to_max - gap_to_min * 0.3
                    low_skill_bonus += (
                        max(0, improvement_potential) * 1.2
                    )  # увеличил премию

            # Премия за покрытие разнообразных белых навыков
            diversity_bonus = (
                len(training_white_skills) * 5
            )  # увеличил премию за разнообразие

            # Премия за равномерность - тренировки, которые помогают уменьшить разрыв между навыками
            balance_bonus = 0
            if len(training_white_skills) > 1:
                # Если тренировка покрывает несколько белых навыков, особенно те, что отстают
                covered_low_skills = training_white_skills.intersection(lowest_skills)
                balance_bonus = (
                    len(covered_low_skills)
                    * 2.0
                    * (len(training_white_skills) / len(self.white_skills))
                )

            # Штраф за повторное тренирование одного и того же навыка
            repetition_penalty = 0
            for skill in training_white_skills:
                if skill in skill_training_counts:
                    repetition_penalty += skill_training_counts[skill] * 2

            # Дополнительная логика: если навыки уже достаточно близки, штрафуем за тренировки,
            # которые усиливают сильные навыки
            if skill_gap < 40:
                for skill in training_white_skills:
                    if skills[skill] >= max_skill_value - 15:  # если навык в топе
                        # Вычисляем насколько этот навык отстает от среднего
                        skill_deviation_from_mean = abs(skills[skill] - mean_value)
                        if (
                            skill_deviation_from_mean > std_dev * 0.5
                        ):  # если навык значительно выше среднего
                            # Чем дальше от среднего, тем больше штраф
                            repetition_penalty += min(
                                25, skill_deviation_from_mean * 1.5
                            )  # увеличил штраф

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

            # Если новая дисперсия будет меньше текущей, добавляем премию
            if new_variance < variance:
                variance_reduction_bonus = (
                    variance - new_variance
                ) * 2.0  # увеличил множитель
                score = (
                    low_skill_bonus
                    + diversity_bonus
                    + balance_bonus
                    + variance_reduction_bonus
                    - gray_penalty
                    - repetition_penalty
                )
            else:
                # Если дисперсия увеличивается, применяем штраф
                variance_increase_penalty = (
                    new_variance - variance
                ) * 1.0  # увеличил штраф
                score = (
                    low_skill_bonus
                    + diversity_bonus
                    + balance_bonus
                    - gray_penalty
                    - repetition_penalty
                    - variance_increase_penalty
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
