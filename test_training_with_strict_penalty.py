#!/usr/bin/env python3
"""
Тестирование работы алгоритма с введенным строгим штрафом за серые навыки > 20
"""

import json
from domain.training_planner import TrainingPlanner
from domain.player import Player
from domain.training_simulator import simulate_training

def analyze_player_skills(player: Player):
    """Анализирует навыки игрока и выводит статистику"""
    white_skills = player.white_skills
    gray_skills = player.gray_skills
    
    white_values = [player.skills[skill] for skill in white_skills]
    gray_values = [player.skills[skill] for skill in gray_skills]
    
    print(f"Имя: {player.name}")
    print(f"Позиции: {player.positions}")
    
    print(f"\nСредние значения навыков")
    print(f"Все навыки: {sum(white_values + gray_values) / len(white_values + gray_values):.2f}")
    print(f"Белые навыки: {sum(white_values) / len(white_values):.2f}")
    print(f"Серые навыки: {sum(gray_values) / len(gray_values):.2f}")
    
    # Разница между максимальным и минимальным навыком
    all_values = list(player.skills.values())
    skill_gap = max(all_values) - min(all_values)
    white_gap = max(white_values) - min(white_values)
    gray_gap = max(gray_values) - min(gray_values)
    
    print(f"Разница (сильнейший-слабейший): {skill_gap}")
    print(f"Разница белых навыков: {white_gap}")
    print(f"Разница серых навыков: {gray_gap}")
    
    print(f"\nСлабые и сильные навыки")
    sorted_white = sorted(white_skills, key=lambda s: player.skills[s])
    print(f"Слабые белые навыки: ", end="")
    for skill in sorted_white[:3]:
        print(f"{SKILLS_MAP[skill]} ({player.skills[skill]})", end="")
        if skill != sorted_white[2]:
            print(", ", end="")
    print()
    
    print(f"Сильные белые навыки: ", end="")
    for skill in reversed(sorted_white[-3:]):
        print(f"{SKILLS_MAP[skill]} ({player.skills[skill]})", end="")
        if skill != sorted_white[-3]:
            print(", ", end="")
    print()

    print(f"Слабые серые навыки: ", end="")
    sorted_gray = sorted(gray_skills, key=lambda s: player.skills[s])
    for skill in sorted_gray[:3]:
        print(f"{SKILLS_MAP[skill]} ({player.skills[skill]})", end="")
        if skill != sorted_gray[2] and skill != sorted_gray[0]:
            print(", ", end="")
        elif skill == sorted_gray[0] and len(sorted_gray) > 1:
            print(", ", end="")
    print()

    print(f"Сильные серые навыки: ", end="")
    for skill in reversed(sorted_gray[-3:]):
        print(f"{SKILLS_MAP[skill]} ({player.skills[skill]})", end="")
        if skill != sorted_gray[-3]:
            print(", ", end="")
    print()

# Карта названий навыков
SKILLS_MAP = {
    "tackling": "Отбор мяча",
    "marking": "Опека",
    "positioning": "Выбор позиции",
    "heading": "Удар головой",
    "bravery": "Храбрость",
    "passing": "Передача",
    "dribbling": "Дриблинг",
    "cross": "Навес",
    "shooting": "Удары",
    "finishing": "Завершение",
    "physical": "Физическая форма",
    "strength": "Сила",
    "aggressiveness": "Агрессивность",
    "pace": "Скорость",
    "creativity": "Креативность",
}

def test_training_impact():
    # Загружаем данные игрока Smith из players.json
    with open('storage/players.json', 'r') as f:
        players_data = json.load(f)
    
    # Находим игрока Smith
    smith_player_data = next(p for p in players_data['players'] if p['name'] == 'Smith')
    
    # Создаем объект игрока (убираем training_count)
    player_data = {k: v for k, v in smith_player_data.items() if k != 'training_count'}
    original_player = Player(**player_data)
    
    print("=== АНАЛИЗ ИГРОКА ДО ТРЕНИРОВОК ===")
    analyze_player_skills(original_player)
    
    # Создаем планировщик тренировок
    planner = TrainingPlanner(original_player)
    
    # Генерируем план тренировок
    training_plan = planner.plan(max_trainings=20)
    
    print(f"\n=== ПЛАН ТРЕНИРОВОК (ТОП-10) ===")
    for i, item in enumerate(training_plan[:10]):
        print(f"{i+1}. {item.name} (ID: {item.training_id}) - повторений: {item.repeats}")
        print(f"   Тренируемые навыки: {[SKILLS_MAP[skill] for skill in item.skills]}")
        
        # Проверяем, есть ли серые навыки в этой тренировке
        gray_skills_in_training = [skill for skill in item.skills if skill in original_player.gray_skills]
        if gray_skills_in_training:
            print(f"   ⚠️  Содержит серые навыки: {[(SKILLS_MAP[skill], original_player.skills[skill]) for skill in gray_skills_in_training]}")
        else:
            print(f"   ✅ Без серых навыков")
    
    # Применим тренировки к копии игрока, чтобы увидеть результат
    simulated_skills = original_player.skills.copy()
    
    # Применим план тренировок
    for item in training_plan:
        for _ in range(item.repeats):
            simulated_skills = simulate_training(simulated_skills, item.training_id, gain_per_skill=10)
    
    # Создаем нового игрока с измененными навыками для анализа
    modified_player_data = {
        "id": original_player.id,
        "name": original_player.name,
        "positions": original_player.positions,
        "skills": simulated_skills
    }
    modified_player = Player(**modified_player_data)
    
    print(f"\n=== АНАЛИЗ ИГРОКА ПОСЛЕ {sum(item.repeats for item in training_plan)} ТРЕНИРОВОК ===")
    analyze_player_skills(modified_player)
    
    # Проверим, насколько увеличились серые навыки
    print(f"\n=== АНАЛИЗ ИЗМЕНЕНИЙ СЕРЫХ НАВЫКОВ ===")
    increased_gray_skills = []
    for skill in original_player.gray_skills:
        original_value = original_player.skills[skill]
        new_value = modified_player.skills[skill]
        increase = new_value - original_value
        if increase > 0:
            increased_gray_skills.append((skill, original_value, new_value, increase))
    
    if increased_gray_skills:
        print("Серые навыки, которые увеличились:")
        for skill, orig_val, new_val, inc in increased_gray_skills:
            print(f"  {SKILLS_MAP[skill]}: {orig_val} → {new_val} (+{inc})")
            # Проверим, были ли они > 20 до тренировок
            if orig_val > 20:
                print(f"    ⚠️  Этот навык был > 20 до тренировок!")
    else:
        print("Серые навыки не увеличились - алгоритм эффективно их избегает!")

if __name__ == "__main__":
    test_training_impact()