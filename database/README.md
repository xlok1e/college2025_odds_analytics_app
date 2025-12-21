# База данных приложения

Этот каталог содержит SQL-скрипты для создания и заполнения базы данных PostgreSQL.

## Структура

```
database/
├── scripts/
│   ├── create_tables.sql       # Создание таблиц и индексов
│   └── insert_mock_data.sql    # Заполнение таблиц тестовыми данными
└── README.md
```

## Схема базы данных

### Основные таблицы

1. **countries** - Страны
2. **sports** - Виды спорта
3. **teams** - Команды
4. **tournaments** - Турниры
5. **events** - События (матчи)
6. **bookmakers** - Букмекерские конторы
7. **bet_types** - Типы ставок
8. **odds_records** - История коэффициентов

### Связи

- `teams` связаны с `sports` и `countries`
- `tournaments` связаны с `sports` и `countries`
- `events` связаны с `teams` и `tournaments`
- `odds_records` связаны с `events`, `bookmakers` и `bet_types`

## Запуск с Docker

### 1. Запуск контейнера PostgreSQL

```bash
docker-compose up -d
```

Это автоматически:
- Создаст контейнер PostgreSQL
- Выполнит скрипты создания таблиц
- Заполнит таблицы тестовыми данными

### 2. Проверка статуса

```bash
docker-compose ps
```

### 3. Подключение к БД из контейнера

```bash
docker exec -it my_app_postgres psql -U myappuser -d myappdb
```

### 4. Остановка контейнера

```bash
docker-compose down
```

### 5. Полная очистка (включая данные)

```bash
docker-compose down -v
```

## Запуск без Docker

### 1. Установка PostgreSQL

Убедитесь, что PostgreSQL установлен и запущен.

### 2. Создание базы данных

```bash
createdb -U postgres myappdb
```

### 3. Выполнение скриптов

```bash
psql -U postgres -d myappdb -f database/scripts/create_tables.sql
psql -U postgres -d myappdb -f database/scripts/insert_mock_data.sql
```

## Автоматическая инициализация

Приложение автоматически проверяет наличие таблиц при запуске и создаёт их, если они отсутствуют.

### Как это работает:

1. При запуске приложения вызывается `DatabaseManager.initialize()`
2. Проверяется существование таблицы `events`
3. Если таблица не существует:
   - Выполняется `create_tables.sql`
   - Выполняется `insert_mock_data.sql`
4. Загружаются данные событий из БД

## Тестирование подключения

Для проверки подключения к базе данных запустите:

```bash
python test_db.py
```

Скрипт выполнит:
- Инициализацию БД
- Проверку существования таблиц
- Получение списка событий
- Получение коэффициентов и букмекеров

## Настройка подключения

Параметры подключения находятся в файле `config.py`:

```python
@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5433
    database: str = "myappdb"
    user: str = "myappuser"
    password: str = "myapppass"
```

## Тестовые данные

После инициализации БД будет создано:
- 8 стран
- 4 вида спорта
- 13 команд
- 6 турниров
- 4 букмекера
- 7 типов ставок
- 6 событий
- ~100 записей коэффициентов

### События в тестовых данных:

1. **Зенит - Спартак** (Футбол, РПЛ)
2. **Реал Мадрид - Манчестер Сити** (Футбол, Лига Чемпионов)
3. **ЦСКА - СКА** (Хоккей, КХЛ)
4. **ЦСКА - Зенит** (Баскетбол, Единая лига ВТБ)
5. **Ливерпуль - Арсенал** (Футбол, АПЛ)
6. **Медведев Д. - Алькарас К.** (Теннис, ATP Masters)

## Полезные SQL-запросы

### Получить все события с коэффициентами

```sql
SELECT
    e.event_id,
    s.sport_name,
    t.tournament_name,
    team1.team_name || ' - ' || team2.team_name as match,
    e.event_datetime
FROM events e
JOIN tournaments t ON e.tournament_id = t.tournament_id
JOIN sports s ON t.sport_id = s.sport_id
JOIN teams team1 ON e.team1_id = team1.team_id
JOIN teams team2 ON e.team2_id = team2.team_id
ORDER BY e.event_datetime;
```

### Получить историю изменения коэффициента

```sql
SELECT
    orr.recorded_at,
    b.bookmaker_name,
    bt.bet_type_name,
    orr.odds_value
FROM odds_records orr
JOIN bookmakers b ON orr.bookmaker_id = b.bookmaker_id
JOIN bet_types bt ON orr.bet_type_id = bt.bet_type_id
WHERE orr.event_id = 1
  AND bt.bet_type_code = 'win_1'
ORDER BY orr.recorded_at;
```

### Статистика по событиям

```sql
SELECT
    s.sport_name,
    COUNT(e.event_id) as events_count,
    COUNT(DISTINCT orr.odds_record_id) as total_odds_records
FROM sports s
LEFT JOIN tournaments t ON s.sport_id = t.sport_id
LEFT JOIN events e ON t.tournament_id = e.tournament_id
LEFT JOIN odds_records orr ON e.event_id = orr.event_id
GROUP BY s.sport_name;
```

## Troubleshooting

### Ошибка подключения

```
✗ Ошибка подключения к PostgreSQL: connection refused
```

**Решение:**
- Проверьте, что PostgreSQL запущен: `docker-compose ps`
- Проверьте порт в `config.py` (по умолчанию 5433)

### Таблицы не создаются

```
✗ Таблицы не найдены
```

**Решение:**
- Убедитесь, что скрипты находятся в `database/scripts/`
- Проверьте права доступа к файлам
- Пересоздайте контейнер: `docker-compose down -v && docker-compose up -d`

### Дублирование данных

При повторном запуске `insert_mock_data.sql` используются `ON CONFLICT` для предотвращения дублирования:

```sql
INSERT INTO countries (country_name, country_code) VALUES
('Россия', 'RUS')
ON CONFLICT (country_code) DO NOTHING;
```

## Миграции

При изменении структуры БД:

1. Создайте новый SQL-скрипт с миграцией
2. Выполните его вручную или через `DatabaseManager.execute_script()`
3. Обновите `create_tables.sql` для новых установок

## Бэкап и восстановление

### Создание бэкапа

```bash
docker exec my_app_postgres pg_dump -U myappuser myappdb > backup.sql
```

### Восстановление из бэкапа

```bash
docker exec -i my_app_postgres psql -U myappuser myappdb < backup.sql
```
