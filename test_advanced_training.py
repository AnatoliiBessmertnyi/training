#!/usr/bin/env python3
"""
Расширенный скрипт для тестирования алгоритма тренировки и анализа проблемы с разницей между навыками
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
    
    all_skills = player.skills
    white_skill_values = [all_skills[skill] for skill in white_skills if skill in all_skills]
    
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
            return avg_white, diff_white
    
    return 0, 0


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
    
    print("Слабые и сильные навыки")
    print("Слабые белые навыки:", ", ".join([f"{skill_names.get(skill, skill)} ({value})" for skill, value in weakest]))
    print("Сильные белые навыки:", ", ".join([f"{skill_names.get(skill, skill)} ({value})" for skill, value in strongest]))
    
    return white_skill_dict, sorted_white_skills


def simulate_training_iterations(player_name: str, iterations: int = 50):
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
    initial_avg, initial_diff = analyze_skills(current_player)
    find_weak_and_strong_skills(current_player)
    
    print("\n" + "="*50)
    print("ПРОЦЕСС ТРЕНИРОВКИ")
    print("="*50)
    
    # Отслеживание статистики
    stats = []
    
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
            avg, diff = analyze_skills(current_player)
            find_weak_and_strong_skills(current_player)
            
            # Сохраняем статистику
            stats.append({
                'iteration': i+1,
                'avg_white': avg,
                'diff_white': diff
            })
            
            print(f"Разница между сильнейшим и слабейшим белыми навыками: {diff}")
            
            # Если разница стала слишком большой, это может быть проблемой
            if diff > 50:
                print(f"ПРЕДУПРЕЖДЕНИЕ: Разница между навыками превысила 50! ({diff})")
            elif diff < 20:
                print(f"ИНФОРМАЦИЯ: Разница между навыками стала меньше 20 ({diff}). Алгоритм может начать работать неэффективно.")
        else:
            print("Не удалось спланировать тренировку!")
            break
    
    print("\n" + "="*50)
    print("ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ")
    print("="*50)
    print("Финальные навыки:")
    analyze_skills(current_player)
    find_weak_and_strong_skills(current_player)
    
    # Анализ статистики
    print("\n" + "="*50)
    print("АНАЛИЗ СТАТИСТИКИ")
    print("="*50)
    
    if stats:
        avg_changes = [stat['avg_white'] for stat in stats]
        diff_changes = [stat['diff_white'] for stat in stats]
        
        print(f"Начальное среднее: {initial_avg:.2f}")
        print(f"Конечное среднее: {stats[-1]['avg_white']:.2f}")
        print(f"Начальная разница: {initial_diff}")
        print(f"Конечная разница: {stats[-1]['diff_white']}")
        
        print("\nЭволюция разницы навыков:")
        for i, stat in enumerate(stats):
            if i % 5 == 0:  # Показываем каждые 5 итераций
                print(f"Итерация {stat['iteration']}: разница = {stat['diff_white']}")
        
        # Анализ проблемы
        print("\nАНАЛИЗ ПРОБЛЕМЫ:")
        min_diff = min(diff_changes)
        max_diff = max(diff_changes)
        print(f"Минимальная разница достигалась: {min_diff}")
        print(f"Максимальная разница: {max_diff}")
        
        # Найдем момент, когда разница начала расти после того, как была низкой
        for i in range(len(diff_changes)):
            if diff_changes[i] == min_diff and i < len(diff_changes) - 1:
                print(f"Минимальная разница {min_diff} была на итерации {i+1}, после чего разница начала расти.")
                break


def create_test_player_with_balanced_skills():
    """Создает тестового игрока с уже частично сбалансированными навыками"""
    test_skills = {
        "tackling": 140,
        "marking": 145,
        "positioning": 135,
        "heading": 130,
        "bravery": 142,
        "passing": 138,
        "dribbling": 132,
        "cross": 125,
        "shooting": 141,
        "finishing": 137,
        "physical": 139,
        "strength": 143,
        "aggressiveness": 136,
        "pace": 144,
        "creativity": 134
    }
    
    # Добавим все остальные навыки с минимальными значениями
    all_skills = test_skills.copy()
    for skill in ["tackling", "marking", "positioning", "heading", "bravery", 
                  "passing", "dribbling", "cross", "shooting", "finishing", 
                  "physical", "strength", "aggressiveness", "pace", "creativity"]:
        if skill not in all_skills:
            all_skills[skill] = 1
    
    return Player(
        id="test_balanced",
        name="Test Balanced Player",
        positions=["DC"],
        skills=all_skills
    )


def test_with_balanced_player():
    """Тестируем алгоритм с уже частично сбалансированным игроком"""
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ С ЧАСТИЧНО СБАЛАНСИРОВАННЫМ ИГРОКОМ")
    print("="*50)
    
    current_player = create_test_player_with_balanced_skills()
    
    print("Начальные навыки:")
    initial_avg, initial_diff = analyze_skills(current_player)
    find_weak_and_strong_skills(current_player)
    
    print("\n" + "="*50)
    print("ПРОЦЕСС ТРЕНИРОВКИ")
    print("="*50)
    
    # Отслеживание статистики
    stats = []
    
    for i in range(30):  # 30 итераций
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
            avg, diff = analyze_skills(current_player)
            find_weak_and_strong_skills(current_player)
            
            # Сохраняем статистику
            stats.append({
                'iteration': i+1,
                'avg_white': avg,
                'diff_white': diff
            })
            
            print(f"Разница между сильнейшим и слабейшим белыми навыками: {diff}")
            
            # Проверка на проблему: когда разница была низкой (< 40), но потом стала расти
            if diff > 50:
                print(f"ПРЕДУПРЕЖДЕНИЕ: Разница между навыками превысила 50! ({diff})")
            elif diff < 20:
                print(f"ИНФОРМАЦИЯ: Разница между навыками стала меньше 20 ({diff}). Алгоритм может начать работать неэффективно.")
        else:
            print("Не удалось спланировать тренировку!")
            break
    
    print("\n" + "="*50)
    print("ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ")
    print("="*50)
    print("Финальные навыки:")
    analyze_skills(current_player)
    find_weak_and_strong_skills(current_player)
    
    # Анализ статистики
    print("\n" + "="*50)
    print("АНАЛИЗ СТАТИСТИКИ")
    print("="*50)
    
    if stats:
        avg_changes = [stat['avg_white'] for stat in stats]
        diff_changes = [stat['diff_white'] for stat in stats]
        
        print(f"Начальное среднее: {initial_avg:.2f}")
        print(f"Конечное среднее: {stats[-1]['avg_white']:.2f}")
        print(f"Начальная разница: {initial_diff}")
        print(f"Конечная разница: {stats[-1]['diff_white']}")
        
        print("\nЭволюция разницы навыков:")
        for i, stat in enumerate(stats):
            if i % 5 == 0:  # Показываем каждые 5 итераций
                print(f"Итерация {stat['iteration']}: разница = {stat['diff_white']}")
        
        # Анализ проблемы
        print("\nАНАЛИЗ ПРОБЛЕМЫ:")
        min_diff = min(diff_changes)
        max_diff = max(diff_changes)
        print(f"Минимальная разница достигалась: {min_diff}")
        print(f"Максимальная разница: {max_diff}")
        
        # Найдем момент, когда разница начала расти после того, как была низкой
        low_diff_moments = [i for i, diff in enumerate(diff_changes) if diff < 40]
        if low_diff_moments:
            print(f"Разница была ниже 40 на итерациях: {low_diff_moments}")
            for idx in low_diff_moments:
                if idx < len(diff_changes) - 1 and diff_changes[idx+1] > diff_changes[idx]:
                    print(f"После итерации {idx+1} (разница={diff_changes[idx]}), разница начала расти: {diff_changes[idx+1]}")


if __name__ == "__main__":
    # Тестируем для игрока Smith
    simulate_training_iterations("Smith", 20)
    
    # Тестируем с уже частично сбалансированным игроком
    test_with_balanced_player()