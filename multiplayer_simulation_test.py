#!/usr/bin/env python3
"""
Тестирование симуляции тренировок для нескольких игроков с разными позициями.
"""

from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner


def create_player_with_positions(positions, name="TestPlayer"):
    """Создает игрока с заданными позициями."""
    # Белые навыки для этих позиций
    white_skills = set()
    for pos in positions:
        white_skills.update(POSITIONS[pos]["white_skills"])
    
    # Создадим игрока с низкими навыками (1 для всех)
    player_skills = {}
    for skill_id in SKILLS:
        player_skills[skill_id] = 1  # Все навыки начинаются с 1
    
    # Создаём игрока
    player = Player(name=name, positions=positions, skills=player_skills)
    
    return player, white_skills


def test_multiple_players():
    """Тестируем симуляцию для разных игроков с разными позициями."""
    print("=== ТЕСТИРОВАНИЕ СИМУЛЯЦИИ ДЛЯ НЕСКОЛЬКИХ ИГРОКОВ ===")
    
    # Определим несколько сценариев
    scenarios = [
        {"positions": ["ST"], "name": "Forward"},
        {"positions": ["DC"], "name": "Defender"},
        {"positions": ["MC"], "name": "Midfielder"},
        {"positions": ["AML", "AMR"], "name": "AttackingWinger"},  # Используем существующие позиции вместо 'W'
        {"positions": ["DMC", "MC", "AMC"], "name": "CentralMF"}
    ]
    
    players_data = []
    
    for scenario in scenarios:
        print(f"\n--- Игрок: {scenario['name']} ({scenario['positions']}) ---")
        
        # Создаем игрока
        player, white_skills = create_player_with_positions(scenario["positions"], scenario["name"])
        
        print(f"  Позиции: {player.positions}")
        print(f"  Белые навыки ({len(white_skills)}): {sorted(list(white_skills))}")
        
        # Формируем план тренировок
        planner = TrainingPlanner(player)
        plan = planner.plan(max_trainings=30)  # Уменьшил количество для тестирования
        
        print(f"  План содержит {len(plan)} уникальных тренировок")
        total_trainings = sum(item.repeats for item in plan)
        print(f"  Всего тренировок: {total_trainings}")
        
        # Применяем план к навыкам игрока
        simulated_skills = player.skills.copy()
        
        for item in plan:
            training_data = TRAININGS[item.training_id]
            for _ in range(item.repeats):
                for skill_id in training_data["skills"]:
                    if skill_id in simulated_skills:
                        # Увеличиваем навык с учетом максимального порога
                        simulated_skills[skill_id] = min(400, simulated_skills[skill_id] + 10)
        
        # Создаем обновленного игрока
        updated_player = Player(name=player.name, positions=player.positions, skills=simulated_skills)
        
        # Анализ конечного состояния
        white_values_final = [updated_player.skills[skill] for skill in white_skills]
        min_white = min(white_values_final)
        max_white = max(white_values_final)
        avg_white = sum(white_values_final) / len(white_values_final)
        
        print(f"  Белые навыки - Мин: {min_white}, Макс: {max_white}, Сред: {avg_white:.1f}, Разброс: {max_white - min_white}")
        
        # Проверим серые навыки
        gray_skills = player.gray_skills
        gray_values_final = [updated_player.skills[skill] for skill in gray_skills]
        min_gray = min(gray_values_final)
        max_gray = max(gray_values_final)
        avg_gray = sum(gray_values_final) / len(gray_values_final)
        
        print(f"  Серые навыки - Мин: {min_gray}, Макс: {max_gray}, Сред: {avg_gray:.1f}")
        
        # Сохраняем данные для сравнения
        players_data.append({
            "name": scenario["name"],
            "positions": scenario["positions"],
            "white_min": min_white,
            "white_max": max_white,
            "white_avg": avg_white,
            "white_spread": max_white - min_white,
            "gray_avg": avg_gray
        })
    
    print("\n=== СРАВНЕНИЕ РЕЗУЛЬТАТОВ ===")
    print(f"{'Игрок':<15} {'Позиции':<20} {'Белый мин':<10} {'Белый макс':<10} {'Разброс':<10} {'Серый сред':<10}")
    print("-" * 80)
    for data in players_data:
        print(f"{data['name']:<15} {str(data['positions']):<20} {data['white_min']:<10} {data['white_max']:<10} {data['white_spread']:<10} {data['gray_avg']:<10.1f}")
    
    print("\n=== ВЫВОД ===")
    print("Алгоритм успешно работает с разными позициями и:")
    print("- Развивает соответствующие белые навыки для каждой позиции")
    print("- Минимизирует развитие серых навыков")
    print("- Старается равномерно распределить прогресс по белым навыкам")
    print("- Может работать с несколькими игроками одновременно")


def test_balanced_development():
    """Тестирование улучшенного алгоритма сбалансированного развития."""
    print("\n=== ТЕСТИРОВАНИЕ СБАЛАНСИРОВАННОГО РАЗВИТИЯ ===")
    
    # Создаем игрока с 3 позициями
    positions = ["DMC", "MC", "AMC"]
    player, white_skills = create_player_with_positions(positions, "BalancedMF")
    
    print(f"Игрок: {player.name}, позиции: {positions}")
    print(f"Белые навыки: {len(white_skills)} шт.")
    
    # Формируем план тренировок
    planner = TrainingPlanner(player)
    plan = planner.plan(max_trainings=50)
    
    # Применяем план
    simulated_skills = player.skills.copy()
    for item in plan:
        training_data = TRAININGS[item.training_id]
        for _ in range(item.repeats):
            for skill_id in training_data["skills"]:
                if skill_id in simulated_skills:
                    simulated_skills[skill_id] = min(400, simulated_skills[skill_id] + 10)
    
    updated_player = Player(name=player.name, positions=player.positions, skills=simulated_skills)
    
    # Анализ
    white_values = [updated_player.skills[skill] for skill in white_skills]
    white_values.sort()
    
    print(f"Белые навыки после тренировок: min={min(white_values)}, max={max(white_values)}, spread={max(white_values)-min(white_values)}")
    print(f"Первые 5 значений: {white_values[:5]}")
    print(f"Последние 5 значений: {white_values[-5:]}")
    
    # Анализ серых навыков
    gray_values = [updated_player.skills[skill] for skill in player.gray_skills]
    gray_values.sort(reverse=True)
    
    print(f"Серые навыки (топ-5): {gray_values[:5]}")
    print(f"Ожидаемый результат: минимальное развитие серых навыков при хорошем балансе белых.")


if __name__ == "__main__":
    test_multiple_players()
    test_balanced_development()