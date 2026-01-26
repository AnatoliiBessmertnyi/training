from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner


def analyze_white_skills_balance(player: Player):
    """Анализирует равномерность белых навыков"""
    white_skills = set(player.white_skills)
    white_values = [player.skills[skill] for skill in white_skills]
    
    min_val = min(white_values)
    max_val = max(white_values)
    avg_val = sum(white_values) / len(white_values)
    spread = max_val - min_val
    
    print(f"  Минимум белых: {min_val}")
    print(f"  Максимум белых: {max_val}")
    print(f"  Среднее белых: {avg_val:.1f}")
    print(f"  Разброс белых: {spread}")
    
    return spread


def simulate_plan_execution(player: Player, plan):
    """Симулирует выполнение плана тренировок"""
    # Создаем копию навыков для симуляции
    simulated_skills = player.skills.copy()
    
    print("\n--- Симуляция выполнения плана ---")
    for item in plan:
        training_data = TRAININGS[item.training_id]
        print(f"\nВыполняем '{item.name}' {item.repeats} раз:")
        
        for _ in range(item.repeats):
            for skill_id in training_data["skills"]:
                if skill_id in simulated_skills:
                    old_value = simulated_skills[skill_id]
                    new_value = min(400, old_value + 10)  # BASE_TRAINING_GAIN = 10
                    simulated_skills[skill_id] = new_value
                    # Выводим только значительные изменения для краткости
                    if skill_id in player.white_skills and new_value != old_value:
                        pass  # Не выводим каждое изменение для краткости
        
        # После каждой тренировки показываем состояние белых навыков
        white_skills = set(player.white_skills)
        white_values = [simulated_skills[skill] for skill in white_skills]
        min_val = min(white_values)
        max_val = max(white_values)
        spread = max_val - min_val
        print(f"  Текущий разброс белых навыков: {spread}")

    # Создаем игрока с новыми навыками для анализа
    new_player = Player(name=player.name, positions=player.positions, skills=simulated_skills)
    
    print(f"\n--- Анализ после выполнения плана ---")
    print(f"Разброс белых навыков ДО: {analyze_white_skills_balance(player)}")
    print(f"Разброс белых навыков ПОСЛЕ: {analyze_white_skills_balance(new_player)}")


def main():
    print("=== Тест: Проверка улучшения равномерности белых навыков ===\n")

    # Создадим игрока с несбалансированными навыками (например, сильный в одних, слабый в других)
    positions = ["ST"]  # Нападающий
    
    # Белые навыки для ST
    white_skills = set()
    for pos in positions:
        white_skills.update(POSITIONS[pos]["white_skills"])
    
    # Создадим сильно несбалансированные навыки
    player_skills = {
        # Очень высокие навыки
        "finishing": 350,
        "shooting": 340,
        "pace": 320,
        
        # Высокие навыки
        "dribbling": 200,
        "physical": 180,
        "strength": 160,
        
        # Средние навыки
        "positioning": 100,
        "heading": 90,
        
        # Очень низкие навыки (проблемные)
        "passing": 30,
        "creativity": 25,
    }
    
    # Заполняем остальные навыки минимальным значением
    for skill_id in SKILLS:
        if skill_id not in player_skills:
            player_skills[skill_id] = 1

    # Создаём игрока
    player = Player(name="Тестовый игрок", positions=positions, skills=player_skills)

    print(f"Позиция игрока: {positions}")
    print(f"Белые навыки: {len(white_skills)} шт.")
    
    print(f"\n--- Анализ начального состояния ---")
    initial_spread = analyze_white_skills_balance(player)
    
    # Формируем план тренировок
    planner = TrainingPlanner(player)
    plan = planner.plan(max_trainings=15)

    # Вывод плана
    print(f"\n--- Рекомендуемый план тренировок ---")
    if not plan:
        print("Нет подходящих тренировок для балансировки белых навыков")
    else:
        total_trainings = sum(item.repeats for item in plan)
        print(f"Всего тренировок в плане: {total_trainings}")
        for i, item in enumerate(plan, 1):
            skills_covered = TRAININGS[item.training_id]["skills"]
            white_covered = [skill for skill in skills_covered if skill in white_skills]
            gray_covered = [skill for skill in skills_covered if skill not in white_skills]
            print(f"{i}. {item.name} ({item.repeats} раз)")
            print(f"   Белые навыки: {len(white_covered)}, Серые навыки: {len(gray_covered)}")
            print(f"   Затрагивает: {[SKILLS[s] for s in white_covered]}")
    
    # Симулируем выполнение плана
    simulate_plan_execution(player, plan)


if __name__ == "__main__":
    main()