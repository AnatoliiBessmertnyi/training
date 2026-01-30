def training_difficulty(skill_value: int, is_gray_skill: bool = False) -> float:
    """
    Коэффициент сложности прокачки навыка.
    Чем выше навык — тем меньше эффективность тренировок.
    Для серых навыков применяется дополнительный штраф при значениях выше 21.
    """
    if is_gray_skill and skill_value > 21:
        # Для серых навыков выше 21 применяем более жесткий штраф
        base_multiplier = 1.0
        if skill_value < 100:
            base_multiplier = 1.0
        elif skill_value < 200:
            base_multiplier = 1.5
        elif skill_value < 300:
            base_multiplier = 2.5
        else:
            base_multiplier = 4.0
        
        # Увеличиваем штраф в зависимости от значения навыка (чем выше, тем дороже)
        if skill_value > 21:
            penalty_factor = 1.0 + (skill_value - 21) * 0.05  # Увеличиваем штраф по мере роста навыка
            return base_multiplier * penalty_factor
        else:
            return base_multiplier
    else:
        # Обычная логика для белых навыков
        if skill_value < 100:
            return 1.0
        elif skill_value < 200:
            return 1.5
        elif skill_value < 300:
            return 2.5
        else:
            return 4.0
