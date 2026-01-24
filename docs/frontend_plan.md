1. Принципы web-версии (важно зафиксировать сразу)

Домен (Player, TrainingRecommender) не трогаем

Web = тонкий слой:

формы

маршруты

сериализация / десериализация

Хранение — пока JSON

Никакой JS на первом этапе

HTML — максимально простой

Это гарантирует:

отсутствие дублирования логики;

возможность легко заменить Flask на FastAPI / Django позже;

чистую архитектуру.

2. Итоговая архитектура (web + domain)
project/
├── domain/
│   ├── player.py
│   └── training_recommender.py
│
├── config/
│   ├── skills.py
│   ├── positions.py
│   └── trainings.py
│
├── storage/
│   ├── player_repository.py
│   └── players.json
│
├── web/
│   ├── app.py
│   ├── forms.py
│   └── templates/
│       ├── base.html
│       ├── players.html
│       ├── player_form.html
│       ├── player_detail.html
│       └── plan.html
│
└── requirements.txt

3. Пользовательские сценарии (что реально будет уметь фронт)
3.1 Список игроков

/players

таблица:

имя

позиции

кнопки: Открыть / Редактировать / План

3.2 Создание игрока

/players/new

поля:

имя

позиции (checkbox)

навыки не вводим здесь (это важно)

3.3 Просмотр / редактирование игрока

/players/<id>

автоматически:

считаются белые навыки по позициям

показываются только они

ввод:

текущее значение

пусто → оставить как есть

3.4 План тренировок

/players/<id>/plan

вывод:

слабые белые навыки

агрегированный план (10 тренировок)

формат как в CLI

4. Storage слой (ключевая часть)
storage/player_repository.py
import json
import uuid
from domain.player import Player

class PlayerRepository:
    FILE = "storage/players.json"

    def load_all(self):
        try:
            with open(self.FILE, "r", encoding="utf-8") as f:
                return json.load(f)["players"]
        except FileNotFoundError:
            return []

    def save_all(self, players):
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump({"players": players}, f, ensure_ascii=False, indent=2)

    def create(self, name, positions):
        players = self.load_all()
        player = {
            "id": str(uuid.uuid4()),
            "name": name,
            "positions": positions,
            "skills": {}
        }
        players.append(player)
        self.save_all(players)
        return player

    def get(self, player_id):
        for p in self.load_all():
            if p["id"] == player_id:
                return p
        return None

    def update(self, player):
        players = self.load_all()
        for i, p in enumerate(players):
            if p["id"] == player["id"]:
                players[i] = player
                break
        self.save_all(players)

5. Flask app (минимальный, но правильный)
web/app.py
from flask import Flask, render_template, request, redirect, url_for
from storage.player_repository import PlayerRepository
from domain.player import Player
from domain.training_recommender import TrainingRecommender
from config.positions import POSITIONS
from config.skills import SKILLS

app = Flask(__name__)
repo = PlayerRepository()


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
        for skill in white_skills:
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

6. HTML — без излишеств (пример)
templates/players.html
<h1>Игроки</h1>

<a href="/players/new">Добавить игрока</a>

<ul>
{% for p in players %}
  <li>
    {{ p.name }} ({{ p.positions | join(", ") }})
    <a href="/players/{{ p.id }}">Открыть</a>
    <a href="/players/{{ p.id }}/plan">План</a>
  </li>
{% endfor %}
</ul>

7. Почему это правильный следующий шаг

UI не влияет на алгоритм

можно быстро тестировать баланс тренировок

игроки становятся сущностями проекта

CLI и Web могут существовать параллельно

следующий шаг — экспорт в .md / PDF

8. Предлагаю следующий шаг

Дальше логично сделать один из двух вариантов:

Довести web до удобного состояния

авто-подсветка слабых навыков

сортировка тренировок

сравнение «до / после»

Стабилизировать домен

веса навыков

ограничение “перекачанных” статов

план на 30 / 60 / 90 тренировок