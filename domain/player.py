from typing import List, Dict, Set
from config.skills import SKILLS
from config.positions import POSITIONS


class Player:
    def __init__(self, name: str, positions: List[str], skills: Dict[str, int], enhancement_level: int = 0):
        """
        :param name: Имя игрока
        :param positions: Список id позиций игрока (1-3)
        :param skills: Словарь всех навыков {id: значение}
        :param enhancement_level: Уровень усиления (0-5)
        """
        self.name = name
        self.positions = positions
        self.skills = skills.copy()  # {skill_id: value}
        self.enhancement_level = enhancement_level
        self.validate()

    def validate(self):
        """Проверка корректности позиций и навыков"""
        for pos in self.positions:
            if pos not in POSITIONS:
                raise ValueError(f"Неизвестная позиция {pos}")
        for skill in self.skills:
            if skill not in SKILLS:
                raise ValueError(f"Неизвестный навык {skill}")
        # Проверка на недостающие навыки
        for skill_id in SKILLS:
            if skill_id not in self.skills:
                self.skills[skill_id] = 1  # Минимальное значение

    @property
    def white_skills(self) -> Set[str]:
        """Возвращает множество белых навыков игрока (по позициям)"""
        result = set()
        for pos in self.positions:
            result.update(POSITIONS[pos]["white_skills"])
        return result

    @property
    def gray_skills(self) -> Set[str]:
        """Все навыки кроме белых"""
        return set(SKILLS.keys()) - self.white_skills

    def weakest_white_skills(self, top_n: int = 3) -> List[str]:
        """Возвращает top_n белых навыков с минимальным значением"""
        whites = {skill: self.skills[skill] for skill in self.white_skills}
        sorted_skills = sorted(whites.items(), key=lambda x: x[1])
        return [skill for skill, val in sorted_skills[:top_n]]

    def strongest_white_skills(self, top_n: int = 3) -> List[str]:
        """Возвращает top_n белых навыков с максимальным значением"""
        whites = {skill: self.skills[skill] for skill in self.white_skills}
        sorted_skills = sorted(whites.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, val in sorted_skills[:top_n]]

    def apply_training(self, training_skills: List[str], gain: int = 1):
        """
        Применение тренировки к игроку.
        :param training_skills: навыки, которые качает тренировка
        :param gain: прирост (по умолчанию +1)
        """
        for skill in training_skills:
            if skill in self.skills:
                self.skills[skill] += gain
                # Максимальное значение навыка теперь 400, как в тренировочном симуляторе
                from domain.training_simulator import MAX_SKILL_VALUE

                if self.skills[skill] > MAX_SKILL_VALUE:
                    self.skills[skill] = MAX_SKILL_VALUE

    @property
    def enhancement_bonus(self) -> int:
        """Возвращает бонус усиления для белых навыков в зависимости от уровня"""
        bonus_map = {0: 0, 1: 10, 2: 30, 3: 50, 4: 80, 5: 120}  # Бонусы для уровней 0-5
        return bonus_map.get(self.enhancement_level, 0)

    def get_enhanced_skill_value(self, skill_id: str) -> int:
        """Возвращает значение навыка с учетом усиления (для белых навыков)"""
        base_value = self.skills.get(skill_id, 0)
        # Добавляем бонус только для белых навыков
        if skill_id in self.white_skills:
            return base_value + self.enhancement_bonus
        return base_value

    def get_enhanced_skills(self) -> Dict[str, int]:
        """Возвращает словарь всех навыков с учетом усиления"""
        enhanced_skills = {}
        for skill_id, value in self.skills.items():
            enhanced_skills[skill_id] = self.get_enhanced_skill_value(skill_id)
        return enhanced_skills

    @property
    def average_overall(self) -> float:
        """Среднее значение всех навыков с учетом усиления"""
        enhanced_skills = self.get_enhanced_skills()
        if not enhanced_skills:
            return 0
        return sum(enhanced_skills.values()) / len(enhanced_skills)

    @property
    def average_white(self) -> float:
        """Среднее значение белых навыков с учетом усиления"""
        enhanced_white_skills = {skill: self.get_enhanced_skill_value(skill) for skill in self.white_skills}
        if not enhanced_white_skills:
            return 0
        return sum(enhanced_white_skills.values()) / len(enhanced_white_skills)

    @property
    def raw_average_overall(self) -> float:
        """Среднее без усиления (но со всеми навыками, включая недостающие = 1)"""
        values = [self.skills.get(skill_id, 1) for skill_id in SKILLS]
        return sum(values) / len(values)

    @property
    def raw_average_white(self) -> float:
        white_vals = [self.skills.get(skill_id, 1) for skill_id in self.white_skills]
        return sum(white_vals) / len(white_vals) if white_vals else 0

    @property
    def raw_average_gray(self) -> float:
        gray_vals = [self.skills.get(skill_id, 1) for skill_id in self.gray_skills]
        return sum(gray_vals) / len(gray_vals) if gray_vals else 0

    @property
    def raw_white_skill_difference(self) -> int:
        white_vals = [self.skills.get(skill_id, 1) for skill_id in self.white_skills]
        return max(white_vals) - min(white_vals) if white_vals else 0
