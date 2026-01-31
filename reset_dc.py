#!/usr/bin/env python3
"""
Reset DC player to initial state and test the improved algorithm
"""

from storage.player_repository import PlayerRepository

def reset_dc_player():
    """Reset the DC player to initial state with all skills at 1"""
    repo = PlayerRepository()
    
    # Find the test_dc player
    player_id = "ffc4f365-4ba3-48d9-a5f2-45052cf6ff5a"
    player_data = repo.get(player_id)
    
    if player_data:
        # Reset all skills to 1
        for skill_key in player_data["skills"]:
            player_data["skills"][skill_key] = 1
        
        # Reset training count
        player_data["training_count"] = 0
        
        # Save the updated player
        repo.update(player_data)
        print(f"Player {player_data['name']} reset to initial state (all skills = 1)")
    else:
        print("DC test player not found!")

if __name__ == "__main__":
    reset_dc_player()