#!/usr/bin/env python3
"""
Тестирование усиленного штрафа за прокачку серых навыков, особенно низкоуровневых.
"""

from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner, training_difficulty


def test_gray_penalty_effectiveness():
    """Тестируем эффективность штрафа за серые навыки."""
    print("=== ТЕСТИРОВАНИЕ ЭФФЕКТИВНОСТИ ШТРАФА ЗА СЕРЫЕ НАВЫКИ ===")
    
    # Создаем игрока с позициями, которые имеют много серых навыков в тренировках
    positions = ["ST"]  # Нападающий - обычно имеет много серых навыков
    
    # Белые навыки для позиции
    white_skills = set()
    for pos in positions:
        white_skills.update(POSITIONS[pos]["white_skills"])
    
    # Создадим игрока с низкими навыками (1 для всех)
    player_skills = {}
    for skill_id in SKILLS:
        player_skills[skill_id] = 1  # Все навыки начинаются с 1
    
    # Создаём игрока
    player = Player(name="GrayPenaltyTest", positions=positions, skills=player_skills)
    
    print(f"Позиции: {positions}")
    print(f"Белые навыки ({len(white_skills)}): {sorted(list(white_skills))}")
    
    # Проверим серые навыки
    gray_skills = player.gray_skills
    print(f"Серые навыки ({len(gray_skills)}): {sorted(list(gray_skills))}")
    
    # Тестируем функцию штрафа
    print("\n--- Тестирование функции training_difficulty ---")
    test_levels = [1, 5, 10, 15, 20, 25, 30, 50, 100, 200, 300]
    for level in test_levels:
        penalty = training_difficulty(level, is_gray_skill=True)
        print(f"  Уровень {level:3d}: штраф = {penalty:4.1f}")
    
    # Формируем план тренировок
    print("\n--- Формирование плана тренировок ---")
    planner = TrainingPlanner(player)
    plan = planner.plan(max_trainings=30)
    
    print(f"План содержит {len(plan)} уникальных тренировок")
    total_trainings = sum(item.repeats for item in plan)
    print(f"Всего тренировок: {total_trainings}")
    
    # Подсчитаем, сколько тренировок влияют на серые навыки
    gray_affecting_trainings = 0
    for item in plan:
        training_data = TRAININGS[item.training_id]
        training_gray_skills = set(training_data["skills"]) & gray_skills
        if training_gray_skills:
            gray_affecting_trainings += 1
            print(f"  {item.name} - влияет на серые: {sorted(list(training_gray_skills))}")
    
    print(f"Тренировок, влияющих на серые навыки: {gray_affecting_trainings} из {len(plan)}")
    
    # Применяем план к навыкам игрока
    simulated_skills = player.skills.copy()
    for item in plan:
        training_data = TRAININGS[item.training_id]
        for _ in range(item.repeats):
            for skill_id in training_data["skills"]:
                if skill_id in simulated_skills:
                    # Увеличиваем навык с учетом максимального порога
                    simulated_skills[skill_id] = min(400, simulated_skills[skill_id] + 10)
    
    # Анализ результатов
    print("\n--- Анализ результатов ---")
    
    # Белые навыки
    white_values_final = [simulated_skills[skill] for skill in white_skills]
    min_white = min(white_values_final)
    max_white = max(white_values_final)
    avg_white = sum(white_values_final) / len(white_values_final)
    
    print(f"Белые навыки - Мин: {min_white}, Макс: {max_white}, Сред: {avg_white:.1f}, Разброс: {max_white - min_white}")
    
    # Серые навыки
    gray_values_final = [simulated_skills[skill] for skill in gray_skills]
    min_gray = min(gray_values_final)
    max_gray = max(gray_values_final)
    avg_gray = sum(gray_values_final) / len(gray_values_final)
    
    # Только серые навыки уровня <= 20
    low_gray_values = [v for v in gray_values_final if v <= 20]
    print(f"Серые навыки - Мин: {min_gray}, Макс: {max_gray}, Сред: {avg_gray:.1f}")
    print(f"Серые навыки <=20: {len(low_gray_values)} шт. из {len(gray_values_final)}")
    
    # Проверим конкретные навыки, которые должны были остаться низкоуровневыми
    print(f"Конкретные низкие серые навыки: {sorted([v for v in gray_values_final if v <= 20])[:10]}...")  # первые 10
    
    print("\n=== ВЫВОД ===")
    if avg_gray < 30:
        print("✓ Усиленный штраф работает эффективно - серые навыки остаются на низком уровне")
    else:
        print("✗ Штраф недостаточно эффективен - серые навыки развиваются слишком сильно")
    
    if max_white - min_white <= 30:
        print("✓ Белые навыки развиваются относительно равномерно")
    else:
        print("✗ Белые навыки недостаточно сбалансированы")
    
    print(f"✓ Серые навыки: средний уровень {avg_gray:.1f}, максимальный {max_gray}")


def test_multi_position_player():
    """Тестирование игрока с 3 позициями."""
    print("\n=== ТЕСТИРОВАНИЕ ИГРОКА С 3 ПОЗИЦИЯМИ ===")
    
    positions = ["DMC", "MC", "AMC"]  # 3 позиции
    
    # Белые навыки для позиций
    white_skills = set()
    for pos in positions:
        white_skills.update(POSITIONS[pos]["white_skills"])
    
    # Создадим игрока с низкими навыками
    player_skills = {skill_id: 1 for skill_id in SKILLS}
    player = Player(name="MultiPositionTest", positions=positions, skills=player_skills)
    
    print(f"Позиции: {positions}")
    print(f"Белые навыки ({len(white_skills)}): {len(white_skills)} шт.")
    
    # Формируем план
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
    
    # Анализ
    white_values = [simulated_skills[skill] for skill in white_skills]
    white_values.sort()
    
    gray_values = [simulated_skills[skill] for skill in player.gray_skills]
    gray_values.sort(reverse=True)
    
    print(f"Белые навыки: min={min(white_values)}, max={max(white_values)}, spread={max(white_values)-min(white_values)}")
    print(f"Серые навыки (топ-5): {gray_values[:5]}")
    
    # Проверка равномерности белых навыков
    white_spread = max(white_values) - min(white_values)
    avg_gray_top5 = sum(gray_values[:5]) / min(5, len(gray_values)) if gray_values else 0
    
    print(f"Разброс белых: {white_spread}, средний верхних 5 серых: {avg_gray_top5:.1f}")
    
    if white_spread <= 25 and avg_gray_top5 <= 50:
        print("✓ Алгоритм эффективно балансирует при 3 позициях")
    else:
        print("✗ Алгоритм требует дальнейшей оптимизации для 3 позиций")


if __name__ == "__main__":
    test_gray_penalty_effectiveness()
    test_multi_position_player()