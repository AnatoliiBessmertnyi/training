from flask import Flask, render_template, request, redirect, url_for, jsonify
from storage.player_repository import PlayerRepository
from domain.player import Player
from domain.training_recommender import TrainingRecommender
from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS

app = Flask(__name__)
repo = PlayerRepository()


@app.route("/")
def index():
    return redirect(url_for("players"))


@app.route("/players")
def players():
    players_data = repo.load_all()
    
    for player in players_data:
        # === ИСПОЛЬЗУЕМ Player ДЛЯ ВСЕХ РАСЧЁТОВ ===
        player_obj = Player(
            name=player["name"],
            positions=player["positions"] or [],
            skills=player.get("skills", {}),
            enhancement_level=player.get("enhancement_level", 0)
        )
        
        # Сырые средние (без усиления)
        player["all_skills_avg"] = player_obj.raw_average_overall
        player["white_skills_avg"] = player_obj.raw_average_white
        player["white_skill_diff"] = player_obj.raw_white_skill_difference
        
        # Усиленные средние
        player["average_overall"] = player_obj.average_overall
        player["average_white"] = player_obj.average_white
        player["enhancement_level"] = player_obj.enhancement_level

    players_data.sort(key=lambda p: p.get("white_skill_diff", 0), reverse=True)
    return render_template("players.html", players=players_data)


@app.route("/players/new", methods=["GET", "POST"])
def new_player():
    if request.method == "POST":
        name = request.form["name"]
        positions = request.form.getlist("positions")
        repo.create(name, positions)
        return redirect(url_for("players"))

    return render_template("player_form.html", positions=POSITIONS.keys())


@app.route("/players/<player_id>", methods=["GET", "POST"])
def player_detail(player_id):
    player_data = repo.get(player_id)
    if player_data is None:
        return "Player not found", 404

    if request.method == "POST":
        for skill in SKILLS.keys():
            val = request.form.get(skill)
            if val:
                try:
                    player_data["skills"][skill] = int(val)
                except ValueError:
                    pass

        training_count = request.form.get("training_count", player_data.get("training_count", 10))
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
            plan_with_types.append({
                "training_id": item.training_id,
                "name": item.name,
                "repeats": item.repeats,
                "skills": item.skills,
                "type": training_type,
            })

        return render_template(
            "player_detail.html",
            player=player_data,
            player_id=player_id,
            white_skills=set(),  # не используется в POST-ответе
            skill_names=SKILLS,
            plan=plan_with_types,
        )

    # === GET: initial load ===
    skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    enhancement_level = player_data.get("enhancement_level", 0)
    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"] or [],
        skills=skills,
        enhancement_level=enhancement_level
    )
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(total_sessions=player_data.get("training_count", 10))

    plan_with_types = []
    for item in plan:
        training_type = TRAININGS.get(item.training_id, {}).get("type", "unknown")
        plan_with_types.append({
            "training_id": item.training_id,
            "name": item.name,
            "repeats": item.repeats,
            "skills": item.skills,
            "type": training_type,
        })

    # === СИМУЛЯЦИЯ ПОСЛЕ ВСЕХ ТРЕНИРОВОК ===
    simulated_skills_after = player_data["skills"].copy()
    for item in plan:
        for _ in range(item.repeats):
            for skill_id in TRAININGS[item.training_id]["skills"]:
                if skill_id in simulated_skills_after:
                    simulated_skills_after[skill_id] = min(400, simulated_skills_after[skill_id] + 1)

    after_all_vals = list(simulated_skills_after.values())
    after_all_avg = sum(after_all_vals) / len(after_all_vals) if after_all_vals else 0

    after_white_vals = [simulated_skills_after[s] for s in player_obj.white_skills if s in simulated_skills_after]
    after_white_avg = sum(after_white_vals) / len(after_white_vals) if after_white_vals else 0
    after_white_diff = max(after_white_vals) - min(after_white_vals) if after_white_vals else 0

    after_gray_vals = [simulated_skills_after[s] for s in player_obj.gray_skills if s in simulated_skills_after]
    after_gray_avg = sum(after_gray_vals) / len(after_gray_vals) if after_gray_vals else 0

    return render_template(
        "player_detail.html",
        player_dict=player_data,
        player=player_obj,
        player_id=player_id,
        white_skills=player_obj.white_skills,
        skill_names=SKILLS,
        plan=plan_with_types,
        after_all_skills_avg=round(after_all_avg, 2),
        after_white_skills_avg=round(after_white_avg, 2),
        after_gray_skills_avg=round(after_gray_avg, 2),
        after_white_skill_difference=after_white_diff,
    )


