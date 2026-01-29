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

    white_skills = set()
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
            # Rebuild plan after update
            skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
            player_obj = Player(
                name=player_data["name"],
                positions=player_data["positions"],
                skills=skills
            )
            recommender = TrainingRecommender(player_obj)
            plan = recommender.build_balanced_plan(total_sessions=10)
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
        positions=player_data["positions"],
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


# 🆕 Новый маршрут для обновления плана и слабых/сильных навыков через JSON
@app.route("/players/<player_id>/update", methods=["POST"])
def update_skills_and_get_data(player_id):
    player_data = repo.get(player_id)

    # Обновляем навыки
    for skill in SKILLS.keys():
        val = request.form.get(f"{skill}")
        if val:
            try:
                player_data["skills"][skill] = int(val)
            except ValueError:
                pass
    repo.update(player_data)

    # Пересчитываем план
    skills = {k: player_data["skills"].get(k, 1) for k in SKILLS}
    player_obj = Player(
        name=player_data["name"],
        positions=player_data["positions"],
        skills=skills
    )
    recommender = TrainingRecommender(player_obj)
    plan = recommender.build_balanced_plan(total_sessions=10)

    # Сортируем навыки
    sorted_skills = sorted(player_data["skills"].items(), key=lambda x: x[1])

    weakest = sorted_skills[:3]
    strongest = sorted_skills[-3:]

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