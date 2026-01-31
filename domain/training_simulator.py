from copy import deepcopy
from config.trainings import TRAININGS

MAX_SKILL_VALUE = 400


def simulate_training(
    skills: dict[str, int],
    training_id: str,
    gain_per_skill: int = 5,
) -> dict[str, int]:
    """
    Виртуально применяет тренировку и возвращает НОВЫЙ словарь навыков.
    Оригинал не мутируется.
    """

    training = TRAININGS[training_id]
    affected_skills = training["skills"]

    new_skills = deepcopy(skills)

    for skill in affected_skills:
        new_skills[skill] = min(
            MAX_SKILL_VALUE, new_skills.get(skill, 1) + gain_per_skill
        )

    return new_skills
