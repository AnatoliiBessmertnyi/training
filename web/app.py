from flask import Flask, render_template, request, redirect, url_for
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
    player = repo.get(player_id)

    white_skills = set()
    for pos in player["positions"]:
        white_skills.update(POSITIONS[pos]["white_skills"])

    if request.method == "POST":
        for skill in SKILLS.keys():  # Update all skills, not just white ones
            val = request.form.get(skill)
            if val:
                player["skills"][skill] = int(val)
        repo.update(player)
        return redirect(request.url)

    return render_template(
        "player_detail.html",
        player=player,
        white_skills=white_skills,
        skill_names=SKILLS
    )


@app.route("/players/<player_id>/plan")
def training_plan(player_id):
    data = repo.get(player_id)

    # серые навыки = 1
    skills = {k: data["skills"].get(k, 1) for k in SKILLS}

    player = Player(
        name=data["name"],
        positions=data["positions"],
        skills=skills
    )

    recommender = TrainingRecommender(player)
    plan = recommender.build_balanced_plan(total_sessions=10)

    return render_template(
        "plan.html",
        player=player,
        plan=plan,
        skill_names=SKILLS
    )


if __name__ == "__main__":
    app.run(debug=True)