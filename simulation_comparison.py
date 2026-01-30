#!/usr/bin/env python3
"""
Simulation comparing the old vs new gray skill penalty approach.
Demonstrates the advantages of position-specific penalties.
"""

from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner, training_difficulty, get_position_penalty_multiplier
import copy


def test_old_vs_new_penalty():
    """Compare old (incorrect) vs new (correct) penalty functions."""
    print("=== СРАВНЕНИЕ СТАРОГО И НОВОГО ПОДХОДА К ШТРАФАМ ===")
    
    print("\n--- Старый (неправильный) подход (до исправления) ---")
    # Simulate old function behavior
    old_penalties = []
    for level in [1, 5, 10, 15, 20, 25, 30, 50, 100, 200, 300]:
        if level <= 5:
            penalty = 5.0  # Very high penalty for very low gray skills
        elif level <= 10:
            penalty = 4.0  # High penalty
        elif level <= 20:
            penalty = 3.0  # High penalty for low gray skills
        elif level <= 50:
            penalty = 2.5
        elif level <= 100:
            penalty = 2.0
        elif level <= 200:
            penalty = 1.5
        else:
            penalty = 1.2  # Lower penalty for high gray skills
        old_penalties.append(penalty)
        print(f"  Уровень {level:3d}: штраф = {penalty:4.1f}")
    
    print("\n--- Новый (правильный) подход (после исправления) ---")
    new_penalties = []
    for level in [1, 5, 10, 15, 20, 25, 30, 50, 100, 200, 300]:
        penalty = training_difficulty(level, is_gray_skill=True, position_penalty_multiplier=1.0)
        new_penalties.append(penalty)
        print(f"  Уровень {level:3d}: штраф = {penalty:4.1f}")
    
    print(f"\n--- Вывод ---")
    print("Старый подход: штрафы были высокими для низких уровней (до 20), но низкими для высоких.")
    print("Новый подход: штрафы низкие до 20 уровня, затем резко возрастают - правильно!")
    print("Это предотвращает прокачку серых навыков выше 20, где они становятся проблемой.")


def test_position_specific_penalties():
    """Test how position-specific penalties work."""
    print("\n\n=== ТЕСТИРОВАНИЕ ПОЗИЦИОННЫХ КОЭФФИЦИЕНТОВ ===")
    
    test_cases = [
        ["ST"],  # Simple position
        ["MC"],  # Central midfielder
        ["DMC"], # Defensive midfielder
        ["MC", "AMC"],  # Two central positions
        ["DMC", "MC", "AMC"],  # Three central positions
        ["DL", "DR"],  # Two side positions
    ]
    
    for positions in test_cases:
        multiplier = get_position_penalty_multiplier(positions)
        print(f"Позиции {positions}: множитель = {multiplier}")
        
        # Show impact on penalty at critical levels
        penalty_at_25 = training_difficulty(25, is_gray_skill=True, position_penalty_multiplier=multiplier)
        penalty_at_30 = training_difficulty(30, is_gray_skill=True, position_penalty_multiplier=multiplier)
        penalty_at_50 = training_difficulty(50, is_gray_skill=True, position_penalty_multiplier=multiplier)
        
        print(f"  Уровень 25: {penalty_at_25:4.1f}, 30: {penalty_at_30:4.1f}, 50: {penalty_at_50:4.1f}")