@app.route("/players/<player_id>/accept_training", methods=["POST"])
def accept_training(player_id):
    player_data = repo.get(player_id)
    if player_data is None:
        return "Player not found", 404

    training_id = request.form.get("training_id")
    repeats = int(request.form.get("repeats", 1))

    if training_id in TRAININGS:
        training_data = TRAININGS[training_id]
        enhancement_level = player_data.get("enhancement_level", 0)
        player_obj = Player(
            name=player_data["name"],
            positions=player_data["positions"] or [],
            skills=player_data["skills"],
            enhancement_level=enhancement_level
        )
        for _ in range(repeats):
            player_obj.apply_training(training_data["skills"], gain=1)
        player_data["skills"] = player_obj.skills

    repo.update(player_data)
    return redirect(url_for("player_detail", player_id=player_id))


@app.route("/players/<player_id>/accept_all_trainings", methods=["POST"])
def accept_all_trainings(player_id):
    player_data = repo.get(player_id)
    if player_data is None:
        return "Player not found", 404

    skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    enhancement_level = player_data.get("enhancement_level", 0)
    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"] or [],
        skills=skills,
        enhancement_level=enhancement_level
    )
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(total_sessions=player_data.get("training_count", 10))

    for item in plan:
        training_data = TRAININGS[item.training_id]
        for _ in range(item.repeats):
            player_obj.apply_training(training_data["skills"], gain=1)

    player_data["skills"] = player_obj.skills
    repo.update(player_data)
    return redirect(url_for("player_detail", player_id=player_id))


@app.route("/players/<player_id>/update", methods=["POST"])
def update_skills_and_get_data(player_id):
    player_data = repo.get(player_id)
    if player_data is None:
        return "Player not found", 404

    for skill in SKILLS.keys():
        val = request.form.get(skill)
        if val:
            try:
                player_data["skills"][skill] = int(val)
            except ValueError:
                pass

    training_count = request.form.get("training_count", player_data.get("training_count", 10))
    try:
        training_count = int(training_count)
        training_count = max(1, min(100, training_count))
    except ValueError:
        training_count = player_data.get("training_count", 10)

    player_data["training_count"] = training_count
    repo.update(player_data)

    # === ИСПОЛЬЗУЕМ Player ДЛЯ ВСЕХ РАСЧЁТОВ ===
    skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    enhancement_level = player_data.get("enhancement_level", 0)
    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"] or [],
        skills=skills,
        enhancement_level=enhancement_level
    )
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(total_sessions=training_count)

    plan_with_types = []
    for item in plan:
        training_type = TRAININGS.get(item.training_id, {}).get("type", "unknown")
        plan_with_types.append({
            "training_id": item.training_id,
            "name": item.name,
            "repeats": item.repeats,
            "skills": item.skills,
            "type": training_type,
        })

    # === СЛАБЫЕ И СИЛЬНЫЕ НАВЫКИ ===
    weakest = [
        {"name": SKILLS[k], "value": player_obj.skills[k]} 
        for k in player_obj.weakest_white_skills(3)
    ]
    strongest = [
        {"name": SKILLS[k], "value": player_obj.skills[k]} 
        for k in player_obj.strongest_white_skills(3)
    ]

    # === СРЕДНИЕ БЕЗ УСИЛЕНИЯ ===
    all_avg = player_obj.raw_average_overall
    white_avg = player_obj.raw_average_white
    gray_avg = player_obj.raw_average_gray
    white_diff = player_obj.raw_white_skill_difference

    # === СИМУЛЯЦИЯ ПОСЛЕ ВСЕХ ТРЕНИРОВОК ===
    simulated_skills = player_data["skills"].copy()
    for item in plan:
        for _ in range(item.repeats):
            for skill_id in TRAININGS[item.training_id]["skills"]:
                if skill_id in simulated_skills:
                    simulated_skills[skill_id] = min(400, simulated_skills[skill_id] + 1)

    after_all_vals = list(simulated_skills.values())
    after_all_avg = sum(after_all_vals) / len(after_all_vals) if after_all_vals else 0

    after_white_vals = [simulated_skills[s] for s in player_obj.white_skills if s in simulated_skills]
    after_white_avg = sum(after_white_vals) / len(after_white_vals) if after_white_vals else 0
    after_white_diff = max(after_white_vals) - min(after_white_vals) if after_white_vals else 0

    after_gray_vals = [simulated_skills[s] for s in player_obj.gray_skills if s in simulated_skills]
    after_gray_avg = sum(after_gray_vals) / len(after_gray_vals) if after_gray_vals else 0

    return jsonify({
        "plan_html": render_template("plan_only.html", plan=plan_with_types, skill_names=SKILLS),
        "weakest_skills": weakest,
        "strongest_skills": strongest,
        "all_skills_avg": round(all_avg, 2),
        "white_skills_avg": round(white_avg, 2),
        "gray_skills_avg": round(gray_avg, 2),
        "white_skill_difference": white_diff,

        "after_all_skills_avg": round(after_all_avg, 2),
        "after_white_skills_avg": round(after_white_avg, 2),
        "after_gray_skills_avg": round(after_gray_avg, 2),
        "after_white_skill_difference": after_white_diff,
    })


if __name__ == "__main__":
    app.run(debug=True)
