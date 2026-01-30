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
    return render_template("players.html", players=repo.load_all())


@app.route("/players/new", methods=["GET", "POST"])
def new_player():
    if request.method == "POST":
        name = request.form["name"]
        positions = request.form.getlist("positions")
        repo.create(name, positions)
        return redirect(url_for("players"))

    return render_template(
        "player_form.html",
        positions=POSITIONS.keys()
    )


@app.route("/players/<player_id>", methods=["GET", "POST"])
def player_detail(player_id):
    player_data = repo.get(player_id)
    
    # Check if player exists
    if player_data is None:
        return "Player not found", 404

    white_skills = set()
    if player_data["positions"]:  # Check if positions is not None
        for pos in player_data["positions"]:
            white_skills.update(POSITIONS[pos]["white_skills"])

    if request.method == "POST":
        # Handle skill updates
        for skill in SKILLS.keys():
            val = request.form.get(f"{skill}")
            if val:
                try:
                    player_data["skills"][skill] = int(val)
                except ValueError:
                    pass  # ignore invalid values
        
        # Update training count if provided
        training_count = request.form.get("training_count", player_data.get("training_count", 10))
        try:
            training_count = int(training_count)
            if training_count < 1:
                training_count = 1
            elif training_count > 100:
                training_count = 100
        except ValueError:
            training_count = player_data.get("training_count", 10)
        
        player_data["training_count"] = training_count
        repo.update(player_data)

        # Determine if we need to rebuild the plan
        action = request.form.get("action", "")
        if action == "update_and_plan":
            # Rebuild plan after update
            skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
            player_obj = Player(
                name=player_data["name"],
                positions=player_data["positions"] if player_data["positions"] else [],
                skills=skills
            )
            recommender = TrainingRecommender(player_obj)
            plan = recommender.build_balanced_plan(total_sessions=training_count)
        else:
            plan = []
            
        # Prepare plan data with training types (only if there's a plan)
        if plan:
            plan_with_types = []
            for item in plan:
                training_type = TRAININGS.get(item.training_id, {}).get("type", "unknown")
                plan_with_types.append({
                    'training_id': item.training_id,
                    'name': item.name,
                    'repeats': item.repeats,
                    'skills': item.skills,
                    'type': training_type
                })
            plan_to_render = plan_with_types
        else:
            plan_to_render = plan

        return render_template(
            "player_detail.html",
            player=player_data,
            player_id=player_id,
            white_skills=white_skills,
            skill_names=SKILLS,
            plan=plan_to_render
        )

    # On GET, show player and initial plan
    skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"] if player_data["positions"] else [],
        skills=skills
    )
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(total_sessions=player_data.get("training_count", 10))
    
    # Prepare plan data with training types
    plan_with_types = []
    for item in plan:
        training_type = TRAININGS.get(item.training_id, {}).get("type", "unknown")
        plan_with_types.append({
            'training_id': item.training_id,
            'name': item.name,
            'repeats': item.repeats,
            'skills': item.skills,
            'type': training_type
        })

    return render_template(
        "player_detail.html",
        player=player_data,
        player_id=player_id,
        white_skills=white_skills,
        skill_names=SKILLS,
        plan=plan_with_types
    )


@app.route("/players/<player_id>/accept_training", methods=["POST"])
def accept_training(player_id):
    player_data = repo.get(player_id)
    
    # Check if player exists
    if player_data is None:
        return "Player not found", 404
    
    training_id = request.form.get("training_id")
    repeats = int(request.form.get("repeats", 1))
    
    # Apply the training to the player using Player's method
    from config.trainings import TRAININGS
    if training_id in TRAININGS:
        training_data = TRAININGS[training_id]
        
        # Create Player object to use its methods
        player_obj = Player(
            name=player_data["name"],
            positions=player_data["positions"] if player_data["positions"] else [],
            skills=player_data["skills"]
        )
        
        # Apply the training multiple times based on repeats
        for _ in range(repeats):
            player_obj.apply_training(training_data["skills"], gain=1)
        
        # Update player data with modified skills
        player_data["skills"] = player_obj.skills
    
    # Save updated player data
    repo.update(player_data)
    
    # Redirect back to the player detail page
    return redirect(url_for("player_detail", player_id=player_id))


