from typing import List, Dict, Set
from config.skills import SKILLS
from config.positions import POSITIONS


class Player:
    def __init__(self, name: str, positions: List[str], skills: Dict[str, int]):
        """
        :param name: Имя игрока
        :param positions: Список id позиций игрока (1-3)
        :param skills: Словарь всех навыков {id: значение}
        """
        self.name = name
        self.positions = positions
        self.skills = skills.copy()  # {skill_id: value}
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
