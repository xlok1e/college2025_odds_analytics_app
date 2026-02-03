import csv
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from db_manager import DatabaseManager


class ImportValidationError(Exception):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EventImportService:

    REQUIRED_FIELDS = ['sport', 'tournament', 'country', 'team1', 'team2', 'date']
    OPTIONAL_FIELDS = ['bookmakers', 'coefficients', 'coef_p1', 'coef_x', 'coef_p2']

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        # Кэши для уменьшения количества запросов к БД
        self._sports_cache: Dict[str, int] = {}
        self._countries_cache: Dict[str, int] = {}
        self._tournaments_cache: Dict[Tuple[str, int, int], int] = {}
        self._teams_cache: Dict[Tuple[str, int], int] = {}
        self._bookmakers_cache: Dict[str, int] = {}
        self._bet_types_cache: Dict[str, int] = {}

    def import_from_file(self, file_path: str) -> Tuple[int, List[str]]:
        if file_path.lower().endswith('.json'):
            return self._import_from_json(file_path)
        elif file_path.lower().endswith('.csv'):
            return self._import_from_csv(file_path)
        else:
            raise ImportValidationError(
                "Неподдерживаемый формат файла",
                {"supported": ["JSON", "CSV"], "provided": file_path.split('.')[-1]}
            )

    def _import_from_json(self, file_path: str) -> Tuple[int, List[str]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ImportValidationError(
                f"Ошибка парсинга JSON файла: {str(e)}",
                {"error": str(e)}
            )
        except Exception as e:
            raise ImportValidationError(
                f"Ошибка чтения файла: {str(e)}",
                {"error": str(e)}
            )

        if not isinstance(data, dict) or 'events' not in data:
            raise ImportValidationError(
                "JSON файл должен содержать корневой объект с полем 'events'",
                {"example": {"events": [{"sport": "...", "tournament": "..."}]}}
            )

        if not isinstance(data['events'], list):
            raise ImportValidationError(
                "Поле 'events' должно быть массивом",
                {"provided_type": type(data['events']).__name__}
            )

        events = data['events']

        if len(events) == 0:
            raise ImportValidationError(
                "Список событий пустой. Добавьте хотя бы одно событие для импорта."
            )

        return self._process_events(events)

    def _import_from_csv(self, file_path: str) -> Tuple[int, List[str]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                events = []

                for row_num, row in enumerate(reader, start=2):
                    event = {
                        'sport': row.get('sport', '').strip(),
                        'tournament': row.get('tournament', '').strip(),
                        'country': row.get('country', '').strip(),
                        'team1': row.get('team1', '').strip(),
                        'team2': row.get('team2', '').strip(),
                        'date': row.get('date', '').strip(),
                    }

                    bookmakers_str = row.get('bookmakers', '').strip()
                    if bookmakers_str:
                        event['bookmakers'] = [b.strip() for b in bookmakers_str.split(',')]

                    coef_p1 = row.get('coef_p1', '').strip()
                    coef_x = row.get('coef_x', '').strip()
                    coef_p2 = row.get('coef_p2', '').strip()

                    if coef_p1 or coef_x or coef_p2:
                        event['coefficients'] = {}
                        if coef_p1:
                            try:
                                event['coefficients']['p1'] = float(coef_p1)
                            except ValueError:
                                pass
                        if coef_x:
                            try:
                                event['coefficients']['x'] = float(coef_x)
                            except ValueError:
                                pass
                        if coef_p2:
                            try:
                                event['coefficients']['p2'] = float(coef_p2)
                            except ValueError:
                                pass

                    events.append(event)

        except Exception as e:
            raise ImportValidationError(
                f"Ошибка чтения CSV файла: {str(e)}",
                {"error": str(e)}
            )

        if not events:
            raise ImportValidationError(
                "CSV файл пустой или не содержит данных",
                {"required_columns": self.REQUIRED_FIELDS}
            )

        return self._process_events(events)

    def _process_events(self, events: List[Dict[str, Any]]) -> Tuple[int, List[str]]:
        imported_count = 0
        errors = []
        has_critical_error = False

        print(f"[ImportService] Начало обработки {len(events)} событий")

        # Предзагружаем кэши для оптимизации
        try:
            self._preload_caches()
            print(f"[ImportService] Кэши предзагружены")
        except Exception as e:
            print(f"[ImportService] Ошибка предзагрузки кэшей: {e}")
            raise ImportValidationError(f"Ошибка подключения к БД: {str(e)}")

        # Используем одну транзакцию для всего импорта
        if not self.db.connection_pool:
            raise ConnectionError("Пул подключений не инициализирован")

        conn = self.db.connection_pool.getconn()
        cursor = None

        try:
            conn.autocommit = False
            cursor = conn.cursor()

            # Устанавливаем таймаут для предотвращения зависания
            cursor.execute("SET statement_timeout = '60s'")
            print(f"[ImportService] Транзакция открыта с таймаутом 60s")

            for idx, event in enumerate(events, start=1):
                try:
                    self._validate_event(event, idx)
                    self._import_single_event_with_cursor(event, cursor)
                    imported_count += 1
                    print(f"[ImportService] Событие #{idx} импортировано успешно")

                except ImportValidationError as e:
                    # Ошибки валидации - не критичные, продолжаем импорт
                    errors.append(f"Событие #{idx}: {e.message}")
                    print(f"[ImportService] Ошибка валидации в событии #{idx}: {e.message}")

                except Exception as e:
                    # Критические ошибки (БД, сеть и т.д.) - откатываем все
                    error_msg = f"Событие #{idx}: Критическая ошибка - {str(e)}"
                    errors.append(error_msg)
                    print(f"[ImportService] КРИТИЧЕСКАЯ ОШИБКА в событии #{idx}: {e}")
                    import traceback
                    print(traceback.format_exc())
                    has_critical_error = True
                    break  # Прерываем импорт при критической ошибке

            # Коммитим только если нет критических ошибок
            if has_critical_error:
                print(f"[ImportService] Откат транзакции из-за критической ошибки")
                conn.rollback()
            else:
                print(f"[ImportService] Коммит транзакции: {imported_count} событий")
                conn.commit()

        except Exception as e:
            print(f"[ImportService] Исключение на уровне транзакции: {e}")
            import traceback
            print(traceback.format_exc())
            try:
                conn.rollback()
                print(f"[ImportService] Транзакция откачена")
            except Exception as rollback_error:
                print(f"[ImportService] Ошибка при откате транзакции: {rollback_error}")
            raise
        finally:
            if cursor:
                cursor.close()
            self.db.connection_pool.putconn(conn)
            print(f"[ImportService] Соединение возвращено в пул")
            # Очищаем кэши после импорта
            self._clear_caches()

        print(f"[ImportService] Импорт завершен: {imported_count} событий, {len(errors)} ошибок")
        return imported_count, errors

    def _preload_caches(self) -> None:
        """Предзагрузка справочников в кэш"""
        # Загружаем все виды спорта
        sports = self.db.fetch_all("SELECT sport_id, sport_name FROM sports")
        self._sports_cache = {s['sport_name']: s['sport_id'] for s in sports}

        # Загружаем все страны
        countries = self.db.fetch_all("SELECT country_id, country_name FROM countries")
        self._countries_cache = {c['country_name']: c['country_id'] for c in countries}

        # Загружаем все турниры
        tournaments = self.db.fetch_all(
            "SELECT tournament_id, tournament_name, sport_id, country_id FROM tournaments"
        )
        self._tournaments_cache = {
            (t['tournament_name'], t['sport_id'], t['country_id']): t['tournament_id']
            for t in tournaments
        }

        # Загружаем все команды
        teams = self.db.fetch_all("SELECT team_id, team_name, sport_id FROM teams")
        self._teams_cache = {
            (t['team_name'], t['sport_id']): t['team_id']
            for t in teams
        }

        # Загружаем всех букмекеров
        bookmakers = self.db.fetch_all("SELECT bookmaker_id, bookmaker_name FROM bookmakers")
        self._bookmakers_cache = {b['bookmaker_name']: b['bookmaker_id'] for b in bookmakers}

        # Загружаем все типы ставок
        bet_types = self.db.fetch_all("SELECT bet_type_id, bet_type_code FROM bet_types")
        self._bet_types_cache = {bt['bet_type_code']: bt['bet_type_id'] for bt in bet_types}

    def _clear_caches(self) -> None:
        """Очистка кэшей"""
        self._sports_cache.clear()
        self._countries_cache.clear()
        self._tournaments_cache.clear()
        self._teams_cache.clear()
        self._bookmakers_cache.clear()
        self._bet_types_cache.clear()

    def _validate_event(self, event: Dict[str, Any], index: int) -> None:
        if not isinstance(event, dict):
            raise ImportValidationError(
                f"Событие должно быть объектом, получен {type(event).__name__}"
            )

        missing_fields = [field for field in self.REQUIRED_FIELDS if not event.get(field)]
        if missing_fields:
            raise ImportValidationError(
                f"Отсутствуют обязательные поля: {', '.join(missing_fields)}",
                {"missing_fields": missing_fields, "required_fields": self.REQUIRED_FIELDS}
            )

        try:
            self._parse_date(event['date'])
        except ValueError as e:
            raise ImportValidationError(
                f"Неверный формат даты: {event['date']}. Ожидается формат: DD.MM.YYYY HH:MM или YYYY-MM-DD HH:MM",
                {"provided": event['date'], "error": str(e)}
            )

        if 'coefficients' in event:
            if not isinstance(event['coefficients'], dict):
                raise ImportValidationError(
                    "Поле 'coefficients' должно быть объектом"
                )

            for key in ['p1', 'x', 'p2']:
                if key in event['coefficients']:
                    try:
                        coef_value = float(event['coefficients'][key])
                        if coef_value <= 0:
                            raise ValueError("Коэффициент должен быть положительным числом")
                    except (ValueError, TypeError):
                        raise ImportValidationError(
                            f"Неверное значение коэффициента '{key}': {event['coefficients'][key]}"
                        )

    def _parse_date(self, date_str: str) -> datetime:
        formats = [
            '%d.%m.%Y %H:%M',
            '%Y-%m-%d %H:%M',
            '%d/%m/%Y %H:%M',
            '%Y/%m/%d %H:%M',
            '%d.%m.%Y %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Не удалось распознать формат даты: {date_str}")

    def _import_single_event(self, event: Dict[str, Any]) -> int:
        """Старый метод для обратной совместимости"""
        if not self.db.connection_pool:
            raise ConnectionError("Пул подключений не инициализирован")

        conn = self.db.connection_pool.getconn()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SET statement_timeout = '30s'")
            event_id = self._import_single_event_with_cursor(event, cursor)
            conn.commit()
            return event_id
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            self.db.connection_pool.putconn(conn)

    def _import_single_event_with_cursor(self, event: Dict[str, Any], cursor) -> int:
        """Импорт одного события с использованием переданного курсора (оптимизированная версия)"""
        sport_id = self._get_or_create_sport_cached(event['sport'], cursor)

        country_id = self._get_or_create_country_cached(event['country'], cursor)

        tournament_id = self._get_or_create_tournament_cached(
            event['tournament'], sport_id, country_id, cursor
        )

        team1_id = self._get_or_create_team_cached(event['team1'], sport_id, country_id, cursor)
        team2_id = self._get_or_create_team_cached(event['team2'], sport_id, country_id, cursor)

        event_datetime = self._parse_date(event['date'])

        # Проверяем существование события
        cursor.execute(
            """
            SELECT event_id FROM events
            WHERE team1_id = %s AND team2_id = %s
            AND tournament_id = %s AND event_datetime = %s
            """,
            (team1_id, team2_id, tournament_id, event_datetime)
        )
        result = cursor.fetchone()

        if result:
            event_id = result[0]
        else:
            cursor.execute(
                """
                INSERT INTO events (team1_id, team2_id, tournament_id, event_datetime)
                VALUES (%s, %s, %s, %s)
                RETURNING event_id
                """,
                (team1_id, team2_id, tournament_id, event_datetime)
            )
            result = cursor.fetchone()
            if not result:
                raise ImportValidationError("Не удалось создать событие")
            event_id = result[0]

        if 'coefficients' in event and event['coefficients']:
            bookmakers = event.get('bookmakers', ['Общий'])
            for bookmaker_name in bookmakers:
                bookmaker_id = self._get_or_create_bookmaker_cached(bookmaker_name, cursor)
                self._create_odds_records_cached(
                    event_id, bookmaker_id, event['coefficients'], cursor
                )

        return event_id

    def _get_or_create_sport(self, sport_name: str) -> int:
        query = "SELECT sport_id FROM sports WHERE sport_name = %s"
        result = self.db.fetch_one(query, (sport_name,))

        if result:
            return result['sport_id']

        insert_query = "INSERT INTO sports (sport_name) VALUES (%s) RETURNING sport_id"
        result = self.db.fetch_one(insert_query, (sport_name,))
        if result:
            return result['sport_id']
        raise ImportValidationError(f"Не удалось создать вид спорта: {sport_name}")

    def _get_or_create_sport_cached(self, sport_name: str, cursor) -> int:
        """Получение или создание спорта с кэшированием"""
        if sport_name in self._sports_cache:
            return self._sports_cache[sport_name]

        cursor.execute("SELECT sport_id FROM sports WHERE sport_name = %s", (sport_name,))
        result = cursor.fetchone()

        if result:
            sport_id = result[0]
        else:
            cursor.execute(
                "INSERT INTO sports (sport_name) VALUES (%s) RETURNING sport_id",
                (sport_name,)
            )
            result = cursor.fetchone()
            if not result:
                raise ImportValidationError(f"Не удалось создать вид спорта: {sport_name}")
            sport_id = result[0]

        self._sports_cache[sport_name] = sport_id
        return sport_id

    def _get_or_create_country(self, country_name: str) -> int:
        query = "SELECT country_id FROM countries WHERE country_name = %s"
        result = self.db.fetch_one(query, (country_name,))

        if result:
            return result['country_id']

        country_code = country_name[:3].upper()

        check_query = "SELECT country_id FROM countries WHERE country_code = %s"
        existing = self.db.fetch_one(check_query, (country_code,))

        if existing:
            import random
            country_code = f"{country_code[:2]}{random.randint(0, 9)}"

        insert_query = """
            INSERT INTO countries (country_name, country_code)
            VALUES (%s, %s)
            RETURNING country_id
        """
        result = self.db.fetch_one(insert_query, (country_name, country_code))
        if result:
            return result['country_id']
        raise ImportValidationError(f"Не удалось создать страну: {country_name}")

    def _get_or_create_country_cached(self, country_name: str, cursor) -> int:
        """Получение или создание страны с кэшированием"""
        if country_name in self._countries_cache:
            return self._countries_cache[country_name]

        cursor.execute("SELECT country_id FROM countries WHERE country_name = %s", (country_name,))
        result = cursor.fetchone()

        if result:
            country_id = result[0]
        else:
            country_code = country_name[:3].upper()

            cursor.execute("SELECT country_id FROM countries WHERE country_code = %s", (country_code,))
            existing = cursor.fetchone()

            if existing:
                import random
                country_code = f"{country_code[:2]}{random.randint(0, 9)}"

            cursor.execute(
                "INSERT INTO countries (country_name, country_code) VALUES (%s, %s) RETURNING country_id",
                (country_name, country_code)
            )
            result = cursor.fetchone()
            if not result:
                raise ImportValidationError(f"Не удалось создать страну: {country_name}")
            country_id = result[0]

        self._countries_cache[country_name] = country_id
        return country_id

    def _get_or_create_tournament(self, tournament_name: str, sport_id: int, country_id: int) -> int:
        query = """
            SELECT tournament_id FROM tournaments
            WHERE tournament_name = %s AND sport_id = %s AND country_id = %s
        """
        result = self.db.fetch_one(query, (tournament_name, sport_id, country_id))

        if result:
            return result['tournament_id']

        insert_query = """
            INSERT INTO tournaments (tournament_name, sport_id, country_id)
            VALUES (%s, %s, %s)
            RETURNING tournament_id
        """
        result = self.db.fetch_one(insert_query, (tournament_name, sport_id, country_id))
        if result:
            return result['tournament_id']
        raise ImportValidationError(f"Не удалось создать турнир: {tournament_name}")

    def _get_or_create_tournament_cached(self, tournament_name: str, sport_id: int, country_id: int, cursor) -> int:
        """Получение или создание турнира с кэшированием"""
        cache_key = (tournament_name, sport_id, country_id)
        if cache_key in self._tournaments_cache:
            return self._tournaments_cache[cache_key]

        cursor.execute(
            "SELECT tournament_id FROM tournaments WHERE tournament_name = %s AND sport_id = %s AND country_id = %s",
            (tournament_name, sport_id, country_id)
        )
        result = cursor.fetchone()

        if result:
            tournament_id = result[0]
        else:
            cursor.execute(
                "INSERT INTO tournaments (tournament_name, sport_id, country_id) VALUES (%s, %s, %s) RETURNING tournament_id",
                (tournament_name, sport_id, country_id)
            )
            result = cursor.fetchone()
            if not result:
                raise ImportValidationError(f"Не удалось создать турнир: {tournament_name}")
            tournament_id = result[0]

        self._tournaments_cache[cache_key] = tournament_id
        return tournament_id

    def _get_or_create_team(self, team_name: str, sport_id: int, country_id: int) -> int:
        query = """
            SELECT team_id FROM teams
            WHERE team_name = %s AND sport_id = %s
        """
        result = self.db.fetch_one(query, (team_name, sport_id))

        if result:
            return result['team_id']

        insert_query = """
            INSERT INTO teams (team_name, sport_id, country_id)
            VALUES (%s, %s, %s)
            RETURNING team_id
        """
        result = self.db.fetch_one(insert_query, (team_name, sport_id, country_id))
        if result:
            return result['team_id']
        raise ImportValidationError(f"Не удалось создать команду: {team_name}")

    def _get_or_create_team_cached(self, team_name: str, sport_id: int, country_id: int, cursor) -> int:
        """Получение или создание команды с кэшированием"""
        cache_key = (team_name, sport_id)
        if cache_key in self._teams_cache:
            return self._teams_cache[cache_key]

        cursor.execute(
            "SELECT team_id FROM teams WHERE team_name = %s AND sport_id = %s",
            (team_name, sport_id)
        )
        result = cursor.fetchone()

        if result:
            team_id = result[0]
        else:
            cursor.execute(
                "INSERT INTO teams (team_name, sport_id, country_id) VALUES (%s, %s, %s) RETURNING team_id",
                (team_name, sport_id, country_id)
            )
            result = cursor.fetchone()
            if not result:
                raise ImportValidationError(f"Не удалось создать команду: {team_name}")
            team_id = result[0]

        self._teams_cache[cache_key] = team_id
        return team_id

    def _create_event(self, team1_id: int, team2_id: int, tournament_id: int,
                     event_datetime: datetime) -> int:
        check_query = """
            SELECT event_id FROM events
            WHERE team1_id = %s AND team2_id = %s
            AND tournament_id = %s AND event_datetime = %s
        """
        result = self.db.fetch_one(check_query, (team1_id, team2_id, tournament_id, event_datetime))

        if result:
            return result['event_id']

        insert_query = """
            INSERT INTO events (team1_id, team2_id, tournament_id, event_datetime)
            VALUES (%s, %s, %s, %s)
            RETURNING event_id
        """
        result = self.db.fetch_one(insert_query, (team1_id, team2_id, tournament_id, event_datetime))
        if result:
            return result['event_id']
        raise ImportValidationError("Не удалось создать событие")

    def _create_event_cached(self, team1_id: int, team2_id: int, tournament_id: int,
                            event_datetime: datetime, cursor) -> int:
        """Создание события с использованием курсора"""
        cursor.execute(
            """
            SELECT event_id FROM events
            WHERE team1_id = %s AND team2_id = %s
            AND tournament_id = %s AND event_datetime = %s
            """,
            (team1_id, team2_id, tournament_id, event_datetime)
        )
        result = cursor.fetchone()

        if result:
            return result[0]

        cursor.execute(
            """
            INSERT INTO events (team1_id, team2_id, tournament_id, event_datetime)
            VALUES (%s, %s, %s, %s)
            RETURNING event_id
            """,
            (team1_id, team2_id, tournament_id, event_datetime)
        )
        result = cursor.fetchone()
        if not result:
            raise ImportValidationError("Не удалось создать событие")
        return result[0]

    def _get_or_create_bookmaker(self, bookmaker_name: str) -> int:
        query = "SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = %s"
        result = self.db.fetch_one(query, (bookmaker_name,))

        if result:
            return result['bookmaker_id']

        insert_query = """
            INSERT INTO bookmakers (bookmaker_name)
            VALUES (%s)
            RETURNING bookmaker_id
        """
        result = self.db.fetch_one(insert_query, (bookmaker_name,))
        if result:
            return result['bookmaker_id']
        raise ImportValidationError(f"Не удалось создать букмекера: {bookmaker_name}")

    def _get_or_create_bookmaker_cached(self, bookmaker_name: str, cursor) -> int:
        """Получение или создание букмекера с кэшированием"""
        if bookmaker_name in self._bookmakers_cache:
            return self._bookmakers_cache[bookmaker_name]

        cursor.execute("SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = %s", (bookmaker_name,))
        result = cursor.fetchone()

        if result:
            bookmaker_id = result[0]
        else:
            cursor.execute(
                "INSERT INTO bookmakers (bookmaker_name) VALUES (%s) RETURNING bookmaker_id",
                (bookmaker_name,)
            )
            result = cursor.fetchone()
            if not result:
                raise ImportValidationError(f"Не удалось создать букмекера: {bookmaker_name}")
            bookmaker_id = result[0]

        self._bookmakers_cache[bookmaker_name] = bookmaker_id
        return bookmaker_id

    def _get_bet_type_id(self, bet_code: str) -> Optional[int]:
        query = "SELECT bet_type_id FROM bet_types WHERE bet_type_code = %s"
        result = self.db.fetch_one(query, (bet_code,))
        return result['bet_type_id'] if result else None

    def _create_odds_records(self, event_id: int, bookmaker_id: int,
                           coefficients: Dict[str, float]) -> None:
        coef_mapping = {
            'p1': 'win_1',
            'x': 'draw',
            'p2': 'win_2'
        }

        for coef_key, bet_code in coef_mapping.items():
            if coef_key in coefficients:
                bet_type_id = self._get_bet_type_id(bet_code)

                if not bet_type_id:
                    bet_type_id = self._create_bet_type(bet_code)

                if bet_type_id:
                    odds_value = coefficients[coef_key]

                    check_query = """
                        SELECT odds_record_id FROM odds_records
                        WHERE event_id = %s AND bookmaker_id = %s
                        AND bet_type_id = %s AND bet_parameter IS NULL
                        ORDER BY recorded_at DESC LIMIT 1
                    """
                    existing = self.db.fetch_one(check_query, (event_id, bookmaker_id, bet_type_id))

                    if not existing:
                        insert_query = """
                            INSERT INTO odds_records
                            (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value)
                            VALUES (%s, %s, %s, NULL, %s)
                        """
                        self.db.execute_query(insert_query, (event_id, bookmaker_id, bet_type_id, odds_value))

    def _create_odds_records_cached(self, event_id: int, bookmaker_id: int,
                                   coefficients: Dict[str, float], cursor) -> None:
        """Создание записей коэффициентов с использованием курсора и кэша (оптимизированная версия с batch insert)"""
        coef_mapping = {
            'p1': 'win_1',
            'x': 'draw',
            'p2': 'win_2'
        }

        # Собираем все данные для batch-вставки
        records_to_insert = []

        for coef_key, bet_code in coef_mapping.items():
            if coef_key in coefficients:
                bet_type_id = self._get_bet_type_id_cached(bet_code, cursor)

                if not bet_type_id:
                    bet_type_id = self._create_bet_type_cached(bet_code, cursor)

                if bet_type_id:
                    odds_value = coefficients[coef_key]

                    # Проверяем существование записи
                    cursor.execute(
                        """
                        SELECT odds_record_id FROM odds_records
                        WHERE event_id = %s AND bookmaker_id = %s
                        AND bet_type_id = %s AND bet_parameter IS NULL
                        ORDER BY recorded_at DESC LIMIT 1
                        """,
                        (event_id, bookmaker_id, bet_type_id)
                    )
                    existing = cursor.fetchone()

                    if not existing:
                        records_to_insert.append((event_id, bookmaker_id, bet_type_id, odds_value))

        # Если есть записи для вставки, делаем batch INSERT
        if records_to_insert:
            values_placeholders = ','.join(['(%s, %s, %s, NULL, %s)'] * len(records_to_insert))
            flat_values = [val for rec in records_to_insert for val in rec]

            cursor.execute(
                f"""
                INSERT INTO odds_records
                (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value)
                VALUES {values_placeholders}
                """,
                flat_values
            )

    def _create_bet_type(self, bet_code: str) -> int:
        bet_names = {
            'win_1': 'Победа 1',
            'draw': 'Ничья',
            'win_2': 'Победа 2'
        }

        bet_name = bet_names.get(bet_code, bet_code)

        insert_query = """
            INSERT INTO bet_types (bet_type_code, bet_type_name, has_parameter)
            VALUES (%s, %s, FALSE)
            RETURNING bet_type_id
        """
        result = self.db.fetch_one(insert_query, (bet_code, bet_name))
        if result:
            return result['bet_type_id']
        raise ImportValidationError(f"Не удалось создать тип ставки: {bet_code}")

    def _get_bet_type_id_cached(self, bet_code: str, cursor) -> Optional[int]:
        """Получение ID типа ставки с кэшированием"""
        if bet_code in self._bet_types_cache:
            return self._bet_types_cache[bet_code]

        cursor.execute("SELECT bet_type_id FROM bet_types WHERE bet_type_code = %s", (bet_code,))
        result = cursor.fetchone()

        if result:
            bet_type_id = result[0]
            self._bet_types_cache[bet_code] = bet_type_id
            return bet_type_id

        return None

    def _create_bet_type_cached(self, bet_code: str, cursor) -> int:
        """Создание нового типа ставки с использованием курсора"""
        bet_names = {
            'win_1': 'Победа 1',
            'draw': 'Ничья',
            'win_2': 'Победа 2'
        }

        bet_name = bet_names.get(bet_code, bet_code)

        cursor.execute(
            """
            INSERT INTO bet_types (bet_type_code, bet_type_name, has_parameter)
            VALUES (%s, %s, FALSE)
            RETURNING bet_type_id
            """,
            (bet_code, bet_name)
        )
        result = cursor.fetchone()
        if not result:
            raise ImportValidationError(f"Не удалось создать тип ставки: {bet_code}")

        bet_type_id = result[0]
        self._bet_types_cache[bet_code] = bet_type_id
        return bet_type_id

    @staticmethod
    def get_format_example_json() -> str:
        return '''{
  "events": [
    {
      "sport": "Футбол",
      "tournament": "Российская Премьер-Лига",
      "country": "Россия",
      "team1": "Зенит",
      "team2": "Спартак",
      "date": "15.03.2025 19:00",
      "bookmakers": ["1xBet", "Fonbet"],
      "coefficients": {
        "p1": 1.85,
        "x": 3.45,
        "p2": 4.20
      }
    }
  ]
}'''

    @staticmethod
    def get_format_example_csv() -> str:
        return '''sport,tournament,country,team1,team2,date,bookmakers,coef_p1,coef_x,coef_p2
Футбол,Российская Премьер-Лига,Россия,Зенит,Спартак,15.03.2025 19:00,"1xBet,Fonbet",1.85,3.45,4.20
Баскетбол,NBA,США,Lakers,Warriors,20.03.2025 21:30,BetBoom,2.10,0,1.75'''

    @staticmethod
    def get_required_fields() -> List[str]:
        return EventImportService.REQUIRED_FIELDS.copy()
