from flask import Flask, render_template, request, redirect, url_for, jsonify
from storage.player_repository import PlayerRepository
from domain.player import Player
from domain.training_recommender import TrainingRecommender
from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS

app = Flask(__name__)
repo = PlayerRepository()

RANK_BONUS = {0: 0, 1: 10, 2: 30, 3: 50, 4: 80, 5: 120, 6: 160}


@app.route("/")
def index():
    return redirect(url_for("players"))


@app.route("/players")
def players():
    players_data = repo.load_all()

    # Бонусы ранга
    RANK_BONUS = {0: 0, 1: 10, 2: 30, 3: 50, 4: 80, 5: 120, 6: 160}

    for player in players_data:
        rank = player.get("rank", 0)
        bonus = RANK_BONUS.get(rank, 0)
        skills = player.get("skills", {})

        # === Эффективные навыки с учётом ранга ===
        effective_skills = {k: v + bonus for k, v in skills.items()}

        if effective_skills:
            all_values = list(effective_skills.values())
            player["all_skills_avg"] = sum(all_values) / len(all_values)
        else:
            player["all_skills_avg"] = 0

        # === Белые навыки с бонусом ===
        white_skills = set()
        if player.get("positions"):
            for pos in player["positions"]:
                if pos in POSITIONS:
                    white_skills.update(POSITIONS[pos]["white_skills"])

        white_skill_values = [
            effective_skills[skill_id]
            for skill_id in white_skills
            if skill_id in effective_skills
        ]

        if white_skill_values:
            player["white_skills_avg"] = sum(white_skill_values) / len(
                white_skill_values
            )
            player["white_skill_diff"] = max(white_skill_values) - min(
                white_skill_values
            )
        else:
            player["white_skills_avg"] = 0
            player["white_skill_diff"] = 0

        # === Сохраняем бонус для отображения в шаблоне ===
        player["rank_bonus"] = bonus

    players_data.sort(key=lambda p: p.get("white_skill_diff", 0), reverse=True)
    return render_template("players.html", players=players_data)


@app.route("/players/new", methods=["GET", "POST"])
def new_player():
    if request.method == "POST":
        name = request.form["name"]
        positions = request.form.getlist("positions")
        repo.create(name, positions)
        return redirect(url_for("players"))

    return render_template("player_form.html", positions=POSITIONS.keys(), player=None)


@app.route("/players/<player_id>/edit", methods=["GET", "POST"])
def edit_player(player_id):
    player_data = repo.get(player_id)
    if player_data is None:
        return "Player not found", 404

    if request.method == "POST":
        # Обновляем основные данные
        player_data["name"] = request.form["name"]
        player_data["positions"] = request.form.getlist("positions")

        # Обновляем ранг (преобразуем в int)
        try:
            player_data["rank"] = int(request.form.get("rank", 0))
        except ValueError:
            player_data["rank"] = 0

        repo.update(player_data)
        return redirect(url_for("players"))

    return render_template(
        "player_form.html", player=player_data, positions=POSITIONS.keys()
    )


