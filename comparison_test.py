from config.positions import POSITIONS
from config.skills import SKILLS
from config.trainings import TRAININGS
from domain.player import Player
from domain.training_planner import TrainingPlanner
import copy


class OriginalTrainingPlanner:
    """Оригинальная версия планировщика для сравнения"""
    def __init__(self, player: Player):
        self.player = player
        self.white_skills = set(player.white_skills)
        self.gray_skills = set(player.gray_skills)

    def plan(self, max_trainings: int = 50) -> list:
        plan_items = {}

        # копия, чтобы симулировать рост
        simulated_skills = self.player.skills.copy()
        
        # Словарь для отслеживания количества тренировок для каждого белого навыка
        skill_training_counts = {skill: 0 for skill in self.white_skills}

        for _ in range(max_trainings):
            # Находим лучшую тренировку для следующего шага
            best_training_id = self._find_best_training_original(simulated_skills, skill_training_counts)
            
            if best_training_id is None:
                break
                
            # Применяем тренировку к симулируемым навыкам
            self._apply_training(simulated_skills, best_training_id)
            
            # Обновляем счетчики тренировок для белых навыков
            training_data = TRAININGS[best_training_id]
            for skill in training_data["skills"]:
                if skill in self.white_skills:
                    skill_training_counts[skill] += 1
            
            # Добавляем тренировку в план
            if best_training_id in plan_items:
                plan_items[best_training_id].repeats += 1
            else:
                from domain.training_planner import TrainingPlanItem
                training_data = TRAININGS[best_training_id]
                plan_items[best_training_id] = TrainingPlanItem(
                    training_id=best_training_id,
                    name=training_data["name"],
                    repeats=1,
                    skills=training_data["skills"]
                )

        return list(plan_items.values())

    def _find_best_training_original(self, skills: dict, skill_training_counts: dict) -> str | None:
        """
        Оригинальная версия метода для нахождения лучшей тренировки
        """
        # Получаем текущие значения белых навыков
        white_skill_values = {skill: skills[skill] for skill in self.white_skills}
        
        if not white_skill_values:
            return None
            
        # Сначала определим, какие навыки наиболее отстают
        sorted_white_skills = sorted(white_skill_values.items(), key=lambda x: x[1])
        
        # Выберем навыки с самыми низкими значениями как приоритетные для тренировки
        lowest_skills = [skill for skill, value in sorted_white_skills[:4]]  # 4 самых слабых навыка
        
        best_training_id = None
        best_score = -float('inf')
        
        for tr_id, tr_data in TRAININGS.items():
            # Проверяем, есть ли белые навыки в этой тренировке
            training_white_skills = set(tr_data["skills"]) & self.white_skills
            if not training_white_skills:
                continue
                
            # Проверяем, есть ли серые навыки (чем их больше, тем хуже)
            training_gray_skills = set(tr_data["skills"]) & self.gray_skills
            
            # Основная логика: штрафуем за серые навыки, премируем за покрытие отстающих навыков
            score = 0
            
            # Штраф за серые навыки
            gray_penalty = len(training_gray_skills) * 20  # усиленный штраф за серые навыки
            
            # Премия за покрытие отстающих навыков
            low_skill_bonus = 0
            for skill in training_white_skills:
                if skill in lowest_skills:
                    low_skill_bonus += 15  # высокая премия за тренировку отстающих навыков
            
            # Премия за покрытие разнообразных белых навыков
            diversity_bonus = len(training_white_skills) * 3
            
            # Штраф за повторное тренирование одного и того же навыка
            repetition_penalty = 0
            for skill in training_white_skills:
                if skill in skill_training_counts:
                    repetition_penalty += skill_training_counts[skill] * 2
            
            score = low_skill_bonus + diversity_bonus - gray_penalty - repetition_penalty
            
            if score > best_score:
                best_score = score
                best_training_id = tr_id
        
        return best_training_id

    def _apply_training(self, skills: dict, training_data_or_id) -> None:
        """
        Применяет тренировку к переданным навыкам (влияет напрямую на переданный словарь).
        """
        MAX_SKILL_LEVEL = 400
        BASE_TRAINING_GAIN = 10
        
        if isinstance(training_data_or_id, str):
            training_data = TRAININGS[training_data_or_id]
        else:
            training_data = training_data_or_id
            
        for skill_id in training_data["skills"]:
            if skill_id in skills:
                # Увеличиваем навык с учетом максимального порога
                skills[skill_id] = min(MAX_SKILL_LEVEL, skills[skill_id] + BASE_TRAINING_GAIN)


