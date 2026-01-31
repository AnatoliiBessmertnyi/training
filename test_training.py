#!/usr/bin/env python3
"""
Тестирование алгоритма тренировки на игроке Smith
"""
import json
from domain.training_planner import TrainingPlanner
from domain.player import Player

def calculate_stats(player):
    """Вычисляет статистику по навыкам игрока"""
    white_skills = set(player.white_skills)
    gray_skills = set(player.gray_skills)
    
    all_skills = list(player.skills.values())
    white_skill_values = [player.skills[skill] for skill in white_skills]
    gray_skill_values = [player.skills[skill] for skill in gray_skills]
    
    all_avg = sum(all_skills) / len(all_skills) if all_skills else 0
    white_avg = sum(white_skill_values) / len(white_skill_values) if white_skill_values else 0
    gray_avg = sum(gray_skill_values) / len(gray_skill_values) if gray_skill_values else 0
    
    if white_skill_values:
        white_max = max(white_skill_values)
        white_min = min(white_skill_values)
        white_diff = white_max - white_min
    else:
        white_diff = 0
    
    return {
        "all_avg": all_avg,
        "white_avg": white_avg,
        "gray_avg": gray_avg,
        "white_diff": white_diff,
        "white_max": max(white_skill_values) if white_skill_values else 0,
        "white_min": min(white_skill_values) if white_skill_values else 0,
        "all_skills": all_skills,
        "white_skills": white_skill_values,
        "gray_skills": gray_skill_values
    }

def load_player(name):
    """Загружает игрока по имени из файла players.json"""
    with open('storage/players.json', 'r') as f:
        data = json.load(f)
        
    for player_data in data['players']:
        if player_data['name'] == name:
            # Создаем объект игрока
            p = Player(
                name=player_data['name'],
                positions=player_data['positions'],
                skills=player_data['skills']
            )
            return p
            
    raise ValueError(f"Player with name {name} not found")

def run_training_iterations(player_name, iterations=10):
    """Проводит указанное количество итераций тренировок"""
    print(f"Тестируем тренировки для игрока {player_name}")
    
    # Загружаем игрока
    original_player = load_player(player_name)
    print(f"Исходные навыки игрока {player_name}:")
    stats = calculate_stats(original_player)
    print(f"Все навыки: {stats['all_avg']:.2f}")
    print(f"Белые навыки: {stats['white_avg']:.2f}")
    print(f"Серые навыки: {stats['gray_avg']:.2f}")
    print(f"Разница (сильнейший-слабейший): {stats['white_diff']}")
    print()
    
    # Копируем игрока для тренировок
    current_player = Player(
        name=original_player.name,
        positions=original_player.positions,
        skills=original_player.skills.copy()
    )
    
    # Проводим итерации тренировок
    for i in range(iterations):
        print(f"--- Итерация {i+1} ---")
        
        # Создаем планировщик тренировок
        planner = TrainingPlanner(current_player)
        
        # Получаем план тренировок (одну тренировку)
        plan = planner.plan(max_trainings=1)
        
        if plan:
            training_item = plan[0]
            print(f"Выбрана тренировка: {training_item.name} (ID: {training_item.training_id})")
            print(f"Навыки: {training_item.skills}")
            
            # Применяем тренировку к навыкам
            for skill in training_item.skills:
                if skill in current_player.skills:
                    current_player.skills[skill] = min(400, current_player.skills[skill] + 10)
        else:
            print("Не найдено подходящих тренировок!")
            break
        
        # Пересчитываем статистику
        stats = calculate_stats(current_player)
        print(f"Все навыки: {stats['all_avg']:.2f}")
        print(f"Белые навыки: {stats['white_avg']:.2f}")
        print(f"Серые навыки: {stats['gray_avg']:.2f}")
        print(f"Разница (сильнейший-слабейший): {stats['white_diff']}")
        print(f"Максимальный белый: {stats['white_max']}, Минимальный белый: {stats['white_min']}")
        print()

def main():
    # Тестируем на игроке Smith
    run_training_iterations("Smith", 20)
    
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТ:")
    
    # Загрузим финального игрока после тренировок
    final_player = load_player("Smith")
    # Применим к нему все тренировки из предыдущего цикла
    current_player = Player(
        name=final_player.name,
        positions=final_player.positions,
        skills=final_player.skills.copy()
    )
    
    # Проведем 20 итераций тренировок
    for i in range(20):
        planner = TrainingPlanner(current_player)
        plan = planner.plan(max_trainings=1)
        
        if plan:
            training_item = plan[0]
            for skill in training_item.skills:
                if skill in current_player.skills:
                    current_player.skills[skill] = min(400, current_player.skills[skill] + 10)
    
    stats = calculate_stats(current_player)
    print(f"Средние значения навыков")
    print(f"Все навыки: {stats['all_avg']:.2f}")
    print(f"Белые навыки: {stats['white_avg']:.2f}")
    print(f"Серые навыки: {stats['gray_avg']:.2f}")
    print(f"Разница (сильнейший-слабейший): {stats['white_diff']}")

if __name__ == "__main__":
    main()