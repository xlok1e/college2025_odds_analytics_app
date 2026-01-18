from typing import List, Optional

from src.models.event import Coefficients, Event


class EventRepository:
    """Репозиторий для работы с событиями из базы данных"""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_all_events(self) -> List[Event]:
        """Получить все события из базы данных"""
        events_data = self.db.get_all_events()
        events = []

        for event_data in events_data:
            # Получаем букмекеров для события
            bookmakers = self.db.get_event_bookmakers(event_data['event_id'])

            # Получаем последние коэффициенты
            coefficients_data = self.db.get_latest_coefficients(event_data['event_id'])

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
                bookmakers=bookmakers,
                coefficients=Coefficients(
                    p1=coefficients_data.get('p1', 0.0),
                    x=coefficients_data.get('x', 0.0),
                    p2=coefficients_data.get('p2', 0.0)
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
