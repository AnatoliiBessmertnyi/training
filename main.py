from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner


def main():
    print("=== Помощник по прокачке игрока ===\n")

    # Позиции игрока (хардкод)
    # positions = ["ST", "AMC"]
    # positions = ["DC"]
    positions = ["AMC", "MC", "DMC"]

    # Белые навыки для этих позиций
    white_skills = set()
    for pos in positions:
        white_skills.update(POSITIONS[pos]["white_skills"])

    # Захардкоженные значения навыков для DC
    # player_skills = {
    #     "tackling": 271,
    #     "marking": 247,
    #     "positioning": 240,
    #     "heading": 223,
    #     "bravery": 253,
    #     "passing": 33,
    #     "dribbling": 15,
    #     "cross": 20,
    #     "finishing": 32,
    #     "shooting": 24,
    #     "physical": 286,
    #     "strength": 302,
    #     "aggressiveness": 276,
    #     "pace": 1,
    #     "creativity": 1,
    # }

    # # Захардкоженные значения навыков для AMC, MC, DMC
    player_skills = {
        "tackling": 67,
        "marking": 55,
        "positioning": 60,
        "heading": 85,
        "bravery": 71,
        "passing": 87,
        "dribbling": 70,
        "cross": 50,
        "finishing": 73,
        "shooting": 86,
        "physical": 79,
        "strength": 54,
        "aggressiveness": 54,
        "pace": 84,
        "creativity": 72,
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