@app.route("/players/<player_id>", methods=["GET", "POST"])
def player_detail(player_id):
    player_data = repo.get(player_id)
    if player_data is None:
        return "Player not found", 404

    white_skills = set()
    if player_data["positions"]:
        for pos in player_data["positions"]:
            white_skills.update(POSITIONS[pos]["white_skills"])
    gray_skills = set(SKILLS.keys()) - white_skills

    if request.method == "POST":
        for skill in SKILLS.keys():
            val = request.form.get(skill)
            if val:
                try:
                    player_data["skills"][skill] = int(val)
                except ValueError:
                    pass

        training_count = request.form.get(
            "training_count", player_data.get("training_count", 10)
        )
        try:
            training_count = int(training_count)
            training_count = max(1, min(100, training_count))
        except ValueError:
            training_count = player_data.get("training_count", 10)

        player_data["training_count"] = training_count
        repo.update(player_data)

        action = request.form.get("action", "")
        if action == "update_and_plan":
            skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
            player_obj = Player(
                name=player_data["name"],
                positions=player_data["positions"] or [],
                skills=skills,
            )
            recommender = TrainingRecommender(player_obj)
            plan = recommender.build_balanced_plan(total_sessions=training_count)
        else:
            plan = []

        plan_with_types = []
        for item in plan:
            training_type = TRAININGS.get(item.training_id, {}).get("type", "unknown")
            plan_with_types.append(
                {
                    "training_id": item.training_id,
                    "name": item.name,
                    "repeats": item.repeats,
                    "skills": item.skills,
                    "type": training_type,
                }
            )

        return render_template(
            "player_detail.html",
            player=player_data,
            player_id=player_id,
            white_skills=white_skills,
            skill_names=SKILLS,
            plan=plan_with_types,
        )

    # === GET: initial load ===
    rank = player_data.get("rank", 0)
    bonus = RANK_BONUS.get(rank, 0)

    # Базовые навыки (из БД)
    base_skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    # Эффективные навыки (для отображения)
    effective_skills = {k: v + bonus for k, v in base_skills.items()}

    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"] or [],
        skills=base_skills,  # Recommender работает с базовыми значениями
    )
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(
        total_sessions=player_data.get("training_count", 10)
    )

    plan_with_types = []
    for item in plan:
        training_type = TRAININGS.get(item.training_id, {}).get("type", "unknown")
        plan_with_types.append(
            {
                "training_id": item.training_id,
                "name": item.name,
                "repeats": item.repeats,
                "skills": item.skills,
                "type": training_type,
            }
        )

    # === СИМУЛЯЦИЯ ПОСЛЕ ВСЕХ ТРЕНИРОВОК (для начального отображения) ===
    simulated_skills_after = player_data["skills"].copy()
    for item in plan:
        for _ in range(item.repeats):
            for skill_id in TRAININGS[item.training_id]["skills"]:
                if skill_id in simulated_skills_after:
                    simulated_skills_after[skill_id] = min(
                        400, simulated_skills_after[skill_id] + 1
                    )

    after_all_vals = list(simulated_skills_after.values())
    after_all_avg = sum(after_all_vals) / len(after_all_vals) if after_all_vals else 0

    after_white_vals = [
        simulated_skills_after[s] for s in white_skills if s in simulated_skills_after
    ]
    after_white_avg = (
        sum(after_white_vals) / len(after_white_vals) if after_white_vals else 0
    )
    after_white_diff = (
        max(after_white_vals) - min(after_white_vals) if after_white_vals else 0
    )

    after_gray_vals = [
        simulated_skills_after[s] for s in gray_skills if s in simulated_skills_after
    ]
    after_gray_avg = (
        sum(after_gray_vals) / len(after_gray_vals) if after_gray_vals else 0
    )

    return render_template(
        "player_detail.html",
        player=player_data,
        player_id=player_id,
        white_skills=white_skills,
        skill_names=SKILLS,
        plan=plan_with_types,
        # === НОВОЕ: передаём эффективные навыки и бонус ===
        effective_skills=effective_skills,
        rank_bonus=bonus,
        # === ПРОГНОЗНЫЕ ЗНАЧЕНИЯ ===
        after_all_skills_avg=round(after_all_avg, 2),
        after_white_skills_avg=round(after_white_avg, 2),
        after_gray_skills_avg=round(after_gray_avg, 2),
        after_white_skill_difference=after_white_diff,
    )


