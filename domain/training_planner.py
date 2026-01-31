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

        # Определяем отстающие навыки более комплексно
        lowest_skills = []
        
        # Используем плавающую систему весов вместо жестких условий
        # Чем больше разница между навыками, тем больше акцент на самых слабых
        # Чем меньше разница, тем больше акцент на равномерное развитие
        
        # Определяем специальный режим балансировки - активируется при высоком уровне навыков
        # и когда разница между навыками становится критичной
        special_balancing_mode = mean_value > 180 and skill_gap > 30

        # Определяем пороги на основе статистики
        weak_threshold = mean_value - std_dev * 0.5 if std_dev > 0 else min_skill_value + 5
        moderate_threshold = mean_value
        
        # Определяем навыки по категориям
        very_weak_skills = [skill for skill, value in sorted_white_skills if value <= weak_threshold]
        weak_skills = [skill for skill, value in sorted_white_skills if weak_threshold < value <= moderate_threshold]
        
        # Выбираем подходящую стратегию взвешивания
        if skill_gap > 50:
            # При очень большой разнице фокус на самых слабых навыках
            lowest_skills = very_weak_skills if very_weak_skills else weak_skills
        elif skill_gap > 25:
            # При средней разнице - более широкий охват
            lowest_skills = very_weak_skills + weak_skills
        else:
            # При малой разнице - фокус на минимальной разнице и максимальной равномерности
            # Вместо выбора только слабых навыков, теперь будем использовать гибкий подход
            # где учитываются не только самые слабые, но и другие факторы равномерности
            lowest_skills = very_weak_skills + weak_skills
        
        # РАДИКАЛЬНОЕ УЛУЧШЕНИЕ: При высоком уровне навыков (>180) и разнице > 30,
        # переопределяем lowest_skills для принудительной балансировки
        if mean_value > 180 and skill_gap > 30:
            # Найдем навыки, которые отстают от среднего значения более чем на 10 пунктов
            significantly_below_average = [
                skill for skill, value in white_skill_values.items() 
                if value < mean_value - 10
            ]
            
            # Если такие навыки есть, сфокусируемся на них
            if significantly_below_average:
                lowest_skills = significantly_below_average
            else:
                # Если нет значительных отстающих, используем навыки ниже медианы
                sorted_by_value = sorted(white_skill_values.items(), key=lambda x: x[1])
                median_pos = len(sorted_by_value) // 2
                median_value = sorted_by_value[median_pos][1]
                
                lowest_skills = [
                    skill for skill, value in white_skill_values.items()
                    if value < median_value
                ]
        
        # Если не нашли подходящих навыков, берем несколько самых слабых
        if not lowest_skills:
            target_range = min(3, len(sorted_white_skills))
            lowest_skills = [
                skill for skill, value in sorted_white_skills[:target_range]
            ]

        # ДОПОЛНЕНИЕ: Теперь добавим более комплексный подход для выбора навыков для развития
        # Когда разница между навыками становится небольшой, но все они высокие,
        # мы должны стремиться к равномерному развитию, а не только к поднятию слабых
        
        # Определяем, насколько равномерно распределены навыки
        # Если навыки уже достаточно близки друг к другу, нужно стремиться к равномерному поднятию
        if skill_gap <= 30 and len(white_skill_values) > 1:
            # Когда разница небольшая, но все равно есть дисбаланс - фокус на равномерное развитие
            # Определяем навыки, которые наиболее далеки от среднего (в обе стороны)
            balanced_focus_skills = []
            
            # Определяем навыки, которые ниже среднего (потенциальные кандидаты для повышения)
            below_average_skills = [skill for skill, value in sorted_white_skills if value < mean_value]
            
            # Если разница между навыками стала небольшой, но все еще есть отстающие - 
            # нужно учитывать не только самые слабые, но и стремиться к равномерности
            if below_average_skills:
                # Сортируем отстающие навыки по удаленности от среднего
                below_average_sorted = sorted(below_average_skills, key=lambda s: skills[s])
                
                # Выбираем не только самые слабые, но и следующие по уровню
                # чтобы обеспечить более равномерное развитие
                balanced_focus_skills.extend(below_average_sorted[:min(3, len(below_average_sorted))])
                
                # Добавляем к lowest_skills эти сбалансированные навыки
                lowest_skills = list(set(lowest_skills + balanced_focus_skills))
        
        # ДОПОЛНЕНИЕ: особенно важная логика при высоком уровне навыков
        # если среднее значение белых навыков > 200, нужно особо акцентировать внимание на равномерности
        if mean_value > 200:
            # Если разница между навыками начинает расти при высоком уровне, 
            # то нужно более агрессивно подбирать тренировки для выравнивания
            if skill_gap > 30:
                # Вместо того, чтобы просто брать слабые навыки, давайте использовать более точный подход
                # Найдем навыки, которые наиболее отстают от идеального равномерного распределения
                
                # Идеальное равномерное распределение - это когда все навыки имеют одинаковое значение
                # которое близко к среднему. Найдем навыки, которые максимально отстают от этого идеала
                ideal_value = mean_value  # идеальное значение для равномерного распределения
                gaps_from_ideal = [(skill, abs(value - ideal_value)) for skill, value in white_skill_values.items()]
                
                # Отсортируем по отставанию от идеала и возьмем топ-3
                gaps_from_ideal.sort(key=lambda x: x[1], reverse=True)
                
                # Нам нужны те, которые НИЖЕ идеального значения (отстающие)
                below_ideal_skills = [(skill, value) for skill, value in white_skill_values.items() if value < ideal_value]
                below_ideal_skills.sort(key=lambda x: x[1])  # отсортируем по возрастанию
                
                # Обновим lowest_skills, добавив отстающие навыки при высоком уровне
                if below_ideal_skills:
                    additional_lowest = [skill for skill, value in below_ideal_skills[:3]]
                    lowest_skills = list(set(lowest_skills + additional_lowest))

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

            # ДОПОЛНИТЕЛЬНО: Балансировка на основе разницы между максимальным и минимальным белыми навыками
            # Чем больше разница, тем важнее тренировки, которые помогают её уменьшить
            balance_importance_bonus = 0
            if skill_gap > 30:  # При большой разнице между навыками
                # Определим, насколько тренировка способствует уменьшению разницы
                # Считаем, сколько из тренируемых навыков являются "отстающими"
                covered_weakest_skills = training_white_skills.intersection(set(lowest_skills))
                if covered_weakest_skills:
                    # Чем больше отстающих навыков тренируется, тем выше премия
                    balance_importance_bonus = len(covered_weakest_skills) * skill_gap * 0.3

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
            
            # ЕЩЕ ОДНА ВАЖНАЯ ЛОГИКА: когда средний уровень белых навыков уже высокий (>150),
            # нужно особенно внимательно следить за разницей между навыками
            if mean_value > 150 and skill_gap > 20:
                # Увеличиваем премию за тренировки, которые помогают уменьшить разницу
                # когда навыки уже на высоком уровне
                for skill in training_white_skills:
                    if skill in lowest_skills:
                        # Если тренировка работает над самым слабым навыком при высоком уровне,
                        # то это особенно важно
                        gap_to_max = max_skill_value - skills[skill]
                        if gap_to_max > 20:  # если навык еще не на пределе
                            low_skill_bonus += gap_to_max * 0.5
                            
                # Также увеличиваем штраф за тренировки, которые усиливают сильные навыки
                # при высоком уровне и большой разнице
                for skill in training_white_skills:
                    if skills[skill] > mean_value + 10:  # если навык явно сильнее среднего
                        # особенно штрафуем, если навык уже высокий (больше 200)
                        if skills[skill] > 200:
                            repetition_penalty += (skills[skill] - mean_value) * 0.7

            # ДОПОЛНИТЕЛЬНО: Очень важная логика - при высоком уровне навыков (>200) и разнице > 30
            # добавляем сильный штраф за тренировки, которые не помогают сбалансировать навыки
            if mean_value > 200 and skill_gap > 30:
                # Подсчитаем, сколько белых навыков из этой тренировки находятся в "верхней половине" навыков
                white_skills_in_training = [skill for skill in training_white_skills]
                if white_skills_in_training:
                    # Найдем медиану белых навыков
                    sorted_white_values = sorted(white_skill_values.items(), key=lambda x: x[1])
                    median_idx = len(sorted_white_values) // 2
                    median_value = sorted_white_values[median_idx][1]
                    
                    # Подсчитаем, сколько тренируемых навыков выше медианы
                    skills_above_median = [skill for skill in white_skills_in_training if skills[skill] > median_value]
                    
                    # Если большинство тренируемых навыков находятся в верхней половине,
                    # это может усугубить дисбаланс - применяем штраф
                    if len(skills_above_median) > len(white_skills_in_training) / 2:
                        # Штраф тем больше, чем больше разница и чем выше средний уровень
                        imbalance_penalty = (skill_gap * (mean_value / 100)) * 1.5
                        score -= imbalance_penalty
            
            # ЕЩЕ БОЛЕЕ ЖЕСТКАЯ ЛОГИКА: когда средний уровень > 150 и разница > 35,
            # применяем очень сильный штраф к тренировкам, которые не направлены на выравнивание
            if mean_value > 150 and skill_gap > 35:
                # Определим, сколько из тренируемых белых навыков являются "отстающими" (ниже среднего)
                weak_skills_in_training = [skill for skill in training_white_skills if skills[skill] < mean_value]
                
                # Если тренировка не фокусируется на отстающих навыках, применяем сильный штраф
                if len(weak_skills_in_training) < len(training_white_skills) / 2:
                    # штраф тем больше, чем больше разница и чем выше средний уровень
                    severe_penalty = (skill_gap * (mean_value / 100)) * 3.0
                    score -= severe_penalty

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
            
            # Вычисляем новую разницу между максимальным и минимальным белыми навыками
            new_min_white = min(new_white_values)
            new_max_white = max(new_white_values)
            new_skill_gap = new_max_white - new_min_white

            # Если новая дисперсия будет меньше текущей, добавляем премию
            if new_variance < variance:
                variance_reduction_bonus = (
                    variance - new_variance
                ) * 2.0  # увеличил множитель
            else:
                variance_reduction_bonus = 0

            # Также добавим премию за уменьшение разницы между навыками
            gap_reduction_bonus = 0
            if new_skill_gap < skill_gap:
                gap_reduction_bonus = (skill_gap - new_skill_gap) * 3.0  # премия за уменьшение разницы

            # И штраф за увеличение разницы между навыками
            gap_increase_penalty = 0
            if new_skill_gap > skill_gap:
                gap_increase_penalty = (new_skill_gap - skill_gap) * 5.0  # штраф за увеличение разницы
                # особенно при высоком уровне навыков
                if mean_value > 150:
                    gap_increase_penalty *= 2.0
                # ЕЩЕ БОЛЕЕ АГРЕССИВНЫЙ ШТРАФ, когда разница между навыками превышает 40
                if new_skill_gap > 40:
                    gap_increase_penalty *= 2.0

            score = (
                low_skill_bonus
                + diversity_bonus
                + balance_bonus
                + variance_reduction_bonus
                + gap_reduction_bonus
                + balance_importance_bonus  # добавляем новый бонус
                - gray_penalty
                - repetition_penalty
                - gap_increase_penalty
            )

            # ОСОБАЯ ЛОГИКА: когда разница между навыками становится маленькой (< 30), 
            # но начинает расти, мы должны особенно акцентировать внимание на балансировке
            # Это решает проблему, когда при малой разнице алгоритм начинает работать неэффективно
            if skill_gap < 30 and new_skill_gap > skill_gap:
                # Если разница между навыками маленькая, но начинает расти, 
                # применяем сильный штраф за увеличение разницы
                critical_balance_penalty = (new_skill_gap - skill_gap) * 15.0
                score -= critical_balance_penalty
            elif skill_gap < 30:
                # Когда разница между навыками маленькая, особенно поощряем тренировки,
                # которые помогают поддерживать баланс, даже если не уменьшают разницу
                # Находим навыки, которые ниже среднего значения, и поощряем их развитие
                below_average_skills = [skill for skill in training_white_skills if skills[skill] < mean_value]
                if below_average_skills:
                    # Тем больше премия, чем меньше текущая разница (чем ближе к идеальному балансу)
                    balance_stability_bonus = (30 - skill_gap) * len(below_average_skills) * 0.5
                    score += balance_stability_bonus
            
            # ДОПОЛНИТЕЛЬНО: ЕЩЕ БОЛЕЕ АГРЕССИВНЫЙ ШТРАФ для предотвращения увеличения разницы между навыками
            # когда средний уровень уже высокий (>200) и разница > 30
            if mean_value > 200 and skill_gap > 30:
                # Если тренировка увеличивает разницу между навыками, применяем дополнительный штраф
                if new_skill_gap > skill_gap:
                    aggressive_penalty = (new_skill_gap - skill_gap) * 10.0
                    score -= aggressive_penalty

            # ДОПОЛНЕНИЕ: Добавим дополнительную логику для улучшения равномерности
            # особенно когда все навыки уже на высоком уровне
            if mean_value > 150:  # Когда средний уровень навыков уже высокий
                # Добавим премию за тренировки, которые помогают уравнять навыки
                # на высоком уровне, а не просто поднимают самые слабые
                
                # Проверим, насколько равномерно тренировка влияет на белые навыки
                # Если она поднимает только самые сильные навыки, это может ухудшить равномерность
                if len(training_white_skills) > 1:
                    # Проверим, насколько равномерно распределены значения среди тренируемых навыков
                    trained_white_values = [skills[skill] for skill in training_white_skills if skill in skills]
                    if trained_white_values:
                        trained_mean = sum(trained_white_values) / len(trained_white_values)
                        trained_std_dev = (sum((x - trained_mean) ** 2 for x in trained_white_values) / len(trained_white_values)) ** 0.5
                        
                        # Если среди тренируемых навыков большие различия, это может быть неоптимально
                        # при высоком уровне навыков, если тренировка фокусируется на самых сильных
                        if trained_std_dev > std_dev * 0.5:  # Если разброс среди тренируемых выше среднего
                            # Проверим, какие навыки из тренируемых самые сильные
                            strong_trained_skills = [skill for skill in training_white_skills if skills[skill] > trained_mean + trained_std_dev * 0.3]
                            
                            # Если тренировка фокусируется на сильных навыках при высоком уровне, штрафуем
                            if len(strong_trained_skills) > len(training_white_skills) // 2:
                                score -= len(strong_trained_skills) * 2
                                
                        # Добавим премию за тренировки, которые поднимают слабые навыки среди тренируемых
                        weak_trained_skills = [skill for skill in training_white_skills if skills[skill] < trained_mean - trained_std_dev * 0.3]
                        score += len(weak_trained_skills) * 1.5

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
