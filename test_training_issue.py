#!/usr/bin/env python3
"""
Тестирование алгоритма тренировки на игроке Smith (DC).
Цель: проверить проблему с равномерностью навыков при высоких уровнях.
"""

import json
from domain.training_planner import TrainingPlanner
from domain.player import Player


def load_players():
    """Загружаем игроков из JSON файла."""
    with open('storage/players.json', 'r') as f:
        data = json.load(f)
    return data['players']


def analyze_skills(player):
    """Анализ навыков игрока."""
    white_skills = player.white_skills
    gray_skills = player.gray_skills
    
    white_values = {skill: player.skills[skill] for skill in white_skills}
    gray_values = {skill: player.skills[skill] for skill in gray_skills}
    
    print("=== Анализ навыков ===")
    print(f"Все навыки: {len(player.skills)}")
    print(f"Белые навыки ({len(white_skills)}): {sorted(white_skills)}")
    print(f"Серые навыки ({len(gray_skills)}): {sorted(gray_skills)}")
    
    all_values = list(player.skills.values())
    avg_all = sum(all_values) / len(all_values)
    
    white_vals = list(white_values.values())
    avg_white = sum(white_vals) / len(white_vals) if white_vals else 0
    
    gray_vals = list(gray_values.values())
    avg_gray = sum(gray_vals) / len(gray_vals) if gray_vals else 0
    
    min_white = min(white_vals) if white_vals else 0
    max_white = max(white_vals) if white_vals else 0
    diff_white = max_white - min_white
    
    print(f"\nСредние значения:")
    print(f"Все навыки: {avg_all:.2f}")
    print(f"Белые навыки: {avg_white:.2f}")
    print(f"Серые навыки: {avg_gray:.2f}")
    
    print(f"\nРазница (сильнейший-слабейший): {diff_white}")
    
    # Найдем слабые и сильные белые навыки
    sorted_white = sorted(white_values.items(), key=lambda x: x[1])
    weak_white = sorted_white[:3]  # 3 самых слабых
    strong_white = sorted_white[-3:]  # 3 самых сильных
    
    print(f"\nСлабые белые навыки: {[f'{skill} ({value})' for skill, value in weak_white]}")
    print(f"Перекачанные белые навыки: {[f'{skill} ({value})' for skill, value in strong_white]}")
    
    return {
        'avg_all': avg_all,
        'avg_white': avg_white,
        'avg_gray': avg_gray,
        'diff_white': diff_white,
        'weak_white': weak_white,
        'strong_white': strong_white
    }


def run_training_cycle(player, num_cycles=10):
    """Запустить несколько циклов тренировки и проанализировать изменения."""
    print(f"=== Запуск {num_cycles} циклов тренировки ===")
    
    for i in range(num_cycles):
        print(f"\n--- Цикл {i+1} ---")
        
        # Создаем планировщик тренировок
        planner = TrainingPlanner(player)
        
        # Планируем 10 тренировок
        plan = planner.plan(max_trainings=10)
        
        print(f"Планируемые тренировки:")
        for item in plan:
            print(f"  {item.name} ({item.repeats} раз)")
        
        # Применяем тренировки к игроку
        from config.trainings import TRAININGS
        for item in plan:
            training_data = TRAININGS[item.training_id]
            for _ in range(item.repeats):
                for skill in training_data["skills"]:
                    if skill in player.skills:
                        # Увеличиваем навык с учетом максимального порога
                        player.skills[skill] = min(400, player.skills[skill] + 10)
        
        # Анализируем навыки после тренировки
        stats = analyze_skills(player)
        
        # Проверяем, не усугубилась ли проблема
        if stats['diff_white'] > 50:
            print(f"ВНИМАНИЕ: Разница белых навыков превысила 50! Текущее значение: {stats['diff_white']}")
        
        print(f"Цикл {i+1} завершен.")


def main():
    players_data = load_players()
    
    # Найдем игрока Smith
    smith_data = None
    for p in players_data:
        if p['name'] == 'Smith':
            smith_data = p
            break
    
    if not smith_data:
        print("Игрок Smith не найден!")
        return
    
    print(f"Тестируем игрока: {smith_data['name']} (позиция: {smith_data['positions']})")
    
    # Создаем объект игрока
    player = Player(
        name=smith_data['name'],
        positions=smith_data['positions'],
        skills=smith_data['skills']
    )
    
    print("\n=== Исходное состояние ===")
    analyze_skills(player)
    
    # Запускаем циклы тренировки
    run_training_cycle(player, num_cycles=10)
    
    print("\n=== Финальное состояние ===")
    analyze_skills(player)


if __name__ == "__main__":
    main()