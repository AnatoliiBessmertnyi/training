# Детальный план реализации Backend (обновлённый)

> Инструмент персональный, ориентирован на максимальную простоту и скорость разработки.  
> Backend пишется первым, без преждевременной оптимизации.

---

## Этап 0. Общие договорённости

- Backend → Frontend → Интеграция → Доработки
- Язык: **только русский** (UI, описания, конфиги)
- Все идентификаторы: `snake_case`
- Хардкод разрешён
- Все справочники хранятся централизованно в `config/`
- Минимум абстракций, читаемость важнее расширяемости
- Инструмент строго для одного пользователя

---

## Этап 1. Config-слой (источник истины)

Config-слой не содержит логики, только данные.

### 1.1 `config/skills.py`

```python
SKILLS: dict[str, str] = {
    # Нападение
    "passing": "Передача",
    "dribbling": "Дриблинг",
    "cross": "Навес",
    "finishing": "Завершение",
    "shooting": "Удары",

    # Психофизика
    "physical": "Физическая форма",
    "strength": "Сила",
    "aggressiveness": "Агрессивность",
    "pace": "Скорость",
    "creativity": "Креативность",

    # Защита
    "tackling": "Отбор мяча",
    "marking": "Опека",
    "positioning": "Выбор позиции",
    "heading": "Игра головой",
    "bravery": "Храбрость",
}

TOTAL_SKILLS_COUNT = 15
id навыка используется везде

после старта проекта id не меняются

значения навыков ∈ [1..100]

✅ Статус: сделано

1.2 config/positions.py
Каждая позиция содержит белые навыки

Обновлено под новый список навыков с креативностью

Пример структуры:

POSITIONS = {
    "ST": {
        "name": "Нападающий",
        "white_skills": [
            "positioning",
            "heading",
            "passing",
            "dribbling",
            "shooting",
            "finishing",
            "strength",
            "pace",
            "creativity",
        ],
    },
    "AMC": {
        "name": "Атакующий полузащитник",
        "white_skills": [
            "heading",
            "passing",
            "dribbling",
            "shooting",
            "finishing",
            "physical",
            "pace",
            "creativity",
        ],
    },
}
✅ Статус: сделано

1.3 config/trainings.py
Каждая тренировка:

влияет на фиксированный набор навыков

содержит name на русском

тип тренировки (attack, defence, possession, physical)

Пример:

TRAININGS = {
    "one_of_one": {
        "name": "Один на один",
        "type": "attack",
        "skills": ["dribbling", "tackling", "finishing"],
    },
    "stretching": {
        "name": "Растяжка",
        "type": "physical",
        "skills": ["strength", "pace", "physical"],
    },
}
✅ Статус: сделано

Этап 2. Domain-слой (чистая логика)
2.1 Модель игрока
class Player:
    id: int
    name: str
    positions: list[str]  # коды позиций
    skills: dict[str, int]  # skill_id -> значение

    @property
    def white_skills(self) -> set[str]:
        ...
    
    @property
    def gray_skills(self) -> set[str]:
        ...
    
    def weakest_white_skills(self, N: int) -> list[str]:
        ...
✅ Статус: сделано (реализовано)

2.2 Алгоритм рекомендаций тренировок
Выбирает топ N слабых белых навыков

Подбирает тренировки:

минимизирующие затрагивание серых навыков

дающие баланс белых навыков

Функции:

def recommend_trainings(player, trainings, N, penalty):
    ...
✅ Статус: сделано (реализовано для анализа и предложений)

2.3 Применение тренировки (симуляция)
Тренировка всегда качает одно и то же количество навыков

Реальный прирост зависит от текущего уровня (не учитываем точный регресс)

def apply_training(player, training):
    ...
2.4 Месячная деградация
def apply_monthly_decay(player):
    for skill in player.skills:
        player.skills[skill] = max(1, player.skills[skill] - 20)
✅ Статус: сделано

Этап 3. Циклы тренировок
Один цикл = 6 тренировок

Тренировки могут повторяться

Алгоритм подбирает цикл, который выравнивает белые навыки

class TrainingCycle:
    trainings: list[str]  # список id тренировок
✅ Статус: реализован базовый скелет

Этап 4. Сервисы
PlayerService

TrainingService

CycleService

Без DI, без репозиториев — простая функциональность через классы и методы

Этап 5. Хранение данных
JSON / in-memory

Один файл на игрока / вся команда

Этап 6. API / Interface
CRUD игроков

Применение тренировки / цикла

Месячная деградация

Получение состояния игрока

Получение рекомендованного тренировочного цикла

Примеры эндпоинтов:

GET /players

POST /players

PUT /players/{id}

POST /players/{id}/degrade

GET /players/{id}/recommendations?top_n=N&penalty=P

Этап 7. Готовность к frontend
Backend полностью функционален

Frontend подключается как тонкий слой

Статус реализации
Этап	Статус
1.1 Config Skills	✅ готово
1.2 Config Positions	✅ готово
1.3 Config Trainings	✅ готово
2.1 Player model	✅ готово
2.2 Training recommendations	✅ реализовано (аналитика без применения)
2.3 Apply training	⚪ нужно подключить к симуляции
2.4 Monthly decay	✅ готово
3 TrainingCycle	⚪ базовый скелет
4 Services	⚪ нужно сделать классы
5 Storage	⚪ пока JSON / in-memory
6 API	⚪ нужно реализовать FastAPI эндпоинты