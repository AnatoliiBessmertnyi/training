#!/usr/bin/env python3
"""
Демонстрационный скрипт работы с функционалом принятия тренировок
"""

from domain.player import Player
from config.trainings import TRAININGS
from config.skills import SKILLS

def demo_accept_training():
    """Демонстрация работы функционала принятия тренировок"""
    
    print("=== Демонстрация функционала принятия тренировок ===\n")
    
    # Создаем тестового игрока
    skills = {skill_id: 10 for skill_id in SKILLS.keys()}
    player = Player(name="Demo Player", positions=["ST"], skills=skills)
    
    print(f"Игрок: {player.name}")
    print(f"Позиция: {player.positions}")
    print(f"Навыки до тренировки (первые 5): {[f'{SKILLS[k]}: {v}' for k, v in list(player.skills.items())[:5]]}\n")
    
    # Показываем тренировку, которую будем применять
    training_id = "one_of_one"
    training_data = TRAININGS[training_id]
    
    print(f"Тренировка: {training_data['name']}")
    print(f"ID тренировки: {training_id}")
    print(f"Качает навыки: {[SKILLS[skill] for skill in training_data['skills']]}\n")
    
    # Применяем тренировку 1 раз
    print("Применяем тренировку 1 раз...")
    player.apply_training(training_data["skills"], gain=1)
    
    print(f"Навыки после 1 тренировки (те, что должны были измениться):")
    for skill_id in training_data["skills"]:
        print(f"  {SKILLS[skill_id]}: {player.skills[skill_id]}")
    print()
    
    # Применяем ту же тренировку 3 раза
    print("Применяем ту же тренировку еще 3 раза...")
    for i in range(3):
        player.apply_training(training_data["skills"], gain=1)
        print(f"  После применения #{i+1}: dribbling = {player.skills['dribbling']}")
    
    print(f"\nИтоговые значения навыков:")
    for skill_id in training_data["skills"]:
        print(f"  {SKILLS[skill_id]}: {player.skills[skill_id]}")
    
    print(f"\nНавыки, которые НЕ должны были измениться:")
    other_skills = [k for k in player.skills.keys() if k not in training_data["skills"]][:5]  # первые 5
    for skill_id in other_skills:
        print(f"  {SKILLS[skill_id]}: {player.skills[skill_id]}")
    
    print("\n=== Демонстрация завершена успешно ===")

if __name__ == "__main__":
    demo_accept_training()