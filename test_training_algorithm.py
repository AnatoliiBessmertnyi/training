#!/usr/bin/env python3
"""
Скрипт для тестирования алгоритма тренировки и анализа проблемы с разницей между навыками
"""

import json
from typing import Dict, List
from domain.training_planner import TrainingPlanner, TrainingPlanItem
from domain.player import Player
from config.trainings import TRAININGS


def load_players():
    """Загружает игроков из файла players.json"""
    with open('storage/players.json', 'r') as f:
        data = json.load(f)
    return data['players']


def get_player_by_name(players, name):
    """Находит игрока по имени"""
    for player_data in players:
        if player_data['name'] == name:
            return Player(
                id=player_data['id'],
                name=player_data['name'],
                positions=player_data['positions'],
                skills=player_data['skills']
            )
    return None


def apply_training(player: Player, training_id: str):
    """Применяет тренировку к игроку, увеличивая соответствующие навыки"""
    training_data = TRAININGS[training_id]
    
    for skill in training_data['skills']:
        if skill in player.skills:
            # Увеличиваем навык с учетом текущего уровня (чем выше уровень, тем сложнее прокачивать)
            current_level = player.skills[skill]
            
            # Ограничиваем максимальный уровень навыка
            if current_level >= 400:
                continue
                
            # Базовый прирост
            gain = 10
            
            # Уменьшаем прирост для высоких уровней навыков
            if current_level > 300:
                gain = 3
            elif current_level > 250:
                gain = 5
            elif current_level > 200:
                gain = 7
            elif current_level > 150:
                gain = 8
            elif current_level > 100:
                gain = 9
            
            # Применяем прирост, но не превышаем максимальный уровень
            new_level = min(400, current_level + gain)
            player.skills[skill] = new_level


def analyze_skills(player: Player):
    """Анализирует навыки игрока и выводит статистику"""
    white_skills = set([
        "tackling", "marking", "positioning", "heading", "bravery", 
        "passing", "dribbling", "cross", "shooting", "finishing", 
        "physical", "strength", "aggressiveness", "pace", "creativity"
    ])
    
    gray_skills = set(["condition"])  # условно серый навык
    
    all_skills = player.skills
    white_skill_values = [all_skills[skill] for skill in white_skills if skill in all_skills]
    gray_skill_values = [all_skills[skill] for skill in gray_skills if skill in all_skills]
    
    print("Средние значения навыков")
    print(f"Все навыки: {sum(all_skills.values()) / len(all_skills):.2f}")
    
    if white_skill_values:
        avg_white = sum(white_skill_values) / len(white_skill_values)
        print(f"Белые навыки: {avg_white:.2f}")
        
        if len(white_skill_values) > 1:
            white_max = max(white_skill_values)
            white_min = min(white_skill_values)
            diff_white = white_max - white_min
            print(f"Разница (сильнейший-слабейший белые): {diff_white}")
    
    if gray_skill_values:
        avg_gray = sum(gray_skill_values) / len(gray_skill_values)
        print(f"Серые навыки: {avg_gray:.2f}")
        
        if len(gray_skill_values) > 1:
            gray_max = max(gray_skill_values)
            gray_min = min(gray_skill_values)
            diff_gray = gray_max - gray_min
            print(f"Разница (сильнейший-слабейший серые): {diff_gray}")