@app.route("/players/<player_id>/update", methods=["POST"])
def update_skills_and_get_data(player_id):
    player_data = repo.get(player_id)
    if player_data is None:
        return "Player not found", 404

    rank = player_data.get("rank", 0)
    bonus = RANK_BONUS.get(rank, 0)

    for skill in SKILLS.keys():
        val = request.form.get(skill)
        if val:
            try:
                effective_value = int(val)
                base_value = effective_value - bonus
                base_value = max(1, min(1000, base_value))
                player_data["skills"][skill] = base_value
            except ValueError:
                pass

    training_count = request.form.get(
        "training_count", player_data.get("training_count", 10)
    )
    try:
        training_count = int(training_count)
        training_count = max(1, min(100, training_count))
    except ValueError:
        training_count = player_data.get("training_count", 10)

    player_data["training_count"] = training_count
    repo.update(player_data)

    white_skills = set()
    if player_data["positions"]:
        for pos in player_data["positions"]:
            white_skills.update(POSITIONS[pos]["white_skills"])
    gray_skills = set(SKILLS.keys()) - white_skills

    skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"] or [],
        skills=skills,
    )
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(total_sessions=training_count)

    plan_with_types = []
    for item in plan:
        training_type = TRAININGS.get(item.training_id, {}).get("type", "unknown")
        plan_with_types.append(
            {
                "training_id": item.training_id,
                "name": item.name,
                "repeats": item.repeats,
                "skills": item.skills,
                "type": training_type,
            }
        )

    white_skill_items = [
        (skill_id, player_data["skills"][skill_id] + bonus)  # + bonus!
        for skill_id in white_skills
        if skill_id in player_data["skills"]
    ]
    sorted_white_skills = sorted(white_skill_items, key=lambda x: x[1])
    weakest = sorted_white_skills[:3]
    strongest = list(reversed(sorted_white_skills[-3:]))

    all_vals = [v + bonus for v in player_data["skills"].values()]
    all_avg = sum(all_vals) / len(all_vals) if all_vals else 0

    white_vals = [
        player_data["skills"][s] + bonus
        for s in white_skills
        if s in player_data["skills"]
    ]
    white_avg = sum(white_vals) / len(white_vals) if white_vals else 0
    white_diff = max(white_vals) - min(white_vals) if white_vals else 0

    gray_vals = [
        player_data["skills"][s] + bonus
        for s in gray_skills
        if s in player_data["skills"]
    ]
    gray_avg = sum(gray_vals) / len(gray_vals) if gray_vals else 0

    # === СИМУЛЯЦИЯ ПОСЛЕ ВСЕХ ТРЕНИРОВОК ===
    simulated_skills = player_data["skills"].copy()
    for item in plan:
        for _ in range(item.repeats):
            for skill_id in TRAININGS[item.training_id]["skills"]:
                if skill_id in simulated_skills:
                    simulated_skills[skill_id] = min(
                        400, simulated_skills[skill_id] + 1
                    )

    after_all_vals = [v + bonus for v in simulated_skills.values()]
    after_all_avg = sum(after_all_vals) / len(after_all_vals) if after_all_vals else 0

    after_white_vals = [
        simulated_skills[s] + bonus for s in white_skills if s in simulated_skills
    ]
    after_white_avg = (
        sum(after_white_vals) / len(after_white_vals) if after_white_vals else 0
    )
    after_white_diff = (
        max(after_white_vals) - min(after_white_vals) if after_white_vals else 0
    )

    after_gray_vals = [
        simulated_skills[s] + bonus for s in gray_skills if s in simulated_skills
    ]
    after_gray_avg = (
        sum(after_gray_vals) / len(after_gray_vals) if after_gray_vals else 0
    )

    return jsonify(
        {
            "plan_html": render_template(
                "plan_only.html",
                plan=plan_with_types,
                skill_names=SKILLS,
                white_skills=white_skills,
            ),
            "weakest_skills": [{"name": SKILLS[k], "value": v} for k, v in weakest],
            "strongest_skills": [{"name": SKILLS[k], "value": v} for k, v in strongest],
            "all_skills_avg": round(all_avg, 2),
            "white_skills_avg": round(white_avg, 2),
            "gray_skills_avg": round(gray_avg, 2),
            "white_skill_difference": white_diff,
            "after_all_skills_avg": round(after_all_avg, 2),
            "after_white_skills_avg": round(after_white_avg, 2),
            "after_gray_skills_avg": round(after_gray_avg, 2),
            "after_white_skill_difference": after_white_diff,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
