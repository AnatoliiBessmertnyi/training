def white_balance_score(
    skills: dict[str, int],
    white_skills: set[str],
) -> int:
    """
    Чем меньше значение — тем лучше баланс.
    Используем разницу между max и min белых навыков.
    """

    values = [skills[s] for s in white_skills]

    return max(values) - min(values)