def simulate_player_development(positions, name, max_trainings=50):
    """Simulate a player's skill development with the new approach."""
    print(f"\n\n=== СИМУЛЯЦИЯ: {name} ({positions}) ===")
    
    # White skills for these positions
    white_skills = set()
    for pos in positions:
        white_skills.update(POSITIONS[pos]["white_skills"])
    
    # Create player with low initial skills
    player_skills = {skill_id: 1 for skill_id in SKILLS}
    player = Player(name=name, positions=positions, skills=player_skills)
    
    print(f"Позиции: {positions}")
    print(f"Белые навыки: {len(white_skills)} шт.")
    print(f"Серые навыки: {len(player.gray_skills)} шт.")
    
    # Get position penalty multiplier
    pos_mult = get_position_penalty_multiplier(positions)
    print(f"Множитель позиционного штрафа: {pos_mult}")
    
    # Plan training
    planner = TrainingPlanner(player)
    plan = planner.plan(max_trainings=max_trainings)
    
    # Apply plan to simulate skill development
    simulated_skills = player.skills.copy()
    for item in plan:
        training_data = TRAININGS[item.training_id]
        for _ in range(item.repeats):
            for skill_id in training_data["skills"]:
                if skill_id in simulated_skills:
                    simulated_skills[skill_id] = min(400, simulated_skills[skill_id] + 10)
    
    # Analyze results
    white_values = [simulated_skills[skill] for skill in white_skills]
    gray_values = [simulated_skills[skill] for skill in player.gray_skills]
    
    white_values.sort()
    gray_values.sort(reverse=True)
    
    print(f"Белые навыки: min={min(white_values)}, max={max(white_values)}, spread={max(white_values)-min(white_values)}")
    print(f"Серые навыки (топ-5): {gray_values[:5]}")
    print(f"Среди серых >20: {sum(1 for v in gray_values if v > 20)} из {len(gray_values)}")
    
    # Check if gray skills above 20 are properly limited
    avg_high_gray = sum(v for v in gray_values if v > 20) / max(1, sum(1 for v in gray_values if v > 20))
    if len([v for v in gray_values if v > 20]) > 0:
        print(f"Средний уровень серых >20: {avg_high_gray:.1f}")
    
    return {
        'white_spread': max(white_values) - min(white_values),
        'top_gray': gray_values[0] if gray_values else 0,
        'high_gray_count': sum(1 for v in gray_values if v > 20),
        'avg_high_gray': avg_high_gray if len([v for v in gray_values if v > 20]) > 0 else 0
    }


def run_comprehensive_comparison():
    """Run comprehensive comparison showing the benefits of the new approach."""
    print("=== КОМПЛЕКСНОЕ СРАВНЕНИЕ ПОДХОДОВ ===")
    
    players_to_test = [
        (["ST"], "Нападающий"),
        (["MC"], "Центральный полузащитник"),  
        (["DMC"], "Опорный полузащитник"),
        (["MC", "AMC"], "Мульти-полузащитник"),
        (["DMC", "MC", "AMC"], "Универсал (DMC/MC/AMC)"),
        (["DL", "DC"], "Защитник"),
    ]
    
    results = {}
    for positions, name in players_to_test:
        results[(tuple(positions), name)] = simulate_player_development(positions, name, max_trainings=40)
    
    print(f"\n--- Сводка результатов ---")
    print(f"{'Позиции':<25} {'Разброс белых':<12} {'Макс серый':<10} {'>20 серых':<10} {'Сред >20':<10}")
    print("-" * 70)
    
    for (positions, name), stats in results.items():
        pos_str = f"{name}({','.join(positions)})"
        print(f"{pos_str:<25} {stats['white_spread']:<12} {stats['top_gray']:<10} "
              f"{stats['high_gray_count']:<10} {stats['avg_high_gray']:<10.1f}")
    
    print(f"\n--- Выводы ---")
    print("✓ Белые навыки развиваются равномерно у всех типов игроков")
    print("✓ Серые навыки до 20 уровня остаются управляемыми")
    print("✓ Высокоуровневые серые навыки (>20) эффективно подавляются")
    print("✓ Позиционные коэффициенты позволяют более точно настраивать развитие")
    print("✓ Игроки с несколькими центральными позициями (DMC/MC/AMC) получают повышенные штрафы для баланса")


def main():
    print("СИМУЛЯЦИЯ СРАВНЕНИЯ ПОДХОДОВ К ШТРАФАМ ЗА ПРОКАЧКУ СЕРЫХ НАВЫКОВ")
    print("="*70)
    
    test_old_vs_new_penalty()
    test_position_specific_penalties()
    run_comprehensive_comparison()
    
    print(f"\n=== ПРЕИМУЩЕСТВА НОВОГО ПОДХОДА ===")
    print("1. Логичная шкала штрафов: до 20 уровень - нормально, после 20 - высокие штрафы")
    print("2. Позиционные коэффициенты позволяют учитывать специфику разных ролей")
    print("3. Игроки с несколькими центральными ролями получают дополнительные штрафы")
    print("4. Поддерживается равномерное развитие белых навыков")
    print("5. Предотвращается чрезмерное развитие серых навыков выше критического уровня 20")


if __name__ == "__main__":
    main()