#!/usr/bin/env python3
"""
Подробное тестирование улучшенного алгоритма тренировок.
"""

from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner


def detailed_test():
    """Подробное тестирование с отслеживанием процесса"""
    
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
    
    # Создаем планировщик
    planner = TrainingPlanner(player)
    
    # Применяем тренировки пошагово с отслеживанием
    print("\n--- Пошаговое применение тренировок ---")
    simulated_skills = player.skills.copy()
    
    # Словарь для отслеживания количества тренировок для каждого белого навыка
    skill_training_counts = {skill: 0 for skill in white_skills}
    
    training_sequence = []
    
    for step in range(10):  # Проверим первые 10 шагов
        print(f"\nШаг {step + 1}:")
        
        # Находим лучшую тренировку
        best_training_id = planner._find_best_training(simulated_skills, skill_training_counts)
        
        if best_training_id is None:
            print("  Нет подходящей тренировки")
            break
        
        training_data = TRAININGS[best_training_id]
        print(f"  Выбрана тренировка: {training_data['name']}")
        print(f"  Затрагиваемые навыки: {training_data['skills']}")
        
        # Применяем тренировку
        for skill_id in training_data["skills"]:
            if skill_id in simulated_skills:
                # Увеличиваем навык с учетом максимального порога
                simulated_skills[skill_id] = min(400, simulated_skills[skill_id] + 10)
        
        # Обновляем счетчики тренировок для белых навыков
        for skill in training_data["skills"]:
            if skill in white_skills:
                skill_training_counts[skill] += 1
        
        training_sequence.append(best_training_id)
        
        # Показываем текущее состояние белых навыков
        white_values = [simulated_skills[skill] for skill in white_skills]
        min_white = min(white_values)
        max_white = max(white_values)
        avg_white = sum(white_values) / len(white_values)
        
        print(f"  Белые навыки - Мин: {min_white}, Макс: {max_white}, Сред: {avg_white:.1f}, Разброс: {max_white - min_white}")
        print(f"  Счетчики тренировок: {dict(sorted(skill_training_counts.items(), key=lambda x: -x[1]))}")
    
    # Теперь применим полный план из 50 тренировок
    print("\n--- Применение полного плана из 50 тренировок ---")
    full_plan = planner.plan(max_trainings=50)
    
    print(f"План содержит {len(full_plan)} уникальных тренировок")
    total_trainings = sum(item.repeats for item in full_plan)
    print(f"Всего тренировок: {total_trainings}")
    
    # Выводим детали плана
    for i, item in enumerate(full_plan, 1):
        training_data = TRAININGS[item.training_id]
        white_hit = set(training_data["skills"]) & white_skills
        gray_hit = set(training_data["skills"]) - white_skills
        print(f"{i}. {item.name} ({item.repeats} раз)")
        print(f"   Затрагивает белые навыки: {len(white_hit)} ({sorted(list(white_hit))})")
        print(f"   Затрагивает серые навыки: {len(gray_hit)} ({sorted(list(gray_hit))})")
    
    # Применяем полный план
    final_simulated_skills = player.skills.copy()
    for item in full_plan:
        training_data = TRAININGS[item.training_id]
        for _ in range(item.repeats):
            for skill_id in training_data["skills"]:
                if skill_id in final_simulated_skills:
                    # Увеличиваем навык с учетом максимального порога
                    final_simulated_skills[skill_id] = min(400, final_simulated_skills[skill_id] + 10)
    
    # Создаем нового игрока с обновленными навыками
    updated_player = Player(name=player.name, positions=player.positions, skills=final_simulated_skills)
    
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


if __name__ == "__main__":
    print("=== ПОДРОБНОЕ ТЕСТИРОВАНИЕ УЛУЧШЕННОГО АЛГОРИТМА ===")
    detailed_test()