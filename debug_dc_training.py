#!/usr/bin/env python3
"""
Script to debug DC player training and analyze the skill progression algorithm
"""

from domain.player import Player
from domain.training_planner import TrainingPlanner
from config.skills import SKILLS
from config.positions import POSITIONS
from config.trainings import TRAININGS


def create_fresh_dc_player():
    """Create a fresh DC player with all skills at level 1"""
    # Create skills dictionary with all skills at level 1
    skills = {skill_id: 1 for skill_id in SKILLS.keys()}
    
    player = Player(
        name="Fresh DC Player",
        positions=["DC"],
        skills=skills
    )
    return player


def calculate_stats(player):
    """Calculate various statistics for the player"""
    white_skills = set()
    for pos in player.positions:
        white_skills.update(POSITIONS[pos]["white_skills"])

    gray_skills = set(SKILLS.keys()) - white_skills

    # Get skill values
    all_skills_values = list(player.skills.values())
    white_skills_values = [player.skills[skill_id] for skill_id in white_skills]
    gray_skills_values = [player.skills[skill_id] for skill_id in gray_skills]

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
        "max_white_skill": max(white_skills_values) if white_skills_values else 0,
        "min_white_skill": min(white_skills_values) if white_skills_values else 0,
        "max_total_skill": max(all_skills_values),
        "total_sum": sum(all_skills_values)
    }


def run_debug_training():
    """Debug the training algorithm step by step"""
    print("Creating fresh DC player...")
    player = create_fresh_dc_player()
    
    print(f"Initial state:")
    initial_stats = calculate_stats(player)
    print(f"  All skills avg: {initial_stats['all_skills_avg']:.2f}")
    print(f"  White skills avg: {initial_stats['white_skills_avg']:.2f}")
    print(f"  Gray skills avg: {initial_stats['gray_skills_avg']:.2f}")
    print(f"  Max white skill: {initial_stats['max_white_skill']}")
    print(f"  Min white skill: {initial_stats['min_white_skill']}")
    print(f"  White skill difference: {initial_stats['white_skill_difference']}")
    print(f"  Max total skill: {initial_stats['max_total_skill']}")
    
    print("\nStarting training...")
    
    # Train step by step
    for i in range(30):  # Do 30 training sessions
        # Create a planner for current state
        planner = TrainingPlanner(player)
        
        # Plan just one training session
        plan = planner.plan(max_trainings=1)
        
        if plan:
            # Apply the training
            for item in plan:
                training_data = TRAININGS[item.training_id]
                player.apply_training(training_data["skills"], gain=10)
                
                # Print info about the training applied
                white_affected = [skill for skill in training_data["skills"] if skill in player.white_skills]
                gray_affected = [skill for skill in training_data["skills"] if skill in player.gray_skills]
                
                print(f"\nSession {i+1}: Applied '{item.name}' ({item.training_id})")
                print(f"  Affected white skills: {len(white_affected)} - {white_affected}")
                print(f"  Affected gray skills: {len(gray_affected)} - {gray_affected[:3]}{'...' if len(gray_affected) > 3 else ''}")  # Show first 3 gray skills
        
        # Calculate stats after each session
        if (i + 1) % 5 == 0 or i == 0 or i == 29:  # Show stats every 5 sessions and at start/end
            stats = calculate_stats(player)
            print(f"\nAfter {i+1} sessions:")
            print(f"  All skills avg: {stats['all_skills_avg']:.2f}")
            print(f"  White skills avg: {stats['white_skills_avg']:.2f}")
            print(f"  Gray skills avg: {stats['gray_skills_avg']:.2f}")
            print(f"  Max white skill: {stats['max_white_skill']}")
            print(f"  Min white skill: {stats['min_white_skill']}")
            print(f"  White skill difference: {stats['white_skill_difference']}")
            print(f"  Max total skill: {stats['max_total_skill']}")
            
            # Show current white skills distribution
            white_skills = [player.skills[skill_id] for skill_id in player.white_skills]
            sorted_white = sorted(white_skills, reverse=True)
            print(f"  Top 5 white skills: {sorted_white[:5]}")
            print(f"  Bottom 5 white skills: {sorted_white[-5:]}")
    
    print(f"\nFinal white skills breakdown:")
    dc_white_skills = POSITIONS["DC"]["white_skills"]
    for skill in dc_white_skills:
        print(f"  {skill}: {player.skills[skill]}")


if __name__ == "__main__":
    run_debug_training()