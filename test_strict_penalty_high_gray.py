#!/usr/bin/env python3
"""
Тестирование строгого штрафа при наличии серых навыков > 20
"""

from domain.training_planner import TrainingPlanner
from domain.player import Player
from domain.training_simulator import simulate_training

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

def test_strict_penalty_with_high_gray_skills():
    # Создадим игрока-центрального защитника с серыми навыками > 20
    player_data = {
        "id": "test_player",
        "name": "Test DC Player",
        "positions": ["DC"],  # Центральный защитник
        "skills": {
            # Белые навыки (для DC)
            "tackling": 180,      # Отбор мяча
            "marking": 175,       # Опека
            "positioning": 185,    # Выбор позиции
            "heading": 170,       # Удар головой
            "bravery": 160,       # Храбрость
            "physical": 165,      # Физическая форма
            "strength": 175,      # Сила
            "aggressiveness": 165, # Агрессивность
            
            # Серые навыки (все > 20)
            "passing": 25,        # Передача
            "dribbling": 28,      # Дриблинг
            "cross": 30,          # Навес
            "shooting": 22,       # Удары
            "finishing": 26,      # Завершение
            "pace": 35,           # Скорость
            "creativity": 24,     # Креативность
        }
    }
    
    player = Player(**player_data)
    
    print("=== ИГРОК С СЕРЫМИ НАВЫКАМИ > 20 ===")
    print(f"Имя: {player.name}")
    print(f"Позиции: {player.positions}")
    
    print(f"\nБелые навыки: {len(player.white_skills)}")
    for skill in sorted(player.white_skills):
        print(f"  {SKILLS_MAP[skill]}: {player.skills[skill]}")
    
    print(f"\nСерые навыки: {len(player.gray_skills)}")
    for skill in sorted(player.gray_skills):
        value = player.skills[skill]
        status = "⚠️ >20" if value > 20 else ""
        print(f"  {SKILLS_MAP[skill]}: {value} {status}")
    
    # Создаем планировщик тренировок
    planner = TrainingPlanner(player)
    
    # Генерируем план тренировок
    training_plan = planner.plan(max_trainings=15)
    
    print(f"\n=== ПЛАН ТРЕНИРОВОК (все 15) ===")
    gray_trainings_count = 0
    for i, item in enumerate(training_plan):
        print(f"{i+1}. {item.name} (ID: {item.training_id}) - повторений: {item.repeats}")
        print(f"   Тренируемые навыки: {[SKILLS_MAP[skill] for skill in item.skills]}")
        
        # Проверяем, есть ли серые навыки в этой тренировке
        gray_skills_in_training = [skill for skill in item.skills if skill in player.gray_skills]
        if gray_skills_in_training:
            gray_trainings_count += 1
            print(f"   ⚠️  СОДЕРЖИТ СЕРЫЕ НАВЫКИ: {[(SKILLS_MAP[skill], player.skills[skill]) for skill in gray_skills_in_training]}")
            
            # Проверим, есть ли среди них те, что > 20
            high_gray_in_training = [skill for skill in gray_skills_in_training if player.skills[skill] > 20]
            if high_gray_in_training:
                print(f"      ❌ СЕРЫЕ НАВЫКИ > 20: {[(SKILLS_MAP[skill], player.skills[skill]) for skill in high_gray_in_training]}")
            else:
                print(f"      ✅ Все серые навыки ≤ 20")
        else:
            print(f"   ✅ Без серых навыков")
    
    print(f"\n=== СТАТИСТИКА ПО ТРЕНИРОВКАМ ===")
    print(f"Всего тренировок: {len(training_plan)}")
    print(f"Тренировок с серыми навыками: {gray_trainings_count}")
    print(f"Тренировок без серых навыков: {len(training_plan) - gray_trainings_count}")
    
    # Применим тренировки и проверим, увеличились ли серые навыки > 20
    print(f"\n=== ПРОВЕРКА ИЗМЕНЕНИЙ СЕРЫХ НАВЫКОВ > 20 ===")
    
    simulated_skills = player.skills.copy()
    
    # Применим план тренировок
    for item in training_plan:
        for _ in range(item.repeats):
            simulated_skills = simulate_training(simulated_skills, item.training_id, gain_per_skill=10)
    
    increased_high_gray_skills = []
    decreased_skills = []
    
    for skill in player.gray_skills:
        original_value = player.skills[skill]
        new_value = simulated_skills[skill]
        change = new_value - original_value
        
        if original_value > 20 and change > 0:
            increased_high_gray_skills.append((skill, original_value, new_value, change))
        elif change < 0:
            decreased_skills.append((skill, original_value, new_value, change))
    
    if increased_high_gray_skills:
        print("❌ СЕРЫЕ НАВЫКИ > 20, КОТОРЫЕ УВЕЛИЧИЛИСЬ:")
        for skill, orig_val, new_val, inc in increased_high_gray_skills:
            print(f"  {SKILLS_MAP[skill]}: {orig_val} → {new_val} (+{inc})")
    else:
        print("✅ НЕТ увеличения серых навыков > 20 - алгоритм эффективно их избегает!")
    
    if decreased_skills:
        print(f"\n⚠️  Некоторые навыки уменьшились (может быть связано с ограничением 400):")
        for skill, orig_val, new_val, dec in decreased_skills:
            print(f"  {SKILLS_MAP[skill]}: {orig_val} → {new_val} ({dec:+d})")

if __name__ == "__main__":
    test_strict_penalty_with_high_gray_skills()