from typing import List, Optional

from src.models.event import Coefficients, Event


class EventRepository:
    """Репозиторий для работы с событиями из базы данных"""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_all_events(self) -> List[Event]:
        """Получить все события из базы данных (оптимизированная версия)"""

        # Используем оптимизированный запрос, который получает все данные за раз
        query = """
            WITH event_bookmakers AS (
                SELECT
                    orr.event_id,
                    array_agg(DISTINCT b.bookmaker_name ORDER BY b.bookmaker_name) as bookmakers
                FROM odds_records orr
                JOIN bookmakers b ON orr.bookmaker_id = b.bookmaker_id
                GROUP BY orr.event_id
            ),
            latest_odds AS (
                SELECT
                    orr.event_id,
                    bt.bet_type_code,
                    orr.odds_value,
                    ROW_NUMBER() OVER (PARTITION BY orr.event_id, bt.bet_type_code
                                       ORDER BY orr.recorded_at DESC) as rn
                FROM odds_records orr
                JOIN bet_types bt ON orr.bet_type_id = bt.bet_type_id
                WHERE bt.bet_type_code IN ('win_1', 'draw', 'win_2')
                  AND orr.bet_parameter IS NULL
            ),
            coefficients AS (
                SELECT
                    event_id,
                    MAX(CASE WHEN bet_type_code = 'win_1' THEN odds_value END) as p1,
                    MAX(CASE WHEN bet_type_code = 'draw' THEN odds_value END) as x,
                    MAX(CASE WHEN bet_type_code = 'win_2' THEN odds_value END) as p2
                FROM latest_odds
                WHERE rn = 1
                GROUP BY event_id
            )
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
                COUNT(DISTINCT or1.odds_record_id) as records_count,
                COALESCE(eb.bookmakers, ARRAY[]::text[]) as bookmakers,
                COALESCE(coef.p1, 0.0) as p1,
                COALESCE(coef.x, 0.0) as x,
                COALESCE(coef.p2, 0.0) as p2
            FROM events e
            JOIN tournaments t ON e.tournament_id = t.tournament_id
            JOIN sports s ON t.sport_id = s.sport_id
            JOIN countries c ON t.country_id = c.country_id
            JOIN teams team1 ON e.team1_id = team1.team_id
            JOIN teams team2 ON e.team2_id = team2.team_id
            LEFT JOIN odds_records or1 ON e.event_id = or1.event_id
            LEFT JOIN event_bookmakers eb ON e.event_id = eb.event_id
            LEFT JOIN coefficients coef ON e.event_id = coef.event_id
            GROUP BY e.event_id, s.sport_name, t.tournament_name, c.country_name,
                     team1.team_id, team1.team_name, team2.team_id, team2.team_name,
                     e.event_datetime, e.is_finished, e.winner_team_id, e.team1_score, e.team2_score,
                     eb.bookmakers, coef.p1, coef.x, coef.p2
            ORDER BY e.event_datetime;
        """

        events_data = self.db.fetch_all(query)
        events = []

        for event_data in events_data:
            # Форматируем дату
            event_datetime = event_data['event_datetime']
            formatted_date = event_datetime.strftime('%d.%m.%Y %H:%M')

            # Определяем победителя
            winner = None
            if event_data.get('is_finished') and event_data.get('winner_team_id'):
                if event_data['winner_team_id'] == event_data['team1_id']:
                    winner = event_data['team1_name']
                elif event_data['winner_team_id'] == event_data['team2_id']:
                    winner = event_data['team2_name']
                else:
                    winner = "Ничья"

            # Создаем объект Event
            event = Event(
                id=event_data['event_id'],
                sport=event_data['sport_name'],
                tournament=event_data['tournament_name'],
                country=event_data['country_name'],
                team1=event_data['team1_name'],
                team2=event_data['team2_name'],
                date=formatted_date,
                records_count=event_data['records_count'],
                bookmakers=list(event_data.get('bookmakers', [])),
                coefficients=Coefficients(
                    p1=float(event_data.get('p1', 0.0)),
                    x=float(event_data.get('x', 0.0)),
                    p2=float(event_data.get('p2', 0.0))
                ),
                is_finished=event_data.get('is_finished', False),
                winner=winner,
                team1_score=event_data.get('team1_score'),
                team2_score=event_data.get('team2_score')
            )
            events.append(event)

        return events

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Получить событие по ID с оптимизированным запросом"""
        event_data = self.db.get_event_with_details(event_id)

        if not event_data:
            return None

        # Форматируем дату
        event_datetime = event_data['event_datetime']
        formatted_date = event_datetime.strftime('%d.%m.%Y %H:%M')

        # Определяем победителя
        winner = None
        if event_data.get('is_finished') and event_data.get('winner_team_id'):
            if event_data['winner_team_id'] == event_data['team1_id']:
                winner = event_data['team1_name']
            elif event_data['winner_team_id'] == event_data['team2_id']:
                winner = event_data['team2_name']
            else:
                winner = "Ничья"

        # Создаем объект Event
        event = Event(
            id=event_data['event_id'],
            sport=event_data['sport_name'],
            tournament=event_data['tournament_name'],
            country=event_data['country_name'],
            team1=event_data['team1_name'],
            team2=event_data['team2_name'],
            date=formatted_date,
            records_count=event_data['records_count'],
            bookmakers=list(event_data.get('bookmakers', [])),
            coefficients=Coefficients(
                p1=float(event_data.get('p1', 0.0)),
                x=float(event_data.get('x', 0.0)),
                p2=float(event_data.get('p2', 0.0))
            ),
            is_finished=event_data.get('is_finished', False),
            winner=winner,
            team1_score=event_data.get('team1_score'),
            team2_score=event_data.get('team2_score')
        )

        return event

    def delete_event(self, event_id: int) -> bool:
        """Удалить событие по ID

        Удаляет событие и все связанные записи коэффициентов
        благодаря ON DELETE CASCADE в схеме БД
        """
        try:
            query = "DELETE FROM events WHERE event_id = %s RETURNING event_id"
            result = self.db.fetch_all(query, (event_id,))

            if result and len(result) > 0:
                print(f"✓ Событие {event_id} успешно удалено")
                return True
            else:
                print(f"✗ Событие {event_id} не найдено")
                return False

        except Exception as e:
            print(f"✗ Ошибка удаления события {event_id}: {e}")
            return False