def find_weak_and_strong_skills(player: Player):
    """Находит слабые и сильные навыки"""
    white_skills = set([
        "tackling", "marking", "positioning", "heading", "bravery", 
        "passing", "dribbling", "cross", "shooting", "finishing", 
        "physical", "strength", "aggressiveness", "pace", "creativity"
    ])
    
    all_skills = player.skills
    white_skill_dict = {skill: all_skills[skill] for skill in white_skills if skill in all_skills}
    
    if not white_skill_dict:
        return {}, {}
    
    sorted_white_skills = sorted(white_skill_dict.items(), key=lambda x: x[1])
    
    # Названия навыков для отображения
    skill_names = {
        "tackling": "Отбор",
        "marking": "Опека", 
        "positioning": "Выбор позиции",
        "heading": "Удар головой",
        "bravery": "Храбрость",
        "passing": "Пас",
        "dribbling": "Дриблинг",
        "cross": "Навес",
        "shooting": "Удар",
        "finishing": "Финиш",
        "physical": "Физическая форма",
        "strength": "Сила",
        "aggressiveness": "Агрессивность",
        "pace": "Скорость",
        "creativity": "Креативность"
    }
    
    # Находим 3 слабейших и 3 сильнейших белых навыка
    weakest = sorted_white_skills[:3]
    strongest = sorted_white_skills[-3:]
    
    print("\nСлабые и сильные навыки")
    print("Слабые белые навыки:", ", ".join([f"{skill_names.get(skill, skill)} ({value})" for skill, value in weakest]))
    print("Сильные белые навыки:", ", ".join([f"{skill_names.get(skill, skill)} ({value})" for skill, value in strongest]))
    
    return white_skill_dict, sorted_white_skills


def simulate_training_iterations(player_name: str, iterations: int = 10):
    """Симулирует несколько итераций тренировок"""
    players = load_players()
    original_player = get_player_by_name(players, player_name)
    
    if not original_player:
        print(f"Игрок {player_name} не найден!")
        return
    
    print(f"Тестируем алгоритм тренировки для игрока {player_name}")
    print("="*50)
    
    # Создаем копию игрока для симуляции
    current_player = Player(
        id=original_player.id,
        name=original_player.name,
        positions=original_player.positions,
        skills=original_player.skills.copy()
    )
    
    print("Начальные навыки:")
    analyze_skills(current_player)
    find_weak_and_strong_skills(current_player)
    
    print("\n" + "="*50)
    print("ПРОЦЕСС ТРЕНИРОВКИ")
    print("="*50)
    
    for i in range(iterations):
        print(f"\n--- Итерация {i+1} ---")
        
        # Создаем планировщик тренировок
        planner = TrainingPlanner(current_player)
        
        # Планируем тренировки (берем только 1 тренировку за итерацию)
        plan = planner.plan(max_trainings=1)
        
        if plan:
            training_item = plan[0]
            print(f"Выбрана тренировка: {training_item.name} (ID: {training_item.training_id})")
            print(f"Тренируемые навыки: {', '.join(training_item.skills)}")
            
            # Применяем тренировку
            apply_training(current_player, training_item.training_id)
            
            print(f"После тренировки:")
            analyze_skills(current_player)
            find_weak_and_strong_skills(current_player)
        else:
            print("Не удалось спланировать тренировку!")
            break
        
        # Проверяем состояние навыков
        white_skills = set([
            "tackling", "marking", "positioning", "heading", "bravery", 
            "passing", "dribbling", "cross", "shooting", "finishing", 
            "physical", "strength", "aggressiveness", "pace", "creativity"
        ])
        
        white_skill_values = [current_player.skills[skill] for skill in white_skills if skill in current_player.skills]
        if white_skill_values:
            white_max = max(white_skill_values)
            white_min = min(white_skill_values)
            diff_white = white_max - white_min
            
            print(f"Разница между сильнейшим и слабейшим белыми навыками: {diff_white}")
            
            # Если разница стала слишком большой, это может быть проблемой
            if diff_white > 50:
                print(f"ПРЕДУПРЕЖДЕНИЕ: Разница между навыками превысила 50! ({diff_white})")
            elif diff_white < 20:
                print(f"ИНФОРМАЦИЯ: Разница между навыками стала меньше 20 ({diff_white}). Алгоритм может начать работать неэффективно.")
    
    print("\n" + "="*50)
    print("ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ")
    print("="*50)
    print("Финальные навыки:")
    analyze_skills(current_player)
    find_weak_and_strong_skills(current_player)


if __name__ == "__main__":
    # Тестируем для игрока Smith
    simulate_training_iterations("Smith", 10)