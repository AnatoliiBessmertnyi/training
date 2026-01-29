import json
import uuid
from pathlib import Path


class PlayerRepository:
    FILE = "storage/players.json"

    def load_all(self):
        try:
            with open(self.FILE, "r", encoding="utf-8") as f:
                return json.load(f)["players"]
        except FileNotFoundError:
            return []

    def save_all(self, players):
        # Create directory if it doesn't exist
        Path(self.FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump({"players": players}, f, ensure_ascii=False, indent=2)

    def create(self, name, positions):
        players = self.load_all()
        player = {
            "id": str(uuid.uuid4()),
            "name": name,
            "positions": positions,
            "skills": {},
            "training_count": 10  # Default training count
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