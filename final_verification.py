#!/usr/bin/env python3
"""
Финальная проверка работы алгоритма с введенным строгим штрафом за серые навыки > 20
"""

import json
from domain.training_planner import TrainingPlanner
from domain.player import Player
from domain.training_simulator import simulate_training

def calculate_balance_stats(skills_dict, white_skills):
    """Вычисляет статистику по балансу белых навыков"""
    white_values = [skills_dict[skill] for skill in white_skills]
    min_val = min(white_values)
    max_val = max(white_values)
    avg_val = sum(white_values) / len(white_values)
    gap = max_val - min_val
    
    # Вычисляем дисперсию для оценки равномерности
    variance = sum((val - avg_val)**2 for val in white_values) / len(white_values)
    std_dev = variance**0.5
    
    return {
        'min': min_val,
        'max': max_val,
        'avg': avg_val,
        'gap': gap,
        'std_dev': std_dev,
        'values': white_values
    }

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

def main():
    # Загружаем данные игрока Smith из players.json
    with open('storage/players.json', 'r') as f:
        players_data = json.load(f)
    
    # Находим игрока Smith
    smith_player_data = next(p for p in players_data['players'] if p['name'] == 'Smith')
    
    # Создаем объект игрока (убираем training_count)
    player_data = {k: v for k, v in smith_player_data.items() if k != 'training_count'}
    original_player = Player(**player_data)
    
    print("=== ФИНАЛЬНАЯ ПРОВЕРКА АЛГОРИТМА ===")
    print(f"Игрок: {original_player.name}, Позиция: {original_player.positions[0]}")
    
    # Статистика до тренировок
    original_stats = calculate_balance_stats(original_player.skills, original_player.white_skills)
    
    print(f"\n--- СОСТОЯНИЕ ДО ТРЕНИРОВОК ---")
    print(f"Среднее белых навыков: {original_stats['avg']:.1f}")
    print(f"Разница (макс-мин): {original_stats['gap']}")
    print(f"Стандартное отклонение: {original_stats['std_dev']:.1f}")
    print(f"Диапазон: {original_stats['min']} - {original_stats['max']}")
    
    # Показываем топ-3 слабых и сильных белых навыков
    sorted_whites = sorted(original_player.white_skills, key=lambda s: original_player.skills[s])
    print(f"Слабые белые навыки: ", end="")
    for i, skill in enumerate(sorted_whites[:3]):
        if i > 0: print(", ", end="")
        print(f"{SKILLS_MAP[skill]}({original_player.skills[skill]})", end="")
    print()
    
    print(f"Сильные белые навыки: ", end="")
    for i, skill in enumerate(reversed(sorted_whites[-3:])):
        if i > 0: print(", ", end="")
        print(f"{SKILLS_MAP[skill]}({original_player.skills[skill]})", end="")
    print()
    
    # Создаем планировщик тренировок
    planner = TrainingPlanner(original_player)
    
    # Генерируем план тренировок
    training_plan = planner.plan(max_trainings=30)  # Больше тренировок для видимости эффекта
    
    print(f"\n--- СОСТАВЛЕНИЕ ПЛАНА ТРЕНИРОВОК ---")
    print(f"Сгенерировано тренировок: {sum(item.repeats for item in training_plan)}")
    
    # Подсчитаем тренировки с/без серыми навыками
    trainings_with_gray = 0
    trainings_with_high_gray = 0  # С навыками > 20
    
    for item in training_plan:
        gray_skills_in_training = [skill for skill in item.skills if skill in original_player.gray_skills]
        if gray_skills_in_training:
            trainings_with_gray += item.repeats
            # Проверяем, есть ли среди них > 20
            high_gray = [skill for skill in gray_skills_in_training if original_player.skills[skill] > 20]
            if high_gray:
                trainings_with_high_gray += item.repeats
    
    total_repeats = sum(item.repeats for item in training_plan)
    print(f"Тренировок без серых навыков: {total_repeats - trainings_with_gray}")
    print(f"Тренировок с серыми навыками ≤20: {trainings_with_gray - trainings_with_high_gray}")
    print(f"Тренировок с серыми навыками >20: {trainings_with_high_gray}")
    
    # Применим тренировки
    simulated_skills = original_player.skills.copy()
    for item in training_plan:
        for _ in range(item.repeats):
            simulated_skills = simulate_training(simulated_skills, item.training_id, gain_per_skill=10)
    
    # Статистика после тренировок
    final_stats = calculate_balance_stats(simulated_skills, original_player.white_skills)
    
    print(f"\n--- СОСТОЯНИЕ ПОСЛЕ ТРЕНИРОВОК ---")
    print(f"Среднее белых навыков: {final_stats['avg']:.1f} (было {original_stats['avg']:.1f}, +{final_stats['avg']-original_stats['avg']:.1f})")
    print(f"Разница (макс-мин): {final_stats['gap']} (было {original_stats['gap']}, {'+' if final_stats['gap'] > original_stats['gap'] else ''}{final_stats['gap']-original_stats['gap']})")
    print(f"Стандартное отклонение: {final_stats['std_dev']:.1f} (было {original_stats['std_dev']:.1f}, {'+' if final_stats['std_dev'] > original_stats['std_dev'] else ''}{final_stats['std_dev']-original_stats['std_dev']:.1f})")
    print(f"Диапазон: {final_stats['min']} - {final_stats['max']} (было {original_stats['min']} - {original_stats['max']})")
    
    # Проверим, увеличились ли белые навыки
    white_increase = final_stats['avg'] - original_stats['avg']
    print(f"Средний прирост белых навыков: +{white_increase:.1f}")
    
    # Проверим, насколько улучшилась равномерность
    gap_improvement = original_stats['gap'] - final_stats['gap']
    std_improvement = original_stats['std_dev'] - final_stats['std_dev']
    
    print(f"Улучшение равномерности (снижение разницы): {gap_improvement}")
    print(f"Улучшение равномерности (снижение stddev): {std_improvement:.1f}")
    
    # Проверим серые навыки > 20
    high_gray_skills_before = {skill: original_player.skills[skill] for skill in original_player.gray_skills if original_player.skills[skill] > 20}
    high_gray_skills_after = {skill: simulated_skills[skill] for skill in original_player.gray_skills if original_player.skills[skill] > 20}
    
    print(f"\n--- ПРОВЕРКА СЕРЫХ НАВЫКОВ > 20 ---")
    if high_gray_skills_before:
        print("Серые навыки > 20 до тренировок:")
        for skill, value in high_gray_skills_before.items():
            new_value = high_gray_skills_after[skill]
            change = new_value - value
            status = "⚠️ +" if change > 0 else "✅" if change == 0 else "⬇️"
            print(f"  {SKILLS_MAP[skill]}: {value} → {new_value} ({status}{change:+d})")
        
        any_increased = any(simulated_skills[skill] > original_player.skills[skill] for skill in high_gray_skills_before)
        if any_increased:
            print("❌ НЕКОТОРЫЕ СЕРЫЕ НАВЫКИ > 20 УВЕЛИЧИЛИСЬ!")
        else:
            print("✅ НИ ОДИН СЕРЫЙ НАВЫК > 20 НЕ УВЕЛИЧИЛСЯ!")
    else:
        print("Нет серых навыков > 20 у этого игрока")
    
    print(f"\n=== ВЫВОД ===")
    if white_increase > 0 and gap_improvement >= 0:
        print("✅ АЛГОРИТМ ЭФФЕКТИВНО РАЗВИВАЕТ БЕЛЫЕ НАВЫКИ")
    else:
        print("⚠️  Белые навыки не развиваются должным образом")
    
    if trainings_with_high_gray == 0:
        print("✅ АЛГОРИТМ ЭФФЕКТИВНО ИЗБЕГАЕТ ТРЕНИРОВОК С СЕРЫМИ НАВЫКАМИ > 20")
    else:
        print(f"❌ Алгоритм выбрал {trainings_with_high_gray} тренировок с серыми навыками > 20")
    
    if not any_increased:
        print("✅ СЕРЫЕ НАВЫКИ > 20 НЕ УВЕЛИЧИЛИСЬ")
    else:
        print("❌ СЕРЫЕ НАВЫКИ > 20 УВЕЛИЧИЛИСЬ")

if __name__ == "__main__":
    main()