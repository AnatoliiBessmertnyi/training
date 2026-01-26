def training_difficulty(skill_value: int) -> float:
    """
    Коэффициент сложности прокачки навыка.
    Чем выше навык — тем меньше эффективность тренировок.
    """
    if skill_value < 100:
        return 1.0
    elif skill_value < 200:
        return 1.5
    elif skill_value < 300:
        return 2.5
    else:
        return 4.0