def analyze_white_skills_balance(player: Player):
    """Анализирует равномерность белых навыков"""
    white_skills = set(player.white_skills)
    white_values = [player.skills[skill] for skill in white_skills]
    
    min_val = min(white_values)
    max_val = max(white_values)
    avg_val = sum(white_values) / len(white_values)
    spread = max_val - min_val
    
    return spread, min_val, max_val, avg_val


def simulate_multiple_cycles_with_comparison(player_data, cycles: int = 5, trainings_per_cycle: int = 30):
    """Симулирует несколько циклов тренировок с обоими алгоритмами"""
    # Подготовим данные игрока
    all_skills = player_data["skills"].copy()
    for skill_id in SKILLS:
        if skill_id not in all_skills:
            all_skills[skill_id] = 1

    # Создаём игрока
    original_player = Player(name=player_data["name"], positions=player_data["positions"], skills=all_skills)
    
    print("=== СРАВНЕНИЕ СТАРОГО И НОВОГО АЛГОРИТМА ===\n")
    
    # Симуляция с оригинальным алгоритмом
    print("--- ОРИГИНАЛЬНЫЙ АЛГОРИТМ ---")
    simulated_skills_orig = original_player.skills.copy()
    
    for cycle in range(cycles):
        print(f"\nЦикл {cycle + 1}:")
        
        # Создаем игрока с текущими навыками для нового планирования
        current_player = Player(name=original_player.name, positions=original_player.positions, skills=simulated_skills_orig)
        
        # Используем оригинальный планировщик
        original_planner = OriginalTrainingPlanner(current_player)
        plan = original_planner.plan(max_trainings=trainings_per_cycle)
        
        # Выполняем план
        for item in plan:
            training_data = TRAININGS[item.training_id]
            
            for _ in range(item.repeats):
                for skill_id in training_data["skills"]:
                    if skill_id in simulated_skills_orig:
                        old_value = simulated_skills_orig[skill_id]
                        new_value = min(400, old_value + 10)  # BASE_TRAINING_GAIN = 10
                        simulated_skills_orig[skill_id] = new_value
        
        # Анализируем результаты цикла
        current_player_after_cycle = Player(name=original_player.name, positions=original_player.positions, skills=simulated_skills_orig)
        spread, min_val, max_val, avg = analyze_white_skills_balance(current_player_after_cycle)
        print(f"  Разброс: {spread}, мин: {min_val}, макс: {max_val}, сред: {avg:.1f}")

    print("\n" + "="*50)
    
    # Симуляция с новым алгоритмом
    print("--- НОВЫЙ АЛГОРИТМ (УЛУЧШЕННЫЙ) ---")
    simulated_skills_new = original_player.skills.copy()
    
    for cycle in range(cycles):
        print(f"\nЦикл {cycle + 1}:")
        
        # Создаем игрока с текущими навыками для нового планирования
        current_player = Player(name=original_player.name, positions=original_player.positions, skills=simulated_skills_new)
        
        # Используем новый планировщик
        new_planner = TrainingPlanner(current_player)
        plan = new_planner.plan(max_trainings=trainings_per_cycle)
        
        # Выполняем план
        for item in plan:
            training_data = TRAININGS[item.training_id]
            
            for _ in range(item.repeats):
                for skill_id in training_data["skills"]:
                    if skill_id in simulated_skills_new:
                        old_value = simulated_skills_new[skill_id]
                        new_value = min(400, old_value + 10)  # BASE_TRAINING_GAIN = 10
                        simulated_skills_new[skill_id] = new_value
        
        # Анализируем результаты цикла
        current_player_after_cycle = Player(name=original_player.name, positions=original_player.positions, skills=simulated_skills_new)
        spread, min_val, max_val, avg = analyze_white_skills_balance(current_player_after_cycle)
        print(f"  Разброс: {spread}, мин: {min_val}, макс: {max_val}, сред: {avg:.1f}")


def main():
    # Данные игрока Geringer
    player_data = {
        "name": "Geringer",
        "positions": ["DMC", "MC", "AMC"],
        "skills": {
            "tackling": 93,
            "marking": 90,
            "positioning": 91,
            "heading": 103,
            "bravery": 102,
            "passing": 108,
            "dribbling": 98,
            "cross": 50,
            "shooting": 109,
            "finishing": 118,
            "physical": 106,
            "strength": 91,
            "aggressiveness": 81,
            "pace": 108,
            "creativity": 90
        }
    }
    
    simulate_multiple_cycles_with_comparison(player_data, cycles=5, trainings_per_cycle=30)


if __name__ == "__main__":
    main()