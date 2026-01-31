from web.app import app
from storage.player_repository import PlayerRepository
from config.positions import POSITIONS
from config.skills import SKILLS
import sys


def input_players():
    """Interactive function to input 11 players manually"""
    repo = PlayerRepository()

    print("=== Ввод данных для 11 игроков ===\n")

    for i in range(1, 12):
        print(f"--- Игрок #{i} ---")

        # Get player name
        name = input(f"Введите имя игрока #{i}: ").strip()
        if not name:
            name = f"Игрок {i}"

        # Show available positions
        print("\nДоступные позиции:")
        position_list = list(POSITIONS.keys())
        for idx, pos in enumerate(position_list):
            print(f"{idx + 1}. {pos}")

        # Get player positions
        positions_input = input(
            f"\nВведите номера позиций через запятую (например: 1,3,5): "
        ).strip()
        selected_positions = []

        if positions_input:
            try:
                pos_indices = [int(x.strip()) - 1 for x in positions_input.split(",")]
                selected_positions = [
                    position_list[idx]
                    for idx in pos_indices
                    if 0 <= idx < len(position_list)
                ]
            except ValueError:
                print("Ошибка ввода, используем первую позицию по умолчанию")
                selected_positions = [position_list[0]] if position_list else []
        else:
            # Default to first position if nothing entered
            selected_positions = [position_list[0]] if position_list else []

        if not selected_positions:
            selected_positions = [position_list[0]]

        print(f"Выбраны позиции: {selected_positions}")

        # Create player
        player = repo.create(name, selected_positions)
        print(f"Игрок '{name}' добавлен с ID: {player['id']}\n")

    print("Все 11 игроков успешно добавлены!\n")


def main():
    print("Фронтенд-приложение для планирования тренировок игроков")
    print("=" * 50)

    print("Запуск веб-сервера...")
    print("Откройте в браузере: http://localhost:5000")
    print("Для остановки сервера нажмите Ctrl+C\n")

    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nСервер остановлен.")


if __name__ == "__main__":
    main()
