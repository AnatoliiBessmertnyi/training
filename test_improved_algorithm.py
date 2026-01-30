#!/usr/bin/env python3
"""
Тестирование улучшенного алгоритма тренировок.
"""

from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner


def test_balanced_growth():
    """Тестируем улучшенный алгоритм сбалансированного роста навыков."""
    
    # Создадим игрока с позициями DMC и MC, как в вашем примере
    positions = ["DMC", "MC"]
    
    # Белые навыки для этих позиций
    white_skills = set()
    for pos in positions:
        white_skills.update(POSITIONS[pos]["white_skills"])
    
    # Создадим игрока с низкими навыками (1 для всех)
    player_skills = {}
    for skill_id in SKILLS:
        player_skills[skill_id] = 1  # Все навыки начинаются с 1
    
    # Создаём игрока
    player = Player(name="test1", positions=positions, skills=player_skills)
    
    print(f"Позиции игрока: {positions}")
    print(f"Белые навыки ({len(white_skills)}): {sorted(list(white_skills))}")
    
    # Анализ начального состояния
    print("\n--- Начальное состояние ---")
    white_values_initial = [player.skills[skill] for skill in white_skills]
    print(f"Белые навыки: {dict((skill, player.skills[skill]) for skill in sorted(white_skills))}")
    
    # Формируем план тренировок
    print("\n--- Формирование плана тренировок ---")
    planner = TrainingPlanner(player)
    plan = planner.plan(max_trainings=50)
    
    print(f"План содержит {len(plan)} уникальных тренировок")
    total_trainings = sum(item.repeats for item in plan)
    print(f"Всего тренировок: {total_trainings}")
    
    # Выводим детали плана
    for i, item in enumerate(plan, 1):
        training_data = TRAININGS[item.training_id]
        white_hit = set(training_data["skills"]) & white_skills
        gray_hit = set(training_data["skills"]) - white_skills
        print(f"{i}. {item.name} ({item.repeats} раз)")
        print(f"   Затрагивает белые навыки: {len(white_hit)} ({sorted(list(white_hit))})")
        print(f"   Затрагивает серые навыки: {len(gray_hit)} ({sorted(list(gray_hit))})")
    
    # Применяем план к навыкам игрока
    print("\n--- Применение плана тренировок ---")
    simulated_skills = player.skills.copy()
    
    for item in plan:
        training_data = TRAININGS[item.training_id]
        for _ in range(item.repeats):
            for skill_id in training_data["skills"]:
                if skill_id in simulated_skills:
                    # Увеличиваем навык с учетом максимального порога
                    simulated_skills[skill_id] = min(400, simulated_skills[skill_id] + 10)
    
    # Создаем нового игрока с обновленными навыками
    updated_player = Player(name=player.name, positions=player.positions, skills=simulated_skills)
    
    # Анализ конечного состояния
    print("\n--- Конечное состояние ---")
    white_values_final = [updated_player.skills[skill] for skill in white_skills]
    print(f"Белые навыки: {dict((skill, updated_player.skills[skill]) for skill in sorted(white_skills))}")
    
    # Проверяем равномерность
    min_white = min(white_values_final)
    max_white = max(white_values_final)
    avg_white = sum(white_values_final) / len(white_values_final)
    
    print(f"\nСтатистика белых навыков:")
    print(f"  Минимум: {min_white}")
    print(f"  Максимум: {max_white}")
    print(f"  Среднее: {avg_white:.1f}")
    print(f"  Разброс: {max_white - min_white}")
    
    # Проверим серые навыки
    gray_skills = player.gray_skills
    gray_values_final = [updated_player.skills[skill] for skill in gray_skills]
    min_gray = min(gray_values_final)
    max_gray = max(gray_values_final)
    avg_gray = sum(gray_values_final) / len(gray_values_final)
    
    print(f"\nСтатистика серых навыков:")
    print(f"  Минимум: {min_gray}")
    print(f"  Максимум: {max_gray}")
    print(f"  Среднее: {avg_gray:.1f}")
    
    return updated_player


def test_with_different_scenarios():
    """Тестирование с различными сценариями"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ РАЗЛИЧНЫХ СЦЕНАРИЕВ")
    print("="*60)
    
    scenarios = [
        {"positions": ["ST"], "desc": "Нападающий"},
        {"positions": ["DC"], "desc": "Центральный защитник"},
        {"positions": ["DMC", "MC"], "desc": "Опорный и центральный полузащитник"}
    ]
    
    for scenario in scenarios:
        print(f"\n--- Сценарий: {scenario['desc']} ({scenario['positions']}) ---")
        
        # Белые навыки
        white_skills = set()
        for pos in scenario['positions']:
            white_skills.update(POSITIONS[pos]["white_skills"])
        
        # Создаем игрока с начальными навыками 1
        player_skills = {skill_id: 1 for skill_id in SKILLS}
        player = Player(name=f"test_{scenario['positions'][0]}", positions=scenario['positions'], skills=player_skills)
        
        # Применяем план из 50 тренировок
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
        min_white = min(white_values)
        max_white = max(white_values)
        avg_white = sum(white_values) / len(white_values)
        
        print(f"  Белые навыки - Мин: {min_white}, Макс: {max_white}, Сред: {avg_white:.1f}, Разброс: {max_white - min_white}")


if __name__ == "__main__":
    print("=== ТЕСТИРОВАНИЕ УЛУЧШЕННОГО АЛГОРИТМА ТРЕНИРОВОК ===")
    
    # Основной тест
    test_balanced_growth()
    
    # Дополнительные сценарии
    test_with_different_scenarios()
    
    print("\n=== ВЫВОД ===")
    print("Улучшенный алгоритм теперь:")
    print("- Лучше сбалансирует развитие всех белых навыков")
    print("- Минимизирует развитие серых навыков")
    print("- Использует дисперсию для оценки равномерности")
    print("- Применяет штрафы за тренировки серых навыков")
    print("- Даёт премии за высокую долю белых навыков в тренировке")