from domain.player import Player
from domain.training_planner import TrainingPlanner
from config.skills import SKILLS
from config.positions import POSITIONS
from config.trainings import TRAININGS


def main():
    print("=== Помощник по прокачке игрока ===")

    # 1. Позиции игрока
    positions = ["ST", "AMC"]

    # 2. Навыки игрока (вводятся ТОЛЬКО реальные)
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

    # 3. Автозаполнение отсутствующих навыков минимальным значением
    for skill_id in SKILLS:
        if skill_id not in player_skills:
            player_skills[skill_id] = 1

    # 4. Создание игрока
    player = Player(
        name="Игрок",
        positions=positions,
        skills=player_skills,
    )

    # 5. Вывод белых навыков
    print("\nПозиции игрока:", positions)
    print("Белые навыки:")

    for skill_id in sorted(player.white_skills):
        value = player.skills[skill_id]
        print(f"  - {SKILLS[skill_id]}: {value}")

    # 6. Слабые белые навыки
    weakest = player.weakest_white_skills(5)

    print("\nСамые слабые белые навыки:")
    for skill_id in weakest:
        print(f"  - {SKILLS[skill_id]}: {player.skills[skill_id]}")

    # 7. Планирование тренировок
    planner = TrainingPlanner(
        player=player,
        max_steps=30,
        gray_penalty=3,
    )

    plan = planner.build_plan()

    # 8. Вывод плана
    print("\n=== Рекомендуемый план тренировок ===")

    if not plan:
        print("Не удалось улучшить баланс белых навыков")
        return

    for tr_id, count in plan.items():
        tr = TRAININGS[tr_id]
        skills_ru = [SKILLS[s] for s in tr["skills"]]

        print(f"- {tr['name']} ({count} раз)")
        print(f"  Качает навыки: {skills_ru}")


if __name__ == "__main__":
    main()
