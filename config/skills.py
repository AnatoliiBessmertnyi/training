# config/skills.py

"""
Справочник всех игровых навыков.

ВАЖНО:
- id навыка используется ВЕЗДЕ: игроки, позиции, тренировки
- менять id после начала проекта нельзя
"""

SKILLS: dict[str, str] = {
    # Защита
    "tackling": "Отбор мяча",
    "marking": "Опека",
    "positioning": "Выбор позиции",
    "heading": "Удар головой",
    "bravery": "Храбрость",

    # Нападение
    "passing": "Передача",
    "dribbling": "Дриблинг",
    "cross": "Навес",
    "finishing": "Завершение",
    "shooting": "Удары",

    # Психофизика
    "physical": "Физическая форма",
    "strength": "Сила",
    "aggressiveness": "Агрессивность",
    "pace": "Скорость",
    "creativity": "Креативность",
}

TOTAL_SKILLS_COUNT = 15
