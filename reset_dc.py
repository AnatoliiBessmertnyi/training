#!/usr/bin/env python3
"""
Reset DC player to initial state and test the improved algorithm
"""

from storage.player_repository import PlayerRepository

def reset_dc_player():
    """Reset the DC player to initial state with proper starting values"""
    repo = PlayerRepository()
    
    # Find the test_dc player
    player_id = "ffc4f365-4ba3-48d9-a5f2-45052cf6ff5a"
    player_data = repo.get(player_id)
    
    if player_data:
        # Set initial skill values as they were originally
        initial_skills = {
            "tackling": 121,
            "marking": 131,
            "positioning": 131,
            "heading": 71,
            "bravery": 121,
            "passing": 1,
            "dribbling": 1,
            "cross": 1,
            "shooting": 1,
            "finishing": 1,
            "physical": 171,
            "strength": 101,
            "aggressiveness": 191,
            "pace": 1,
            "creativity": 1
        }
        
        player_data["skills"] = initial_skills
        # Reset training count
        player_data["training_count"] = 0
        
        # Save the updated player
        repo.update(player_data)
        print(f"Player {player_data['name']} reset to initial state")
    else:
        print("DC test player not found!")

if __name__ == "__main__":
    reset_dc_player()