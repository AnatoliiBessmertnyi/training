"""
Справочник игровых позиций и их приоритетных (белых) навыков.

ВАЖНО:
- id навыков берутся строго из config/skills.py
- id позиций используются везде (игроки, логика)
- менять состав навыков после старта проекта нельзя
"""

from config.skills import SKILLS

POSITIONS: dict[str, dict] = {
    # Защитники флангов
    "DL": {
        "name": "Левый защитник",
        "white_skills": [
            "tackling",
            "marking",
            "positioning",
            "bravery",
            "cross",
            "physical",
            "aggressiveness",
            "pace",
        ],
    },
    "DR": {
        "name": "Правый защитник",
        "white_skills": [
            "tackling",
            "marking",
            "positioning",
            "bravery",
            "cross",
            "physical",
            "aggressiveness",
            "pace",
        ],
    },
    # Центральный защитник
    "DC": {
        "name": "Центральный защитник",
        "white_skills": [
            "tackling",
            "marking",
            "positioning",
            "heading",
            "bravery",
            "physical",
            "strength",
            "aggressiveness",
        ],
    },
    # Опорный полузащитник
    "DMC": {
        "name": "Опорный полузащитник",
        "white_skills": [
            "tackling",
            "marking",
            "positioning",
            "heading",
            "bravery",
            "passing",
            "physical",
            "strength",
            "aggressiveness",
            "creativity",
        ],
    },
    # Центральный полузащитник
    "MC": {
        "name": "Центральный полузащитник",
        "white_skills": [
            "tackling",
            "marking",
            "positioning",
            "bravery",
            "passing",
            "dribbling",
            "shooting",
            "physical",
            "pace",
            "creativity",
        ],
    },
    # Фланговые полузащитники
    "ML": {
        "name": "Левый полузащитник",
        "white_skills": [
            "positioning",
            "passing",
            "dribbling",
            "cross",
            "physical",
            "pace",
            "creativity",
        ],
    },
    "MR": {
        "name": "Правый полузащитник",
        "white_skills": [
            "positioning",
            "passing",
            "dribbling",
            "cross",
            "physical",
            "pace",
            "creativity",
        ],
    },
    # Атакующие фланги
    "AML": {
        "name": "Левый атакующий полузащитник",
        "white_skills": [
            "passing",
            "dribbling",
            "cross",
            "finishing",
            "shooting",
            "physical",
            "pace",
            "creativity",
        ],
    },
    "AMR": {
        "name": "Правый атакующий полузащитник",
        "white_skills": [
            "passing",
            "dribbling",
            "cross",
            "finishing",
            "shooting",
            "physical",
            "pace",
            "creativity",
        ],
    },
    # Атакующий центр
    "AMC": {
        "name": "Атакующий полузащитник",
        "white_skills": [
            "heading",
            "passing",
            "dribbling",
            "shooting",
            "finishing",
            "physical",
            "pace",
            "creativity",
        ],
    },
    # Нападающий
    "ST": {
        "name": "Нападающий",
        "white_skills": [
            "positioning",
            "heading",
            "passing",
            "dribbling",
            "shooting",
            "finishing",
            "strength",
            "pace",
            "creativity",
        ],
    },
}


def validate_positions() -> None:
    """Проверка целостности справочника."""
    for pos_id, data in POSITIONS.items():
        for skill in data["white_skills"]:
            if skill not in SKILLS:
                raise ValueError(f"Позиция {pos_id}: неизвестный навык '{skill}'")
