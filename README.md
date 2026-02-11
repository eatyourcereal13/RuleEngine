```markdown
# Rule Engine

Движок правил для управления рекламными кампаниями

## Запуск
1. Скопируйте файл с переменными окружения:
```bash
   cp .env.example .env

# 2. Запуск с Docker
docker-compose up --build

# Миграции применяются автоматически
# API доступно на http://localhost:8000
# Документация: http://localhost:8000/docs
```

## Тесты

```bash
# Unit-тесты правил и сценариев
pytest tests/rules/ -v
pytest tests/scenarios/ -v

# Все тесты
pytest tests/ -v

```

## Архитектура

### Движок правил

Правила применяются строго по приоритету (1 - наивысший):

1. **disabled_management** - управление отключено
2. **schedule** - время вне активных слотов
3. **low_stock** - мало остатков (< stock_days_min)
4. **budget_exceeded** - превышен дневной бюджет
5. **no_restrictions** - нет ограничений (active)

```python
#== БАЗОВЫЙ ИНТЕРФЕЙС ПРАВИЛА ==
class Rule(ABC):
    @property
    def priority(self) -> int
    @property
    def rule_name(self) -> TriggeredRule
    async def evaluate(campaign, schedules, current_time) -> Tuple[bool, str]
```

### Структура проекта
## Был выбран именно такой паттерн для избежания оверинжиниринга (потому что этот бэкэнд очень простой И не будет требовать расширения в будущем). Выбор был из "django-подобного" - этого и четкого разделения по папкам Domain/Infrastructure/Application. Если потребуется - перепишу на другой паттерн :)
```
app/
├── campaigns/      # Модели, схемы, роуты кампаний
├── schedules/      # Модели, схемы, роуты расписания
├── rules/          # Классы правил (каждое в отдельном файле)
├── evaluations/    # RuleEngine, история, роуты evaluate
└── core/           # Config, database, enums
```

## Эндпоинты API

### Кампании

| Метод | Эндпоинт | Описание |
|--------|----------|----------|
| `POST` | `/api/v1/campaigns` | Создание кампании |
| `GET` | `/api/v1/campaigns` | Список кампаний (с пагинацией и фильтрацией) |
| `GET` | `/api/v1/campaigns/{id}` | Получение кампании по ID |
| `PATCH` | `/api/v1/campaigns/{id}` | Обновление кампании |

**Параметры фильтрации GET /campaigns:**
- `skip` - смещение (по умолч. 0)
- `limit` - лимит (по умолч. 100, макс. 1000)
- `needs_sync` - только кампании где `current_status != target_status` (`true/false`)

### Расписание

| Метод | Эндпоинт | Описание |
|--------|----------|----------|
| `PUT` | `/api/v1/campaigns/{id}/schedule` | Установить расписание (заменяет все слоты) |
| `GET` | `/api/v1/campaigns/{id}/schedule` | Получить расписание |
| `DELETE` | `/api/v1/campaigns/{id}/schedule` | Удалить расписание |

### Вычисление правил

| Метод | Эндпоинт | Описание |
|--------|----------|----------|
| `POST` | `/api/v1/campaigns/{id}/evaluate` | Вычислить target_status для кампании |
| `POST` | `/api/v1/campaigns/evaluate-all` | Вычислить target_status для всех управляемых кампаний |
| `GET` | `/api/v1/campaigns/{id}/evaluation-history` | История вычислений для кампании |

**Параметр `dry_run` для evaluate-эндпоинтов:**
- `?dry_run=true` - только вычислить, не сохранять в БД
- `?dry_run=false` - вычислить и сохранить (по умолч.)

