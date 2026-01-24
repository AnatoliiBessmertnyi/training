from domain.player import Player
from domain.training_recommender import TrainingRecommender
from config.skills import SKILLS
from config.positions import POSITIONS

def main():
    print("=== Помощник по прокачке игрока (хардкод) ===")

    # Позиции игрока
    positions = ["ST", "AMC"]

    # Белые навыки для этих позиций
    white_skills = set()
    for pos in positions:
        white_skills.update(POSITIONS[pos]["white_skills"])

    print("\nБелые навыки игрока:", [SKILLS[s] for s in white_skills])

    # Захардкоженные значения навыков
    player_skills = {
        "tackling": 35,
        "marking": 44,
        "positioning": 215,
        "heading": 219,
        "bravery": 32,
        "passing": 254,
        "dribbling": 259,
        "cross": 41,
        "finishing": 265,
        "shooting": 271,
        "physical": 206,
        "strength": 201,
        "aggressiveness": 16,
        "pace": 256,
        "creativity": 200,
    }

    # Заполняем серые навыки минимальным значением 1
    for skill_id in SKILLS:
        if skill_id not in player_skills:
            player_skills[skill_id] = 1

    # Создаём игрока
    player = Player(name="Игрок", positions=positions, skills=player_skills)

    # Получаем рекомендации
    recommender = TrainingRecommender(player)
    recommendations = recommender.recommend(max_results=10)

    print("\n=== Рекомендованные тренировки ===")
    if not recommendations:
        print("Нет подходящих тренировок для слабых белых навыков")
    else:
        for tr_id, name, desired, all_skills in recommendations:
            print(f"- {name} ({tr_id}):")
            print(f"  Желательные белые навыки: {[SKILLS[s] for s in desired]}")
            print(f"  Все навыки, которые тренировка качает: {[SKILLS[s] for s in all_skills]}")

if __name__ == "__main__":
    main()
