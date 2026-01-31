"""
Справочник всех тренировок.

ВАЖНО:
- тренировки статичны
- каждая тренировка качает фиксированный набор навыков
- навыки должны строго совпадать с SKILLS из config/skills.py
"""

from config.skills import SKILLS

TRAININGS: dict[str, dict] = {
    # ------------------ Атакующие ------------------
    "one_of_one": {
        "name": "Один на один",
        "type": "attack",
        "skills": ["dribbling", "tackling", "finishing"],
    },
    "pass_dash_strike": {
        "name": "Пас, рывок, удар!",
        "type": "attack",
        "skills": ["pace", "shooting", "passing"],
    },
    "standarts": {
        "name": "Стандарты",
        "type": "attack",
        "skills": ["marking", "cross", "heading", "shooting"],
    },
    "striking_technique": {
        "name": "Техника ударов",
        "type": "attack",
        "skills": ["finishing", "strength", "shooting"],
    },
    "slalom": {
        "name": "Слалом",
        "type": "attack",
        "skills": ["dribbling", "passing", "pace", "physical"],
    },
    "flank_play": {
        "name": "Игра флангами",
        "type": "attack",
        "skills": ["finishing", "cross", "heading", "shooting"],
    },
    "fast_counterattacks": {
        "name": "Быстрые контратаки",
        "type": "attack",
        "skills": ["passing", "finishing", "cross", "creativity"],
    },
    # ------------------ Защитные ------------------
    "video_analysis": {
        "name": "Видеоанализ",
        "type": "defence",
        "skills": ["creativity", "bravery", "positioning"],
    },
    "head_work": {
        "name": "Работой головой",
        "type": "defence",
        "skills": ["heading", "creativity", "passing", "positioning"],
    },
    "line_keeping": {
        "name": "Держать линию",
        "type": "defence",
        "skills": ["marking", "positioning"],
    },
    "stop_attack": {
        "name": "Остановить нападение",
        "type": "defence",
        "skills": ["dribbling", "bravery", "tackling", "marking", "strength"],
    },
    "defence_from_cross": {
        "name": "Защита от навесов",
        "type": "defence",
        "skills": ["bravery", "marking", "cross", "heading"],
    },
    "pressing": {
        "name": "Прессинг",
        "type": "defence",
        "skills": ["aggressiveness", "bravery", "tackling", "marking", "positioning"],
    },
    # ------------------ Владение ------------------
    "ball_control": {
        "name": "Контроль мяча",
        "type": "possession",
        "skills": ["dribbling", "heading", "creativity"],
    },
    "little_dog": {
        "name": "Собачка",
        "type": "possession",
        "skills": ["passing", "tackling", "positioning", "aggressiveness", "physical"],
    },
    "one_touch": {
        "name": "Игра в касание",
        "type": "possession",
        "skills": ["dribbling", "passing", "physical"],
    },
    "fast_flank": {
        "name": "Быстрый перевод на фланг",
        "type": "possession",
        "skills": ["creativity", "cross", "positioning", "pace", "passing"],
    },
    "line_keeping_possession": {
        "name": "Держать линию",
        "type": "possession",
        "skills": ["pace", "positioning", "physical"],
    },
    "contact_game": {
        "name": "Контактная игра",
        "type": "possession",
        "skills": ["dribbling", "bravery", "marking", "strength", "aggressiveness"],
    },
    "passes_before_strike": {
        "name": "Пасы перед ударом",
        "type": "possession",
        "skills": ["passing", "finishing", "positioning", "creativity"],
    },
    # ------------------ Психофизика ------------------
    "warmup": {
        "name": "Разминка",
        "type": "physical",
        "skills": ["heading", "aggressiveness", "physical"],
    },
    "stretching": {
        "name": "Растяжка",
        "type": "physical",
        "skills": ["strength", "pace", "physical"],
    },
    "carioca": {
        "name": "Кариока с лестницей",
        "type": "physical",
        "skills": ["pace", "aggressiveness"],
    },
    "long_run": {
        "name": "Долгий забег",
        "type": "physical",
        "skills": ["physical", "pace"],
    },
    "shuttle_run": {
        "name": "Челночный бег",
        "type": "physical",
        "skills": ["strength", "bravery", "pace"],
    },
    "obstacle_run": {
        "name": "Бег с препятствиями",
        "type": "physical",
        "skills": ["pace", "bravery", "aggressiveness"],
    },
    "gym": {
        "name": "Спортивный зал",
        "type": "physical",
        "skills": ["strength", "physical"],
    },
    "acceleration": {
        "name": "Ускорение",
        "type": "physical",
        "skills": ["dribbling", "pace", "physical"],
    },
}


def validate_trainings() -> None:
    """Проверка целостности справочника тренировок."""
    for tr_id, data in TRAININGS.items():
        for skill in data["skills"]:
            if skill not in SKILLS:
                raise ValueError(f"Тренировка {tr_id}: неизвестный навык '{skill}'")
