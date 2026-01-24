from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner


def main():
    print("=== Помощник по прокачке игрока ===\n")

    # Позиции игрока (хардкод)
    positions = ["ST", "AMC"]

    # Белые навыки для этих позиций
    white_skills = set()
    for pos in positions:
        white_skills.update(POSITIONS[pos]["white_skills"])

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

    # Вывод белых навыков
    print(f"Позиции игрока: {positions}")
    print("Белые навыки:")
    for s in sorted(white_skills):
        print(f"  - {SKILLS[s]}: {player.skills[s]}")

    # Определяем слабые белые навыки (для справки)
    weakest = sorted(white_skills, key=lambda s: player.skills[s])[:5]
    print("\nСамые слабые белые навыки:")
    for s in weakest:
        print(f"  - {SKILLS[s]}: {player.skills[s]}")

    # Формируем план тренировок
    planner = TrainingPlanner(player)
    plan = planner.plan(max_cycles=20)

    # Вывод плана
    print("\n=== Рекомендуемый план тренировок ===")
    if not plan:
        print("Нет подходящих тренировок для балансировки белых навыков")
    else:
        for tr_id, name, count in plan:
            skills_covered = TRAININGS[tr_id]["skills"]
            print(f"- {name} ({count} раз)")
            print(f"  Качает навыки: {[SKILLS[s] for s in skills_covered]}")

if __name__ == "__main__":
    main()
