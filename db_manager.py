import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2 import Error, extensions, pool
from psycopg2.extras import RealDictCursor

from config import DatabaseConfig


class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection_pool: Optional[pool.SimpleConnectionPool] = None
        self._initialized = False

    def connect(self) -> None:
        """Создание пула подключений к базе данных"""
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password
            )
            print("✓ Подключение к PostgreSQL установлено")
        except Error as e:
            print(f"✗ Ошибка подключения к PostgreSQL: {e}")
            raise

    def initialize(self) -> None:
        """Инициализация базы данных: подключение, создание таблиц, заполнение данными"""
        if self._initialized:
            return

        try:
            # Подключение к БД
            self.connect()

            # Проверка существования таблиц
            if not self.tables_exist():
                print("⚠ Таблицы не найдены. Создание структуры БД...")
                self.create_tables()
                self.insert_mock_data()
            else:
                print("✓ Таблицы уже существуют")

            self._initialized = True
        except Exception as e:
            print(f"✗ Ошибка инициализации БД: {e}")
            raise

    def tables_exist(self) -> bool:
        """Проверка существования основных таблиц"""
        try:
            query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'events'
                );
            """
            result = self.fetch_one(query)
            return result['exists'] if result else False
        except Error:
            return False

    def create_tables(self) -> None:
        """Создание таблиц из SQL-скрипта"""
        script_path = os.path.join(os.path.dirname(__file__), 'database', 'scripts', 'create_tables.sql')
        self.execute_script(script_path)

    def insert_mock_data(self) -> None:
        """Заполнение таблиц моковыми данными"""
        script_path = os.path.join(os.path.dirname(__file__), 'database', 'scripts', 'insert_mock_data.sql')
        self.execute_script(script_path)

    @contextmanager
    def get_cursor(self, dict_cursor: bool = False):
        """Контекстный менеджер для получения курсора"""
        if not self.connection_pool:
            raise ConnectionError("Пул подключений не инициализирован")

        conn: extensions.connection = self.connection_pool.getconn()
        cursor_factory = RealDictCursor if dict_cursor else None

        try:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            yield cursor
            conn.commit()
        except Error as e:
            conn.rollback()
            print(f"✗ Ошибка выполнения запроса: {e}")
            raise
        finally:
            cursor.close()
            self.connection_pool.putconn(conn)

    def execute_script(self, script_path: str) -> None:
        """Выполнение SQL-скрипта из файла"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            with self.get_cursor() as cursor:
                cursor.execute(sql_script)

            print(f"✓ Скрипт {script_path} выполнен успешно")
        except FileNotFoundError:
            print(f"✗ Файл {script_path} не найден")
            raise
        except Error as e:
            print(f"✗ Ошибка выполнения скрипта: {e}")
            raise

    def execute_query(self, query: str, params: tuple = None) -> None:
        """Выполнение запроса без возврата данных (INSERT, UPDATE, DELETE)"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)

    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Выполнение SELECT запроса и возврат всех результатов"""
        with self.get_cursor(dict_cursor=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Выполнение SELECT запроса и возврат одного результата"""
        with self.get_cursor(dict_cursor=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Получение всех событий с подробной информацией"""
        query = """
            SELECT
                e.event_id,
                s.sport_name,
                t.tournament_name,
                c.country_name,
                team1.team_id as team1_id,
                team1.team_name as team1_name,
                team2.team_id as team2_id,
                team2.team_name as team2_name,
                e.event_datetime,
                e.is_finished,
                e.winner_team_id,
                e.team1_score,
                e.team2_score,
                COUNT(DISTINCT or1.odds_record_id) as records_count
            FROM events e
            JOIN tournaments t ON e.tournament_id = t.tournament_id
            JOIN sports s ON t.sport_id = s.sport_id
            JOIN countries c ON t.country_id = c.country_id
            JOIN teams team1 ON e.team1_id = team1.team_id
            JOIN teams team2 ON e.team2_id = team2.team_id
            LEFT JOIN odds_records or1 ON e.event_id = or1.event_id
            GROUP BY e.event_id, s.sport_name, t.tournament_name, c.country_name,
                     team1.team_id, team1.team_name, team2.team_id, team2.team_name,
                     e.event_datetime, e.is_finished, e.winner_team_id, e.team1_score, e.team2_score
            ORDER BY e.event_datetime;
        """
        return self.fetch_all(query)

    def get_event_bookmakers(self, event_id: int) -> List[str]:
        """Получение списка букмекеров для события"""
        query = """
            SELECT DISTINCT b.bookmaker_name
            FROM odds_records orr
            JOIN bookmakers b ON orr.bookmaker_id = b.bookmaker_id
            WHERE orr.event_id = %s
            ORDER BY b.bookmaker_name;
        """
        result = self.fetch_all(query, (event_id,))
        return [row['bookmaker_name'] for row in result]

    def get_latest_coefficients(self, event_id: int) -> Dict[str, float]:
        """Получение последних коэффициентов П1, X, П2 для события"""
        query = """
            WITH latest_odds AS (
                SELECT
                    orr.event_id,
                    bt.bet_type_code,
                    orr.odds_value,
                    ROW_NUMBER() OVER (PARTITION BY orr.event_id, bt.bet_type_code
                                       ORDER BY orr.recorded_at DESC) as rn
                FROM odds_records orr
                JOIN bet_types bt ON orr.bet_type_id = bt.bet_type_id
                WHERE orr.event_id = %s
                  AND bt.bet_type_code IN ('win_1', 'draw', 'win_2')
                  AND orr.bet_parameter IS NULL
            )
            SELECT bet_type_code, odds_value
            FROM latest_odds
            WHERE rn = 1;
        """
        result = self.fetch_all(query, (event_id,))

        coefficients = {'p1': 0.0, 'x': 0.0, 'p2': 0.0}
        for row in result:
            if row['bet_type_code'] == 'win_1':
                coefficients['p1'] = float(row['odds_value'])
            elif row['bet_type_code'] == 'draw':
                coefficients['x'] = float(row['odds_value'])
            elif row['bet_type_code'] == 'win_2':
                coefficients['p2'] = float(row['odds_value'])

        return coefficients

    def close(self) -> None:
        """Закрытие всех соединений"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ Все подключения закрыты")
