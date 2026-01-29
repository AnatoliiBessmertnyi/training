#!/usr/bin/env python3
"""
Тестирование функционала применения тренировок
"""

from domain.player import Player
from config.trainings import TRAININGS
from config.skills import SKILLS

def test_apply_training():
    """Тест применения одной тренировки к игроку"""
    
    # Создаем тестового игрока
    skills = {skill_id: 10 for skill_id in SKILLS.keys()}  # Все навыки на уровне 10
    player = Player(name="Test Player", positions=["ST"], skills=skills)
    
    print("Изначальные навыки:")
    print(f"  dribbling: {player.skills['dribbling']}")
    print(f"  finishing: {player.skills['finishing']}")
    print(f"  passing: {player.skills['passing']}")
    
    # Выбираем тренировку "Один на один", которая качает dribbling, tackling, finishing
    training_id = "one_of_one"
    training_data = TRAININGS[training_id]
    
    print(f"\nПрименяем тренировку '{training_data['name']}' ({training_id})")
    print(f"Качает навыки: {training_data['skills']}")
    
    # Применяем тренировку
    player.apply_training(training_data["skills"], gain=1)
    
    print("\nНавыки после тренировки:")
    print(f"  dribbling: {player.skills['dribbling']} (+1)")
    print(f"  finishing: {player.skills['finishing']} (+1)")
    print(f"  passing: {player.skills['passing']} (без изменений)")
    print(f"  tackling: {player.skills['tackling']} (+1)")
    
    # Проверяем, что нужные навыки увеличились
    assert player.skills['dribbling'] == 11, "Dribbling should increase by 1"
    assert player.skills['finishing'] == 11, "Finishing should increase by 1"
    assert player.skills['tackling'] == 11, "Tackling should increase by 1"
    assert player.skills['passing'] == 10, "Passing should remain unchanged"
    
    print("\n✓ Тест применения одной тренировки пройден")

def test_apply_multiple_trainings():
    """Тест применения нескольких тренировок"""
    
    # Создаем тестового игрока
    skills = {skill_id: 10 for skill_id in SKILLS.keys()}
    player = Player(name="Test Player", positions=["ST"], skills=skills)
    
    # Применяем тренировку 3 раза (например, как если бы было 3 повторения)
    training_id = "one_of_one"
    training_data = TRAININGS[training_id]
    
    print(f"\nПрименяем тренировку '{training_data['name']}' 3 раза")
    
    for i in range(3):
        player.apply_training(training_data["skills"], gain=1)
        print(f"  После применения #{i+1}: dribbling={player.skills['dribbling']}")
    
    # Проверяем, что навыки увеличились на 3
    assert player.skills['dribbling'] == 13, "Dribbling should increase by 3"
    assert player.skills['finishing'] == 13, "Finishing should increase by 3"
    assert player.skills['tackling'] == 13, "Tackling should increase by 3"
    
    print("✓ Тест применения нескольких тренировок пройден")

def test_apply_training_with_different_gains():
    """Тест применения тренировок с разными значениями прироста"""
    
    skills = {skill_id: 10 for skill_id in SKILLS.keys()}
    player = Player(name="Test Player", positions=["ST"], skills=skills)
    
    training_id = "one_of_one"
    training_data = TRAININGS[training_id]
    
    print(f"\nПрименяем тренировку с приростом 5")
    
    player.apply_training(training_data["skills"], gain=5)
    
    assert player.skills['dribbling'] == 15, "Dribbling should increase by 5"
    
    print("✓ Тест с разными значениями прироста пройден")

if __name__ == "__main__":
    test_apply_training()
    test_apply_multiple_trainings()
    test_apply_training_with_different_gains()
    print("\n✓ Все тесты пройдены успешно!")