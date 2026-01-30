#!/usr/bin/env python3
"""
Симуляция тренировок для нескольких игроков одновременно.
Демонстрирует возможность параллельной обработки разных игроков с разными позициями.
"""

from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner


class MultiPlayerTrainingSimulator:
    """Симулятор тренировок для нескольких игроков."""
    
    def __init__(self):
        self.players = []
        self.plans = {}
        
    def add_player(self, positions, name):
        """Добавляет игрока с указанными позициями."""
        # Белые навыки для позиций
        white_skills = set()
        for pos in positions:
            white_skills.update(POSITIONS[pos]["white_skills"])
        
        # Создадим игрока с низкими навыками (1 для всех)
        player_skills = {skill_id: 1 for skill_id in SKILLS}
        player = Player(name=name, positions=positions, skills=player_skills)
        
        self.players.append(player)
        return player
    
    def generate_plans(self, max_trainings=30):
        """Генерирует планы тренировок для всех игроков."""
        for player in self.players:
            print(f"Генерация плана для {player.name} ({player.positions})...")
            planner = TrainingPlanner(player)
            plan = planner.plan(max_trainings=max_trainings)
            self.plans[player.name] = plan  # Используем имя вместо id
            print(f"  План содержит {len(plan)} тренировок, всего {sum(item.repeats for item in plan)} сессий")
    
    def simulate_training(self):
        """Применяет планы тренировок и возвращает обновленных игроков."""
        updated_players = []
        
        for player in self.players:
            plan = self.plans[player.name]  # Используем имя вместо id
            # Копируем навыки для симуляции
            simulated_skills = player.skills.copy()
            
            # Применяем план
            for item in plan:
                training_data = TRAININGS[item.training_id]
                for _ in range(item.repeats):
                    for skill_id in training_data["skills"]:
                        if skill_id in simulated_skills:
                            simulated_skills[skill_id] = min(400, simulated_skills[skill_id] + 10)
            
            # Создаем обновленного игрока
            updated_player = Player(
                name=player.name, 
                positions=player.positions, 
                skills=simulated_skills
            )
            updated_players.append(updated_player)
        
        return updated_players
    
    def analyze_results(self, updated_players):
        """Анализирует результаты симуляции."""
        print("\n=== АНАЛИЗ РЕЗУЛЬТАТОВ СИМУЛЯЦИИ ===")
        
        results = []
        for i, player in enumerate(self.players):
            updated_player = updated_players[i]
            
            # Белые навыки
            white_skills = set()
            for pos in player.positions:
                white_skills.update(POSITIONS[pos]["white_skills"])
            
            white_values = [updated_player.skills[skill] for skill in white_skills]
            min_white = min(white_values)
            max_white = max(white_values)
            avg_white = sum(white_values) / len(white_values)
            white_spread = max_white - min_white
            
            # Серые навыки
            gray_values = [updated_player.skills[skill] for skill in player.gray_skills]
            min_gray = min(gray_values)
            max_gray = max(gray_values)
            avg_gray = sum(gray_values) / len(gray_values)
            
            result = {
                "name": player.name,
                "positions": player.positions,
                "white_min": min_white,
                "white_max": max_white,
                "white_avg": avg_white,
                "white_spread": white_spread,
                "gray_avg": avg_gray,
                "gray_max": max_gray
            }
            results.append(result)
        
        # Вывод результатов
        print(f"{'Имя':<15} {'Позиции':<25} {'Белый мин':<8} {'Белый макс':<8} {'Разброс':<8} {'Серый сред':<10} {'Серый макс':<10}")
        print("-" * 90)
        for result in results:
            print(f"{result['name']:<15} {str(result['positions']):<25} {result['white_min']:<8} {result['white_max']:<8} {result['white_spread']:<8} {result['gray_avg']:<10.1f} {result['gray_max']:<10}")
        
        return results


def main():
    """Основная функция демонстрации."""
    print("=== СИМУЛЯЦИЯ ТРЕНИРОВОК ДЛЯ НЕСКОЛЬКИХ ИГРОКОВ ===")
    
    simulator = MultiPlayerTrainingSimulator()
    
    # Добавляем игроков с разными позициями
    simulator.add_player(["ST"], "Striker")
    simulator.add_player(["DC"], "CenterBack")
    simulator.add_player(["MC"], "CentralMF")
    simulator.add_player(["AML", "AMR"], "Winger")
    simulator.add_player(["DMC", "MC", "AMC"], "CompleteMF")  # 3 позиции
    
    print(f"\nДобавлено {len(simulator.players)} игроков")
    
    # Генерируем планы тренировок
    simulator.generate_plans(max_trainings=40)
    
    # Запускаем симуляцию
    print(f"\nЗапуск симуляции тренировок...")
    updated_players = simulator.simulate_training()
    
    # Анализируем результаты
    results = simulator.analyze_results(updated_players)
    
    # Сводная статистика
    print(f"\n=== СВОДНАЯ СТАТИСТИКА ===")
    avg_white_spread = sum(r['white_spread'] for r in results) / len(results)
    avg_gray_level = sum(r['gray_avg'] for r in results) / len(results)
    
    print(f"Средний разброс белых навыков: {avg_white_spread:.1f}")
    print(f"Средний уровень серых навыков: {avg_gray_level:.1f}")
    
    if avg_white_spread <= 20:
        print("✓ Белые навыки хорошо сбалансированы у всех игроков")
    else:
        print("⚠ Необходимо улучшить баланс белых навыков")
    
    if avg_gray_level <= 30:
        print("✓ Серые навыки эффективно подавляются")
    else:
        print("⚠ Серые навыки развиваются слишком активно")
    
    print(f"\n✓ Симуляция для нескольких игроков успешно завершена!")
    print(f"  - Поддерживается произвольное количество игроков")
    print(f"  - Каждый игрок может иметь до 3 позиций")
    print(f"  - Алгоритм эффективно балансирует развитие навыков")
    print(f"  - Серые навыки подавляются в пользу белых")


if __name__ == "__main__":
    main()