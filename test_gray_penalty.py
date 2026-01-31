#!/usr/bin/env python3
"""
Тестирование строгого штрафа за тренировки, которые качают серые навыки выше 20
"""

import json
from domain.training_planner import TrainingPlanner
from domain.player import Player

def test_strict_gray_penalty():
    # Загружаем данные игрока Smith из players.json
    with open('storage/players.json', 'r') as f:
        players_data = json.load(f)
    
    # Находим игрока Smith
    smith_player_data = next(p for p in players_data['players'] if p['name'] == 'Smith')
    
    # Создаем объект игрока (убираем training_count, т.к. он не нужен для инициализации)
    player_data = {k: v for k, v in smith_player_data.items() if k != 'training_count'}
    player = Player(**player_data)
    
    print("Текущий игрок:")
    print(f"Имя: {player.name}")
    print(f"Позиции: {player.positions}")
    print(f"Навыки: {player.skills}")
    
    # Определяем белые и серые навыки для позиции DC
    dc_white_skills = [
        "tackling", "marking", "positioning", "heading", 
        "bravery", "physical", "strength", "aggressiveness"
    ]
    
    all_skills = set(player.skills.keys())
    white_skills = set(dc_white_skills)
    gray_skills = all_skills - white_skills
    
    print(f"\nБелые навыки: {white_skills}")
    print(f"Серые навыки: {gray_skills}")
    
    print("\nТекущие значения серых навыков:")
    for skill in gray_skills:
        value = player.skills[skill]
        print(f"  {skill}: {value}")
    
    # Создаем планировщик тренировок
    planner = TrainingPlanner(player)
    
    # Генерируем план тренировок
    training_plan = planner.plan(max_trainings=10)
    
    print(f"\nСгенерированный план тренировок (первые 5):")
    for i, item in enumerate(training_plan[:5]):
        print(f"  {i+1}. {item.name} (ID: {item.training_id}) - повторений: {item.repeats}")
        print(f"     Тренируемые навыки: {item.skills}")
        
        # Проверяем, есть ли серые навыки в этой тренировке
        gray_skills_in_training = [skill for skill in item.skills if skill in gray_skills]
        if gray_skills_in_training:
            print(f"     ⚠️  Содержит серые навыки: {gray_skills_in_training}")
            for gray_skill in gray_skills_in_training:
                current_value = player.skills[gray_skill]
                print(f"        {gray_skill}: {current_value} {'⚠️ >20!' if current_value > 20 else ''}")
        else:
            print(f"     ✅ Без серых навыков")

    # Проверим также, как алгоритм оценивает конкретные тренировки
    print(f"\nПроверка оценки тренировок:")
    
    test_player_data = {
        "id": "test",
        "name": "Test Player",
        "positions": ["DC"],
        "skills": {
            "tackling": 200, "marking": 200, "positioning": 200, "heading": 200,
            "bravery": 200, "physical": 200, "strength": 200, "aggressiveness": 200,
            "passing": 25, "dribbling": 25, "cross": 25, "shooting": 25, "finishing": 25,
            "pace": 25, "creativity": 25  # Эти серые навыки > 20
        }
    }
    
    test_player = Player(**test_player_data)
    test_planner = TrainingPlanner(test_player)
    
    # Проверим, как алгоритм оценивает тренировки, содержащие серые навыки > 20
    print(f"\nТестирование с серыми навыками > 20:")
    print(f"Серые навыки > 20: {[skill for skill, value in test_player.skills.items() if skill not in dc_white_skills and value > 20]}")
    
    # Получим несколько первых тренировок из плана
    test_plan = test_planner.plan(max_trainings=5)
    for i, item in enumerate(test_plan):
        print(f"  {i+1}. {item.name} (ID: {item.training_id}) - повторений: {item.repeats}")
        gray_in_test = [skill for skill in item.skills if skill in (set(test_player.skills.keys()) - set(dc_white_skills))]
        if gray_in_test:
            print(f"     ⚠️  Содержит серые навыки: {[(skill, test_player.skills[skill]) for skill in gray_in_test if test_player.skills[skill] > 20]}")

if __name__ == "__main__":
    test_strict_gray_penalty()