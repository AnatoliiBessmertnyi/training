from flask import Flask, render_template, request, redirect, url_for, jsonify
from storage.player_repository import PlayerRepository
from domain.player import Player
from domain.training_recommender import TrainingRecommender
from config.positions import POSITIONS
from config.skills import SKILLS

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
        repo.update(player_data)

        # Determine if we need to rebuild the plan
        action = request.form.get("action", "")
        if action == "update_and_plan":
            # Get training count from form, default to 10
            training_count = request.form.get("training_count", 10)
            try:
                training_count = int(training_count)
                if training_count < 1:
                    training_count = 1
                elif training_count > 100:
                    training_count = 100
            except ValueError:
                training_count = 10
            
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
        return render_template(
            "player_detail.html",
            player=player_data,
            white_skills=white_skills,
            skill_names=SKILLS,
            plan=plan
        )

    # On GET, show player and initial plan
    skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"] if player_data["positions"] else [],
        skills=skills
    )
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(total_sessions=10)

    return render_template(
        "player_detail.html",
        player=player_data,
        white_skills=white_skills,
        skill_names=SKILLS,
        plan=plan
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
    
    # Rebuild the plan to get all current trainings
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
    plan = recommender.build_balanced_plan(total_sessions=10)  # Get current plan
    
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
    
    # Get training count from form, default to 10
    training_count = request.form.get("training_count", 10)
    try:
        training_count = int(training_count)
        if training_count < 1:
            training_count = 1
        elif training_count > 100:
            training_count = 100
    except ValueError:
        training_count = 10
    
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(total_sessions=training_count)

    # Сортируем навыки
    # Only consider white skills for weak/strong skills display
    white_skill_items = [(skill_id, player_data["skills"][skill_id]) for skill_id in white_skills 
                         if skill_id in player_data["skills"]]
    sorted_white_skills = sorted(white_skill_items, key=lambda x: x[1])

    weakest = sorted_white_skills[:3]
    strongest = sorted_white_skills[-3:]

    # Возвращаем JSON
    return jsonify({
        "plan_html": render_template("plan_only.html", plan=plan, skill_names=SKILLS),
        "weakest_skills": [
            {"name": SKILLS[k], "value": v} for k, v in weakest
        ],
        "strongest_skills": [
            {"name": SKILLS[k], "value": v} for k, v in strongest
        ]
    })


if __name__ == "__main__":
    app.run(debug=True)