@app.route("/players/<player_id>/accept_all_trainings", methods=["POST"])
def accept_all_trainings(player_id):
    player_data = repo.get(player_id)
    
    # Check if player exists
    if player_data is None:
        return "Player not found", 404
    
    # Rebuild the plan to get all current trainings using player's specific training count
    from domain.training_recommender import TrainingRecommender
    from domain.player import Player
    from config.skills import SKILLS
    
    skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"] if player_data["positions"] else [],
        skills=skills
    )
    recommender = TrainingRecommender(player_obj)
    # Use the player's saved training count instead of hardcoded 10
    plan = recommender.build_balanced_plan(total_sessions=player_data.get("training_count", 10))
    
    # Apply all trainings in the plan using Player's method
    from config.trainings import TRAININGS
    for item in plan:
        training_data = TRAININGS[item.training_id]
        # Apply the training multiple times based on repeats
        for _ in range(item.repeats):
            player_obj.apply_training(training_data["skills"], gain=1)
    
    # Update player data with modified skills
    player_data["skills"] = player_obj.skills
    
    # Save updated player data
    repo.update(player_data)
    
    # Redirect back to the player detail page
    return redirect(url_for("player_detail", player_id=player_id))


# 🆕 Новый маршрут для обновления плана и слабых/сильных навыков через JSON
@app.route("/players/<player_id>/update", methods=["POST"])
def update_skills_and_get_data(player_id):
    player_data = repo.get(player_id)
    
    # Check if player exists
    if player_data is None:
        return "Player not found", 404

    # Обновляем навыки
    for skill in SKILLS.keys():
        val = request.form.get(f"{skill}")
        if val:
            try:
                player_data["skills"][skill] = int(val)
            except ValueError:
                pass

    # Update training count if provided
    training_count = request.form.get("training_count", player_data.get("training_count", 10))
    try:
        training_count = int(training_count)
        if training_count < 1:
            training_count = 1
        elif training_count > 100:
            training_count = 100
    except ValueError:
        training_count = player_data.get("training_count", 10)
    
    player_data["training_count"] = training_count
    repo.update(player_data)

    # Calculate white skills
    white_skills = set()
    if player_data["positions"]:  # Check if positions is not None
        for pos in player_data["positions"]:
            white_skills.update(POSITIONS[pos]["white_skills"])

    # Пересчитываем план
    skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"] if player_data["positions"] else [],
        skills=skills
    )
    
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(total_sessions=training_count)

    # Prepare plan data with training types (to match the format expected by player_detail.html)
    plan_with_types = []
    for item in plan:
        training_type = TRAININGS.get(item.training_id, {}).get("type", "unknown")
        plan_with_types.append({
            'training_id': item.training_id,
            'name': item.name,
            'repeats': item.repeats,
            'skills': item.skills,
            'type': training_type
        })

    # Сортируем навыки
    # Only consider white skills for weak/strong skills display
    white_skill_items = [(skill_id, player_data["skills"][skill_id]) for skill_id in white_skills 
                         if skill_id in player_data["skills"]]
    sorted_white_skills = sorted(white_skill_items, key=lambda x: x[1])

    weakest = sorted_white_skills[:3]
    strongest = sorted_white_skills[-3:]
    
    # Calculate averages for all skills, white skills, and gray skills
    all_skills_values = list(player_data["skills"].values())
    all_skills_avg = sum(all_skills_values) / len(all_skills_values) if all_skills_values else 0
    
    white_skills_values = [player_data["skills"][skill_id] for skill_id in white_skills 
                          if skill_id in player_data["skills"]]
    white_skills_avg = sum(white_skills_values) / len(white_skills_values) if white_skills_values else 0
    
    gray_skills = set(SKILLS.keys()) - white_skills
    gray_skills_values = [player_data["skills"][skill_id] for skill_id in gray_skills 
                         if skill_id in player_data["skills"]]
    gray_skills_avg = sum(gray_skills_values) / len(gray_skills_values) if gray_skills_values else 0

    # Возвращаем JSON
    return jsonify({
        "plan_html": render_template("plan_only.html", plan=plan_with_types, skill_names=SKILLS),
        "weakest_skills": [
            {"name": SKILLS[k], "value": v} for k, v in weakest
        ],
        "strongest_skills": [
            {"name": SKILLS[k], "value": v} for k, v in strongest
        ],
        "all_skills_avg": round(all_skills_avg, 2),
        "white_skills_avg": round(white_skills_avg, 2),
        "gray_skills_avg": round(gray_skills_avg, 2)
    })


if __name__ == "__main__":
    app.run(debug=True)