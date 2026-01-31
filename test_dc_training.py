#!/usr/bin/env python3
"""
Script to test DC player training and analyze results
"""

from storage.player_repository import PlayerRepository
from domain.player import Player
from domain.training_recommender import TrainingRecommender
from config.skills import SKILLS
from config.positions import POSITIONS

def calculate_stats(player_data):
    """Calculate various statistics for the player"""
    # Calculate white skills
    white_skills = set()
    for pos in player_data["positions"]:
        white_skills.update(POSITIONS[pos]["white_skills"])

    gray_skills = set(SKILLS.keys()) - white_skills

    # Get skill values
    all_skills_values = list(player_data["skills"].values())
    white_skills_values = [player_data["skills"][skill_id] for skill_id in white_skills]
    gray_skills_values = [player_data["skills"][skill_id] for skill_id in gray_skills]

    # Calculate averages
    all_skills_avg = sum(all_skills_values) / len(all_skills_values) if all_skills_values else 0
    white_skills_avg = sum(white_skills_values) / len(white_skills_values) if white_skills_values else 0
    gray_skills_avg = sum(gray_skills_values) / len(gray_skills_values) if gray_skills_values else 0

    # Calculate difference between strongest and weakest white skills
    sorted_white_values = sorted(white_skills_values)
    white_skill_difference = sorted_white_values[-1] - sorted_white_values[0] if sorted_white_values else 0

    return {
        "all_skills_avg": all_skills_avg,
        "white_skills_avg": white_skills_avg,
        "gray_skills_avg": gray_skills_avg,
        "white_skill_difference": white_skill_difference,
        "max_total_skill": max(all_skills_values),
        "total_sum": sum(all_skills_values)
    }

def run_training_sessions(player_id, sessions=30):
    """Run multiple training sessions for the specified player"""
    repo = PlayerRepository()

    # Load the player
    player_data = repo.get(player_id)
    if not player_data:
        print(f"Player with ID {player_id} not found!")
        return

    print(f"Initial state for {player_data['name']}:")
    stats = calculate_stats(player_data)
    print(f"All skills avg: {stats['all_skills_avg']:.2f}")
    print(f"White skills avg: {stats['white_skills_avg']:.2f}")
    print(f"Gray skills avg: {stats['gray_skills_avg']:.2f}")
    print(f"Max total skill: {stats['max_total_skill']}")
    print(f"Total sum: {stats['total_sum']}")
    
    # Run training sessions - apply just one training session at a time
    for i in range(sessions):
        # Create Player object
        player_obj = Player(
            name=player_data["name"],
            positions=player_data["positions"],
            skills=player_data["skills"],
        )
        
        # Get training recommendation for just one training session
        from domain.training_planner import TrainingPlanner
        planner = TrainingPlanner(player_obj)
        plan = planner.plan(max_trainings=1)  # Just one training session
        
        # Apply the training to the player
        if plan:
            from config.trainings import TRAININGS
            for item in plan:
                training_data = TRAININGS[item.training_id]
                # Apply the training
                for _ in range(item.repeats):
                    player_obj.apply_training(training_data["skills"], gain=10)  # Using gain of 10 like in training_planner

        # Update player data with modified skills
        player_data["skills"] = player_obj.skills

    # Update player in repository
    repo.update(player_data)
    
    print(f"\nAfter {sessions} training sessions:")
    stats = calculate_stats(player_data)
    print(f"All skills avg: {stats['all_skills_avg']:.2f}")
    print(f"White skills avg: {stats['white_skills_avg']:.2f}")
    print(f"Gray skills avg: {stats['gray_skills_avg']:.2f}")
    print(f"Max total skill: {stats['max_total_skill']}")
    print(f"White skill difference (strongest-weakest): {stats['white_skill_difference']}")
    print(f"Total sum: {stats['total_sum']}")
    
    # Show some example skills
    print("\nSample white skills:", {k: v for k, v in player_data["skills"].items() 
                                   if k in POSITIONS[player_data["positions"][0]]["white_skills"]} )
    print("Sample gray skills:", {k: v for k, v in player_data["skills"].items() 
                                 if k not in POSITIONS[player_data["positions"][0]]["white_skills"]} )

if __name__ == "__main__":
    # Test with the DC player (test_dc)
    player_id = "ffc4f365-4ba3-48d9-a5f2-45052cf6ff5a"
    run_training_sessions(player_id, sessions=30)